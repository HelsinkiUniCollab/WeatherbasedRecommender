from . import times
from ..services.scoring.outdoor_scorer import OutdoorScorer
from ..services.scoring.indoor_scorer import IndoorScorer


class PointOfInterest:
    INDOOR_CATEGORIES = ['Sport halls']
    OUTDOOR_CATEGORIES = ['Open air pools and beaches',
                          'Athletic fields and venues',
                          'Neighbourhood sports facilities and parks']

    def __init__(self, name=None, latitude=None, longitude=None, not_accessible_for=None, categories=None,
                 activities=None, hours=None, sat=None, sun=None):
        self.sun = times.get_sun_data()
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.not_accessible_for = not_accessible_for
        self.categories = []
        self.categories = categories
        self.weather = {}
        self.categorytype = None
        self.activities = activities
        self.hours = hours
        self.saturday = sat
        self.sunday = sun
        self.scorers = {
            "Indoor": IndoorScorer(),
            "Outdoor": OutdoorScorer()
        }

    def _extract_weather_data(self, data):
        def extract_float(value, multiplier=1.0):
            extracted_value = value.split(' ')[0]
            if extracted_value == "-":
                return 0.0
            return float(extracted_value) * multiplier

        return {
            'wind_speed': extract_float(data.get('Wind speed')),
            'precipitation': extract_float(data.get('Precipitation')),
            'clouds': extract_float(data.get('Cloud amount'), 0.01),
            'temperature': extract_float(data.get('Air temperature')),
            'humidity': extract_float(data.get('Humidity'), 0.01),
            'air_quality': extract_float(data.get('Air quality')),
        }

    def calculate_score(self, cur_time=None, sunrise=None, sunset=None):
        """
        Calculates a score for the Point of Interest based on weather and time.

        Args:
            cur_time (str, optional): Current time (HH:MM). Defaults to None.
            sunrise (str, optional): Sunrise time (HH:MM). Defaults to None.
            sunset (str, optional): Sunset time (HH:MM). Defaults to None.

        Returns:
            None

        Calculates scores based on weather and time for the POI's categories.
        The calculated scores are added to the POI's weather data.
        """
        if sunrise is None and sunset is None:
            sunrise, sunset = self.sun

        sunrise_time = times.time_from_string(sunrise)
        sunset_time = times.time_from_string(sunset)

        for category in self.categories:
            for timeinterval, data in enumerate(self.weather.values()):
                if cur_time is None:
                    cur_time = times.get_current_time(timeinterval)

                current_time = times.time_from_string(cur_time)
                weather_data = self._extract_weather_data(data)

                scorer = None
                if category in PointOfInterest.OUTDOOR_CATEGORIES:
                    self.categorytype = "Outdoor"
                    scorer = self.scorers["Outdoor"]
                elif category in PointOfInterest.INDOOR_CATEGORIES:
                    self.categorytype = "Indoor"
                    scorer = self.scorers["Indoor"]

                if scorer:
                    data['Score'] = scorer.score(
                        weather_data['temperature'], weather_data['wind_speed'],
                        weather_data['humidity'], weather_data['precipitation'],
                        weather_data['clouds'], weather_data['air_quality'],
                        sunrise_time, sunset_time, current_time
                    )

    def set_simulated_weather(self, air_temperature, wind_speed, humidity,
                              precipitation, cloud_amount, air_quality):
        """
        Sets simulated weather data for testing score calculations.

        Args:
            air_temperature (float): Simulated air temperature in Celsius.
            wind_speed (float): Simulated wind speed in meters per second.
            humidity (float): Simulated humidity level in percentage.
            precipitation (float): Simulated precipitation amount in millimeters.
            cloud_amount (float): Simulated cloud coverage in percentage.
            air_quality (str): Simulated air quality information.

        This method sets simulated weather data for the Point of Interest (POI) to facilitate testing
        the score calculation functionality.
        """

        self.weather = {
            "Weather": {
                "Air temperature": f"{air_temperature} °C",
                "Wind speed": f"{wind_speed} m/s",
                "Humidity": f"{humidity} %",
                "Precipitation": f"{precipitation} mm",
                "Cloud amount": f"{cloud_amount} %",
                "Air quality": f"{air_quality} AQI",
            }
        }

    def get_json(self):
        """
        Returns a JSON representation of the Point of Interest.

        Returns:
            dict: A dictionary containing the POI's information in JSON format.
        """
        return {'name': self.name, 'weather': self.weather,
                'latitude': self.latitude, 'longitude': self.longitude,
                'category': self.categories[-1], 'catetype': self.categorytype,
                'activities':self.activities,
                'not_accessible_for': self.not_accessible_for, 'all_categories': self.categories,
                'hours':self.hours, 'saturday':self.saturday, 'sunday':self.sunday}
