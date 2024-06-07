#!/bin/bash
imagename="activity-recommender/graphhopper:${1:-latest}"
echo "Building docker image ${imagename}"
docker build . -t "${imagename}"

