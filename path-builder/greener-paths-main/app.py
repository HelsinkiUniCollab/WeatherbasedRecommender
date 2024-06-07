import dash
import dash_bootstrap_components as dbc
import dash_leaflet as dl
import requests
from dash import ALL, Dash, Input, Output, State, ctx, dcc, html
from pymongo import MongoClient

from activity_definitions import medical_conditions
from utils.recommender_utils import filter_POIs
from utils.graphhopper_utils import (
    get_round_trip,
    get_route_to_location,
    get_routing_profile,
    process_routing_result,
)

# Connect to mongodb
url = "mongodb://mongodb:27017"
client = MongoClient(url)
db = client["activities"]["units"]


##################################################
# Functions for generating dynamic elements
##################################################


def create_recommendation_list(pois):
    list_items = []
    for ind, poi in enumerate(pois):
        # resp = requests.get(f"https://api.hel.fi/servicemap/v2/unit/?id={poi['id']}")
        # resp.raise_for_status()
        # resp = resp.json()
        # poi_details = resp["results"][0]

        content = html.Div(
            [
                html.H5(poi["name"]["en"])
                if "en" in poi["name"].keys()
                else html.H5(poi["name"]["fi"]),
                # html.P(
                #     poi_details["street_address"]["en"]
                #     if "en" in poi_details["street_address"].keys()
                #     else "No street address"
                # ),
                html.Div(
                    [
                        poi["location"]["coordinates"][1],
                        poi["location"]["coordinates"][0],
                    ],
                    id={"type": "poi-location-div", "index": ind},
                    style={"display": "none"},
                )
                # html.P(poi_details['description']['en'] if 'en' in poi_details['description'].keys() else 'No description')
            ]
        )
        list_items.append(
            dbc.ListGroupItem(
                content,
                id={"type": "poi-info-item", "index": ind},
                active=False,
                action=True,
            )
        )

    return html.Div(
        dbc.ListGroup(
            list_items,
            id="recommedation-list",
            flush=True,
            numbered=True,
        ),
        style={"maxHeight": "500px", "overflow": "scroll"},
    )


def create_explanation_list(rec_criteria):
    res = []
    if "medical_condition" in rec_criteria:
        res.append(
            dbc.Alert(
                "You have selected a medical condition. Recommendations are based on medical recommendations (Pedersen et.al...)",
                color="info",
            )
        )
    if "pregnant" in rec_criteria:
        res.append(
            dbc.Alert(
                "You have selected 'Pregnancy' as a condition. Potentially traumatic activities are not recommended.",
                color="danger",
            )
        )
    if "high_temperature" in rec_criteria:
        res.append(
            dbc.Alert(
                "The outdoor temperature is high (over 25 degrees). Outdoor activities are not recommended",
                color="warning",
            )
        )
    if "rain" in rec_criteria:
        res.append(
            dbc.Alert(
                "It's raining outside. Outdoor activities are not recommended",
                color="warning",
            )
        )
    return res


def create_refine_search_box(db):
    # Get the activity "classes"
    # Define the aggregation pipeline
    pipeline = [
        {
            "$group": {
                "_id": None,
                "lastPathElements": {"$addToSet": {"$arrayElemAt": ["$path", -1]}},
            }
        }
    ]
    # Execute the aggregation query
    result = db.aggregate(pipeline)
    # Extract the unique last elements from the result
    activity_classes = sorted(list(result.next()["lastPathElements"]))

    res = html.Div(
        [
            dcc.Dropdown(
                activity_classes,
                multi=True,
                id="include-activity-classes-dropdown",
                placeholder="Choose preferred activities",
            ),
        ]
    )
    return res


def create_route_information_box(route):
    has_bridge = False
    has_tunnel = False
    has_ferry = False

    for road_env_item in route["details"]["road_environment"]:
        road_env = road_env_item[2]
        if road_env == "bridge":
            has_bridge = True
        if road_env == "tunnel":
            has_tunnel = True
        if road_env == "ferry":
            has_ferry = True

    content = dbc.ListGroup(
        [
            dbc.ListGroupItem(f"Distance: {round(route['distance'],2)} meters."),
            dbc.ListGroupItem(f"Travel Time: {round(route['time']/60000)} minutes."),
            dbc.ListGroupItem(f"Ascend: {round(route['ascend'], 1)} meters."),
            dbc.ListGroupItem(f"Descend: {round(route['descend'], 1)} meters."),
            dbc.ListGroupItem(
                f"Has bridge: {has_bridge}.",
                color="warning" if has_bridge else None,
            ),
            dbc.ListGroupItem(
                f"Has tunnel: {has_tunnel}.",
                color="warning" if has_tunnel else None,
            ),
            dbc.ListGroupItem(
                f"Has ferry: {has_ferry}.",
                color="warning" if has_ferry else None,
            ),
        ],
        flush=True,
    )

    return [content]


