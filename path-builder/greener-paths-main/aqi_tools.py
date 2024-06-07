import datetime
import shutil
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
import netCDF4

import requests
from netCDF4 import Dataset  # type: ignore

from utils.weather_utils import ns


def download_current_aqi(savepath: str, max_retries: int = 1):
    # Get the query parameters
    url = (
        "http://opendata.fmi.fi/wfs/fin?service=WFS&version=2.0.0"
        "&request=GetFeature"
        "&storedquery_id=fmi::forecast::enfuser::airquality::helsinki-metropolitan::grid"
        "&parameters=AQIndex"
        "bbox=24.58,60.1321,25.1998,60.368"
    )

    resp = requests.get(url)
    resp.raise_for_status()

    # The fromstring method returns the root
    root = ET.fromstring(resp.content.decode("utf-8"))

    begin_position = root.find(
        "./wfs:member/omso:GridSeriesObservation/om:phenomenonTime/gml:TimePeriod/gml:beginPosition",
        ns,
    )
    end_position = root.find(
        "./wfs:member/omso:GridSeriesObservation/om:phenomenonTime/gml:TimePeriod/gml:endPosition",
        ns,
    )
    if begin_position is None or end_position is None:
        raise ValueError("The XML member beingPosition or endPosition was not found.")

    begin_position = begin_position.text
    end_position = end_position.text

    # Compose the url
    url = (
        "https://opendata.fmi.fi/download?producer=enfuser_helsinki_metropolitan"
        "&param=AQIndex"
        "&bbox=24.58,60.1321,25.1998,60.368"
        "&levels=0"
        f"&origintime={begin_position}"
        f"&starttime={begin_position}"
        f"&endtime={end_position}"
        "&format=netcdf"
        "&projection=EPSG:4326"
    )
    # Download the data
    print("Downloading AQI data...")
    download_success = False
    for r in range(max_retries):
        print(f"Try {r}")
        try:
            with requests.get(url, stream=True, timeout=300) as response:
                response.raise_for_status()

                with open(Path(savepath), "wb") as file:
                    # Iterate over the response content in chunks and save them to the file
                    for chunk in response.iter_content(
                        chunk_size=1024 * 1024 * 5
                    ):  # 5MB chunks
                        if chunk:
                            file.write(chunk)

            print(f"Downloaded {url} to {Path(savepath)}")
            download_success = True
            break

        except (
            requests.exceptions.RequestException,
            requests.exceptions.ConnectionError,
            IOError,
        ) as e:
            print(f"Error: {e}")
            print("Downloading AQI data failed!")
            Path(savepath).unlink(missing_ok=True)
    if not download_success:
        raise RuntimeError("Downloading AQI data failed!")
    else:
        print("Latest AQI data fetched!")


def is_aqi_up_to_date(aqi_savepath: str) -> bool:
    aqi_path = Path(aqi_savepath)
    if aqi_path.is_file():
        try:
            nc = Dataset(aqi_path)
        except Exception as e:
            print(f"Opening NetCDF formatted file {aqi_path} produced an error:")
            print(e)
            return False
        else:
            time_var = nc.variables["time"]
            last_time = netCDF4.num2date(time_var[:], time_var.units, time_var.calendar)[-1]  # type: ignore
            now = datetime.datetime.utcnow()
            # Check that there is at least two hours left of up-to-date data
            if last_time - now > datetime.timedelta(hours=2):
                return True

    return False


def main(savepath: str = "./data/aqi_data.nc") -> None:
    if Path(savepath).exists() and is_aqi_up_to_date(savepath):
        print("AQI file is up to date!")
    else:
        download_current_aqi(savepath)


if __name__ == "__main__":
    if len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        main()
