import numpy as np
import tempfile
import requests
import defusedxml.ElementTree as ET
import time
from datetime import datetime
from urllib.parse import urlencode
from netCDF4 import Dataset
from ..config import Config
from datetime import timedelta
from .times import get_forecast_times

class AQI:
    def __init__(self):
        """A class representing a single AQI object

        Args:
            data (numpy array): aqi data as numpy array
            json (string): full parsed aqi data in json format
            dataset (netcdf): netcdf dataset containing the aqi data
            datetimes (dict): dictionary containing datetimes and aqi objects
            latitudes (numpy array): latitude coordinates as numpy array
            longitudes (numpy array): longitude coordinates as numpy array
        """
        self.data = None
        self.dataset = None
        self.datetimes = None
        self.latitudes = None
        self.longitudes = None

    def download_netcdf_and_store(self):
        """Downloads netcdf file, parses it and stores the data in the object.
           The temporary file is deleted afterwards.
        """
        netcdf_file_url = self._parse_xml()

        with tempfile.NamedTemporaryFile(delete=True) as temp_file:
            netcdf_file_name = temp_file.name
            self._download_to_file(netcdf_file_url, netcdf_file_name, 5)
            self.dataset = Dataset(netcdf_file_name)
            self._parse_netcdf()

    def _parse_xml(self):
        """Parses the fmi open data xml file

        Returns:
            string: url link of latest queried netcdf file
        """

        url = self._get_xml_url()
        req = requests.get(url)
        content = req.content
        xml = ET.fromstring(content)
        file_reference = xml.findall(Config.FILEREF_MEMBER)
        latest_file_url = file_reference[-1].text
        return latest_file_url

    def _get_xml_url(self):
        """Fetches the xml file url based on query

        Returns:
            string: xml file url
        """
        _, start_time, end_time = get_forecast_times()
        args = {'starttime': start_time,
                'endtime': end_time,
                'parameters': Config.AQI_PARAMS,
                'bbox': Config.BBOX_FORECAST}
        xml_url = Config.FMI_QUERY_URL + Config.AQI_QUERY + "&" + urlencode(args)
        return xml_url

    def _parse_netcdf(self):
        """Parses the given netcdf file

        Returns:
            dict: A dictionary of datetimes keys and AQI object values
        """
        self.latitudes = self.dataset.variables['lat'][:]
        self.longitudes = self.dataset.variables['lon'][:]
        time = self.dataset.variables['time'][:]
        aqi = self.dataset.variables['index_of_airquality_194'][:]

        forecast_time = datetime.now() + timedelta(hours=1)

        datetimes = {}
        for times in time:
            forecast_datetime = forecast_time + timedelta(hours=int(times))
            forecast_datetime = forecast_datetime.replace(minute=0, second=0, microsecond=0)
            aqi_data = aqi[int(times)]
            aqi_obj = AQI()
            aqi_obj.data = aqi_data
            datetimes[forecast_datetime] = aqi_obj

        self.datetimes = datetimes
        self.dataset.close()

    def to_json(self, pois):
        """Converts the parsed netcdf data into JSON format and calculates nearest AQI values for POIs

        Args:
            pois (list): List of POI objects.

        Returns:
            dict: AQI data in JSON format with nearest AQI values for POIs
        """
        data = {}
        for datetime in self.datetimes:
            time_str = datetime.strftime('%Y-%m-%d %H:%M:%S')
            aqi_object = self.datetimes[datetime]

            nearest_aqi_values = {}
            for poi in pois:
                lat_poi, lon_poi = float(poi.latitude), float(poi.longitude)
                lat_index = np.abs(self.latitudes - lat_poi).argmin()
                lon_index = np.abs(self.longitudes - lon_poi).argmin()
                aqi_value = aqi_object.data[lat_index, lon_index]

                if aqi_value == 0:
                    valid_indices = np.where(aqi_object.data != 0)
                    if valid_indices[0].size == 0:
                        aqi_value = 0
                    else:
                        distances = np.sqrt((self.latitudes[valid_indices] - lat_poi)**2 
                                            + 
                                            (self.longitudes[valid_indices] - lon_poi)**2)
                        nearest_valid_index = np.argmin(distances)
                        aqi_value = aqi_object.data[valid_indices][nearest_valid_index]

                poi_coords = f'{lat_poi}, {lon_poi}'
                nearest_aqi_values[poi_coords] = {'Air Quality Index': str(aqi_value)}

            data[time_str] = nearest_aqi_values

        return data

    def _download_to_file(self, url, file_name, max_retries):
            """Downloads the file content

            Args:
                url (string): url of the file to be downloaded
                file_name (string): name of the file
                max_retries (int): maximum number of retries
            """
            for retry_attempt in range(max_retries-1):
                try:
                    start_time = time.time()
                    print('Downloading AQI data')
                    with open(file_name, 'wb') as file:
                        response = requests.get(url, stream=True)
                        for chunk in response.iter_content(chunk_size=10*1024*1024):
                            file.write(chunk)
                        print('Finished downloading. Parsing data...')
                        end_time = time.time()
                        print(f'{end_time - start_time} seconds')
                        return
                except (requests.RequestException, ConnectionResetError) as e:
                    print(f"Download attempt {retry_attempt + 1} failed with error: {str(e)}")
                    if retry_attempt < max_retries:
                        print(f'Retrying...')
                    else:
                        print(f"Maximum retries reached. Download failed.")
