import { LngLatBounds, LngLatLike } from 'mapbox-gl';

// Map configuration types
export interface MapConfig {
  accessToken: string;
  style: string;
  center: [number, number];
  zoom: number;
  bounds?: LngLatBounds;
  maxBounds?: LngLatBounds;
}

// Location types
export interface Location {
  id?: string;
  name: string;
  address: string;
  coordinates: [number, number]; // [longitude, latitude]
  type?: 'origin' | 'destination' | 'waypoint' | 'toll' | 'fuel_station';
  metadata?: Record<string, any>;
}

// Route geometry types
export interface RouteGeometry {
  type: 'LineString';
  coordinates: [number, number][];
}

export interface RouteFeature {
  type: 'Feature';
  properties: {
    route_id: string;
    route_type: 'fastest' | 'shortest' | 'recommended';
    distance: number; // meters
    duration: number; // seconds
    fuel_cost: number;
    toll_cost: number;
    total_cost: number;
    color: string;
    weight: number;
    opacity: number;
  };
  geometry: RouteGeometry;
}

// Marker types
export interface MarkerData {
  id: string;
  coordinates: [number, number];
  type: 'origin' | 'destination' | 'waypoint' | 'toll' | 'fuel_station';
  title: string;
  description?: string;
  icon?: string;
  color?: string;
  size?: 'small' | 'medium' | 'large';
  data?: Record<string, any>;
}

// Toll point types
export interface TollPoint extends MarkerData {
  type: 'toll';
  data: {
    toll_id: string;
    name: string;
    cost: number;
    highway: string;
    direction?: string;
    payment_methods: string[];
  };
}

// Fuel station types
export interface FuelStation extends MarkerData {
  type: 'fuel_station';
  data: {
    station_id: string;
    name: string;
    brand: string;
    fuel_types: string[];
    prices: Record<string, number>;
    services: string[];
    is_open: boolean;
    hours?: string;
  };
}

// Map bounds for Argentina/Misiones
export const ARGENTINA_BOUNDS: LngLatBounds = new LngLatBounds(
  [-73.5, -55.0], // Southwest
  [-53.6, -21.8]  // Northeast
);

export const MISIONES_BOUNDS: LngLatBounds = new LngLatBounds(
  [-56.5, -28.2], // Southwest
  [-53.6, -25.2]  // Northeast
);

// Default map configuration
export const DEFAULT_MAP_CONFIG: MapConfig = {
  accessToken: process.env.VITE_MAPBOX_ACCESS_TOKEN || '',
  style: 'mapbox://styles/mapbox/streets-v12',
  center: [-55.9, -27.4], // Posadas, Misiones
  zoom: 8,
  bounds: MISIONES_BOUNDS,
  maxBounds: ARGENTINA_BOUNDS,
};

// Map style options
export const MAP_STYLES = {
  STREETS: 'mapbox://styles/mapbox/streets-v12',
  SATELLITE: 'mapbox://styles/mapbox/satellite-v9',
  SATELLITE_STREETS: 'mapbox://styles/mapbox/satellite-streets-v12',
  LIGHT: 'mapbox://styles/mapbox/light-v11',
  DARK: 'mapbox://styles/mapbox/dark-v11',
  OUTDOORS: 'mapbox://styles/mapbox/outdoors-v12',
  NAVIGATION_DAY: 'mapbox://styles/mapbox/navigation-day-v1',
  NAVIGATION_NIGHT: 'mapbox://styles/mapbox/navigation-night-v1',
} as const;

export type MapStyle = typeof MAP_STYLES[keyof typeof MAP_STYLES];

// Route colors
export const ROUTE_COLORS = {
  FASTEST: '#ef4444', // red-500
  SHORTEST: '#3b82f6', // blue-500
  RECOMMENDED: '#10b981', // emerald-500
  ALTERNATIVE: '#f59e0b', // amber-500
  SELECTED: '#8b5cf6', // violet-500
} as const;

// Marker icons
export const MARKER_ICONS = {
  ORIGIN: 'marker-start',
  DESTINATION: 'marker-end',
  WAYPOINT: 'marker',
  TOLL: 'toll',
  FUEL_STATION: 'fuel',
} as const;

// Map interaction types
export interface MapClickEvent {
  lngLat: [number, number];
  point: [number, number];
  features?: any[];
}

export interface MapMoveEvent {
  center: [number, number];
  zoom: number;
  bounds: LngLatBounds;
}

