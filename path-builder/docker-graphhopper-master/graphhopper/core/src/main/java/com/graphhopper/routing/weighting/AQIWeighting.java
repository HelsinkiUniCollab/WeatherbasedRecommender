package com.graphhopper.routing.weighting;

import java.io.IOException;
import java.time.LocalDate;
import java.time.LocalTime;
import java.util.Date;

import com.graphhopper.routing.ev.BooleanEncodedValue;
import com.graphhopper.routing.ev.DecimalEncodedValue;
import com.graphhopper.util.EdgeIteratorState;
import com.graphhopper.util.FetchMode;
import com.graphhopper.util.shapes.GHPoint3D;

import ucar.ma2.Array;
import ucar.ma2.Index;
import ucar.ma2.InvalidRangeException;
import ucar.nc2.NetcdfFile;
import ucar.nc2.NetcdfFiles;
import ucar.nc2.Variable;
import ucar.nc2.units.DateUnit;
import ucar.units.UnitException;

public class AQIWeighting extends AbstractWeighting {
    protected final static double SPEED_CONV = 3.6;

    private final double maxSpeed;
    private final Array lat;
    private final Array lon;
    // private final Array time;
    private final Array aqi;
    private final Index aqiIndex;

    public AQIWeighting(BooleanEncodedValue accessEnc, DecimalEncodedValue speedEnc,
            TurnCostProvider turnCostProvider, String ncFilename)
            throws IOException, IllegalArgumentException, InvalidRangeException, NullPointerException, UnitException {
        super(accessEnc, speedEnc, turnCostProvider);
        maxSpeed = speedEnc.getMaxOrMaxStorableDecimal() / SPEED_CONV;

        // Read in the AQI data
        try (NetcdfFile ncfile = NetcdfFiles.open(ncFilename)) {
            // Read data for one timestep
            lat = get1DVariableData("lat", ncfile);
            lon = get1DVariableData("lon", ncfile);
            // time = get1DVariableData("time", ncfile);
            aqi = getAQIData(ncfile);
            aqiIndex = aqi.getIndex();
        }

    }

    @Override
    public double getMinWeight(double distance) {
        // Same as in FastestWeighting.java
        return distance / maxSpeed;
    }

    @Override
    public String getName() {
        return "aqi";
    }

    @Override
    public double calcEdgeWeight(EdgeIteratorState edgeState, boolean reverse) {
        double speed = reverse ? edgeState.getReverse(speedEnc) : edgeState.get(speedEnc);

        double tot = 0;
        int numPoints = 0;
        // Loop through the nodes of a road
        for (GHPoint3D point : edgeState.fetchWayGeometry(FetchMode.ALL)) {
            int latInd = getClosestCoordIndex(point.getLat(), lat);
            int lonInd = getClosestCoordIndex(point.getLon(), lon);
            double aqi_value = aqi.getDouble(aqiIndex.set(latInd, lonInd));
            // AQI coefficient as in Green Paths (range 0-1)
            tot += (aqi_value < 1.0) ? 0 : (aqi_value - 1) / 4;
            numPoints++;
        }
        double avgAQI = tot / numPoints;
        // Environmental impedance function (See Green Paths)
        double Ct = edgeState.getDistance() / speed * SPEED_CONV; // Base cost
        double s = 1.0; // Sensitivity coefficient
        double res = Ct + Ct * avgAQI * s;

        return res;
    }

    /**
     * This method is used to read AQI data from NetCDF file for one timestep.
     * 
     * @param ncfile NetCDF file containing AQI data.
     * @return 3D Array of AQI raster data.
     * @throws IOException
     * @throws NullPointerException
     * @throws InvalidRangeException
     * @throws UnitException
     */
    private Array getAQIData(NetcdfFile ncfile)
            throws IOException, NullPointerException, InvalidRangeException, UnitException {
        Variable var = ncfile.findVariable("index_of_airquality_194");
        // System.out.println(var);
        if (var == null) {
            throw new NullPointerException("No AQI field in the NetCDF file!");
        }

        // Get the AQI data for one timestep
        int[] varShape = var.getShape();
        int[] origin = new int[3];

        // Temporary indexing for testing purposes
        // Every even minute use index 0 and odd index 1
        // LocalTime currentTime = LocalTime.now();
        // int minutes = currentTime.getMinute();
        // System.out.println("Current Time: " + currentTime);
        // int origin_index = (minutes % 2 == 0) ? 0 : 1;
        // System.out.println(origin_index);
        // origin[0] = origin_index;

        // Find the current time index
        Date currentTime = new Date();

        // Extract the time variable and units
        Variable timeVariable = ncfile.findVariable("time");
        String timeUnits = timeVariable.findAttribute("units").getStringValue();
        int timeLenght = (int) timeVariable.getSize();

        // Convert the current time to the units used in the NetCDF file
        DateUnit dateUnit = new DateUnit(timeUnits);
        int timeOffset = (int) Math.floor(dateUnit.makeValue(currentTime));

        if (timeOffset > timeLenght - 1) {
            System.out.println("AQI data too old! Using the last avaliable values.");
            origin[0] = timeLenght - 1;
        } else {
            origin[0] = timeOffset;
        }

        int[] size = new int[] { 1, varShape[1], varShape[2] };

        Array varData = var.read(origin, size).reduce();

        return varData;
    }

    /**
     * This method is used to read 1D fields from NetCDF file.
     * 
     * @param variableName The name of the datafield to be extracted.
     * @param ncfile       NetCDF file containing.
     * @return 1D Array populated with the data of the wanted variable.
     * @throws IOException
     * @throws IllegalArgumentException
     * @throws InvalidRangeException
     */
    private Array get1DVariableData(String variableName, NetcdfFile ncfile)
            throws IOException, IllegalArgumentException, InvalidRangeException {
        Variable var = ncfile.findVariable(variableName);
        // System.out.println(var);
        if (var == null) {
            throw new IllegalArgumentException("No variable with variable name " + variableName + ".");
        }

        Array varData = var.read();

        return varData;
    }

    /**
     * Method that returns the index of the closest coordinate to the target
     * coordinate.
     * 
     * @param targetCoord The coordinate whose closest match is searched for.
     * @param coords      Array of coordinates (1D)
     * @return
     */
    private int getClosestCoordIndex(double targetCoord, Array coords) {
        double minDist = 99999;
        int argmin = -1;

        for (int i = 0; i < coords.getShape()[0]; i++) {
            double dist = Math.abs(targetCoord - coords.getDouble(i));
            if (minDist > dist) {
                minDist = dist;
                argmin = i;
            }
        }
        return argmin;
    }

}
