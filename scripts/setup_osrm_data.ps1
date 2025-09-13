# PowerShell script to download and prepare OSRM data for Argentina
# This script downloads OpenStreetMap data for Argentina and prepares it for OSRM

param(
    [string]$DataDir = "./osrm-data",
    [switch]$Force
)

# Configuration
$OSM_FILE = "argentina-latest.osm.pbf"
$OSRM_FILE = "argentina-latest.osrm"
$DOWNLOAD_URL = "https://download.geofabrik.de/south-america/argentina-latest.osm.pbf"

Write-Host "Setting up OSRM data for Argentina..." -ForegroundColor Green

# Create data directory
if (!(Test-Path $DataDir)) {
    New-Item -ItemType Directory -Path $DataDir -Force | Out-Null
}

Set-Location $DataDir
$FullDataDir = (Get-Location).Path

# Download Argentina OSM data if not exists
$OSMPath = Join-Path $FullDataDir $OSM_FILE
if (!(Test-Path $OSMPath) -or $Force) {
    Write-Host "Downloading Argentina OSM data..." -ForegroundColor Yellow
    try {
        Invoke-WebRequest -Uri $DOWNLOAD_URL -OutFile $OSMPath -UseBasicParsing
        Write-Host "Download completed." -ForegroundColor Green
    }
    catch {
        Write-Error "Failed to download OSM data: $_"
        exit 1
    }
} else {
    Write-Host "OSM data already exists, skipping download." -ForegroundColor Cyan
}

# Check if OSRM files already exist
$OSRMPath = Join-Path $FullDataDir $OSRM_FILE
if ((Test-Path $OSRMPath) -and !$Force) {
    Write-Host "OSRM data already prepared." -ForegroundColor Green
    exit 0
}

Write-Host "Preparing OSRM data..." -ForegroundColor Yellow

# Check if Docker is available
try {
    docker --version | Out-Null
} catch {
    Write-Error "Docker is required but not found. Please install Docker Desktop."
    exit 1
}

try {
    # Extract and prepare data using Docker
    Write-Host "Extracting OSM data..." -ForegroundColor Yellow
    docker run -t -v "${FullDataDir}:/data" osrm/osrm-backend osrm-extract -p /opt/car.lua /data/$OSM_FILE
    
    Write-Host "Partitioning data..." -ForegroundColor Yellow
    docker run -t -v "${FullDataDir}:/data" osrm/osrm-backend osrm-partition /data/$OSRM_FILE
    
    Write-Host "Customizing data..." -ForegroundColor Yellow
    docker run -t -v "${FullDataDir}:/data" osrm/osrm-backend osrm-customize /data/$OSRM_FILE
    
    Write-Host "OSRM data preparation completed!" -ForegroundColor Green
    Write-Host "You can now start the OSRM service with: docker-compose up osrm" -ForegroundColor Cyan
}
catch {
    Write-Error "Failed to prepare OSRM data: $_"
    exit 1
}

# Return to original directory
Set-Location ..