##############################
# "Static" UI elements
##############################


search_box = [
    html.Div(
        [
            dbc.Label("Choose your medical condtion"),
            dcc.Dropdown(medical_conditions, medical_conditions[0], id="med_cond"),
        ]
    ),
    html.Br(),
    dbc.Accordion(
        [
            dbc.AccordionItem(
                [
                    html.Div(
                        [
                            dbc.Checkbox(
                                id="ignore-rain-checkbox",
                                label="I don't care if it's raining outside.",
                                value=False,
                            ),
                            dbc.Checkbox(
                                id="ignore-heat-checkbox",
                                label="I don't care if it's hot outside.",
                                value=False,
                            ),
                        ]
                    )
                ],
                id="extra-settings",
                item_id="extra-settings",
                title="Additional search settings",
            ),
        ],
        start_collapsed=True,
    ),
    html.Br(),
    html.Div(
        [
            dbc.Button(
                id="find-activities-button",
                n_clicks=0,
                children="Find activities",
                color="success",
                className="me-1",
            ),
            dbc.Button(
                id="walk-submit-button",
                n_clicks=0,
                children="Take a walk",
                color="success",
                className="me-1",
            ),
            dbc.Tooltip(
                "WHO recommeds at least 150-300 minutes for moderate aerobic activity per week.",
                target="walk-submit-button",
            ),
        ],
    ),
]

walk_preferences_box = html.Div(
    [
        dbc.Label("Roundtrip length (in meters)"),
        dbc.Input(
            id="route-length-input",
            type="number",
            value=1000,
            min=100,
            max=90000,
            step=100,
        ),
        html.Br(),
        dbc.Label("Route type"),
        dbc.RadioItems(
            options=[
                {"label": "Fast", "value": "fast"},
                {"label": "Clean", "value": "clean"},
            ],
            value="fast",
            id="routing-type",
            inline=True,
        ),
        html.Br(),
        dbc.Label("Mobility profile"),
        dcc.Dropdown(
            [
                {"label": "Foot", "value": "foot"},
                {"label": "Wheelchair", "value": "wheelchair"},
            ],
            "foot",
            clearable=False,
            id="mobility-type",
        ),
        html.Br(),
        dbc.Button(
            id="walk-submit-button",
            n_clicks=0,
            children="Find a walking route",
            color="success",
        ),
    ]
)

mapview = dl.Map(
    [
        dl.TileLayer(),
        dl.LayerGroup(id="user-marker-layer"),
        dl.LayerGroup(id="poi-marker-layer"),
        dl.LayerGroup(id="route-layer"),
    ],
    center=[60.1699, 24.9384],
    zoom=13,
    id="map",
    style={"width": "100%", "height": "75vh", "margin": "auto", "display": "block"},
)

######################
# Dash app definition
######################

app = Dash(
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    prevent_initial_callbacks=True,
    suppress_callback_exceptions=True,
)

app.layout = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Accordion(
                            [
                                dbc.AccordionItem(
                                    search_box,
                                    id="search-box",
                                    item_id="search-box",
                                    title="Search settings",
                                ),
                                dbc.AccordionItem(
                                    html.Div([html.P("No recommendations yet!")]),
                                    id="recommendation-list",
                                    item_id="recommendation-list",
                                    title="Recommendations",
                                ),
                                dbc.AccordionItem(
                                    walk_preferences_box,
                                    id="round-walk-preferences",
                                    item_id="round-walk-preferences",
                                    title="Walk preferences",
                                ),
                                dbc.AccordionItem(
                                    [dbc.Label("No route generated yet.")],
                                    id="route-information-box",
                                    item_id="route-information-box",
                                    title="Route information",
                                ),
                                dbc.AccordionItem(
                                    html.Div(
                                        [html.P("Search for recommendations first")]
                                    ),
                                    id="explanation-box",
                                    item_id="explanation-box",
                                    title="Recommendations explained",
                                ),
                                dbc.AccordionItem(
                                    create_refine_search_box(db),
                                    id="search_refinement-box",
                                    item_id="search_refinement-box",
                                    title="Refine recommendations",
                                ),
                            ],
                            id="sidebar-accordion",
                            flush=True,
                        )
                    ],
                    width=4,
                ),
                dbc.Col(
                    [
                        mapview,
                        html.Div(id="hidden-div", style={"display": "none"}),
                    ]
                ),
            ]
        ),
        html.Footer(
            html.P("Created by University of Helsinki"),
            style={
                "text_align": "center",
                "fontSize": 11,
                "padding": 3,
                "font-weight": "bold",
            },
        ),
    ],
    style={"padding": "20px"},
)


########################
# Callbacks
########################


@app.callback(
    Output("user-marker-layer", "children"),
    Input("map", "click_lat_lng"),
)
def map_click(click_lat_lng):
    """Callback for handling user's clicking on the map to choose the starting location."""
    return [
        dl.Marker(
            id="start-marker",
            position=click_lat_lng,
            children=dl.Tooltip(
                "Starting position (lat, long): ({:.3f}, {:.3f})".format(*click_lat_lng)
            ),
        )
    ]


