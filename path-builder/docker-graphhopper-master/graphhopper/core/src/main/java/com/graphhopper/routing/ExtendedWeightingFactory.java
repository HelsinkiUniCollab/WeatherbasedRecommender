package com.graphhopper.routing;

import com.graphhopper.config.Profile;
import com.graphhopper.routing.ev.BooleanEncodedValue;
import com.graphhopper.routing.ev.DecimalEncodedValue;
import com.graphhopper.routing.ev.EnumEncodedValue;
import com.graphhopper.routing.ev.RoadAccess;
import com.graphhopper.routing.ev.TurnCost;
import com.graphhopper.routing.ev.VehicleAccess;
import com.graphhopper.routing.ev.VehiclePriority;
import com.graphhopper.routing.ev.VehicleSpeed;
import com.graphhopper.routing.util.EncodingManager;
import com.graphhopper.routing.util.VehicleEncodedValues;
import com.graphhopper.routing.weighting.AQIWeighting;
import com.graphhopper.routing.weighting.DefaultTurnCostProvider;
import com.graphhopper.routing.weighting.FastestWeighting;
import com.graphhopper.routing.weighting.PriorityWeighting;
import com.graphhopper.routing.weighting.ShortFastestWeighting;
import com.graphhopper.routing.weighting.ShortestWeighting;
import com.graphhopper.routing.weighting.TurnCostProvider;
import com.graphhopper.routing.weighting.Weighting;
import com.graphhopper.routing.weighting.custom.CustomModelParser;
import com.graphhopper.routing.weighting.custom.CustomProfile;
import com.graphhopper.routing.weighting.custom.CustomWeighting;
import com.graphhopper.storage.BaseGraph;
import com.graphhopper.util.CustomModel;
import com.graphhopper.util.PMap;
import com.graphhopper.util.Parameters;

import ucar.ma2.InvalidRangeException;
import ucar.units.UnitException;

import static com.graphhopper.routing.weighting.FastestWeighting.DESTINATION_FACTOR;
import static com.graphhopper.routing.weighting.FastestWeighting.PRIVATE_FACTOR;
import static com.graphhopper.routing.weighting.TurnCostProvider.NO_TURN_COST_PROVIDER;
import static com.graphhopper.routing.weighting.Weighting.INFINITE_U_TURN_COSTS;
import static com.graphhopper.util.Helper.toLowerCase;

import java.io.IOException;

public class ExtendedWeightingFactory implements WeightingFactory {

    private final BaseGraph graph;
    private final EncodingManager encodingManager;

    public ExtendedWeightingFactory(BaseGraph graph, EncodingManager encodingManager) {
        this.graph = graph;
        this.encodingManager = encodingManager;
    }

