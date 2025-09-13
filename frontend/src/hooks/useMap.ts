import { useState, useCallback, useRef, useEffect } from 'react';
import { MapRef } from 'react-map-gl';
import {
  Location,
  RouteFeature,
  MarkerData,
  TollPoint,
  FuelStation,
  MapClickEvent,
  getBoundsFromLocations,
} from '../types/map';

interface UseMapOptions {
  autoFit?: boolean;
  fitPadding?: number;
}

export function useMap(options: UseMapOptions = {}) {
  const { autoFit = true, fitPadding = 50 } = options;
  const mapRef = useRef<MapRef>(null);
  const [isLoaded, setIsLoaded] = useState(false);
  const [selectedMarker, setSelectedMarker] = useState<MarkerData | null>(null);

  // Map control methods
  const fitBounds = useCallback((bounds: any, padding?: number) => {
    if (!mapRef.current) return;
    
    mapRef.current.fitBounds(bounds, {
      padding: padding || fitPadding,
      duration: 1000,
    });
  }, [fitPadding]);

  const flyTo = useCallback((coordinates: [number, number], zoom?: number) => {
    if (!mapRef.current) return;
    
    mapRef.current.flyTo({
      center: coordinates,
      zoom: zoom || 12,
      duration: 1000,
    });
  }, []);

  const fitToLocations = useCallback((locations: Location[]) => {
    if (!mapRef.current || locations.length === 0) return;
    
    const bounds = getBoundsFromLocations(locations);
    fitBounds(bounds);
  }, [fitBounds]);

  const centerOnLocation = useCallback((location: Location, zoom?: number) => {
    flyTo(location.coordinates, zoom);
  }, [flyTo]);

  // Marker management
  const selectMarker = useCallback((marker: MarkerData | null) => {
    setSelectedMarker(marker);
  }, []);

  const closePopup = useCallback(() => {
    setSelectedMarker(null);
  }, []);

  // Map event handlers
  const handleMapLoad = useCallback(() => {
    setIsLoaded(true);
  }, []);

  const handleMapClick = useCallback((event: MapClickEvent) => {
    // Close any open popups when clicking on the map
    setSelectedMarker(null);
  }, []);

  const handleMarkerClick = useCallback((marker: MarkerData) => {
    setSelectedMarker(marker);
  }, []);

  // Auto-fit functionality
  const autoFitToContent = useCallback((
    locations: Location[],
    routes: RouteFeature[] = []
  ) => {
    if (!autoFit || !isLoaded) return;

    // Collect all locations from various sources
    const allLocations: Location[] = [...locations];

    // Add route waypoints if available
    routes.forEach(route => {
      if (route.geometry.coordinates.length > 0) {
        const startCoord = route.geometry.coordinates[0];
        const endCoord = route.geometry.coordinates[route.geometry.coordinates.length - 1];
        
        allLocations.push({
          name: 'Route Start',
          address: '',
          coordinates: startCoord,
        });
        
        allLocations.push({
          name: 'Route End',
          address: '',
          coordinates: endCoord,
        });
      }
    });

    if (allLocations.length > 0) {
      fitToLocations(allLocations);
    }
  }, [autoFit, isLoaded, fitToLocations]);

  return {
    // Refs
    mapRef,
    
    // State
    isLoaded,
    selectedMarker,
    
    // Map controls
    fitBounds,
    flyTo,
    fitToLocations,
    centerOnLocation,
    autoFitToContent,
    
    // Marker management
    selectMarker,
    closePopup,
    
    // Event handlers
    handleMapLoad,
    handleMapClick,
    handleMarkerClick,
  };
}

// Hook for route visualization
export function useRouteVisualization() {
  const [selectedRouteId, setSelectedRouteId] = useState<string | null>(null);
  const [showAllRoutes, setShowAllRoutes] = useState(true);
  const [highlightedRoute, setHighlightedRoute] = useState<string | null>(null);

  const selectRoute = useCallback((routeId: string | null) => {
    setSelectedRouteId(routeId);
  }, []);

  const toggleShowAllRoutes = useCallback(() => {
    setShowAllRoutes(prev => !prev);
  }, []);

  const highlightRoute = useCallback((routeId: string | null) => {
    setHighlightedRoute(routeId);
  }, []);

  const getVisibleRoutes = useCallback((routes: RouteFeature[]) => {
    if (showAllRoutes) {
      return routes;
    }
    
    if (selectedRouteId) {
      return routes.filter(route => route.properties.route_id === selectedRouteId);
    }
    
    // Show recommended route by default
    const recommendedRoute = routes.find(route => route.properties.route_type === 'recommended');
    return recommendedRoute ? [recommendedRoute] : routes.slice(0, 1);
  }, [showAllRoutes, selectedRouteId]);

  return {
    selectedRouteId,
    showAllRoutes,
    highlightedRoute,
    selectRoute,
    toggleShowAllRoutes,
    highlightRoute,
    getVisibleRoutes,
  };
}