// Geocoding types
export interface GeocodingResult {
  id: string;
  place_name: string;
  center: [number, number];
  place_type: string[];
  relevance: number;
  properties: Record<string, any>;
  context?: Array<{
    id: string;
    text: string;
    short_code?: string;
  }>;
}

export interface GeocodingResponse {
  type: 'FeatureCollection';
  query: string[];
  features: GeocodingResult[];
  attribution: string;
}

// Route calculation types for map
export interface RouteRequest {
  origin: Location;
  destination: Location;
  waypoints?: Location[];
  vehicle_id?: string;
  preferences?: {
    avoid_tolls?: boolean;
    avoid_highways?: boolean;
    optimize_for?: 'time' | 'distance' | 'cost';
  };
}

export interface RouteResponse {
  routes: RouteFeature[];
  waypoints: Location[];
  toll_points: TollPoint[];
  fuel_stations?: FuelStation[];
  summary: {
    total_distance: number;
    total_duration: number;
    total_fuel_cost: number;
    total_toll_cost: number;
    total_cost: number;
    recommended_route_id: string;
  };
}

// Map layer types
export interface MapLayer {
  id: string;
  type: 'line' | 'circle' | 'symbol' | 'fill';
  source: string;
  layout?: Record<string, any>;
  paint?: Record<string, any>;
  filter?: any[];
  minzoom?: number;
  maxzoom?: number;
}

// Map source types
export interface MapSource {
  id: string;
  type: 'geojson' | 'vector' | 'raster' | 'image';
  data?: any;
  url?: string;
  tiles?: string[];
}

// Map control types
export type MapControl = 
  | 'navigation'
  | 'fullscreen'
  | 'scale'
  | 'geolocate'
  | 'style-switcher'
  | 'route-info';

// Map theme types
export interface MapTheme {
  style: MapStyle;
  routeColors: typeof ROUTE_COLORS;
  markerColors: Record<string, string>;
  uiColors: {
    background: string;
    text: string;
    border: string;
    accent: string;
  };
}

// Utility functions
export function createLocation(
  name: string,
  address: string,
  coordinates: [number, number],
  type?: Location['type']
): Location {
  return {
    name,
    address,
    coordinates,
    type,
  };
}

export function isValidCoordinates(coordinates: [number, number]): boolean {
  const [lng, lat] = coordinates;
  return (
    typeof lng === 'number' &&
    typeof lat === 'number' &&
    lng >= -180 &&
    lng <= 180 &&
    lat >= -90 &&
    lat <= 90
  );
}

export function calculateDistance(
  point1: [number, number],
  point2: [number, number]
): number {
  const [lng1, lat1] = point1;
  const [lng2, lat2] = point2;
  
  const R = 6371e3; // Earth's radius in meters
  const φ1 = (lat1 * Math.PI) / 180;
  const φ2 = (lat2 * Math.PI) / 180;
  const Δφ = ((lat2 - lat1) * Math.PI) / 180;
  const Δλ = ((lng2 - lng1) * Math.PI) / 180;

  const a =
    Math.sin(Δφ / 2) * Math.sin(Δφ / 2) +
    Math.cos(φ1) * Math.cos(φ2) * Math.sin(Δλ / 2) * Math.sin(Δλ / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

  return R * c;
}

export function formatDistance(meters: number): string {
  if (meters < 1000) {
    return `${Math.round(meters)}m`;
  }
  return `${(meters / 1000).toFixed(1)}km`;
}

export function formatDuration(seconds: number): string {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  
  if (hours > 0) {
    return `${hours}h ${minutes}m`;
  }
  return `${minutes}m`;
}

export function getBoundsFromLocations(locations: Location[]): LngLatBounds {
  if (locations.length === 0) {
    return MISIONES_BOUNDS;
  }
  
  const bounds = new LngLatBounds();
  locations.forEach(location => {
    bounds.extend(location.coordinates);
  });
  
  return bounds;
}

export function getRouteColor(routeType: string, isSelected: boolean = false): string {
  if (isSelected) {
    return ROUTE_COLORS.SELECTED;
  }
  
  switch (routeType) {
    case 'fastest':
      return ROUTE_COLORS.FASTEST;
    case 'shortest':
      return ROUTE_COLORS.SHORTEST;
    case 'recommended':
      return ROUTE_COLORS.RECOMMENDED;
    default:
      return ROUTE_COLORS.ALTERNATIVE;
  }
}