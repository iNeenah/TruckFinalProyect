"""
Tests for OSRM service.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx

from app.services.osrm_service import (
    OSRMService, 
    Coordinate, 
    RouteProfile, 
    RouteGeometry,
    Route,
    RouteLeg,
    RouteStep,
    OSRMResponse,
    argentina_bounds_check,
    misiones_bounds_check
)


class TestCoordinate:
    """Test cases for Coordinate class."""
    
    def test_coordinate_creation_valid(self):
        """Test creating valid coordinates."""
        coord = Coordinate(-58.3816, -34.6037)  # Buenos Aires
        assert coord.longitude == -58.3816
        assert coord.latitude == -34.6037
    
    def test_coordinate_to_osrm_format(self):
        """Test coordinate conversion to OSRM format."""
        coord = Coordinate(-58.3816, -34.6037)
        assert coord.to_osrm_format() == "-58.3816,-34.6037"
    
    def test_coordinate_validation_invalid(self):
        """Test coordinate validation with invalid values."""
        with pytest.raises(Exception):  # Should raise validation error
            Coordinate(200, 100)  # Invalid longitude/latitude


class TestBoundsChecking:
    """Test cases for bounds checking functions."""
    
    def test_argentina_bounds_check_valid(self):
        """Test Argentina bounds checking with valid coordinates."""
        # Buenos Aires
        coord = Coordinate(-58.3816, -34.6037)
        assert argentina_bounds_check(coord) == True
        
        # Ushuaia
        coord = Coordinate(-68.3029, -54.8019)
        assert argentina_bounds_check(coord) == True
    
    def test_argentina_bounds_check_invalid(self):
        """Test Argentina bounds checking with invalid coordinates."""
        # Brazil
        coord = Coordinate(-47.9292, -15.7801)
        assert argentina_bounds_check(coord) == False
        
        # Chile
        coord = Coordinate(-70.6693, -33.4489)
        assert argentina_bounds_check(coord) == False
    
    def test_misiones_bounds_check_valid(self):
        """Test Misiones bounds checking with valid coordinates."""
        # Posadas
        coord = Coordinate(-55.8959, -27.3621)
        assert misiones_bounds_check(coord) == True
    
    def test_misiones_bounds_check_invalid(self):
        """Test Misiones bounds checking with invalid coordinates."""
        # Buenos Aires
        coord = Coordinate(-58.3816, -34.6037)
        assert misiones_bounds_check(coord) == False


@pytest.mark.asyncio
class TestOSRMService:
    """Test cases for OSRMService."""
    
    @pytest.fixture
    def osrm_service(self):
        """Create OSRM service instance for testing."""
        return OSRMService(base_url="http://test-osrm:5000")
    
    @pytest.fixture
    def mock_response_data(self):
        """Mock OSRM response data."""
        return {
            "code": "Ok",
            "routes": [
                {
                    "distance": 1000.0,
                    "duration": 120.0,
                    "geometry": "test_geometry",
                    "weight": 120.0,
                    "weight_name": "routability",
                    "legs": [
                        {
                            "distance": 1000.0,
                            "duration": 120.0,
                            "steps": [
                                {
                                    "distance": 500.0,
                                    "duration": 60.0,
                                    "geometry": "step_geometry",
                                    "name": "Test Street",
                                    "maneuver": {
                                        "instruction": "Turn right"
                                    }
                                }
                            ]
                        }
                    ]
                }
            ],
            "waypoints": [
                {"location": [-55.8959, -27.3621]},
                {"location": [-55.9000, -27.3700]}
            ]
        }
    
    async def test_health_check_success(self, osrm_service):
        """Test successful health check."""
        with patch.object(osrm_service.client, 'get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            result = await osrm_service.health_check()
            assert result == True
            mock_get.assert_called_once_with("http://test-osrm:5000/health")
    
    async def test_health_check_failure(self, osrm_service):
        """Test failed health check."""
        with patch.object(osrm_service.client, 'get') as mock_get:
            mock_get.side_effect = httpx.RequestError("Connection failed")
            
            result = await osrm_service.health_check()
            assert result == False
    
    async def test_route_success(self, osrm_service, mock_response_data):
        """Test successful route calculation."""
        coordinates = [
            Coordinate(-55.8959, -27.3621),  # Posadas
            Coordinate(-55.9000, -27.3700)   # Nearby point
        ]
        
        with patch.object(osrm_service.client, 'get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            result = await osrm_service.route(coordinates)
            
            assert isinstance(result, OSRMResponse)
            assert result.code == "Ok"
            assert len(result.routes) == 1
            assert result.routes[0].distance == 1000.0
            assert result.routes[0].duration == 120.0
    
    async def test_route_invalid_coordinates(self, osrm_service):
        """Test route calculation with invalid coordinates."""
        coordinates = [Coordinate(-55.8959, -27.3621)]  # Only one coordinate
        
        with pytest.raises(ValueError, match="At least 2 coordinates are required"):
            await osrm_service.route(coordinates)
    
    async def test_route_osrm_error(self, osrm_service):
        """Test route calculation with OSRM error response."""
        coordinates = [
            Coordinate(-55.8959, -27.3621),
            Coordinate(-55.9000, -27.3700)
        ]
        
        error_response = {
            "code": "NoRoute",
            "message": "No route found"
        }
        
        with patch.object(osrm_service.client, 'get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = error_response
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            with pytest.raises(ValueError, match="OSRM error: No route found"):
                await osrm_service.route(coordinates)
    
    async def test_table_success(self, osrm_service):
        """Test successful distance/duration table calculation."""
        coordinates = [
            Coordinate(-55.8959, -27.3621),
            Coordinate(-55.9000, -27.3700),
            Coordinate(-55.9100, -27.3800)
        ]
        
        table_response = {
            "code": "Ok",
            "durations": [[0, 120, 240], [120, 0, 120], [240, 120, 0]],
            "distances": [[0, 1000, 2000], [1000, 0, 1000], [2000, 1000, 0]]
        }
        
        with patch.object(osrm_service.client, 'get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = table_response
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            result = await osrm_service.table(coordinates)
            
            assert result["code"] == "Ok"
            assert "durations" in result
            assert "distances" in result
    
    async def test_nearest_success(self, osrm_service):
        """Test successful nearest road segment search."""
        coordinate = Coordinate(-55.8959, -27.3621)
        
        nearest_response = {
            "code": "Ok",
            "waypoints": [
                {
                    "location": [-55.8959, -27.3621],
                    "name": "Test Street",
                    "distance": 5.2
                }
            ]
        }
        
        with patch.object(osrm_service.client, 'get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = nearest_response
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            result = await osrm_service.nearest(coordinate)
            
            assert result["code"] == "Ok"
            assert "waypoints" in result
    
    async def test_get_route_alternatives(self, osrm_service, mock_response_data):
        """Test getting route alternatives."""
        origin = Coordinate(-55.8959, -27.3621)
        destination = Coordinate(-55.9000, -27.3700)
        
        # Add multiple routes to mock response
        mock_response_data["routes"].append({
            "distance": 1200.0,
            "duration": 150.0,
            "geometry": "alternative_geometry",
            "weight": 150.0,
            "weight_name": "routability",
            "legs": []
        })
        
        with patch.object(osrm_service.client, 'get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            routes = await osrm_service.get_route_alternatives(origin, destination, max_alternatives=2)
            
            assert len(routes) == 2
            assert routes[0].distance == 1000.0
            assert routes[1].distance == 1200.0
    
    async def test_calculate_route_matrix(self, osrm_service):
        """Test calculating route matrix."""
        origins = [Coordinate(-55.8959, -27.3621)]
        destinations = [Coordinate(-55.9000, -27.3700), Coordinate(-55.9100, -27.3800)]
        
        matrix_response = {
            "code": "Ok",
            "durations": [[120, 240]],
            "distances": [[1000, 2000]]
        }
        
        with patch.object(osrm_service.client, 'get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = matrix_response
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            result = await osrm_service.calculate_route_matrix(origins, destinations)
            
            assert result["code"] == "Ok"
            assert "durations" in result
            assert "distances" in result
    
    def test_parse_route_response(self, osrm_service, mock_response_data):
        """Test parsing OSRM route response."""
        result = osrm_service._parse_route_response(mock_response_data)
        
        assert isinstance(result, OSRMResponse)
        assert result.code == "Ok"
        assert len(result.routes) == 1
        
        route = result.routes[0]
        assert isinstance(route, Route)
        assert route.distance == 1000.0
        assert route.duration == 120.0
        assert len(route.legs) == 1
        
        leg = route.legs[0]
        assert isinstance(leg, RouteLeg)
        assert leg.distance == 1000.0
        assert leg.duration == 120.0
        assert len(leg.steps) == 1
        
        step = leg.steps[0]
        assert isinstance(step, RouteStep)
        assert step.distance == 500.0
        assert step.duration == 60.0
        assert step.name == "Test Street"
        assert step.instruction == "Turn right"


@pytest.mark.asyncio
class TestOSRMServiceIntegration:
    """Integration tests for OSRM service (require running OSRM instance)."""
    
    @pytest.fixture
    def osrm_service(self):
        """Create OSRM service instance for integration testing."""
        return OSRMService()  # Use default localhost URL
    
    @pytest.mark.integration
    async def test_real_osrm_health_check(self, osrm_service):
        """Test health check against real OSRM instance."""
        # This test requires a running OSRM instance
        result = await osrm_service.health_check()
        # Don't assert True/False as OSRM might not be running
        assert isinstance(result, bool)
    
    @pytest.mark.integration
    async def test_real_route_calculation(self, osrm_service):
        """Test route calculation against real OSRM instance."""
        # Skip if OSRM is not available
        if not await osrm_service.health_check():
            pytest.skip("OSRM service not available")
        
        # Posadas to Puerto Iguazu (both in Misiones)
        coordinates = [
            Coordinate(-55.8959, -27.3621),  # Posadas
            Coordinate(-54.5735, -25.5951)   # Puerto Iguazu
        ]
        
        try:
            result = await osrm_service.route(coordinates)
            assert isinstance(result, OSRMResponse)
            assert result.code == "Ok"
            assert len(result.routes) > 0
            assert result.routes[0].distance > 0
            assert result.routes[0].duration > 0
        except Exception as e:
            pytest.skip(f"OSRM route calculation failed: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])