// Hook for location management
export function useLocationManagement() {
  const [origin, setOrigin] = useState<Location | null>(null);
  const [destination, setDestination] = useState<Location | null>(null);
  const [waypoints, setWaypoints] = useState<Location[]>([]);

  const updateOrigin = useCallback((location: Location | null) => {
    setOrigin(location);
  }, []);

  const updateDestination = useCallback((location: Location | null) => {
    setDestination(location);
  }, []);

  const addWaypoint = useCallback((location: Location) => {
    setWaypoints(prev => [...prev, location]);
  }, []);

  const removeWaypoint = useCallback((index: number) => {
    setWaypoints(prev => prev.filter((_, i) => i !== index));
  }, []);

  const updateWaypoint = useCallback((index: number, location: Location) => {
    setWaypoints(prev => prev.map((wp, i) => i === index ? location : wp));
  }, []);

  const clearWaypoints = useCallback(() => {
    setWaypoints([]);
  }, []);

  const clearAll = useCallback(() => {
    setOrigin(null);
    setDestination(null);
    setWaypoints([]);
  }, []);

  const getAllLocations = useCallback((): Location[] => {
    const locations: Location[] = [];
    if (origin) locations.push(origin);
    if (destination) locations.push(destination);
    locations.push(...waypoints);
    return locations;
  }, [origin, destination, waypoints]);

  const isValidRoute = useCallback(() => {
    return origin !== null && destination !== null;
  }, [origin, destination]);

  return {
    origin,
    destination,
    waypoints,
    updateOrigin,
    updateDestination,
    addWaypoint,
    removeWaypoint,
    updateWaypoint,
    clearWaypoints,
    clearAll,
    getAllLocations,
    isValidRoute,
  };
}

// Hook for map markers management
export function useMapMarkers() {
  const [tollPoints, setTollPoints] = useState<TollPoint[]>([]);
  const [fuelStations, setFuelStations] = useState<FuelStation[]>([]);
  const [showTollPoints, setShowTollPoints] = useState(true);
  const [showFuelStations, setShowFuelStations] = useState(false);

  const updateTollPoints = useCallback((points: TollPoint[]) => {
    setTollPoints(points);
  }, []);

  const updateFuelStations = useCallback((stations: FuelStation[]) => {
    setFuelStations(stations);
  }, []);

  const toggleTollPoints = useCallback(() => {
    setShowTollPoints(prev => !prev);
  }, []);

  const toggleFuelStations = useCallback(() => {
    setShowFuelStations(prev => !prev);
  }, []);

  const getAllMarkers = useCallback((
    origin?: Location | null,
    destination?: Location | null,
    waypoints: Location[] = []
  ): MarkerData[] => {
    const markers: MarkerData[] = [];

    // Add origin marker
    if (origin) {
      markers.push({
        id: 'origin',
        coordinates: origin.coordinates,
        type: 'origin',
        title: origin.name,
        description: origin.address,
      });
    }

    // Add destination marker
    if (destination) {
      markers.push({
        id: 'destination',
        coordinates: destination.coordinates,
        type: 'destination',
        title: destination.name,
        description: destination.address,
      });
    }

    // Add waypoint markers
    waypoints.forEach((waypoint, index) => {
      markers.push({
        id: `waypoint-${index}`,
        coordinates: waypoint.coordinates,
        type: 'waypoint',
        title: waypoint.name,
        description: waypoint.address,
      });
    });

    // Add toll points if enabled
    if (showTollPoints) {
      markers.push(...tollPoints);
    }

    // Add fuel stations if enabled
    if (showFuelStations) {
      markers.push(...fuelStations);
    }

    return markers;
  }, [tollPoints, fuelStations, showTollPoints, showFuelStations]);

  return {
    tollPoints,
    fuelStations,
    showTollPoints,
    showFuelStations,
    updateTollPoints,
    updateFuelStations,
    toggleTollPoints,
    toggleFuelStations,
    getAllMarkers,
  };
}