@app.callback(
    Output("poi-marker-layer", "children"),
    Output("recommendation-list", "children"),
    Output("explanation-box", "children"),
    Output("sidebar-accordion", "active_item"),
    Input("find-activities-button", "n_clicks"),
    State("med_cond", "value"),
    State("start-marker", "position"),
    State("ignore-rain-checkbox", "value"),
    State("ignore-heat-checkbox", "value"),
    State("include-activity-classes-dropdown", "value"),
)
def find_activities_button_click(
    n_cliks, med_cond, user_location, ignore_rain, ignore_heat, preferred_activities
):
    """This callback retrieves POI recommendations and updates the UI with their information."""
    # Find relevant POIs
    pois, rec_criteria = filter_POIs(
        db, med_cond, user_location, ignore_rain, ignore_heat, preferred_activities
    )

    pois = list(pois)

    # Handle empty recommendations (too strict search criteria)
    if not pois:
        return (
            [],
            html.Div(
                [html.P("No activities found! Try to relax the search criteria.")]
            ),
            create_explanation_list(rec_criteria),
            "recommendation-list",
        )

    poi_markers = [
        dl.Marker(
            id={"type": "poi-marker", "index": ind},
            position=(
                poi["location"]["coordinates"][1],
                poi["location"]["coordinates"][0],
            ),
            children=dl.Tooltip(
                html.Div(
                    [html.P(poi["name"]["fi"]), html.P(f"Location: {poi['location']}")]
                )
            ),
        )
        for ind, poi in enumerate(pois)
    ]
    return (
        poi_markers,
        create_recommendation_list(pois),
        create_explanation_list(rec_criteria),
        "recommendation-list",
    )


@app.callback(
    Output("route-layer", "children", allow_duplicate=True),
    Output("route-information-box", "children", allow_duplicate=True),
    Input("walk-submit-button", "n_clicks"),
    State("start-marker", "position"),
    State("route-length-input", "value"),
    State("routing-type", "value"),
    State("mobility-type", "value"),
    prevent_initial_call=True,
)
def walk_submit_click(
    n_clicks, start_position, route_length, routing_type, mobility_type
):
    """Callback that gets a round trip and shows in UI."""
    routing_profile = get_routing_profile(routing_type, mobility_type)
    # Need to transform to (lon, lat)
    routing_result = get_round_trip(
        (start_position[1], start_position[0]), route_length, routing_profile
    )

    distance, travel_time, route = process_routing_result(routing_result)

    return [
        dl.Polyline(
            positions=route,
            children=dl.Tooltip(
                f"Distance: {distance} meters. Estimated walking time: {travel_time} minutes.",
            ),
        ),
        create_route_information_box(routing_result["paths"][0]),
    ]


@app.callback(
    Output({"type": "poi-info-item", "index": ALL}, "active"),
    Output("route-layer", "children", allow_duplicate=True),
    Output("route-information-box", "children", allow_duplicate=True),
    Input({"type": "poi-info-item", "index": ALL}, "n_clicks"),
    Input({"type": "poi-marker", "index": ALL}, "n_clicks"),
    State({"type": "poi-info-item", "index": ALL}, "active"),
    State({"type": "poi-location-div", "index": ALL}, "children"),
    State("start-marker", "position"),
    State("routing-type", "value"),
    State("mobility-type", "value"),
    prevent_initial_call=True,
)
def handle_poi_click(
    n_clicks_item,
    n_clicks_marker,
    is_active,
    location,
    start_position,
    routing_type,
    mobility_type,
):
    """Callback that handles clicking on POI, either in the POI list or map marker,
    by finding a route to that POI and showing it in UI.
    """
    # Prevent triggering callback on initial recommendation update
    if ctx.triggered_id is None or (
        n_clicks_item[ctx.triggered_id.index] is None
        and n_clicks_marker[ctx.triggered_id.index] is None
    ):
        return dash.no_update

    routing_profile = get_routing_profile(routing_type, mobility_type)

    poi_coordinates = location[ctx.triggered_id.index]
    poi_coordinates = (poi_coordinates[1], poi_coordinates[0])

    routing_result = get_route_to_location(
        (start_position[1], start_position[0]), poi_coordinates, routing_profile
    )

    distance, travel_time, route = process_routing_result(routing_result)

    is_active = [False for _ in is_active]
    is_active[ctx.triggered_id.index] = True
    return (
        is_active,
        [
            dl.Polyline(
                positions=route,
                children=dl.Tooltip(
                    f"Distance: {distance} meters. Estimated walking time: {travel_time} minutes.",
                ),
            )
        ],
        create_route_information_box(routing_result["paths"][0]),
    )


if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0")
