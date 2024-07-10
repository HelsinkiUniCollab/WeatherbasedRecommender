class Config:
    # General FMI
    FMI_GENERAL = {
        'FMI_QUERY_URL': 'http://opendata.fmi.fi/wfs?service=WFS&version=2.0.0&request=getFeature&storedquery_id=',
        'FMI_QUERIES': {
            'AQI_FORECAST_GRID_ENFUSER': 'fmi::forecast::enfuser::airquality::helsinki-metropolitan::grid'
        }
    }

    # FMI current time queries
    FMI_CURRENT = {
        'WEATHER': {
            'BBOX': '24.5,60,25.5,60.5',
        },
        'AIR_QUALITY': {
            'BBOX': '24.5,60,25.5,60.5',
            'PARAMETERS': 'AQINDEX_PT1H_avg',
        }
    }

    # FMI forecasted queries
    FMI_FORECAST = {
        'WEATHER': {
            'BBOX': '24.5,60,25.5,60.5',
            'PARAMETERS': 'Temperature,Humidity,WindUMS,WindVMS,PrecipitationAmount,TotalCloudCover',
            'TIMESTEP': 60
        },
        'AIR_QUALITY': {
            'BBOX': '24.857740,60.137557,25.226838,60.278260',
            'PARAMETERS': 'AQIndex'
        }
    }

    # Caching
    CACHING = {
        'REDIS': {
            'URL': 'redis://redis:6379/0'
        },
        'TIMEOUT': {
            'WEATHER_WARNING': 3600,
            'FORECAST_WEATHER': 3600,
            'FORECAST_AIRQUALITY': 86400,
        }
    }

    # XML 
    XML = {
        'MEMBERS': {
            'FILE_REFERENCE': './/{http://www.opengis.net/gml/3.2}fileReference'
        }
    }
