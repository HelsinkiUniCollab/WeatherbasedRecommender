from typing import Any
import requests
import random


def get_routing_profile(routing_type: str, mobility_profile: str) -> str:
    if routing_type == "fast" and mobility_profile == "foot":
        return "foot"
    if routing_type == "fast" and mobility_profile == "wheelchair":
        return "wheelchair_fastest"
    if routing_type == "clean" and mobility_profile == "foot":
        return "clean"
    if routing_type == "clean" and mobility_profile == "wheelchair":
        return "wheelchair_clean"
    raise (
        ValueError(
            f"The combination of routing_type: {routing_type} ",
            f"and mobility_profile: {mobility_profile} ",
            "doesn't correspond to any routing profile!",
        )
    )


def gh_post_request(payload: dict) -> dict[str, Any]:
    url = "http://graphhopper:8989/route"
    query = {}
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=payload, headers=headers, params=query)
    response.raise_for_status()
    data = response.json()

    return data


def get_round_trip(
    starting_point: tuple[float, float],
    distance: int = 1000,
    profile: str = "foot",
) -> dict[str, Any]:
    seed = random.randint(0, 999999)

    payload = {
        "points": [starting_point],
        "profile": profile,
        "locale": "en",
        "instructions": False,
        "calc_points": True,
        "points_encoded": False,
        "debug": False,
        "ch.disable": True,
        "algorithm": "round_trip",
        "round_trip.distance": distance,
        "round_trip.seed": seed,
        "elevation": True,
        "details": ["road_environment", "surface", "smoothness"],
    }

    return gh_post_request(payload)


def get_route_to_location(
    starting_point: tuple[float, float],
    destination: tuple[float, float],
    profile: str = "foot",
) -> dict[str, Any]:
    payload = {
        "points": [starting_point, destination],
        "profile": profile,
        "locale": "en",
        "instructions": False,
        "calc_points": True,
        "points_encoded": False,
        "debug": False,
        "ch.disable": False,
        "elevation": True,
        "details": ["road_environment", "surface", "smoothness"],
    }

    return gh_post_request(payload)


def process_routing_result(
    routing_result: dict[str, Any]
) -> tuple[int, int, list[list[float]]]:
    distance = round(routing_result["paths"][0]["distance"])
    # Convert time from milliseconds to the nearest minute
    travel_time = routing_result["paths"][0]["time"]
    travel_time = round(travel_time / 60000)

    route = routing_result["paths"][0]["points"]["coordinates"]
    # Transform to (lat, lon)
    route = [[p[1], p[0]] for p in route]

    return distance, travel_time, route


def main():
    start_point = (24.949416, 60.173151)
    end_point = (24.95, 60.18)
    # dist = 1000  # in meters
    # result = get_round_trip(start_point, dist)
    result = get_route_to_location(start_point, end_point)

    print(result)


if __name__ == "__main__":
    main()
