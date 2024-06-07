#!/bin/bash

# Run this script to download all the necessary files and do the preprocessing
# before starting the Graphopper server for the first time.

####################################
# Requires: Docker and Osmconvert! #
####################################

# Remove the graph cache if exists
if [ -d "$(pwd)"/graphhopper_data/graph_cache ]; then
    echo "Old graph cache exists. Removing..."
    rm -rf "$(pwd)/graphhopper_data/graph_cache"
fi
mkdir "$(pwd)/graphhopper_data/graph_cache"

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

docker run \
    --rm -p 8989:8989 \
    --mount type=bind,source="$(pwd)"/graphhopper_data,target=/graphhopper/data \
    activity-recommender/graphhopper \
    --input /graphhopper/data/helsinki.osm.pbf \
    --config /graphhopper/data/config.yml \
    --graph-cache /graphhopper/data/graph_cache \
    --port 8989 \
    --host 0.0.0.0 \
    --import