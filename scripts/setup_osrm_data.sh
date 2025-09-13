#!/bin/bash

# Script to download and prepare OSRM data for Argentina
# This script downloads OpenStreetMap data for Argentina and prepares it for OSRM

set -e

# Configuration
OSRM_DATA_DIR="./osrm-data"
OSM_FILE="argentina-latest.osm.pbf"
OSRM_FILE="argentina-latest.osrm"
DOWNLOAD_URL="https://download.geofabrik.de/south-america/argentina-latest.osm.pbf"

echo "Setting up OSRM data for Argentina..."

# Create data directory
mkdir -p "$OSRM_DATA_DIR"
cd "$OSRM_DATA_DIR"

# Download Argentina OSM data if not exists
if [ ! -f "$OSM_FILE" ]; then
    echo "Downloading Argentina OSM data..."
    wget -O "$OSM_FILE" "$DOWNLOAD_URL"
    echo "Download completed."
else
    echo "OSM data already exists, skipping download."
fi

# Check if OSRM files already exist
if [ -f "$OSRM_FILE" ]; then
    echo "OSRM data already prepared."
    exit 0
fi

echo "Preparing OSRM data..."

# Extract and prepare data using Docker
echo "Extracting OSM data..."
docker run -t -v "${PWD}:/data" osrm/osrm-backend osrm-extract -p /opt/car.lua /data/$OSM_FILE

echo "Partitioning data..."
docker run -t -v "${PWD}:/data" osrm/osrm-backend osrm-partition /data/$OSRM_FILE

echo "Customizing data..."
docker run -t -v "${PWD}:/data" osrm/osrm-backend osrm-customize /data/$OSRM_FILE

echo "OSRM data preparation completed!"
echo "You can now start the OSRM service with: docker-compose up osrm"