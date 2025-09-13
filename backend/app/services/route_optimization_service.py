"""
Route optimization service that combines OSRM routing with fuel cost calculation and toll detection.
"""
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime
import asyncio

from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from geoalchemy2.functions import ST_DWithin, ST_Intersects, ST_GeomFromText

from app.services.osrm_service import OSRMService, Coordinate, Route as OSRMRoute
from app.services.geocoding_service import GeocodingService, GeocodingResult
from app.models.vehicle import Vehicle
from app.models.fuel_price import FuelPrice
from app.models.toll import Toll
from app.models.calculated_route import CalculatedRoute
from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


@dataclass
class RoutePoint:
    """A point in a route with coordinates and optional address."""
    coordinate: Coordinate
    address: Optional[str] = None
    name: Optional[str] = None


@dataclass
class TollInfo:
    """Information about a toll on a route."""
    toll_id: str
    name: str
    coordinate: Coordinate
    cost: Decimal
    vehicle_type: str
    road_name: str


@dataclass
class FuelCostInfo:
    """Fuel cost information for a route."""
    distance_km: float
    fuel_consumption_per_100km: Decimal
    fuel_needed_liters: float
    fuel_price_per_liter: Decimal
    total_fuel_cost: Decimal
    fuel_type: str


@dataclass
class RouteCostBreakdown:
    """Complete cost breakdown for a route."""
    fuel_cost: FuelCostInfo
    tolls: List[TollInfo]
    total_toll_cost: Decimal
    total_cost: Decimal
    savings_vs_fastest: Optional[Decimal] = None


@dataclass
class OptimizedRoute:
    """An optimized route with cost analysis."""
    osrm_route: OSRMRoute
    cost_breakdown: RouteCostBreakdown
    route_type: str  # 'fastest', 'cheapest', 'alternative'
    geometry: str  # GeoJSON or encoded polyline
    waypoints: List[RoutePoint]
    estimated_savings: Optional[Decimal] = None


@dataclass
class RouteOptimizationRequest:
    """Request for route optimization."""
    origin: RoutePoint
    destination: RoutePoint
    vehicle_id: str
    waypoints: Optional[List[RoutePoint]] = None
    avoid_tolls: bool = False
    max_alternatives: int = 3


@dataclass
class RouteOptimizationResponse:
    """Response from route optimization."""
    routes: List[OptimizedRoute]
    recommended_route: OptimizedRoute
    total_savings: Decimal
    calculation_time_ms: int
    warnings: List[str]


