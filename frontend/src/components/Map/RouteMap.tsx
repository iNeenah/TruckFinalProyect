import React, { useState, useCallback, useEffect, useRef } from 'react';
import { MapRef } from 'react-map-gl';
import BaseMap from './BaseMap';
import MapMarker from './MapMarker';
import RouteLayer from './RouteLayer';
import MapControls from './MapControls';
import {
  Location,
  RouteFeature,
  MarkerData,
  TollPoint,
  FuelStation,
  MapClickEvent,
  MapMoveEvent,
  getBoundsFromLocations,
} from '../../types/map';

interface RouteMapProps {
  // Route data
  routes?: RouteFeature[];
  selectedRouteId?: string;
  onRouteSelect?: (routeId: string) => void;
  
  // Locations
  origin?: Location;
  destination?: Location;
  waypoints?: Location[];
  tollPoints?: TollPoint[];
  fuelStations?: FuelStation[];
  
  // Interaction handlers
  onLocationSelect?: (location: Location, type: 'origin' | 'destination') => void;
  onMapClick?: (event: MapClickEvent) => void;
  
  // Display options
  showAllRoutes?: boolean;
  showTollPoints?: boolean;
  showFuelStations?: boolean;
  showRouteInfo?: boolean;
  
  // Map configuration
  className?: string;
  height?: string;
}

function RouteMap({
  routes = [],
  selectedRouteId,
  onRouteSelect,
  origin,
  destination,
  waypoints = [],
  tollPoints = [],
  fuelStations = [],
  onLocationSelect,
  onMapClick,
  showAllRoutes = true,
  showTollPoints = true,
  showFuelStations = false,
  showRouteInfo = true,
  className = 'w-full',
  height = '500px',
}: RouteMapProps) {
  const mapRef = useRef<MapRef>(null);
  const [selectedMarker, setSelectedMarker] = useState<MarkerData | null>(null);
  const [mapLoaded, setMapLoaded] = useState(false);

  // Create markers array
  const markers: MarkerData[] = React.useMemo(() => {
    const allMarkers: MarkerData[] = [];

    // Add origin marker
    if (origin) {
      allMarkers.push({
        id: 'origin',
        coordinates: origin.coordinates,
        type: 'origin',
        title: origin.name,
        description: origin.address,
      });
    }

    // Add destination marker
    if (destination) {
      allMarkers.push({
        id: 'destination',
        coordinates: destination.coordinates,
        type: 'destination',
        title: destination.name,
        description: destination.address,
      });
    }

    // Add waypoint markers
    waypoints.forEach((waypoint, index) => {
      allMarkers.push({
        id: `waypoint-${index}`,
        coordinates: waypoint.coordinates,
        type: 'waypoint',
        title: waypoint.name,
        description: waypoint.address,
      });
    });

    // Add toll point markers
    if (showTollPoints) {
      tollPoints.forEach(tollPoint => {
        allMarkers.push(tollPoint);
      });
    }

    // Add fuel station markers
    if (showFuelStations) {
      fuelStations.forEach(fuelStation => {
        allMarkers.push(fuelStation);
      });
    }

    return allMarkers;
  }, [origin, destination, waypoints, tollPoints, fuelStations, showTollPoints, showFuelStations]);

  // Fit map to show all locations
  const fitToLocations = useCallback(() => {
    if (!mapRef.current || markers.length === 0) return;

    const locations = markers.map(marker => ({
      name: marker.title,
      address: marker.description || '',
      coordinates: marker.coordinates,
    }));

    const bounds = getBoundsFromLocations(locations);
    mapRef.current.fitBounds(bounds, {
      padding: 50,
      duration: 1000,
    });
  }, [markers]);

  // Auto-fit when locations change
  useEffect(() => {
    if (mapLoaded && markers.length > 0) {
      const timer = setTimeout(fitToLocations, 100);
      return () => clearTimeout(timer);
    }
  }, [mapLoaded, markers, fitToLocations]);

  const handleMapClick = useCallback((event: MapClickEvent) => {
    // Close any open popups
    setSelectedMarker(null);
    
    // Call parent handler
    onMapClick?.(event);
  }, [onMapClick]);

  const handleMarkerClick = useCallback((marker: MarkerData) => {
    setSelectedMarker(marker);
  }, []);

  const handlePopupClose = useCallback(() => {
    setSelectedMarker(null);
  }, []);

  const handleRouteClick = useCallback((routeId: string) => {
    onRouteSelect?.(routeId);
  }, [onRouteSelect]);

  const handleMapLoad = useCallback(() => {
    setMapLoaded(true);
  }, []);

  const selectedRoute = routes.find(route => route.properties.route_id === selectedRouteId);

  return (
    <div className={className} style={{ height }}>
      <BaseMap
        ref={mapRef}
        controls={['navigation', 'fullscreen', 'scale', 'geolocate']}
        onClick={handleMapClick}
        onLoad={handleMapLoad}
        className="relative"
      >
        {/* Route layers */}
        {routes.length > 0 && (
          <RouteLayer
            routes={routes}
            selectedRouteId={selectedRouteId}
            onRouteClick={handleRouteClick}
            showAllRoutes={showAllRoutes}
          />
        )}

        {/* Markers */}
        {markers.map(marker => (
          <MapMarker
            key={marker.id}
            marker={marker}
            showPopup={selectedMarker?.id === marker.id}
            onPopupClose={handlePopupClose}
            onClick={handleMarkerClick}
          />
        ))}

        {/* Map controls */}
        <MapControls
          routes={routes}
          selectedRouteId={selectedRouteId}
          onRouteSelect={onRouteSelect}
          onFitToRoute={() => fitToLocations()}
          showRouteInfo={showRouteInfo}
        />
      </BaseMap>
    </div>
  );
}

export default RouteMap;