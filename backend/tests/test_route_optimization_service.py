"""
Tests for route optimization service.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from decimal import Decimal
from datetime import datetime, timedelta

from app.services.route_optimization_service import (
    RouteOptimizationService,
    RoutePoint,
    RouteOptimizationRequest,
    FuelCostInfo,
    TollInfo,
    RouteCostBreakdown,
    OptimizedRoute
)
from app.services.osrm_service import Coordinate, Route as OSRMRoute, RouteLeg
from app.models.vehicle import Vehicle, FuelType
from app.models.fuel_price import FuelPrice
from app.models.toll import Toll


@pytest.fixture
def mock_db():
    """Mock database session."""
    return MagicMock()


@pytest.fixture
def mock_vehicle():
    """Mock vehicle for testing."""
    vehicle = MagicMock(spec=Vehicle)
    vehicle.id = "test-vehicle-id"
    vehicle.fuel_consumption = Decimal("15.0")
    vehicle.fuel_type = FuelType.DIESEL_500
    vehicle.max_weight = 3000
    vehicle.model = "Transit"
    return vehicle


@pytest.fixture
def mock_fuel_price():
    """Mock fuel price for testing."""
    fuel_price = MagicMock(spec=FuelPrice)
    fuel_price.price_per_liter = Decimal("150.00")
    fuel_price.fuel_type = "diesel_500"
    fuel_price.updated_at = datetime.now()
    fuel_price.is_active = True
    return fuel_price


@pytest.fixture
def mock_toll():
    """Mock toll for testing."""
    toll = MagicMock(spec=Toll)
    toll.id = "test-toll-id"
    toll.name = "Test Toll"
    toll.longitude = -55.8959
    toll.latitude = -27.3621
    toll.cost_car = Decimal("50.00")
    toll.cost_truck = Decimal("100.00")
    toll.cost_motorcycle = Decimal("25.00")
    toll.road_name = "RN12"
    toll.is_active = True
    return toll


@pytest.fixture
def mock_osrm_route():
    """Mock OSRM route for testing."""
    route = MagicMock(spec=OSRMRoute)
    route.distance = 100000  # 100 km
    route.duration = 3600    # 1 hour
    route.geometry = "test_geometry"
    route.legs = [MagicMock(spec=RouteLeg)]
    return route


@pytest.fixture
def route_optimization_service(mock_db):
    """Create route optimization service for testing."""
    return RouteOptimizationService(mock_db)


@pytest.fixture
def sample_request():
    """Sample route optimization request."""
    return RouteOptimizationRequest(
        origin=RoutePoint(
            coordinate=Coordinate(-55.8959, -27.3621),
            address="Posadas, Misiones",
            name="Origin"
        ),
        destination=RoutePoint(
            coordinate=Coordinate(-54.5735, -25.5951),
            address="Puerto Iguazú, Misiones",
            name="Destination"
        ),
        vehicle_id="test-vehicle-id",
        avoid_tolls=False,
        max_alternatives=3
    )


class TestRouteOptimizationService:
    """Test cases for RouteOptimizationService."""
    
    def test_calculate_fuel_cost(self, route_optimization_service, mock_vehicle):
        """Test fuel cost calculation."""
        distance_km = 100.0
        fuel_price = Decimal("150.00")
        
        fuel_cost_info = route_optimization_service._calculate_fuel_cost(
            distance_km, mock_vehicle, fuel_price
        )
        
        assert fuel_cost_info.distance_km == 100.0
        assert fuel_cost_info.fuel_consumption_per_100km == Decimal("15.0")
        assert fuel_cost_info.fuel_needed_liters == 15.0  # 100km * 15L/100km
        assert fuel_cost_info.fuel_price_per_liter == Decimal("150.00")
        assert fuel_cost_info.total_fuel_cost == Decimal("2250.00")  # 15L * 150 ARS/L
        assert fuel_cost_info.fuel_type == "diesel_500"
    
    def test_get_vehicle_category_car(self, route_optimization_service):
        """Test vehicle category determination for car."""
        vehicle = MagicMock()
        vehicle.max_weight = 2000
        vehicle.model = "Corolla"
        
        category = route_optimization_service._get_vehicle_category(vehicle)
        assert category == "car"
    
    def test_get_vehicle_category_truck(self, route_optimization_service):
        """Test vehicle category determination for truck."""
        vehicle = MagicMock()
        vehicle.max_weight = 5000
        vehicle.model = "F-150"
        
        category = route_optimization_service._get_vehicle_category(vehicle)
        assert category == "truck"
    
    def test_get_vehicle_category_motorcycle(self, route_optimization_service):
        """Test vehicle category determination for motorcycle."""
        vehicle = MagicMock()
        vehicle.max_weight = 300
        vehicle.model = "Honda Moto"
        
        category = route_optimization_service._get_vehicle_category(vehicle)
        assert category == "motorcycle"
    
    def test_get_toll_cost_for_vehicle_car(self, route_optimization_service, mock_toll):
        """Test toll cost calculation for car."""
        vehicle = MagicMock()
        vehicle.max_weight = 2000
        vehicle.model = "Corolla"
        
        cost = route_optimization_service._get_toll_cost_for_vehicle(mock_toll, vehicle)
        assert cost == Decimal("50.00")
    
    def test_get_toll_cost_for_vehicle_truck(self, route_optimization_service, mock_toll):
        """Test toll cost calculation for truck."""
        vehicle = MagicMock()
        vehicle.max_weight = 5000
        vehicle.model = "F-150"
        
        cost = route_optimization_service._get_toll_cost_for_vehicle(mock_toll, vehicle)
        assert cost == Decimal("100.00")
    
    def test_get_default_fuel_price_diesel(self, route_optimization_service):
        """Test default fuel price for diesel."""
        price = route_optimization_service._get_default_fuel_price("diesel_500")
        assert price == Decimal("150.00")
    
    def test_get_default_fuel_price_gasoline(self, route_optimization_service):
        """Test default fuel price for gasoline."""
        price = route_optimization_service._get_default_fuel_price("gasoline")
        assert price == Decimal("160.00")
    
    def test_get_default_fuel_price_unknown(self, route_optimization_service):
        """Test default fuel price for unknown fuel type."""
        price = route_optimization_service._get_default_fuel_price("unknown")
        assert price == Decimal("160.00")  # Default fallback
    
    @pytest.mark.asyncio
    async def test_get_current_fuel_price_found(self, route_optimization_service, mock_fuel_price):
        """Test getting current fuel price when available."""
        route_optimization_service.db.query.return_value.filter.return_value.order_by.return_value.first.return_value = mock_fuel_price
        
        price = await route_optimization_service._get_current_fuel_price("diesel_500")
        assert price == Decimal("150.00")
    
    @pytest.mark.asyncio
    async def test_get_current_fuel_price_not_found(self, route_optimization_service):
        """Test getting current fuel price when not available."""
        route_optimization_service.db.query.return_value.filter.return_value.order_by.return_value.first.return_value = None
        
        price = await route_optimization_service._get_current_fuel_price("diesel_500")
        assert price is None
    
    @pytest.mark.asyncio
    async def test_get_current_fuel_price_too_old(self, route_optimization_service):
        """Test getting current fuel price when too old."""
        old_fuel_price = MagicMock()
        old_fuel_price.price_per_liter = Decimal("150.00")
        old_fuel_price.updated_at = datetime.now() - timedelta(days=35)  # Too old
        
        route_optimization_service.db.query.return_value.filter.return_value.order_by.return_value.first.return_value = old_fuel_price
        
        price = await route_optimization_service._get_current_fuel_price("diesel_500")
        assert price is None
    
    @pytest.mark.asyncio
    async def test_detect_route_tolls_success(self, route_optimization_service, mock_osrm_route, mock_vehicle, mock_toll):
        """Test successful toll detection."""
        route_optimization_service.db.query.return_value.filter.return_value.all.return_value = [mock_toll]
        
        tolls = await route_optimization_service._detect_route_tolls(mock_osrm_route, mock_vehicle)
        
        assert len(tolls) == 1
        assert tolls[0].toll_id == "test-toll-id"
        assert tolls[0].name == "Test Toll"
        assert tolls[0].cost == Decimal("50.00")  # Car cost
        assert tolls[0].vehicle_type == "car"
    
    @pytest.mark.asyncio
    async def test_detect_route_tolls_error(self, route_optimization_service, mock_osrm_route, mock_vehicle):
        """Test toll detection with database error."""
        route_optimization_service.db.query.side_effect = Exception("Database error")
        
        tolls = await route_optimization_service._detect_route_tolls(mock_osrm_route, mock_vehicle)
        
        assert tolls == []  # Should return empty list on error
    
    @pytest.mark.asyncio
    async def test_calculate_route_costs(self, route_optimization_service, mock_osrm_route, mock_vehicle, mock_fuel_price):
        """Test route cost calculation."""
        fuel_price = Decimal("150.00")
        
        # Mock toll detection
        with patch.object(route_optimization_service, '_detect_route_tolls') as mock_detect_tolls:
            mock_toll_info = TollInfo(
                toll_id="test-toll",
                name="Test Toll",
                coordinate=Coordinate(-55.8959, -27.3621),
                cost=Decimal("50.00"),
                vehicle_type="car",
                road_name="RN12"
            )
            mock_detect_tolls.return_value = [mock_toll_info]
            
            cost_breakdown = await route_optimization_service._calculate_route_costs(
                mock_osrm_route, mock_vehicle, fuel_price, avoid_tolls=False
            )
            
            assert cost_breakdown.fuel_cost.total_fuel_cost == Decimal("2250.00")  # 100km * 15L/100km * 150 ARS/L
            assert cost_breakdown.total_toll_cost == Decimal("50.00")
            assert cost_breakdown.total_cost == Decimal("2300.00")  # 2250 + 50
            assert len(cost_breakdown.tolls) == 1
    
    @pytest.mark.asyncio
    async def test_calculate_route_costs_avoid_tolls(self, route_optimization_service, mock_osrm_route, mock_vehicle):
        """Test route cost calculation when avoiding tolls."""
        fuel_price = Decimal("150.00")
        
        cost_breakdown = await route_optimization_service._calculate_route_costs(
            mock_osrm_route, mock_vehicle, fuel_price, avoid_tolls=True
        )
        
        assert cost_breakdown.fuel_cost.total_fuel_cost == Decimal("2250.00")
        assert cost_breakdown.total_toll_cost == Decimal("0.00")
        assert cost_breakdown.total_cost == Decimal("2250.00")
        assert len(cost_breakdown.tolls) == 0
    
    @pytest.mark.asyncio
    async def test_optimize_route_success(self, route_optimization_service, sample_request, mock_vehicle, mock_fuel_price):
        """Test successful route optimization."""
        # Mock database queries
        route_optimization_service.db.query.return_value.filter.return_value.first.return_value = mock_vehicle
        route_optimization_service.db.query.return_value.filter.return_value.order_by.return_value.first.return_value = mock_fuel_price
        
        # Mock OSRM service
        mock_osrm_routes = [
            MagicMock(distance=100000, duration=3600, geometry="route1"),
            MagicMock(distance=110000, duration=3900, geometry="route2")
        ]
        
        with patch('app.services.route_optimization_service.OSRMService') as mock_osrm_class:
            mock_osrm = AsyncMock()
            mock_osrm.health_check.return_value = True
            mock_osrm.get_route_alternatives.return_value = mock_osrm_routes
            mock_osrm_class.return_value.__aenter__.return_value = mock_osrm
            
            # Mock cost calculation
            with patch.object(route_optimization_service, '_calculate_route_costs') as mock_calc_costs:
                mock_cost_breakdown = MagicMock()
                mock_cost_breakdown.total_cost = Decimal("2300.00")
                mock_calc_costs.return_value = mock_cost_breakdown
                
                response = await route_optimization_service.optimize_route(sample_request)
                
                assert len(response.routes) == 2
                assert response.recommended_route is not None
                assert response.calculation_time_ms > 0
                assert isinstance(response.warnings, list)
    
    @pytest.mark.asyncio
    async def test_optimize_route_vehicle_not_found(self, route_optimization_service, sample_request):
        """Test route optimization when vehicle is not found."""
        route_optimization_service.db.query.return_value.filter.return_value.first.return_value = None
        
        with pytest.raises(ValueError, match="Vehicle .* not found"):
            await route_optimization_service.optimize_route(sample_request)
    
    @pytest.mark.asyncio
    async def test_optimize_route_osrm_unavailable(self, route_optimization_service, sample_request, mock_vehicle):
        """Test route optimization when OSRM is unavailable."""
        route_optimization_service.db.query.return_value.filter.return_value.first.return_value = mock_vehicle
        
        with patch('app.services.route_optimization_service.OSRMService') as mock_osrm_class:
            mock_osrm = AsyncMock()
            mock_osrm.health_check.return_value = False
            mock_osrm_class.return_value.__aenter__.return_value = mock_osrm
            
            with pytest.raises(RuntimeError, match="OSRM service is not available"):
                await route_optimization_service.optimize_route(sample_request)
    
    @pytest.mark.asyncio
    async def test_geocode_and_optimize_success(self, route_optimization_service):
        """Test geocoding and route optimization."""
        with patch('app.services.route_optimization_service.GeocodingService') as mock_geocoder_class:
            # Mock geocoding results
            mock_geocoder = AsyncMock()
            mock_origin_result = MagicMock()
            mock_origin_result.coordinate = Coordinate(-55.8959, -27.3621)
            mock_origin_result.address = "Posadas, Misiones"
            
            mock_dest_result = MagicMock()
            mock_dest_result.coordinate = Coordinate(-54.5735, -25.5951)
            mock_dest_result.address = "Puerto Iguazú, Misiones"
            
            mock_geocoder.geocode_argentina_address.side_effect = [
                [mock_origin_result],  # Origin results
                [mock_dest_result]     # Destination results
            ]
            mock_geocoder_class.return_value.__aenter__.return_value = mock_geocoder
            
            # Mock optimize_route
            with patch.object(route_optimization_service, 'optimize_route') as mock_optimize:
                mock_response = MagicMock()
                mock_optimize.return_value = mock_response
                
                response = await route_optimization_service.geocode_and_optimize(
                    origin_address="Posadas, Misiones",
                    destination_address="Puerto Iguazú, Misiones",
                    vehicle_id="test-vehicle-id"
                )
                
                assert response == mock_response
                mock_optimize.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_geocode_and_optimize_origin_not_found(self, route_optimization_service):
        """Test geocoding when origin address is not found."""
        with patch('app.services.route_optimization_service.GeocodingService') as mock_geocoder_class:
            mock_geocoder = AsyncMock()
            mock_geocoder.geocode_argentina_address.return_value = []  # No results
            mock_geocoder_class.return_value.__aenter__.return_value = mock_geocoder
            
            with pytest.raises(ValueError, match="Could not geocode origin address"):
                await route_optimization_service.geocode_and_optimize(
                    origin_address="Invalid Address",
                    destination_address="Puerto Iguazú, Misiones",
                    vehicle_id="test-vehicle-id"
                )
    
    @pytest.mark.asyncio
    async def test_get_route_statistics_no_routes(self, route_optimization_service):
        """Test route statistics when no routes exist."""
        route_optimization_service.db.query.return_value.count.return_value = 0
        
        stats = await route_optimization_service.get_route_statistics()
        
        assert stats["total_routes"] == 0
        assert stats["total_distance_km"] == 0
        assert stats["total_savings"] == 0
        assert stats["average_savings"] == 0
    
    @pytest.mark.asyncio
    async def test_get_route_statistics_with_routes(self, route_optimization_service):
        """Test route statistics with existing routes."""
        # Mock query results
        route_optimization_service.db.query.return_value.count.return_value = 5
        
        mock_stats = MagicMock()
        mock_stats.total_distance = 500.0
        mock_stats.total_savings = 250.0
        mock_stats.avg_savings = 50.0
        
        route_optimization_service.db.query.return_value.with_entities.return_value.first.return_value = mock_stats
        
        stats = await route_optimization_service.get_route_statistics()
        
        assert stats["total_routes"] == 5
        assert stats["total_distance_km"] == 500.0
        assert stats["total_savings"] == 250.0
        assert stats["average_savings"] == 50.0


class TestDataClasses:
    """Test cases for data classes."""
    
    def test_route_point_creation(self):
        """Test RoutePoint creation."""
        coordinate = Coordinate(-55.8959, -27.3621)
        point = RoutePoint(
            coordinate=coordinate,
            address="Posadas, Misiones",
            name="Test Point"
        )
        
        assert point.coordinate == coordinate
        assert point.address == "Posadas, Misiones"
        assert point.name == "Test Point"
    
    def test_toll_info_creation(self):
        """Test TollInfo creation."""
        coordinate = Coordinate(-55.8959, -27.3621)
        toll = TollInfo(
            toll_id="test-toll",
            name="Test Toll",
            coordinate=coordinate,
            cost=Decimal("50.00"),
            vehicle_type="car",
            road_name="RN12"
        )
        
        assert toll.toll_id == "test-toll"
        assert toll.name == "Test Toll"
        assert toll.coordinate == coordinate
        assert toll.cost == Decimal("50.00")
        assert toll.vehicle_type == "car"
        assert toll.road_name == "RN12"
    
    def test_fuel_cost_info_creation(self):
        """Test FuelCostInfo creation."""
        fuel_cost = FuelCostInfo(
            distance_km=100.0,
            fuel_consumption_per_100km=Decimal("15.0"),
            fuel_needed_liters=15.0,
            fuel_price_per_liter=Decimal("150.00"),
            total_fuel_cost=Decimal("2250.00"),
            fuel_type="diesel_500"
        )
        
        assert fuel_cost.distance_km == 100.0
        assert fuel_cost.fuel_consumption_per_100km == Decimal("15.0")
        assert fuel_cost.fuel_needed_liters == 15.0
        assert fuel_cost.fuel_price_per_liter == Decimal("150.00")
        assert fuel_cost.total_fuel_cost == Decimal("2250.00")
        assert fuel_cost.fuel_type == "diesel_500"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])