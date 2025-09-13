"""
Tests for route calculation API endpoints.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from datetime import datetime
from decimal import Decimal
import uuid

from app.main import app
from app.schemas.route import RouteRequest, Coordinates


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_user():
    """Mock authenticated user."""
    user = MagicMock()
    user.id = str(uuid.uuid4())
    user.company_id = str(uuid.uuid4())
    return user


@pytest.fixture
def mock_db():
    """Mock database session."""
    return MagicMock()


@pytest.fixture
def sample_route_request():
    """Sample route calculation request."""
    return {
        "origin": "Av. Mitre 1234, Posadas, Misiones",
        "destination": "Av. Victoria Aguirre 567, Puerto Iguazú, Misiones",
        "vehicle_id": str(uuid.uuid4()),
        "alternatives": 3,
        "avoid_tolls": False,
        "optimize_for": "cost"
    }


@pytest.fixture
def mock_optimization_response():
    """Mock route optimization response."""
    response = MagicMock()
    response.routes = []
    response.recommended_route = MagicMock()
    response.total_savings = Decimal("50.00")
    response.calculation_time_ms = 1500
    response.warnings = []
    return response


class TestRouteCalculationEndpoint:
    """Test cases for route calculation endpoint."""
    
    @patch('app.api.routes.get_current_active_user')
    @patch('app.api.routes.get_db')
    @patch('app.api.routes.RouteOptimizationService')
    @patch('app.api.routes.RouteComparisonService')
    @patch('app.api.routes.GeocodingService')
    def test_calculate_route_success(
        self,
        mock_geocoding_service,
        mock_comparison_service,
        mock_route_service,
        mock_get_db,
        mock_get_user,
        client,
        mock_user,
        mock_db,
        sample_route_request,
        mock_optimization_response
    ):
        """Test successful route calculation."""
        # Setup mocks
        mock_get_user.return_value = mock_user
        mock_get_db.return_value = mock_db
        
        # Mock geocoding
        mock_geocoder = AsyncMock()
        mock_origin_result = MagicMock()
        mock_origin_result.coordinate.longitude = -55.8959
        mock_origin_result.coordinate.latitude = -27.3621
        mock_origin_result.address = "Posadas, Misiones"
        
        mock_dest_result = MagicMock()
        mock_dest_result.coordinate.longitude = -54.5735
        mock_dest_result.coordinate.latitude = -25.5951
        mock_dest_result.address = "Puerto Iguazú, Misiones"
        
        mock_geocoder.geocode_argentina_address.side_effect = [
            [mock_origin_result],
            [mock_dest_result]
        ]
        mock_geocoding_service.return_value.__aenter__.return_value = mock_geocoder
        
        # Mock route optimization
        mock_route_service_instance = MagicMock()
        mock_route_service_instance.optimize_route = AsyncMock(return_value=mock_optimization_response)
        mock_route_service.return_value = mock_route_service_instance
        
        # Mock route comparison
        mock_comparison_service_instance = MagicMock()
        mock_analysis_summary = MagicMock()
        mock_comparison_service_instance.analyze_routes.return_value = mock_analysis_summary
        mock_comparison_service.return_value = mock_comparison_service_instance
        
        # Make request
        response = client.post("/routes/calculate", json=sample_route_request)
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert "request_id" in data
        assert "recommended_route" in data
        assert "alternative_routes" in data
        assert "savings_analysis" in data
        assert "calculation_time_ms" in data
        assert "timestamp" in data
    
    @patch('app.api.routes.get_current_active_user')
    @patch('app.api.routes.get_db')
    def test_calculate_route_invalid_request(
        self,
        mock_get_db,
        mock_get_user,
        client,
        mock_user,
        mock_db
    ):
        """Test route calculation with invalid request."""
        mock_get_user.return_value = mock_user
        mock_get_db.return_value = mock_db
        
        # Invalid request (missing required fields)
        invalid_request = {
            "origin": "Posadas",
            # Missing destination and vehicle_id
        }
        
        response = client.post("/routes/calculate", json=invalid_request)
        assert response.status_code == 422  # Validation error
    
    @patch('app.api.routes.get_current_active_user')
    @patch('app.api.routes.get_db')
    def test_calculate_route_with_coordinates(
        self,
        mock_get_db,
        mock_get_user,
        client,
        mock_user,
        mock_db
    ):
        """Test route calculation with coordinate inputs."""
        mock_get_user.return_value = mock_user
        mock_get_db.return_value = mock_db
        
        request_with_coords = {
            "origin": {"longitude": -55.8959, "latitude": -27.3621},
            "destination": {"longitude": -54.5735, "latitude": -25.5951},
            "vehicle_id": str(uuid.uuid4()),
            "alternatives": 2,
            "avoid_tolls": True,
            "optimize_for": "time"
        }
        
        with patch('app.api.routes.RouteOptimizationService') as mock_service:
            mock_instance = MagicMock()
            mock_instance.optimize_route = AsyncMock(return_value=MagicMock())
            mock_service.return_value = mock_instance
            
            with patch('app.api.routes.RouteComparisonService'):
                response = client.post("/routes/calculate", json=request_with_coords)
                # Should not fail on validation
                assert response.status_code in [200, 500]  # 500 if services not available


class TestGeocodingEndpoint:
    """Test cases for geocoding endpoint."""
    
    @patch('app.api.routes.get_current_active_user')
    @patch('app.api.routes.GeocodingService')
    def test_geocode_address_success(
        self,
        mock_geocoding_service,
        mock_get_user,
        client,
        mock_user
    ):
        """Test successful address geocoding."""
        mock_get_user.return_value = mock_user
        
        # Mock geocoding result
        mock_geocoder = AsyncMock()
        mock_result = MagicMock()
        mock_result.address = "Posadas, Misiones, Argentina"
        mock_result.coordinate.longitude = -55.8959
        mock_result.coordinate.latitude = -27.3621
        mock_result.confidence = 0.9
        mock_result.place_type = "city"
        
        mock_geocoder.geocode_argentina_address.return_value = [mock_result]
        mock_geocoding_service.return_value.__aenter__.return_value = mock_geocoder
        
        response = client.get("/routes/geocode?address=Posadas, Misiones")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert len(data["results"]) == 1
        assert data["results"][0]["address"] == "Posadas, Misiones, Argentina"
        assert data["results"][0]["coordinates"]["longitude"] == -55.8959
        assert data["results"][0]["coordinates"]["latitude"] == -27.3621
    
    @patch('app.api.routes.get_current_active_user')
    @patch('app.api.routes.GeocodingService')
    def test_geocode_address_no_results(
        self,
        mock_geocoding_service,
        mock_get_user,
        client,
        mock_user
    ):
        """Test geocoding with no results."""
        mock_get_user.return_value = mock_user
        
        mock_geocoder = AsyncMock()
        mock_geocoder.geocode_argentina_address.return_value = []
        mock_geocoding_service.return_value.__aenter__.return_value = mock_geocoder
        
        response = client.get("/routes/geocode?address=Invalid Address")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "no_results"
        assert len(data["results"]) == 0
    
    @patch('app.api.routes.get_current_active_user')
    def test_geocode_address_missing_parameter(
        self,
        mock_get_user,
        client,
        mock_user
    ):
        """Test geocoding without address parameter."""
        mock_get_user.return_value = mock_user
        
        response = client.get("/routes/geocode")
        assert response.status_code == 422  # Missing required parameter


class TestRouteHistoryEndpoint:
    """Test cases for route history endpoint."""
    
    @patch('app.api.routes.get_current_active_user')
    @patch('app.api.routes.get_db')
    def test_get_route_history_success(
        self,
        mock_get_db,
        mock_get_user,
        client,
        mock_user,
        mock_db
    ):
        """Test successful route history retrieval."""
        mock_get_user.return_value = mock_user
        mock_get_db.return_value = mock_db
        
        # Mock database query
        mock_route = MagicMock()
        mock_route.id = uuid.uuid4()
        mock_route.user_id = mock_user.id
        mock_route.vehicle_id = str(uuid.uuid4())
        mock_route.origin_address = "Posadas"
        mock_route.destination_address = "Puerto Iguazú"
        mock_route.origin_longitude = -55.8959
        mock_route.origin_latitude = -27.3621
        mock_route.destination_longitude = -54.5735
        mock_route.destination_latitude = -25.5951
        mock_route.distance_km = 295.2
        mock_route.duration_minutes = 225
        mock_route.fuel_cost = Decimal("847.50")
        mock_route.toll_cost = Decimal("90.00")
        mock_route.total_cost = Decimal("937.50")
        mock_route.estimated_savings = Decimal("50.00")
        mock_route.created_at = datetime.now()
        
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 1
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = [mock_route]
        
        mock_db.query.return_value = mock_query
        
        response = client.get("/routes/history")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["page"] == 1
        assert len(data["routes"]) == 1
        assert data["routes"][0]["origin_address"] == "Posadas"
    
    @patch('app.api.routes.get_current_active_user')
    @patch('app.api.routes.get_db')
    def test_get_route_history_with_filters(
        self,
        mock_get_db,
        mock_get_user,
        client,
        mock_user,
        mock_db
    ):
        """Test route history with filters."""
        mock_get_user.return_value = mock_user
        mock_get_db.return_value = mock_db
        
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 0
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []
        
        mock_db.query.return_value = mock_query
        
        vehicle_id = str(uuid.uuid4())
        response = client.get(f"/routes/history?vehicle_id={vehicle_id}&page=2&size=10")
        
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 2
        assert data["size"] == 10


class TestRouteStatisticsEndpoint:
    """Test cases for route statistics endpoint."""
    
    @patch('app.api.routes.get_current_active_user')
    @patch('app.api.routes.get_db')
    @patch('app.api.routes.RouteOptimizationService')
    def test_get_route_statistics_success(
        self,
        mock_route_service,
        mock_get_db,
        mock_get_user,
        client,
        mock_user,
        mock_db
    ):
        """Test successful route statistics retrieval."""
        mock_get_user.return_value = mock_user
        mock_get_db.return_value = mock_db
        
        # Mock service response
        mock_service_instance = MagicMock()
        mock_stats = {
            "total_routes": 25,
            "total_distance_km": 2500.0,
            "total_cost": 15000.0,
            "total_savings": 1250.0,
            "average_distance": 100.0,
            "average_cost": 600.0
        }
        mock_service_instance.get_route_statistics = AsyncMock(return_value=mock_stats)
        mock_route_service.return_value = mock_service_instance
        
        response = client.get("/routes/statistics")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_routes"] == 25
        assert data["total_distance"] == 2500.0
        assert data["total_cost"] == 15000.0
        assert data["total_savings"] == 1250.0
        assert "date_range" in data


class TestRouteReportsEndpoint:
    """Test cases for route reports endpoint."""
    
    @patch('app.api.routes.get_current_active_user')
    @patch('app.api.routes.get_db')
    def test_generate_route_report_success(
        self,
        mock_get_db,
        mock_get_user,
        client,
        mock_user,
        mock_db
    ):
        """Test successful route report generation."""
        mock_get_user.return_value = mock_user
        mock_get_db.return_value = mock_db
        
        # Mock route in database
        mock_route = MagicMock()
        mock_route.id = uuid.uuid4()
        mock_route.user_id = mock_user.id
        
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_route
        mock_db.query.return_value = mock_query
        
        report_request = {
            "route_id": str(mock_route.id),
            "report_type": "complete",
            "include_map": True,
            "format": "pdf"
        }
        
        response = client.post("/routes/reports", json=report_request)
        
        assert response.status_code == 200
        data = response.json()
        assert "report_id" in data
        assert "download_url" in data
        assert "expires_at" in data
        assert data["format"] == "pdf"
    
    @patch('app.api.routes.get_current_active_user')
    @patch('app.api.routes.get_db')
    def test_generate_route_report_not_found(
        self,
        mock_get_db,
        mock_get_user,
        client,
        mock_user,
        mock_db
    ):
        """Test route report generation for non-existent route."""
        mock_get_user.return_value = mock_user
        mock_get_db.return_value = mock_db
        
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None  # Route not found
        mock_db.query.return_value = mock_query
        
        report_request = {
            "route_id": str(uuid.uuid4()),
            "report_type": "simple",
            "include_map": False,
            "format": "html"
        }
        
        response = client.post("/routes/reports", json=report_request)
        assert response.status_code == 404


class TestRouteHealthEndpoint:
    """Test cases for route health endpoint."""
    
    @patch('app.api.routes.OSRMService')
    def test_route_health_check_healthy(self, mock_osrm_service, client):
        """Test health check when all services are healthy."""
        mock_osrm = AsyncMock()
        mock_osrm.health_check.return_value = True
        mock_osrm_service.return_value.__aenter__.return_value = mock_osrm
        
        response = client.get("/routes/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["services"]["osrm"] == "healthy"
        assert data["services"]["database"] == "healthy"
        assert "timestamp" in data
    
    @patch('app.api.routes.OSRMService')
    def test_route_health_check_degraded(self, mock_osrm_service, client):
        """Test health check when OSRM is unavailable."""
        mock_osrm = AsyncMock()
        mock_osrm.health_check.return_value = False
        mock_osrm_service.return_value.__aenter__.return_value = mock_osrm
        
        response = client.get("/routes/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "degraded"
        assert data["services"]["osrm"] == "unavailable"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])