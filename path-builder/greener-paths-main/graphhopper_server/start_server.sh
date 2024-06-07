#!/bin/bash

# Script for starting a graphhopper server in a Docker.
# Run init.sh before starting for the first time

#docker run -p 8989:8989 israelhikingmap/graphhopper --url https://download.geofabrik.de/europe/finland-latest.osm.pbf --host 0.0.0.0
  # --mount type=bind,source="$(pwd)"/finland-latest.osm.pbf,target=/graphhopper/data/finland-latest.osm.pbf \
  
docker run --rm -d -p 8989:8989 \
    --name graphhopper_server \
    --mount type=bind,source="$(pwd)"/graphhopper_data,target=/graphhopper/data \
    activity-recommender/graphhopper \
    --input /graphhopper/data/helsinki.osm.pbf \
    --config /graphhopper/data/config.yml \
    --graph-cache /graphhopper/data/graph_cache \
    --port 8989 \
    --host 0.0.0.0
