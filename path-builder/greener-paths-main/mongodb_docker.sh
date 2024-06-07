#!/bin/bash

# Script for starting a mongodb server

# Pull the MongoDB Docker image
docker pull mongodb/mongodb-community-server

# Run the image as a container
docker run --rm --name mongodb -d -p 27017:27017 \
    --mount source=mongo-test,target=/data/db \
    mongodb/mongodb-community-server:latest
