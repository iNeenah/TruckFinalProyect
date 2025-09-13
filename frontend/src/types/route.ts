// Route related types

import { Coordinates, OptimizationCriteria } from './common';

export interface RouteRequest {
  origin: string | Coordinates;
  destination: string | Coordinates;
  vehicle_id: string;
  alternatives?: number;
  avoid_tolls?: boolean;
  optimize_for?: OptimizationCriteria;
}

export interface RouteResponse {
  request_id: string;
  recommended_route: Route;
  alternative_routes: Route[];
  savings_analysis: SavingsAnalysis;
  calculation_time_ms: number;
  timestamp: string;
}

export interface Route {
  id: string;
  geometry: GeoJSONLineString;
  distance: number; // km
  duration: number; // minutes
  cost_breakdown: CostBreakdown;
  toll_points: TollPoint[];
  route_type: RouteType;
}

export interface CostBreakdown {
  fuel_cost: number;
  toll_cost: number;
  total_cost: number;
  fuel_liters: number;
  toll_count: number;
}

export interface TollPoint {
  toll_id: string;
  name: string;
  coordinates: Coordinates;
  tariff: number;
  route_code: string;
}

export interface SavingsAnalysis {
  recommended_route_id: string;
  fastest_route_cost: number | null;
  cheapest_route_cost: number;
  savings_amount: number | null;
  savings_percentage: number | null;
  comparison_summary: string;
}

export type RouteType = 'recommended' | 'fastest' | 'cheapest' | 'alternative' | 'scenic';

export interface GeoJSONLineString {
  type: 'LineString';
  coordinates: [number, number][]; // [longitude, latitude]
}

export interface RouteHistory {
  id: string;
  user_id: string;
  vehicle_id: string;
  company_id: string;
  origin_address: string;
  destination_address: string;
  origin_coordinates: Coordinates;
  destination_coordinates: Coordinates;
  selected_route: Route;
  total_distance: number;
  total_duration: number;
  fuel_cost: number;
  toll_cost: number;
  total_cost: number;
  savings_amount: number;
  created_at: string;
}

export interface RouteHistoryResponse {
  routes: RouteHistory[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface RouteStatistics {
  total_routes: number;
  total_distance: number;
  total_cost: number;
  total_savings: number;
  average_distance: number;
  average_cost: number;
  most_used_vehicle: string | null;
  most_common_origin: string | null;
  most_common_destination: string | null;
  date_range: {
    start: string;
    end: string;
  };
}

export interface GeocodingResponse {
  results: GeocodingResult[];
  status: 'success' | 'no_results' | 'error';
}

export interface GeocodingResult {
  address: string;
  coordinates: Coordinates;
  formatted_address: string;
  confidence: number;
  place_type: string;
}

export interface RouteReportRequest {
  route_id: string;
  report_type: 'complete' | 'simple';
  include_map: boolean;
  format: 'pdf' | 'html';
}

export interface RouteReportResponse {
  report_id: string;
  download_url: string;
  expires_at: string;
  file_size: number;
  format: 'pdf' | 'html';
}

// Map related types
export interface MapViewState {
  longitude: number;
  latitude: number;
  zoom: number;
  bearing?: number;
  pitch?: number;
}

export interface MapBounds {
  north: number;
  south: number;
  east: number;
  west: number;
}

export interface RouteVisualizationOptions {
  showTolls: boolean;
  showAlternatives: boolean;
  highlightRecommended: boolean;
  showCostLabels: boolean;
}

// Route planning types
export interface RoutePlanningState {
  origin: {
    address: string;
    coordinates: Coordinates | null;
  };
  destination: {
    address: string;
    coordinates: Coordinates | null;
  };
  selectedVehicle: string | null;
  optimizationCriteria: OptimizationCriteria;
  avoidTolls: boolean;
  maxAlternatives: number;
}

export interface RouteCalculationProgress {
  step: 'geocoding' | 'routing' | 'cost_analysis' | 'complete';
  progress: number; // 0-100
  message: string;
}