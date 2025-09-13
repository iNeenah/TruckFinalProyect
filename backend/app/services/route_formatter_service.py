"""
Route response formatting service for API responses.
"""
import logging
import json
from typing import List, Dict, Any, Optional, Tuple
from decimal import Decimal
from datetime import datetime
import uuid

from app.services.route_optimization_service import OptimizedRoute, RouteOptimizationResponse
from app.services.route_comparison_service import OptimizationSummary
from app.services.osrm_service import Coordinate
from app.schemas.route import (
    Route,
    CostBreakdown,
    TollPoint,
    SavingsAnalysis,
    RouteResponse,
    Coordinates
)

logger = logging.getLogger(__name__)


class RouteFormatterService:
    """Service for formatting route responses with GeoJSON and analysis."""
    
    def __init__(self):
        """Initialize route formatter service."""
        self.logger = logging.getLogger(__name__)
    
    def format_route_response(
        self,
        request_id: str,
        optimization_response: RouteOptimizationResponse,
        analysis_summary: OptimizationSummary,
        start_time: datetime
    ) -> RouteResponse:
        """
        Format complete route response for API.
        
        Args:
            request_id: Unique request identifier
            optimization_response: Route optimization results
            analysis_summary: Route comparison analysis
            start_time: Request start time
            
        Returns:
            Formatted route response
        """
        try:
            # Format individual routes
            formatted_routes = []
            for i, route in enumerate(optimization_response.routes):
                formatted_route = self._format_single_route(route, f"route_{i}")
                formatted_routes.append(formatted_route)
            
            # Identify recommended route
            recommended_route = self._find_recommended_route(
                formatted_routes, analysis_summary.recommended_route
            )
            
            # Get alternative routes (excluding recommended)
            alternative_routes = [
                route for route in formatted_routes 
                if route.id != recommended_route.id
            ]
            
            # Format savings analysis
            savings_analysis = self._format_savings_analysis(
                analysis_summary, formatted_routes
            )
            
            # Calculate response time
            calculation_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            
            return RouteResponse(
                request_id=request_id,
                recommended_route=recommended_route,
                alternative_routes=alternative_routes,
                savings_analysis=savings_analysis,
                calculation_time_ms=calculation_time_ms,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Error formatting route response: {e}")
            raise
    
    def _format_single_route(self, optimized_route: OptimizedRoute, route_id: str) -> Route:
        """
        Format a single optimized route for API response.
        
        Args:
            optimized_route: Optimized route data
            route_id: Route identifier
            
        Returns:
            Formatted route
        """
        # Convert geometry to GeoJSON
        geometry = self._convert_to_geojson(optimized_route.geometry)
        
        # Format cost breakdown
        cost_breakdown = CostBreakdown(
            fuel_cost=optimized_route.cost_breakdown.fuel_cost.total_fuel_cost,
            toll_cost=optimized_route.cost_breakdown.total_toll_cost,
            total_cost=optimized_route.cost_breakdown.total_cost,
            fuel_liters=optimized_route.cost_breakdown.fuel_cost.fuel_needed_liters,
            toll_count=len(optimized_route.cost_breakdown.tolls)
        )
        
        # Format toll points
        toll_points = self._format_toll_points(optimized_route.cost_breakdown.tolls)
        
        return Route(
            id=route_id,
            geometry=geometry,
            distance=optimized_route.osrm_route.distance / 1000,  # Convert to km
            duration=int(optimized_route.osrm_route.duration / 60),  # Convert to minutes
            cost_breakdown=cost_breakdown,
            toll_points=toll_points,
            route_type=optimized_route.route_type
        )
    
    def _convert_to_geojson(self, geometry: str) -> Dict[str, Any]:
        """
        Convert route geometry to GeoJSON format.
        
        Args:
            geometry: Route geometry (could be encoded polyline or GeoJSON)
            
        Returns:
            GeoJSON LineString geometry
        """
        try:
            # Try to parse as JSON first (already GeoJSON)
            if geometry.startswith('{'):
                return json.loads(geometry)
            
            # If it's an encoded polyline, decode it
            coordinates = self._decode_polyline(geometry)
            
            return {
                "type": "LineString",
                "coordinates": coordinates
            }
            
        except Exception as e:
            self.logger.warning(f"Error converting geometry to GeoJSON: {e}")
            # Return empty LineString as fallback
            return {
                "type": "LineString",
                "coordinates": []
            }
    
    def _decode_polyline(self, encoded: str) -> List[List[float]]:
        """
        Decode Google polyline to coordinates.
        
        Args:
            encoded: Encoded polyline string
            
        Returns:
            List of [longitude, latitude] coordinates
        """
        try:
            # This is a simplified polyline decoder
            # In production, use a proper library like polyline
            coordinates = []
            index = 0
            lat = 0
            lng = 0
            
            while index < len(encoded):
                # Decode latitude
                shift = 0
                result = 0
                while True:
                    byte = ord(encoded[index]) - 63
                    index += 1
                    result |= (byte & 0x1f) << shift
                    shift += 5
                    if byte < 0x20:
                        break
                
                dlat = ~(result >> 1) if result & 1 else result >> 1
                lat += dlat
                
                # Decode longitude
                shift = 0
                result = 0
                while True:
                    byte = ord(encoded[index]) - 63
                    index += 1
                    result |= (byte & 0x1f) << shift
                    shift += 5
                    if byte < 0x20:
                        break
                
                dlng = ~(result >> 1) if result & 1 else result >> 1
                lng += dlng
                
                coordinates.append([lng / 1e5, lat / 1e5])
            
            return coordinates
            
        except Exception as e:
            self.logger.warning(f"Error decoding polyline: {e}")
            return []
    
    def _format_toll_points(self, tolls: List) -> List[TollPoint]:
        """
        Format toll information for API response.
        
        Args:
            tolls: List of toll information
            
        Returns:
            List of formatted toll points
        """
        toll_points = []
        
        for toll in tolls:
            toll_point = TollPoint(
                toll_id=uuid.uuid4(),  # Generate UUID for API
                name=toll.name,
                coordinates=Coordinates(
                    longitude=toll.coordinate.longitude,
                    latitude=toll.coordinate.latitude
                ),
                tariff=toll.cost,
                route_code=toll.road_name
            )
            toll_points.append(toll_point)
        
        return toll_points
    
    def _find_recommended_route(
        self,
        formatted_routes: List[Route],
        recommended_optimized_route: OptimizedRoute
    ) -> Route:
        """
        Find the recommended route from formatted routes.
        
        Args:
            formatted_routes: List of formatted routes
            recommended_optimized_route: Original recommended route
            
        Returns:
            Recommended formatted route
        """
        # Find by route type or default to first route
        for route in formatted_routes:
            if route.route_type == "recommended" or route.route_type == recommended_optimized_route.route_type:
                return route
        
        # Fallback to first route
        return formatted_routes[0] if formatted_routes else None
    
    def _format_savings_analysis(
        self,
        analysis_summary: OptimizationSummary,
        formatted_routes: List[Route]
    ) -> SavingsAnalysis:
        """
        Format savings analysis for API response.
        
        Args:
            analysis_summary: Route analysis summary
            formatted_routes: List of formatted routes
            
        Returns:
            Formatted savings analysis
        """
        if not formatted_routes:
            return SavingsAnalysis(
                recommended_route_id="",
                fastest_route_cost=None,
                cheapest_route_cost=Decimal("0"),
                savings_amount=None,
                savings_percentage=None,
                comparison_summary="No routes available"
            )
        
        # Find fastest and cheapest routes
        fastest_route = min(formatted_routes, key=lambda r: r.duration)
        cheapest_route = min(formatted_routes, key=lambda r: r.cost_breakdown.total_cost)
        
        # Calculate savings
        savings_amount = None
        savings_percentage = None
        
        if fastest_route.id != cheapest_route.id:
            savings_amount = fastest_route.cost_breakdown.total_cost - cheapest_route.cost_breakdown.total_cost
            if fastest_route.cost_breakdown.total_cost > 0:
                savings_percentage = float(savings_amount / fastest_route.cost_breakdown.total_cost * 100)
        
        # Generate comparison summary
        comparison_summary = self._generate_comparison_summary(
            analysis_summary, fastest_route, cheapest_route, savings_amount
        )
        
        return SavingsAnalysis(
            recommended_route_id=analysis_summary.recommended_route.route_type if analysis_summary.recommended_route else "",
            fastest_route_cost=fastest_route.cost_breakdown.total_cost,
            cheapest_route_cost=cheapest_route.cost_breakdown.total_cost,
            savings_amount=savings_amount,
            savings_percentage=savings_percentage,
            comparison_summary=comparison_summary
        )
    
    def _generate_comparison_summary(
        self,
        analysis_summary: OptimizationSummary,
        fastest_route: Route,
        cheapest_route: Route,
        savings_amount: Optional[Decimal]
    ) -> str:
        """
        Generate human-readable comparison summary.
        
        Args:
            analysis_summary: Route analysis summary
            fastest_route: Fastest route
            cheapest_route: Cheapest route
            savings_amount: Calculated savings
            
        Returns:
            Comparison summary text
        """
        if not savings_amount or savings_amount <= 0:
            return "The fastest route is also the most economical option."
        
        time_difference = fastest_route.duration - cheapest_route.duration
        
        if time_difference > 30:  # More than 30 minutes difference
            return (f"The recommended route saves ARS ${savings_amount:.2f} "
                   f"but takes {time_difference} minutes longer than the fastest route.")
        elif time_difference > 10:  # 10-30 minutes difference
            return (f"The recommended route saves ARS ${savings_amount:.2f} "
                   f"with only {time_difference} minutes additional travel time.")
        else:  # Less than 10 minutes difference
            return (f"The recommended route saves ARS ${savings_amount:.2f} "
                   f"with minimal additional travel time.")
    
    def create_route_geojson_feature_collection(
        self,
        routes: List[Route],
        include_toll_markers: bool = True
    ) -> Dict[str, Any]:
        """
        Create a GeoJSON FeatureCollection with routes and toll markers.
        
        Args:
            routes: List of routes to include
            include_toll_markers: Whether to include toll point markers
            
        Returns:
            GeoJSON FeatureCollection
        """
        features = []
        
        # Add route features
        for i, route in enumerate(routes):
            route_feature = {
                "type": "Feature",
                "properties": {
                    "route_id": route.id,
                    "route_type": route.route_type,
                    "distance_km": route.distance,
                    "duration_minutes": route.duration,
                    "total_cost": float(route.cost_breakdown.total_cost),
                    "fuel_cost": float(route.cost_breakdown.fuel_cost),
                    "toll_cost": float(route.cost_breakdown.toll_cost),
                    "toll_count": route.cost_breakdown.toll_count,
                    "color": self._get_route_color(route.route_type, i),
                    "stroke_width": 5 if route.route_type == "recommended" else 3
                },
                "geometry": route.geometry
            }
            features.append(route_feature)
            
            # Add toll markers if requested
            if include_toll_markers:
                for toll in route.toll_points:
                    toll_feature = {
                        "type": "Feature",
                        "properties": {
                            "type": "toll",
                            "route_id": route.id,
                            "toll_name": toll.name,
                            "toll_cost": float(toll.tariff),
                            "route_code": toll.route_code,
                            "marker_color": "#ff6b6b",
                            "marker_symbol": "toll"
                        },
                        "geometry": {
                            "type": "Point",
                            "coordinates": [toll.coordinates.longitude, toll.coordinates.latitude]
                        }
                    }
                    features.append(toll_feature)
        
        return {
            "type": "FeatureCollection",
            "features": features
        }
    
    def _get_route_color(self, route_type: str, index: int) -> str:
        """
        Get color for route visualization.
        
        Args:
            route_type: Type of route
            index: Route index
            
        Returns:
            Hex color code
        """
        color_map = {
            "recommended": "#2ecc71",  # Green
            "fastest": "#3498db",      # Blue
            "cheapest": "#f39c12",     # Orange
            "alternative": "#9b59b6",  # Purple
            "scenic": "#1abc9c"        # Teal
        }
        
        # Default colors for numbered alternatives
        default_colors = ["#e74c3c", "#34495e", "#95a5a6", "#16a085", "#8e44ad"]
        
        return color_map.get(route_type, default_colors[index % len(default_colors)])
    
    def create_route_summary_table(self, routes: List[Route]) -> Dict[str, Any]:
        """
        Create a summary table of route comparisons.
        
        Args:
            routes: List of routes to compare
            
        Returns:
            Route comparison table data
        """
        if not routes:
            return {"headers": [], "rows": []}
        
        headers = [
            "Route Type",
            "Distance (km)",
            "Duration",
            "Fuel Cost (ARS)",
            "Toll Cost (ARS)",
            "Total Cost (ARS)",
            "Tolls"
        ]
        
        rows = []
        for route in routes:
            # Format duration
            hours = route.duration // 60
            minutes = route.duration % 60
            duration_str = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
            
            row = [
                route.route_type.title(),
                f"{route.distance:.1f}",
                duration_str,
                f"${route.cost_breakdown.fuel_cost:.2f}",
                f"${route.cost_breakdown.toll_cost:.2f}",
                f"${route.cost_breakdown.total_cost:.2f}",
                str(route.cost_breakdown.toll_count)
            ]
            rows.append(row)
        
        return {
            "headers": headers,
            "rows": rows
        }
    
    def create_cost_breakdown_chart_data(self, routes: List[Route]) -> Dict[str, Any]:
        """
        Create chart data for cost breakdown visualization.
        
        Args:
            routes: List of routes
            
        Returns:
            Chart data for cost breakdown
        """
        chart_data = {
            "labels": [],
            "datasets": [
                {
                    "label": "Fuel Cost",
                    "data": [],
                    "backgroundColor": "#3498db",
                    "borderColor": "#2980b9",
                    "borderWidth": 1
                },
                {
                    "label": "Toll Cost",
                    "data": [],
                    "backgroundColor": "#e74c3c",
                    "borderColor": "#c0392b",
                    "borderWidth": 1
                }
            ]
        }
        
        for route in routes:
            chart_data["labels"].append(route.route_type.title())
            chart_data["datasets"][0]["data"].append(float(route.cost_breakdown.fuel_cost))
            chart_data["datasets"][1]["data"].append(float(route.cost_breakdown.toll_cost))
        
        return chart_data
    
    def create_savings_visualization_data(
        self,
        savings_analysis: SavingsAnalysis,
        routes: List[Route]
    ) -> Dict[str, Any]:
        """
        Create visualization data for savings analysis.
        
        Args:
            savings_analysis: Savings analysis data
            routes: List of routes
            
        Returns:
            Savings visualization data
        """
        if not savings_analysis.savings_amount or savings_analysis.savings_amount <= 0:
            return {"type": "no_savings", "message": "No significant savings available"}
        
        # Find recommended and fastest routes
        recommended_route = None
        fastest_route = None
        
        for route in routes:
            if route.route_type == "recommended":
                recommended_route = route
            if route.route_type == "fastest" or (fastest_route is None):
                fastest_route = route
        
        if not recommended_route or not fastest_route:
            return {"type": "insufficient_data", "message": "Insufficient route data"}
        
        return {
            "type": "savings_comparison",
            "savings_amount": float(savings_analysis.savings_amount),
            "savings_percentage": savings_analysis.savings_percentage,
            "fastest_route": {
                "cost": float(fastest_route.cost_breakdown.total_cost),
                "duration": fastest_route.duration,
                "distance": fastest_route.distance
            },
            "recommended_route": {
                "cost": float(recommended_route.cost_breakdown.total_cost),
                "duration": recommended_route.duration,
                "distance": recommended_route.distance
            },
            "time_trade_off": recommended_route.duration - fastest_route.duration,
            "distance_trade_off": recommended_route.distance - fastest_route.distance
        }