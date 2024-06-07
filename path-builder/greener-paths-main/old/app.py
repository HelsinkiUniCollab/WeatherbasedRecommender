import json
import re
import time

import dash_leaflet as dl
from dash import Dash, Input, Output, State, dcc, html
import dash_bootstrap_components as dbc
from shapely.geometry import Point, shape
import geopandas as gpd
import pandas as pd


from utils import find_n_closest, get_paths, route_segment

# Load the data

# Sport units
units_df = pd.read_csv('sport_units.csv')
units_df['location'] = gpd.GeoSeries.from_wkt(units_df['location'])
units_df = gpd.GeoDataFrame(units_df, geometry='location')
# Services
with open('sport_services.json', 'r') as f:
    services = json.load(f)
# services = {173: 'Golfin harjoitusalue', 174: 'Golfin harjoitushalli', 175: 'Golfkenttä', 573: 'Ratagolf', 235: 'Kaukalo', 406: 'Luistelukenttä', 407: 'Luistelureitti', 514: 'Pikaluistelurata', 695: 'Tekojääkenttä', 169: 'Frisbeegolf-rata', 401: 'Liikuntapuisto', 415: 'Lähiliikuntapaikka', 499: 'Parkour- alue', 538: 'Pyöräilyalue', 539: 'Pyöräilyrata', 630: 'Skeitti / rullaluistelupaikka', 737: 'Ulkokuntoiluvälineet', 125: 'Beachvolleykenttä', 205: 'Jalkapallostadion', 331: 'Koripallokenttä', 392: 'Lentopallokenttä', 1014: 'Padelkenttäalue', 495: 'Pallokenttä', 511: 'Pesäpallostadion', 1015: 'Pöytätennisalue', 585: 'Rullakiekkokenttä', 700: 'Tenniskenttäalue', 817: 'Yleisurheilukenttä', 818: 'Yleisurheilun harjoitusalue'}

# Dash app
app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP], prevent_initial_callbacks=True, suppress_callback_exceptions=True)
app.layout = html.Div([
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(['Fast', 'Green', 'Quiet', 'Clean'], 'Fast', id='path-pref'),
            html.Br(),
            dcc.Dropdown(services, id='poi-class-1', placeholder='Choose a service to include in your route'),
            dcc.Dropdown(services, id='poi-class-2', placeholder='Choose a service to include in your route'),
            dcc.Dropdown(services, id='poi-class-3', placeholder='Choose a service to include in your route'),
            html.Br(),
            dbc.Button(id='submit-button-state', n_clicks=0, children='Route the journey!', color='success')
        ], width=2),
        dbc.Col([
            dl.Map([dl.TileLayer(), dl.LayerGroup(id="marker-layer"), dl.LayerGroup(id='path-layer')],
                center=[60.1699,24.9384],
                zoom=13,
                id="map", style={'width': '100%', 'height': '75vh', 'margin': "auto", "display": "block"}),
            
            html.Div(id='hidden-div', style={'display':'none'})
        ])
    ])
], style={'padding':'20px'})

# Callbacks
@app.callback(Output("marker-layer", "children"),
             [Input("map", "click_lat_lng")])
def map_click(click_lat_lng):
    return [dl.Marker(id='start-marker', position=click_lat_lng, children=dl.Tooltip("({:.3f}, {:.3f})".format(*click_lat_lng)))]

@app.callback(Output('path-layer', 'children'),
              Input('submit-button-state', 'n_clicks'),
              State('start-marker', 'position'),
              State('path-pref', 'value'),
              State('poi-class-1', 'value'),
              State('poi-class-2', 'value'),
              State('poi-class-3', 'value')
              )
def button_click(n_clicks, coords, path_pref, poi_class_1, poi_class_2, poi_class_3):
    # NOTE: Longitude and latitude: the preferred way here will be lat, long, since 
    # Leaflet uses this convention and green paths returns the paths in that format as well
    print(f"Routing a journey...")
    origin = Point(coords)
    pois = []
    pois.append(poi_class_1) if poi_class_1 else None
    pois.append(poi_class_2) if poi_class_2 else None
    pois.append(poi_class_3) if poi_class_3 else None

    res = []

    start_time = time.time()

    current = origin
    for p in pois:
        destinations = units_df.loc[units_df['service_id'] == int(p)]['location']
        path, best_poi_coord = route_segment(origin=current, places=destinations, path_pref=path_pref)
        res.append(dl.Polyline(positions=path, color='green'))
        res.append(dl.Marker(position=[best_poi_coord.x, best_poi_coord.y], children=dl.Tooltip(services[p])))
        current = best_poi_coord
    path, _ = route_segment(origin=current, places=[origin], path_pref=path_pref)
    res.append(dl.Polyline(positions=path, color='black'))

    end_time = time.time()
    print(f"Elapsed time for routing: {end_time-start_time:.2f}")
  
    return res


if __name__ == '__main__':
    app.run_server(debug=True)