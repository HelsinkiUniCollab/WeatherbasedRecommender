# greener-paths

# Instructions

## Using Docker
The simplest way of running the application is using Docker. To do so:

1. Install Docker.
2. Prepare Graphhopper
   - Clone `https://version.helsinki.fi/ivkropot/docker-graphhopper`.
   - Got into the cloned directory.
   - Run `build.sh` to build a Docker image.
3. Go to the root of this repository and run `docker compose up`.

## Local installation
If for some reason one needs to run the files locally, you should follow the instructions below.

1. Install the required software
   - Python libraries from requirements.txt (preferrably into a virtual environment)
   - osmconvert (from osmctools on Debian/Ubuntu)
   - Docker
   - mongo shell
2. Prepare Graphhopper
   - Clone `https://version.helsinki.fi/ivkropot/docker-graphhopper`.
   - Got into the cloned directory.
   - Run `build.sh` to build a Docker image.

For additional information on how the app can be started see Dockerfiles and `start_background_services.sh`. Notice, that you might need to change some urls (e.g., for mongodb) to make it work. 

# Documentation
The application consists of three main components: UI built as a Dash app, Graphhopper routing engine and a MongoDB database.

## Dash application
The UI is built using a python library called [Dash](https://dash.plotly.com/). The UI shows the map of Helsinki and provides user with controls and information.

Most of the relevant code used for the interactive UI is in a file called `app.py`. Miscellaneous helper functions (e.g., poi filtering, weather information, etc.) are found in the `utils` directory.

## MongoDB database
The application is using MongoDB to store POIs and for filtering the results (including geospatial filtering).

The data in the database is gathered from the [Servicemap API](https://api.hel.fi/servicemap/v2/) and has basic POI information (id, name, location, activity attributes). The activity attributes are given according to the deifinitions in the file `activity_definitions.py`, where each activity class is given one or multiple attributes. 

### Running without `docker compose`
The sctipt `mongodb_docker.sh` starts mongoDB in a Docker container. When the database is running, use `build_mongodb.py` to get the POI data from servicemap API and save it in the database for further usage.

## Graphhopper
[Graphhopper](https://www.graphhopper.com/) routing engine is used for providing directions for the user. In this application a slightly modified version of the engine is used (to accomodate for air quality index (AQI) based route suggestions). The modified version is found [here](https://version.helsinki.fi/ivkropot/graphhopper-fork).

Directory `graphhopper_server` has useful scripts and also contains data used by Graphhopper (e.g., OpenStreetMap data, AQI data, etc.). The most important file is `config.yml` (located under `graphopper_server/graphhopper_data`) which is used for modifying the settings of Graphhopper routing engine (e.g., specifying different routing profiles, etc.). For more information see the file itself and Graphhopper documentation in [GitHub](https://github.com/graphhopper/graphhopper/tree/master/docs/core).

### Running without `docker compose`
The script `init.sh` should be ran before the Graphhopper server is started for the first time (or after modifying Graphhopper image or `config.yml`). `start_server.sh` simply starts the Docker container with the Graphhopper server.

## Other
`aqi_tools.py` is a script used for downloading up-to-date AQI data from FMI API. It is used in `update_aqi.sh` script for downloading the AQI data to a cache folder where Graphhopper can see it. **WARNING:** Sometimes downloading AQI fails (due to unknown server error) in which case you should try again!

## More on Docker
This application uses multiple Docker containers which are started via command `docker compose up`. The different services and how they are defined can be found in `compose.yaml`. 

A quick overview of the services (each a separate Docker container) in order that they are started (NOTE: See Quirks section for details):

1. `mongodb`
   - As the name implies, this is simply a mongodb server.
2. `background_services`
   - This container runs some services that help others.
   - It periodically checks for new AQI data and downloads it when available.
   - Handles downloading and preprocessing of some files used by Graphhopper server (e.g., openstreetmaps).
3. `graphhopper`
   - The Grapphopper server which handles all the routing.
   - Based on the docker image built in the preparation phase.
4. `greener_paths`
   - The app itself running (by default) on port 8050.

## Quirks
1. On initial start-up the Graphhopper server will do a lot of preprocessing, during which Docker might flag the container as `unhealthy`. After the preprocessing is done and the server is up an running everything should get back in order.
   - As a consquence of this, the UI Dash app might start before the Graphhopper's preprocessing step done, which results in routing not working until it is finished.
2. As mentioned previously, downloading AQI data is prone to erorrs and time-outs, which might affect the initial start of the application (start up failure is a possibility if downloading AQI fails too many times in a row).
   - If internet speed is slow, one might want to tune the timeout parameter in the `get` request in `aqi_tools.py`.