import numpy as np
import tempfile
import requests
import defusedxml.ElementTree as ET
import time
from urllib.parse import urlencode
from netCDF4 import Dataset
from ..config import Config
from datetime import timedelta
from .times import get_forecast_times, server_time_to_finnish
from scipy.spatial import cKDTree
import pickle
import os


class AQI:
    def __init__(self):
        """A class representing a single AQI object.

        Args:
            data (numpy array): aqi data as numpy array
            dataset (netcdf): netcdf dataset containing the AQI data
            datetimes (dict): dictionary containing datetimes and AQI objects
            coord_kdtree (cKDTree): kdtree containing all possible lat, lon pairs
        """
        self.data = None
        self.dataset = None
        self.datetimes = None
        self.coords_kdtree = None

    def download_netcdf_and_store(self):
        """Downloads NETCDF file, parses it and stores the data in the object.
           The temporary file is deleted afterwards.
        """
        path = "aqi.pkl"
        if os.path.isfile(path):
            print("download_netcdf_and_store stopped")
            return

        netcdf_file_url = self._parse_xml()

        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            netcdf_file_name = temp_file.name
            self._download_to_file(netcdf_file_url, netcdf_file_name, 5)
            self.dataset = Dataset(netcdf_file_name)
            self._parse_netcdf()

    def _parse_xml(self):
        """Parses the FMI open data XML file.

        Returns:
            String: URL link of the latest queried NETCDF file
        """
        url = self._get_xml_url()
        req = requests.get(url)
        content = req.content
        xml = ET.fromstring(content)
        file_reference = xml.findall(Config.XML['MEMBERS']['FILE_REFERENCE'])
        return file_reference[-1].text

    def _get_xml_url(self):
        """Fetches the XML -file URL based on query.

        Returns:
            String: XML -file URL
        """
        _, start_time, end_time = get_forecast_times()

        args = {
            'starttime': start_time,
            'endtime': end_time,
            'parameters': Config.FMI_FORECAST['AIR_QUALITY']['PARAMETERS'],
            'bbox': Config.FMI_FORECAST['AIR_QUALITY']['BBOX']
        }

        xml_url = (
            Config.FMI_GENERAL['FMI_QUERY_URL'] +
            Config.FMI_GENERAL['FMI_QUERIES']['AQI_FORECAST_GRID_ENFUSER'] +
            "&" +
            urlencode(args)
        )

        return xml_url

    def _parse_netcdf(self):
        """Parses the given NETCDF -file.

        Returns:
            dict: A dictionary of datetimes keys and AQI object values
        """
        latitudes = self.dataset.variables['lat'][:]
        longitudes = self.dataset.variables['lon'][:]
        times = self.dataset.variables['time'][:]
        aqi = self.dataset.variables['index_of_airquality_194'][:]

        forecast_time = server_time_to_finnish() + timedelta(hours=1)

        datetimes = {}
        for hour in times:
            forecast_datetime = forecast_time + timedelta(hours=int(hour))
            forecast_datetime = forecast_datetime.replace(
                minute=0, second=0, microsecond=0)
            aqi_data = aqi[int(hour)]

            non_zero_lat_indices, non_zero_lon_indices = np.where(
                aqi_data != 0)

            filtered_coords = (
                np.column_stack(
                    (
                        latitudes[non_zero_lat_indices],
                        longitudes[non_zero_lon_indices]
                    )
                )
            )

            coords_kdtree = cKDTree(filtered_coords)
            filtered_aqi = aqi_data[non_zero_lat_indices, non_zero_lon_indices]

            aqi_obj = AQI()
            aqi_obj.data = filtered_aqi
            aqi_obj.coords_kdtree = coords_kdtree
            datetimes[forecast_datetime] = aqi_obj

        self.datetimes = datetimes
        self.dataset.close()

    def to_json(self, pois):
        """Converts the parsed netcdf data into JSON format and calculates nearest AQI values for POI's.

        Args:
            pois (list): List of POI objects.

        Returns:
            dict: AQI data in JSON format with nearest AQI values for POI's
        """
        path = "aqi.pkl"
        if os.path.isfile(path):
            print("READ FROM FILE")
            with open(path, 'rb') as file:
                data = pickle.load(file)
                return data
        data = {}
        for datetime in self.datetimes:
            time_str = datetime.strftime('%Y-%m-%d %H:%M:%S')
            aqi_object = self.datetimes[datetime]

            nearest_aqi_values = {}
            for poi in pois:
                lat_poi, lon_poi = float(poi.latitude), float(poi.longitude)
                _, closest_index = aqi_object.coords_kdtree.query(
                    [lat_poi, lon_poi])
                aqi_value = aqi_object.data[closest_index]
                poi_coords = f'{lat_poi}, {lon_poi}'
                nearest_aqi_values[poi_coords] = {
                    'Air Quality Index': str(aqi_value)}

            data[time_str] = nearest_aqi_values

        if not os.path.isfile(path):
            with open(path, 'wb') as file:
                print("SAVED TO FILE")
                pickle.dump(data, file)

        return data

    def _download_to_file(self, url, file_name, max_retries):
        """Downloads the files content.

            Args:
                url (String): URL of the file to be downloaded
                file_name (String): name of the file
                max_retries (int): maximum number of retries
            """
        #print("download paused")
        #return
        path = "aqi.pkl"
        if os.path.isfile(path):
            print("The file exists")
            return
        else:
            print("The file does not exist")
        for retry_attempt in range(max_retries-1):
            try:
                start_time = time.time()
                print('Downloading the AQI data...')
                with open(file_name, 'wb') as file:
                    response = requests.get(url, stream=True, timeout=240)
                    for chunk in response.iter_content(chunk_size=10*1024*1024):
                        file.write(chunk)
                    end_time = time.time()
                    print(
                        f'Finished downloading in {end_time - start_time} seconds. Parsing the data...')
                    return
            except (requests.RequestException, ConnectionResetError) as error:
                print(
                    f"Download attempt {retry_attempt + 1} failed with error: {str(error)}")
                if retry_attempt < max_retries:
                    print('Retrying...')
                else:
                    print("Maximum retries reached. Download failed.")
