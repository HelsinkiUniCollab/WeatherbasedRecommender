import requests
import random
import os
from dotenv import load_dotenv


class GreenPathsAPI:
    """
    A class for fetching route information from the Green Paths API and plotting the route on a map.
        Parameters:
        start_coords (tuple): Tuple containing the latitude and longitude of the starting point.
        end_coords (tuple): Tuple containing the latitude and longitude of the ending point.
        travel_mode (str, optional): Mode of travel, can be 'walk' or 'bike'. Defaults to 'walk'.
        routing_mode (str, optional): Routing mode, can be 'fast', 'short', 'clean', 'quiet', or 'safe' (for bikes).
            Defaults to 'fast'.
    """

    def __init__(self, travel_mode="walk", routing_mode="fast"):
        self.travel_mode = travel_mode
        self.routing_mode = routing_mode

    def fetch_api_data(self, start_coords, end_coords):
        """
        Fetches route data from the Green Paths API.
        Returns:
            dict: JSON response containing route information or None if an error occurred.
        """
        url = f"https://www.greenpaths.fi/paths/{self.travel_mode}/{self.routing_mode}/{start_coords[0]},{start_coords[1]}/{end_coords[0]},{end_coords[1]}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as error:
            print(f"Failed to fetch data from the API: {error}")
            return None

    def extract_path_coordinates(self, api_response):
        """
        Extracts the latitude and longitude coordinates of the route from the API response.
        Returns:
            list: List of tuples containing latitude and longitude coordinates of the route or empty list if no data.
        """
        path_coordinates = []

        if not api_response:
            return path_coordinates

        path_fc = api_response.get("path_FC") or {}
        if not path_fc:
            return path_coordinates

        for feature in path_fc.get("features", []):
            geometry = feature.get("geometry", {})
            if geometry.get("type") == "LineString" and geometry.get("coordinates"):
                path_coordinates.extend(geometry.get("coordinates"))
        return path_coordinates


class GraphhopperAPI:
    """
    A class for fetching route information from the Green Paths API and plotting the route on a map.
        Parameters:
        start_coords (tuple): Tuple containing the latitude and longitude of the starting point.
        end_coords (tuple): Tuple containing the latitude and longitude of the ending point.
        travel_mode (str, optional): Mode of travel, can be 'walk' or 'bike'. Defaults to 'walk'.
        routing_mode (str, optional): Routing mode, can be 'fast', 'short', 'clean', 'quiet', or 'safe' (for bikes).
            Defaults to 'fast'.
    """

    def __init__(self, travel_mode="walk", routing_mode="fast"):
        self.travel_mode = travel_mode
        self.routing_mode = routing_mode
        load_dotenv()
        self.path_uri = os.environ['PATH_URI']

    def get_routing_profile(self, routing_type: str, mobility_profile: str) -> str:
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

    def fetch_round_path_data(self, start_coords, route_len, route_type, mobility_type):
        """
        Fetches route data from the Green Paths API.
        Returns:
            dict: JSON response containing route information or None if an error occurred.
        """
        starting_point = (start_coords[1], start_coords[0])
        profile = self.get_routing_profile(route_type, mobility_type)
        url = self.path_uri
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
        "round_trip.distance": route_len,
        "round_trip.seed": random.randint(0, 999999),
        "elevation": True,
        "details": ["road_environment", "surface", "smoothness"],
        }
        query = {}
        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(url, json=payload, headers=headers, params=query)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as error:
            print(f"Failed to fetch data from the API: {error}")
            return None

    def fetch_path_data(self, start_coords, end_coords, route_type, mobility_type):
        """
        Fetches route data from the Green Paths API.
        Returns:
            dict: JSON response containing route information or None if an error occurred.
        """
        starting_point = (start_coords[1], start_coords[0])
        destination = (end_coords[1], end_coords[0])
        profile = self.get_routing_profile(route_type, mobility_type)
        url = self.path_uri
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
        query = {}
        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(url, json=payload, headers=headers, params=query)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as error:
            print(f"Failed to fetch data from the API: {error}")
            return None

    def extract_path_coordinates(self, api_response):
        """
        Extracts the latitude and longitude coordinates of the route from the API response.
        Returns:
            list: List of tuples containing latitude and longitude coordinates of the route or empty list if no data.
        """
        path_coordinates = []

        if not api_response:
            return path_coordinates

        routing_result = api_response

        # distance = round(routing_result["paths"][0]["distance"])
        # # Convert time from milliseconds to the nearest minute
        # travel_time = routing_result["paths"][0]["time"]
        # travel_time = round(travel_time / 60000)

        route = routing_result["paths"][0]["points"]["coordinates"]
        # Transform to (lat, lon)
        route = [[p[0], p[1]] for p in route]

        return route