    @Override
    public Weighting createWeighting(Profile profile, PMap requestHints, boolean disableTurnCosts) {
        // TODO: Move the filepath definition to more sensible place
        String filename = "/graphhopper/data/aqi_data.nc";

        PMap hints = new PMap();
        hints.putAll(profile.getHints());
        hints.putAll(requestHints);

        final String vehicle = profile.getVehicle();
        if (isOutdoorVehicle(vehicle)) {
            hints.putObject(PRIVATE_FACTOR, hints.getDouble(PRIVATE_FACTOR, 1.2));
        } else {
            hints.putObject(DESTINATION_FACTOR, hints.getDouble(DESTINATION_FACTOR, 10));
            hints.putObject(PRIVATE_FACTOR, hints.getDouble(PRIVATE_FACTOR, 10));
        }
        TurnCostProvider turnCostProvider;
        if (profile.isTurnCosts() && !disableTurnCosts) {
            DecimalEncodedValue turnCostEnc = encodingManager.getDecimalEncodedValue(TurnCost.key(vehicle));
            if (turnCostEnc == null)
                throw new IllegalArgumentException("Vehicle " + vehicle + " does not support turn costs");
            int uTurnCosts = hints.getInt(Parameters.Routing.U_TURN_COSTS, INFINITE_U_TURN_COSTS);
            turnCostProvider = new DefaultTurnCostProvider(turnCostEnc, graph.getTurnCostStorage(), uTurnCosts);
        } else {
            turnCostProvider = NO_TURN_COST_PROVIDER;
        }

        String weightingStr = toLowerCase(profile.getWeighting());
        if (weightingStr.isEmpty())
            throw new IllegalArgumentException("You have to specify a weighting");

        Weighting weighting = null;
        BooleanEncodedValue accessEnc = encodingManager.getBooleanEncodedValue(VehicleAccess.key(vehicle));
        DecimalEncodedValue speedEnc = encodingManager.getDecimalEncodedValue(VehicleSpeed.key(vehicle));
        DecimalEncodedValue priorityEnc = encodingManager.hasEncodedValue(VehiclePriority.key(vehicle))
                ? encodingManager.getDecimalEncodedValue(VehiclePriority.key(vehicle))
                : null;

        if (CustomWeighting.NAME.equalsIgnoreCase(weightingStr)) {
            if (!(profile instanceof CustomProfile))
                throw new IllegalArgumentException(
                        "custom weighting requires a CustomProfile but was profile=" + profile.getName());
            CustomModel queryCustomModel = requestHints.getObject(CustomModel.KEY, null);
            CustomProfile customProfile = (CustomProfile) profile;

            queryCustomModel = CustomModel.merge(customProfile.getCustomModel(), queryCustomModel);
            weighting = CustomModelParser.createWeighting(accessEnc, speedEnc,
                    priorityEnc, encodingManager, turnCostProvider, queryCustomModel);
        } else if ("shortest".equalsIgnoreCase(weightingStr)) {
            weighting = new ShortestWeighting(accessEnc, speedEnc, turnCostProvider);
        } else if ("fastest".equalsIgnoreCase(weightingStr)) {
            if (!encodingManager.hasEncodedValue(RoadAccess.KEY))
                throw new IllegalArgumentException("The fastest weighting requires road_access");
            EnumEncodedValue<RoadAccess> roadAccessEnc = encodingManager.getEnumEncodedValue(RoadAccess.KEY,
                    RoadAccess.class);
            if (priorityEnc != null)
                weighting = new PriorityWeighting(accessEnc, speedEnc, priorityEnc, roadAccessEnc, hints,
                        turnCostProvider);
            else
                weighting = new FastestWeighting(accessEnc, speedEnc, roadAccessEnc, hints, turnCostProvider);
        } else if ("curvature".equalsIgnoreCase(weightingStr)) {
            throw new IllegalArgumentException(
                    "The curvature weighting is no longer supported since 7.0. Use a custom " +
                            "model with the EncodedValue 'curvature' instead");
        } else if ("short_fastest".equalsIgnoreCase(weightingStr)) {
            if (!encodingManager.hasEncodedValue(RoadAccess.KEY))
                throw new IllegalArgumentException("The short_fastest weighting requires road_access");
            EnumEncodedValue<RoadAccess> roadAccessEnc = encodingManager.getEnumEncodedValue(RoadAccess.KEY,
                    RoadAccess.class);
            weighting = new ShortFastestWeighting(accessEnc, speedEnc, roadAccessEnc, hints, turnCostProvider);
        } else if ("clean".equalsIgnoreCase(weightingStr)) {

            try {
                weighting = new AQIWeighting(accessEnc, speedEnc, turnCostProvider,
                        filename);
            } catch (IllegalArgumentException | NullPointerException | IOException | InvalidRangeException | UnitException e) {
                System.out.println("Creating AQI weighting failed!");
                e.printStackTrace();
                System.out.println("Working Directory = " + System.getProperty("user.dir"));
                weighting = null;
            }
        }

        if (weighting == null)
            throw new IllegalArgumentException("Weighting '" + weightingStr + "' not supported");

        return weighting;

        // PMap hints = new PMap();
        // hints.putAll(profile.getHints());
        // hints.putAll(pHints);

        // final String vehicle = profile.getVehicle();

        // BooleanEncodedValue accessEnc =
        // encodingManager.getBooleanEncodedValue(VehicleAccess.key(vehicle));
        // DecimalEncodedValue speedEnc =
        // encodingManager.getDecimalEncodedValue(VehicleSpeed.key(vehicle));
        // DecimalEncodedValue priorityEnc =
        // encodingManager.hasEncodedValue(VehiclePriority.key(vehicle))
        // ? encodingManager.getDecimalEncodedValue(VehiclePriority.key(vehicle))
        // : null;

        // TurnCostProvider turnCostProvider = NO_TURN_COST_PROVIDER;

        // Weighting AQIWeighting;
        // try {
        // AQIWeighting = new AQIWeighting(accessEnc, speedEnc, turnCostProvider,
        // filename);
        // } catch (IllegalArgumentException | NullPointerException | IOException |
        // InvalidRangeException e) {
        // System.out.println("-----------------------------");
        // System.out.println("******************************");
        // System.out.println("******************************");
        // System.out.println("******************************");
        // System.out.println("******************************");
        // System.out.println("Creating AQI weighting failed!");
        // System.out.println("-----------------------------");
        // System.out.println("******************************");
        // System.out.println("******************************");
        // System.out.println("******************************");
        // System.out.println("******************************");
        // e.printStackTrace();
        // System.out.println("Working Directory = " + System.getProperty("user.dir"));
        // AQIWeighting = null;
        // }

        // return AQIWeighting;
    }

    public boolean isOutdoorVehicle(String name) {
        return VehicleEncodedValues.OUTDOOR_VEHICLES.contains(name);
    }
}