class RouteOptimizationService:
    """Service for optimizing routes with cost analysis."""
    
    def __init__(self, db: Session):
        """
        Initialize route optimization service.
        
        Args:
            db: Database session
        """
        self.db = db
        self.logger = logging.getLogger(__name__)
    
    async def optimize_route(
        self, 
        request: RouteOptimizationRequest
    ) -> RouteOptimizationResponse:
        """
        Optimize a route considering fuel costs and tolls.
        
        Args:
            request: Route optimization request
            
        Returns:
            Route optimization response with alternatives
        """
        start_time = datetime.now()
        warnings = []
        
        try:
            # Get vehicle information
            vehicle = self.db.query(Vehicle).filter(
                Vehicle.id == request.vehicle_id
            ).first()
            
            if not vehicle:
                raise ValueError(f"Vehicle {request.vehicle_id} not found")
            
            # Get current fuel prices
            fuel_price = await self._get_current_fuel_price(vehicle.fuel_type)
            if not fuel_price:
                warnings.append(f"No current fuel price found for {vehicle.fuel_type}, using default")
                fuel_price = self._get_default_fuel_price(vehicle.fuel_type)
            
            # Calculate routes using OSRM
            async with OSRMService() as osrm:
                if not await osrm.health_check():
                    raise RuntimeError("OSRM service is not available")
                
                # Build coordinate list
                coordinates = [request.origin.coordinate]
                if request.waypoints:
                    coordinates.extend([wp.coordinate for wp in request.waypoints])
                coordinates.append(request.destination.coordinate)
                
                # Get route alternatives
                osrm_routes = await osrm.get_route_alternatives(
                    request.origin.coordinate,
                    request.destination.coordinate,
                    max_alternatives=request.max_alternatives
                )
                
                if not osrm_routes:
                    raise ValueError("No routes found between origin and destination")
            
            # Analyze each route
            optimized_routes = []
            for i, osrm_route in enumerate(osrm_routes):
                route_type = "fastest" if i == 0 else f"alternative_{i}"
                
                # Calculate costs
                cost_breakdown = await self._calculate_route_costs(
                    osrm_route, vehicle, fuel_price, request.avoid_tolls
                )
                
                # Create optimized route
                optimized_route = OptimizedRoute(
                    osrm_route=osrm_route,
                    cost_breakdown=cost_breakdown,
                    route_type=route_type,
                    geometry=osrm_route.geometry,
                    waypoints=[request.origin, request.destination]
                )
                
                optimized_routes.append(optimized_route)
            
            # Find recommended route (cheapest total cost)
            recommended_route = min(optimized_routes, key=lambda r: r.cost_breakdown.total_cost)
            recommended_route.route_type = "cheapest"
            
            # Calculate savings
            fastest_route = optimized_routes[0]  # First route is fastest
            total_savings = Decimal('0')
            
            if recommended_route != fastest_route:
                total_savings = fastest_route.cost_breakdown.total_cost - recommended_route.cost_breakdown.total_cost
                recommended_route.estimated_savings = total_savings
                
                # Add savings info to other routes
                for route in optimized_routes:
                    if route != recommended_route:
                        route.cost_breakdown.savings_vs_fastest = (
                            fastest_route.cost_breakdown.total_cost - route.cost_breakdown.total_cost
                        )
            
            # Calculate response time
            end_time = datetime.now()
            calculation_time_ms = int((end_time - start_time).total_seconds() * 1000)
            
            return RouteOptimizationResponse(
                routes=optimized_routes,
                recommended_route=recommended_route,
                total_savings=total_savings,
                calculation_time_ms=calculation_time_ms,
                warnings=warnings
            )
            
        except Exception as e:
            self.logger.error(f"Route optimization failed: {e}")
            raise
    
    async def _calculate_route_costs(
        self,
        osrm_route: OSRMRoute,
        vehicle: Vehicle,
        fuel_price: Decimal,
        avoid_tolls: bool = False
    ) -> RouteCostBreakdown:
        """
        Calculate complete cost breakdown for a route.
        
        Args:
            osrm_route: OSRM route data
            vehicle: Vehicle information
            fuel_price: Current fuel price per liter
            avoid_tolls: Whether to avoid tolls
            
        Returns:
            Complete cost breakdown
        """
        distance_km = osrm_route.distance / 1000
        
        # Calculate fuel costs
        fuel_cost_info = self._calculate_fuel_cost(
            distance_km, vehicle, fuel_price
        )
        
        # Detect tolls on route
        tolls = []
        total_toll_cost = Decimal('0')
        
        if not avoid_tolls:
            tolls = await self._detect_route_tolls(osrm_route, vehicle)
            total_toll_cost = sum(toll.cost for toll in tolls)
        
        # Calculate total cost
        total_cost = fuel_cost_info.total_fuel_cost + total_toll_cost
        
        return RouteCostBreakdown(
            fuel_cost=fuel_cost_info,
            tolls=tolls,
            total_toll_cost=total_toll_cost,
            total_cost=total_cost
        )
    
    def _calculate_fuel_cost(
        self,
        distance_km: float,
        vehicle: Vehicle,
        fuel_price: Decimal
    ) -> FuelCostInfo:
        """
        Calculate fuel cost for a route.
        
        Args:
            distance_km: Route distance in kilometers
            vehicle: Vehicle information
            fuel_price: Fuel price per liter
            
        Returns:
            Fuel cost information
        """
        fuel_needed_liters = (distance_km / 100) * float(vehicle.fuel_consumption)
        total_fuel_cost = Decimal(str(fuel_needed_liters)) * fuel_price
        
        return FuelCostInfo(
            distance_km=distance_km,
            fuel_consumption_per_100km=vehicle.fuel_consumption,
            fuel_needed_liters=fuel_needed_liters,
            fuel_price_per_liter=fuel_price,
            total_fuel_cost=total_fuel_cost,
            fuel_type=vehicle.fuel_type.value
        )
    
    async def _detect_route_tolls(
        self,
        osrm_route: OSRMRoute,
        vehicle: Vehicle
    ) -> List[TollInfo]:
        """
        Detect tolls along a route using spatial queries.
        
        Args:
            osrm_route: OSRM route data
            vehicle: Vehicle information
            
        Returns:
            List of tolls on the route
        """
        try:
            # Convert route geometry to PostGIS geometry
            # Note: This assumes the geometry is in a format PostGIS can understand
            route_geometry = osrm_route.geometry
            
            # Query tolls that intersect with the route
            # Using a buffer around the route to account for GPS accuracy
            buffer_meters = 100  # 100 meter buffer
            
            tolls_query = self.db.query(Toll).filter(
                and_(
                    Toll.is_active == True,
                    ST_DWithin(
                        Toll.location,
                        ST_GeomFromText(route_geometry, 4326),
                        buffer_meters
                    )
                )
            )
            
            toll_records = tolls_query.all()
            
            # Convert to TollInfo objects
            tolls = []
            for toll_record in toll_records:
                # Get appropriate cost for vehicle type
                cost = self._get_toll_cost_for_vehicle(toll_record, vehicle)
                
                if cost > 0:
                    toll_info = TollInfo(
                        toll_id=str(toll_record.id),
                        name=toll_record.name,
                        coordinate=Coordinate(
                            longitude=toll_record.longitude,
                            latitude=toll_record.latitude
                        ),
                        cost=cost,
                        vehicle_type=self._get_vehicle_category(vehicle),
                        road_name=toll_record.road_name or "Unknown"
                    )
                    tolls.append(toll_info)
            
            return tolls
            
        except Exception as e:
            self.logger.warning(f"Error detecting tolls: {e}")
            return []
    
    def _get_toll_cost_for_vehicle(self, toll: Toll, vehicle: Vehicle) -> Decimal:
        """
        Get toll cost for a specific vehicle.
        
        Args:
            toll: Toll record
            vehicle: Vehicle information
            
        Returns:
            Toll cost for the vehicle
        """
        # Determine vehicle category
        vehicle_category = self._get_vehicle_category(vehicle)
        
        # Get cost based on vehicle category
        if vehicle_category == "car":
            return toll.cost_car or Decimal('0')
        elif vehicle_category == "truck":
            return toll.cost_truck or Decimal('0')
        elif vehicle_category == "motorcycle":
            return toll.cost_motorcycle or Decimal('0')
        else:
            return toll.cost_car or Decimal('0')  # Default to car cost
    
    def _get_vehicle_category(self, vehicle: Vehicle) -> str:
        """
        Determine vehicle category for toll calculation.
        
        Args:
            vehicle: Vehicle information
            
        Returns:
            Vehicle category string
        """
        # Simple categorization based on vehicle properties
        if vehicle.max_weight and vehicle.max_weight > 3500:
            return "truck"
        elif "moto" in vehicle.model.lower() or "scooter" in vehicle.model.lower():
            return "motorcycle"
        else:
            return "car"
    
    async def _get_current_fuel_price(self, fuel_type: str) -> Optional[Decimal]:
        """
        Get current fuel price for a fuel type.
        
        Args:
            fuel_type: Type of fuel
            
        Returns:
            Current fuel price or None
        """
        try:
            # Get most recent fuel price
            fuel_price = self.db.query(FuelPrice).filter(
                and_(
                    FuelPrice.fuel_type == fuel_type,
                    FuelPrice.is_active == True
                )
            ).order_by(FuelPrice.updated_at.desc()).first()
            
            if fuel_price:
                # Check if price is not too old (within 30 days)
                days_old = (datetime.now() - fuel_price.updated_at).days
                if days_old <= 30:
                    return fuel_price.price_per_liter
                else:
                    self.logger.warning(f"Fuel price for {fuel_type} is {days_old} days old")
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting fuel price: {e}")
            return None
    
    def _get_default_fuel_price(self, fuel_type: str) -> Decimal:
        """
        Get default fuel price when current price is not available.
        
        Args:
            fuel_type: Type of fuel
            
        Returns:
            Default fuel price
        """
        # Default prices in ARS per liter (approximate values for Argentina 2024)
        default_prices = {
            "diesel_500": Decimal("150.00"),
            "diesel_premium": Decimal("170.00"),
            "gasoline": Decimal("160.00")
        }
        
        return default_prices.get(fuel_type, Decimal("160.00"))
    
    async def save_calculated_route(
        self,
        optimization_response: RouteOptimizationResponse,
        request: RouteOptimizationRequest,
        user_id: str
    ) -> CalculatedRoute:
        """
        Save calculated route to database for history.
        
        Args:
            optimization_response: Route optimization response
            request: Original request
            user_id: User who requested the calculation
            
        Returns:
            Saved calculated route record
        """
        try:
            recommended_route = optimization_response.recommended_route
            
            calculated_route = CalculatedRoute(
                user_id=user_id,
                vehicle_id=request.vehicle_id,
                origin_latitude=request.origin.coordinate.latitude,
                origin_longitude=request.origin.coordinate.longitude,
                origin_address=request.origin.address,
                destination_latitude=request.destination.coordinate.latitude,
                destination_longitude=request.destination.coordinate.longitude,
                destination_address=request.destination.address,
                distance_km=recommended_route.osrm_route.distance / 1000,
                duration_minutes=recommended_route.osrm_route.duration / 60,
                fuel_cost=recommended_route.cost_breakdown.fuel_cost.total_fuel_cost,
                toll_cost=recommended_route.cost_breakdown.total_toll_cost,
                total_cost=recommended_route.cost_breakdown.total_cost,
                estimated_savings=optimization_response.total_savings,
                route_geometry=recommended_route.geometry,
                calculation_time_ms=optimization_response.calculation_time_ms
            )
            
            self.db.add(calculated_route)
            self.db.commit()
            self.db.refresh(calculated_route)
            
            return calculated_route
            
        except Exception as e:
            self.logger.error(f"Error saving calculated route: {e}")
            self.db.rollback()
            raise
    
    async def geocode_and_optimize(
        self,
        origin_address: str,
        destination_address: str,
        vehicle_id: str,
        waypoint_addresses: Optional[List[str]] = None,
        avoid_tolls: bool = False,
        max_alternatives: int = 3
    ) -> RouteOptimizationResponse:
        """
        Geocode addresses and optimize route.
        
        Args:
            origin_address: Origin address string
            destination_address: Destination address string
            vehicle_id: Vehicle ID
            waypoint_addresses: Optional waypoint addresses
            avoid_tolls: Whether to avoid tolls
            max_alternatives: Maximum number of alternatives
            
        Returns:
            Route optimization response
        """
        async with GeocodingService() as geocoder:
            # Geocode origin
            origin_results = await geocoder.geocode_argentina_address(origin_address)
            if not origin_results:
                raise ValueError(f"Could not geocode origin address: {origin_address}")
            
            origin_result = origin_results[0]
            origin_point = RoutePoint(
                coordinate=origin_result.coordinate,
                address=origin_result.address,
                name="Origin"
            )
            
            # Geocode destination
            dest_results = await geocoder.geocode_argentina_address(destination_address)
            if not dest_results:
                raise ValueError(f"Could not geocode destination address: {destination_address}")
            
            dest_result = dest_results[0]
            destination_point = RoutePoint(
                coordinate=dest_result.coordinate,
                address=dest_result.address,
                name="Destination"
            )
            
            # Geocode waypoints if provided
            waypoints = None
            if waypoint_addresses:
                waypoints = []
                for i, waypoint_address in enumerate(waypoint_addresses):
                    waypoint_results = await geocoder.geocode_argentina_address(waypoint_address)
                    if waypoint_results:
                        waypoint_result = waypoint_results[0]
                        waypoint = RoutePoint(
                            coordinate=waypoint_result.coordinate,
                            address=waypoint_result.address,
                            name=f"Waypoint {i+1}"
                        )
                        waypoints.append(waypoint)
            
            # Create optimization request
            request = RouteOptimizationRequest(
                origin=origin_point,
                destination=destination_point,
                vehicle_id=vehicle_id,
                waypoints=waypoints,
                avoid_tolls=avoid_tolls,
                max_alternatives=max_alternatives
            )
            
            # Optimize route
            return await self.optimize_route(request)
    
    async def get_route_statistics(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get route calculation statistics.
        
        Args:
            user_id: Optional user ID to filter statistics
            
        Returns:
            Route statistics
        """
        try:
            query = self.db.query(CalculatedRoute)
            
            if user_id:
                query = query.filter(CalculatedRoute.user_id == user_id)
            
            # Basic statistics
            total_routes = query.count()
            
            if total_routes == 0:
                return {
                    "total_routes": 0,
                    "total_distance_km": 0,
                    "total_savings": 0,
                    "average_savings": 0,
                    "most_common_origin": None,
                    "most_common_destination": None
                }
            
            # Aggregate statistics
            stats = query.with_entities(
                func.sum(CalculatedRoute.distance_km).label('total_distance'),
                func.sum(CalculatedRoute.estimated_savings).label('total_savings'),
                func.avg(CalculatedRoute.estimated_savings).label('avg_savings')
            ).first()
            
            return {
                "total_routes": total_routes,
                "total_distance_km": float(stats.total_distance or 0),
                "total_savings": float(stats.total_savings or 0),
                "average_savings": float(stats.avg_savings or 0),
                "most_common_origin": self._get_most_common_origin(user_id),  # Implement if needed
                "most_common_destination": self._get_most_common_destination(user_id)  # Implement if needed
            }
            
        except Exception as e:
            self.logger.error(f"Error getting route statistics: {e}")
            return {
                "total_routes": 0,
                "total_distance_km": 0,
                "total_savings": 0,
                "average_savings": 0,
                "error": str(e)
            }

    def _get_most_common_origin(self, user_id: str) -> str:
        """
        Get the most common origin for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Most common origin location
        """
        try:
            from app.models.route import CalculatedRoute
            from sqlalchemy import func, desc
            from app.core.database import get_db
            
            db = next(get_db())
            result = db.query(
                CalculatedRoute.origin,
                func.count(CalculatedRoute.origin).label('count')
            ).filter(
                CalculatedRoute.user_id == user_id
            ).group_by(
                CalculatedRoute.origin
            ).order_by(
                desc('count')
            ).first()
            
            return result.origin if result else "N/A"
            
        except Exception as e:
            self.logger.error(f"Error getting most common origin: {e}")
            return "N/A"

    def _get_most_common_destination(self, user_id: str) -> str:
        """
        Get the most common destination for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Most common destination location
        """
        try:
            from app.models.route import CalculatedRoute
            from sqlalchemy import func, desc
            from app.core.database import get_db
            
            db = next(get_db())
            result = db.query(
                CalculatedRoute.destination,
                func.count(CalculatedRoute.destination).label('count')
            ).filter(
                CalculatedRoute.user_id == user_id
            ).group_by(
                CalculatedRoute.destination
            ).order_by(
                desc('count')
            ).first()
            
            return result.destination if result else "N/A"
            
        except Exception as e:
            self.logger.error(f"Error getting most common destination: {e}")
            return "N/A"
