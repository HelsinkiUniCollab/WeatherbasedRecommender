#!/bin/bash

# This script initializes all services and starts the application.
# The user should activate the python virtual environment with the required
# libraries before running the script.

# FLAGS:
#   -i : Initialize Graphhopper
#   -s : Skip AQI update

init_gh="false"
skip_update_aqi="false"

while getopts :is flag; do
  case "$flag" in
    i) init_gh="true";;
    s) skip_update_aqi="true";;
    \?)
      echo "Invalid flag"
      exit
    ;;
  esac
done

#-------------------#
#------MongoDB------#
#-------------------#
echo "Initializing MongoDB..."

# Check if activity database already exists
MONGO_HOST="mongodb"
MONGO_PORT="27017"
DB_NAME="activities"

database_exists=$(mongosh --quiet --host "$MONGO_HOST" --port "$MONGO_PORT" --eval "db.getMongo().getDBNames().indexOf('$DB_NAME') != -1")

# Rebuild the database if needed
if [ "$database_exists" = "true" ]; then
  echo "Database '$DB_NAME' exists."
  echo "No need for rebuilding"
else
  echo "Database '$DB_NAME' does not exist."
  echo "Building database..."
  python build_mongodb.py
fi

echo "MongoDB initialized"

# Run this script to download all the necessary files and do the preprocessing
# before starting the Graphopper server for the first time.

####################################
# Requires: Docker and Osmconvert! #
####################################

echo "Setting up Graphhopper files..."

# Copy the config file
cp config.yml graphhopper_data/

# Remove the graph cache if exists
if [ "$init_gh" = "true" ]; then
    if [ -d "$(pwd)"/graphhopper_data/graph_cache ]; then
        echo "Old graph cache exists. Removing..."
        rm -rf "$(pwd)/graphhopper_data/graph_cache"
    fi
fi
if [ ! -d "$(pwd)/graphhopper_data/graph_cache" ]; then
    echo "Directory graph_cache doesn't exist! Creating.."
    mkdir "$(pwd)/graphhopper_data/graph_cache"
fi

# Download the OSM data of Finland if needed
if [ ! -f "$(pwd)"/graphhopper_data/finland-latest.osm.pbf ]; then
    echo "Downloading Finland OSM data..."
    wget https://download.geofabrik.de/europe/finland-latest.osm.pbf  -P "$(pwd)"/graphhopper_data/
fi
# Extract an area around Helsinki to reduce resource consumption
if [ ! -f "$(pwd)"/graphhopper_data/helsinki.osm.pbf ]; then
    echo "Extracting Helsinki area..."
    osmconvert graphhopper_data/finland-latest.osm.pbf -b=24.153,59.908,25.609,60.387 --out-pbf -o=graphhopper_data/helsinki.osm.pbf
fi

echo "Graphopper files initialzed"

echo "Updating AQI for the first time..."
# Run the AQI update for the first time
/update_aqi.sh

# Start cron 
cron -f