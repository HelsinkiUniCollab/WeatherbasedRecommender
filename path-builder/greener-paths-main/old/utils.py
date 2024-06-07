import requests
from shapely.geometry import Point, shape
import json


def load_data():
    filepath = "./data/activities_data.json"
    with open(filepath, "r") as f:
        temp = json.load(f)

    data = temp["data"]
    # Transform geojson into shapely point
    for key, value in data.items():
        point_location = shape(value["location"])
        # Change to lat-long -format
        point_location = Point(point_location.y, point_location.x)
        data[key]["location"] = point_location
    # Transform lists back to sets (sets cannot be in JSON)
    index = temp["index"]
    for key in index:
        index[key] = set(index[key])
    return data, index


def get_paginated_items(url, verbose=False):
    data = []
    while url is not None:
        resp = requests.get(url)
        resp.raise_for_status()
        resp = resp.json()

        data.extend(resp["results"])
        url = resp["next"]
        if verbose:
            print(url)
    return data


def get_paths(start, end, path_type):
    url = f"https://www.greenpaths.fi/paths/walk/{path_type.lower()}/{start.x},{start.y}/{end.x},{end.y}"
    resp = requests.get(url)
    data = resp.json()
    return data


def str_to_dict(string):
    # remove the curly braces from the string
    string = string.strip("{}")

    # split the string into key-value pairs
    pairs = string.split(", ")

    # use a dictionary comprehension to create the dictionary, converting the values to integers and removing the quotes from the keys
    return {
        key[1:-2]: int(value) for key, value in (pair.split(": ") for pair in pairs)
    }


def find_n_closest(orig, destinations, n=3):
    points = [(d, ind) for ind, d in enumerate(destinations)]
    # points = [(Point(p[0].y,p[0].x), p[1]) for p in points]
    distances = [(orig.distance(p[0]), p[1]) for p in points]
    distances = sorted(distances, key=lambda x: x[0])

    return [points[d[1]] for d in distances[:n]]


def route_segment(origin, places, path_pref):
    # Find closest POIs, to lessen the load on API
    if len(places) > 1:
        closest_places = find_n_closest(origin, places, 5)
    else:
        closest_places = [(places[0], 0)]
    # 3. Calculate the paths of desired type to each of the POIs
    paths = []
    for gym in closest_places:
        # print(gym)
        path = get_paths(origin, gym[0], path_pref)
        paths.append(path)
    # 4. Get the best POI/path according to the desired criteria (fastest, quietest, cleanest, etc.)
    best_cost = 99999
    best_path = []
    best_poi_coord = Point()
    for path, gym in zip(paths, closest_places):
        for p in path["path_FC"]["features"]:
            if path_pref == "Clean":
                cost = p["properties"]["aqc"]
            elif path_pref == "Quiet":
                cost = p["properties"]["nei"]
            elif path_pref == "Green":
                cost = -p["properties"]["gvi_m"]  # Here higher->better, hence minus
            elif path_pref == "Fast":
                cost = p["properties"]["length"]
            else:
                raise TypeError(f"Unknown preference class: {path_pref}")
            if cost < best_cost:
                best_cost = cost
                best_path = p["geometry"]["coordinates"]
                best_poi_coord = gym[0]

    path = [[c[1], c[0]] for c in best_path]

    return (path, best_poi_coord)
