import datetime
import re
import xml.etree.ElementTree as ET

import requests

# Extract namespaces
ns = {
    "wfs": "http://www.opengis.net/wfs/2.0",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    "xlink": "http://www.w3.org/1999/xlink",
    "om": "http://www.opengis.net/om/2.0",
    "omso": "http://inspire.ec.europa.eu/schemas/omso/3.0",
    "ompr": "http://inspire.ec.europa.eu/schemas/ompr/3.0",
    "gml": "http://www.opengis.net/gml/3.2",
    "gmd": "http://www.isotc211.org/2005/gmd",
    "gco": "http://www.isotc211.org/2005/gco",
    "swe": "http://www.opengis.net/swe/2.0",
    "gmlcov": "http://www.opengis.net/gmlcov/1.0",
    "sam": "http://www.opengis.net/sampling/2.0",
    "sams": "http://www.opengis.net/samplingSpatial/2.0",
    "wml2": "http://www.opengis.net/waterml/2.0",
    "target": "http://xml.fmi.fi/namespace/om/atmosphericfeatures/1.1",
}


def get_weather_data() -> tuple[float, float, float]:
    start_time = datetime.datetime.now()
    end_time = start_time + datetime.timedelta(hours=1)
    start_time = start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
    end_time = end_time.strftime("%Y-%m-%dT%H:%M:%SZ")

    # Get the data from FMI in xml format
    url = (
        "http://opendata.fmi.fi/wfs/fin?service=WFS&version=2.0.0"
        "&request=GetFeature"
        "&storedquery_id=fmi::forecast::edited::weather::scandinavia::point::timevaluepair"
        "&place=Helsinki"
        "&parameters=temperature,precipitation1h,weathersymbol3"
        f"&starttime={start_time}&endtime={end_time}&"
    )
    resp = requests.get(url)
    resp.raise_for_status()

    # The fromstring method returns the root
    root = ET.fromstring(resp.content.decode("utf-8"))

    # Get the temperature value
    temperature = root.find(
        ".//wml2:MeasurementTimeseries[@gml:id='mts-1-1-temperature']//wml2:value",
        ns,
    )
    temperature = float(temperature.text)

    # Get the precipitation amount
    precipitation = root.find(
        ".//wml2:MeasurementTimeseries[@gml:id='mts-1-1-precipitation1h']//wml2:value",
        ns,
    )
    precipitation = float(precipitation.text)

    # Get the weather symbol
    weathersymbol = root.find(
        ".//wml2:MeasurementTimeseries[@gml:id='mts-1-1-weathersymbol3']//wml2:value",
        ns,
    )
    weathersymbol = float(weathersymbol.text)

    return temperature, precipitation, weathersymbol


def main():
    print(get_weather_data())


if __name__ == "__main__":
    main()
