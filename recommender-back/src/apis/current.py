import copy
import math
from .poi import PointOfInterest
from ..services.data_fetcher import DataFetcher
from ..config import Config


class Current:
    def __init__(self, fetcher: DataFetcher):
        self.fetcher = fetcher
        self.weather = None
        self.aqi = None
        self.get_current_weather()
        self.get_current_air_quality()

    def get_current_weather(self):
        '''
        Retrieves the current weather data for various stations.

        Returns:
            dict: A dictionary containing the current weather data for each station.
        '''

        obs = self.fetcher.get_current_weather_data(Config.FMI_CURRENT['WEATHER']['BBOX'], True)
        data = {}
        for station, metadata in obs.location_metadata.items():
            weatherdata = {
                'Air temperature': str(obs.data[station]['t2m']['values'][-1]) + ' °C',
                'Wind speed': str(obs.data[station]['ws_10min']['values'][-1]) + ' m/s',
                'Humidity': str(obs.data[station]['rh']['values'][-1]) + ' %',
                'Precipitation': str(obs.data[station]['ri_10min']['values'][-1])
                + ' mm',
                'Cloud amount': str(obs.data[station]['n_man']['values'][-1] / 8 * 100) + ' %',
            }
            for value in list(weatherdata):
                if 'nan' in str(weatherdata[value]):
                    weatherdata.pop(value)
            if weatherdata:
                weatherdata['Latitude'] = metadata['latitude']
                weatherdata['Longitude'] = metadata['longitude']
                data[station] = weatherdata
        self.weather = data

    def get_current_weather_warning(self, station):
        '''
        Retrieves the wind speed for one station and calculates if it's too high.

        Returns:
            boolean: If the wind speed is too high.
        '''
        weather = self.weather.get(station)
        wind_speed = weather['Wind speed'].split(' ')[0]
        return float(wind_speed) > 17

    def get_current_air_quality(self):
        '''
        Retrieves the current AQI data for various stations.

        Returns:
            dict: A dictionary containing the current weather data for each station.
        '''
        raw_aqi_data = self.get_latest_air_quality()
        self.aqi = self.parse_latest_aqi_data(raw_aqi_data)

    def get_latest_air_quality(self):
        '''
        Retrieves the Air Quality Index data for the last 24 hours within specified area
        '''
        return self.fetcher.get_current_air_quality_data(
            Config.FMI_CURRENT['AIR_QUALITY']['BBOX'],
            True,
            Config.FMI_CURRENT['AIR_QUALITY']['PARAMETERS']
        )

    def parse_latest_aqi_data(self, raw_aqi_data: dict):
        '''
        Finds latest AQI value and coordinates that is not 'nan' for each station.

        Returns:
            dict: A dictionary containing stations and their aqi and coordinates.
        '''
        latest_aqi_data = {}
        for station, metadata in raw_aqi_data.location_metadata.items():
            values = raw_aqi_data.data[station]['AQINDEX_PT1H_avg']['values']
            latest_aqi_value = next(
                (v for v in reversed(values) if not math.isnan(v)), 'nan')
            if latest_aqi_value == 'nan':
                continue
            aqi = {
                'Air quality': f'{str(latest_aqi_value)} AQI',
                'Latitude': metadata['latitude'],
                'Longitude': metadata['longitude'],
            }
            latest_aqi_data[station] = aqi
        return latest_aqi_data

    def find_nearest_stations_aqi(self, aqi, lat, lon):
        '''
        Calculates the closest stations index in the list of AQI-stations,
        and returns the index of it.
        '''
        smallest, nearest = float('inf'), ''
        for station in aqi:
            dist = abs(aqi[station]['Latitude'] - lat)\
                + abs(aqi[station]['Longitude'] - lon)
            if dist < smallest:
                smallest, nearest = dist, station
        return nearest

    def find_nearest_stations_weather_data(self, poi: PointOfInterest):
        '''
        Finds the nearest weather station to a given point of interest (POI) and adds its weather data to the POI,
        also adds the Air Quality Index data.

        Args:
            poi (PointOfInterest): The POI for which weather data needs to be added.

        Returns:
            PointOfInterest: The modified POI with weather information.

        '''
        lat = poi.latitude
        lon = poi.longitude
        weather = copy.deepcopy(self.weather)
        missing_fields = [
            'Air temperature',
            'Wind speed',
            'Precipitation',
            'Cloud amount',
            'Humidity',
        ]
        returned = {}
        aqi = copy.deepcopy(self.aqi)
        while True:
            smallest, nearest = float('inf'), ''
            for station in weather:
                dist = ((weather[station]['Latitude'] - lat)**2 +
                        (weather[station]['Longitude'] - lon)**2)**0.5
                if dist < smallest:
                    smallest, nearest = dist, station
            for key, value in weather[nearest].items():
                if key not in ['Latitude', 'Longitude']:
                    returned.setdefault(key, value)
                    if key in missing_fields:
                        missing_fields.remove(key)
            if not missing_fields or not weather:
                smallest, nearest = float('inf'), ''
                if len(aqi) > 0:
                    nearest = self.find_nearest_stations_aqi(aqi, lat, lon)
                    returned.setdefault(
                        'Air quality', aqi[nearest]['Air quality'])
                break
            del weather[nearest]
        poi.weather['Current'] = returned
        return poi
