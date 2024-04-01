import json
from requests import Timeout
from .current import Current
from .poi import PointOfInterest
from ..services.data_fetcher import DataFetcher
from ..services.api_fetcher import InternalApiService
from ..db.db import get_collection
from ..db.db import read_POIs
import time

def get_simulated_pois_as_json(air_temperature, wind_speed, humidity,
                                              precipitation, cloud_amount, air_quality, current_time, sunrise, sunset):
    """
    Retrieves points of interest (POIs) from a JSON file and enriches them with simulated weather data.

    Returns:
        str: JSON string containing the POIs with calculated scores.

    Raises:
        KeyError: If an error occurs while processing the data.
    """
    try:
        pois = get_pois()
        updated_data = []
        for poi in pois:
            poi.set_simulated_weather(air_temperature, wind_speed, humidity,
                                            precipitation, cloud_amount, air_quality)
            poi.calculate_score(current_time, sunrise, sunset)
            updated_data.append(poi.get_json())
        return json.dumps(updated_data)
    except KeyError as error:
        return {"message": "An error occurred", "status": 500, "error": str(error)}
    except Timeout as error:
        return {"message": "Forecast timed out", "status": 500, "error": str(error)}


def get_pois_as_json(category="All"):
    """
    Retrieves points of interest (POIs) from MongoDB and enriches them with current weather data.

    Returns:
        str: JSON string containing the POIs with weather information.

    Raises:
        KeyError: If an error occurs while processing the data.
    """
    try:
        pois = get_pois()
        weather_fetcher = DataFetcher()
        current = Current(weather_fetcher)
        start_time = time.time()
        forecast_data = InternalApiService.fetch_forecast()
        print(f"Time taken: {time.time() - start_time} seconds")
        aqi_data = InternalApiService.fetch_aqi()
        aqi_data = _replace_datetime_in_aqi_data(forecast_data, aqi_data)
        forecast_data = _add_aqi_to_forecast(forecast_data, aqi_data)
        updated_data = []
        for poi in pois:
            if category not in poi.categories:
                continue
            poi: PointOfInterest = current.find_nearest_stations_weather_data(poi)
            poi = find_nearest_coordinate_forecast_data(poi, forecast_data)
            poi.calculate_score()
            updated_data.append(poi.get_json())
        return json.dumps(updated_data)
    except KeyError as error:
        return {"message": "An error occurred", "status": 500, "error": str(error)}
    except Timeout as error:
        return {"message": "Forecast timed out", "status": 500, "error": str(error)}


def find_nearest_coordinate_forecast_data(poi: PointOfInterest, forecast_data):
    """
    Retrieves all points of interest (POIs) from JSON files and merges them together.

    Args:
        category (list): List of categories of POIs to retrieve. If None, default categories will be used.

    Returns:
        list: List of all POIs.
    """
    try:
        lat = poi.latitude
        lon = poi.longitude
        coord_key = f"{lat}, {lon}"
        for hour in forecast_data:
            data = forecast_data[hour]
            if forecast_data is None or coord_key not in data:
                return poi

            time_key = f"{hour[11:16]}"
            poi.weather[time_key] = data[coord_key]
    except TypeError:
        print("Failed to find nearest coordinate forecast data. TypeError occurred.")

    return poi

def get_pois():
    """
    Fetches and converts mongoDB documents into POI -objects.

    Args:
        test (bool): A flag to indicate if the test environment is used.

    Returns:
        list: List of POI -objects.
    """
    #collection = get_collection()
    #all_documents = collection.find({})
    pois = []
    read_pois = read_POIs()
    for parsed_poi in read_pois:
        poi = PointOfInterest(parsed_poi['name'], parsed_poi['latitude'], parsed_poi['longitude'],
                            parsed_poi['not_accessible_for'], parsed_poi['categories'])
        pois.append(poi)
    return pois

def _add_aqi_to_forecast(forecast_data, aqi_data):
    """Adds air quality index data to forecast data.

    Args:
        forecast_data (dict): Forecast data containing date-time and POI coordinates.
        aqi_data (dict): Air Quality Index (AQI) data associated with date-time and POI coordinates.

    Returns:
        dict: Updated forecast_data with added air quality index values.
    """
    for datetime, poi_coords in aqi_data.items():
        if datetime in forecast_data:
            for poi_coord, air_quality in poi_coords.items():
                if poi_coord not in forecast_data[datetime]:
                    continue
                aqi_value = air_quality['Air Quality Index']
                forecast_data[datetime][poi_coord]['Air quality'] = f'{aqi_value} AQI'
    return forecast_data

def _replace_datetime_in_aqi_data(forecast_data, aqi_data):
    """Replaces the datetime in AQI data to match forecast data's caching times.

    Args:
        forecast_data (dict): Forecast data containing date-time and POI coordinates.
        aqi_data (dict): Air Quality Index (AQI) data associated with date-time and POI coordinates.

    Returns:
        dict: Updated AQI data with adjusted datetimes.
    """
    aqi_dates = list(aqi_data.keys())
    updated_aqi_data = {}
    for fore_date, _ in forecast_data.items():
        if aqi_dates:
            aqi_date = aqi_dates.pop(0)
            updated_aqi_data[fore_date] = aqi_data[aqi_date]
    return updated_aqi_data
