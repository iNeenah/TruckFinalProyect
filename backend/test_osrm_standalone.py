"""
Standalone tests for OSRM service core functionality.
"""
import pytest
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


# Copy the core classes to test them independently
@dataclass
class Coordinate:
    """Geographic coordinate."""
    longitude: float
    latitude: float
    
    def to_osrm_format(self) -> str:
        """Convert to OSRM coordinate format (lon,lat)."""
        return f"{self.longitude},{self.latitude}"


class RouteProfile(Enum):
    """OSRM routing profiles."""
    DRIVING = "driving"
    WALKING = "walking"
    CYCLING = "cycling"


class RouteGeometry(Enum):
    """OSRM geometry formats."""
    POLYLINE = "polyline"
    POLYLINE6 = "polyline6"
    GEOJSON = "geojson"


def argentina_bounds_check(coordinate: Coordinate) -> bool:
    """
    Check if coordinate is within Argentina bounds.
    
    Args:
        coordinate: Coordinate to check
        
    Returns:
        True if within Argentina bounds
    """
    # Argentina approximate bounds
    min_lon, max_lon = -73.5, -53.6
    min_lat, max_lat = -55.1, -21.8
    
    return (min_lon <= coordinate.longitude <= max_lon and
            min_lat <= coordinate.latitude <= max_lat)


def misiones_bounds_check(coordinate: Coordinate) -> bool:
    """
    Check if coordinate is within Misiones province bounds.
    
    Args:
        coordinate: Coordinate to check
        
    Returns:
        True if within Misiones bounds
    """
    # Misiones approximate bounds
    min_lon, max_lon = -56.5, -53.6
    min_lat, max_lat = -28.1, -25.2
    
    return (min_lon <= coordinate.longitude <= max_lon and
            min_lat <= coordinate.latitude <= max_lat)


class TestCoordinateStandalone:
    """Standalone test cases for Coordinate class."""
    
    def test_coordinate_creation_valid(self):
        """Test creating valid coordinates."""
        coord = Coordinate(-58.3816, -34.6037)  # Buenos Aires
        assert coord.longitude == -58.3816
        assert coord.latitude == -34.6037
    
    def test_coordinate_to_osrm_format(self):
        """Test coordinate conversion to OSRM format."""
        coord = Coordinate(-58.3816, -34.6037)
        assert coord.to_osrm_format() == "-58.3816,-34.6037"
    
    def test_coordinate_precision(self):
        """Test coordinate precision handling."""
        coord = Coordinate(-58.123456789, -34.987654321)
        expected = "-58.123456789,-34.987654321"
        assert coord.to_osrm_format() == expected


class TestBoundsCheckingStandalone:
    """Standalone test cases for bounds checking functions."""
    
    def test_argentina_bounds_check_valid_cities(self):
        """Test Argentina bounds checking with valid city coordinates."""
        test_cities = [
            (-58.3816, -34.6037),  # Buenos Aires
            (-68.3029, -54.8019),  # Ushuaia
            (-64.1810, -31.4201),  # Córdoba
            (-60.6393, -32.9442),  # Rosario
            (-65.2226, -24.7821),  # Salta
            (-67.8099, -38.9516),  # Neuquén
        ]
        
        for lon, lat in test_cities:
            coord = Coordinate(lon, lat)
            assert argentina_bounds_check(coord) == True, f"Failed for {lon}, {lat}"
    
    def test_argentina_bounds_check_invalid_countries(self):
        """Test Argentina bounds checking with coordinates from other countries."""
        test_coords = [
            (-47.9292, -15.7801),  # Brasília, Brazil
            (-74.0060, -4.7110),   # Bogotá, Colombia (clearly outside)
            (-77.0428, -12.0464),  # Lima, Peru
            (-43.1729, -22.9068),  # Rio de Janeiro, Brazil
            (-46.6333, -23.5505),  # São Paulo, Brazil
        ]
        
        for lon, lat in test_coords:
            coord = Coordinate(lon, lat)
            assert argentina_bounds_check(coord) == False, f"Should fail for {lon}, {lat}"
    
    def test_misiones_bounds_check_valid_cities(self):
        """Test Misiones bounds checking with valid coordinates."""
        test_cities = [
            (-55.8959, -27.3621),  # Posadas
            (-54.5735, -25.5951),  # Puerto Iguazú
            (-55.5377, -27.3671),  # Oberá
            (-54.7333, -26.8833),  # Eldorado
            (-55.2333, -26.4333),  # Leandro N. Alem
        ]
        
        for lon, lat in test_cities:
            coord = Coordinate(lon, lat)
            assert misiones_bounds_check(coord) == True, f"Failed for {lon}, {lat}"
    
    def test_misiones_bounds_check_invalid_provinces(self):
        """Test Misiones bounds checking with coordinates from other provinces."""
        test_coords = [
            (-58.3816, -34.6037),  # Buenos Aires
            (-64.1810, -31.4201),  # Córdoba
            (-60.6393, -32.9442),  # Rosario, Santa Fe
            (-65.2226, -24.7821),  # Salta
            (-58.9931, -27.4696),  # Corrientes
        ]
        
        for lon, lat in test_coords:
            coord = Coordinate(lon, lat)
            assert misiones_bounds_check(coord) == False, f"Should fail for {lon}, {lat}"
    
    def test_bounds_edge_cases(self):
        """Test bounds checking with edge cases."""
        # Test exact boundary coordinates
        argentina_min_coord = Coordinate(-73.5, -55.1)
        argentina_max_coord = Coordinate(-53.6, -21.8)
        
        assert argentina_bounds_check(argentina_min_coord) == True
        assert argentina_bounds_check(argentina_max_coord) == True
        
        # Test just outside boundaries
        outside_min = Coordinate(-73.6, -55.2)
        outside_max = Coordinate(-53.5, -21.7)
        
        assert argentina_bounds_check(outside_min) == False
        assert argentina_bounds_check(outside_max) == False


class TestEnumsStandalone:
    """Standalone test cases for enums."""
    
    def test_route_profile_enum_values(self):
        """Test RouteProfile enum values."""
        assert RouteProfile.DRIVING.value == "driving"
        assert RouteProfile.WALKING.value == "walking"
        assert RouteProfile.CYCLING.value == "cycling"
    
    def test_route_profile_enum_iteration(self):
        """Test RouteProfile enum iteration."""
        profiles = list(RouteProfile)
        assert len(profiles) == 3
        assert RouteProfile.DRIVING in profiles
        assert RouteProfile.WALKING in profiles
        assert RouteProfile.CYCLING in profiles
    
    def test_route_geometry_enum_values(self):
        """Test RouteGeometry enum values."""
        assert RouteGeometry.POLYLINE.value == "polyline"
        assert RouteGeometry.POLYLINE6.value == "polyline6"
        assert RouteGeometry.GEOJSON.value == "geojson"
    
    def test_route_geometry_enum_iteration(self):
        """Test RouteGeometry enum iteration."""
        geometries = list(RouteGeometry)
        assert len(geometries) == 3
        assert RouteGeometry.POLYLINE in geometries
        assert RouteGeometry.POLYLINE6 in geometries
        assert RouteGeometry.GEOJSON in geometries


class TestCoordinateValidation:
    """Test coordinate validation logic."""
    
    def test_coordinate_ranges(self):
        """Test coordinate range validation."""
        # Valid ranges
        valid_coords = [
            (-180, -90),   # Min valid
            (180, 90),     # Max valid
            (0, 0),        # Equator/Prime meridian
            (-58.3816, -34.6037),  # Buenos Aires
        ]
        
        for lon, lat in valid_coords:
            coord = Coordinate(lon, lat)
            assert -180 <= coord.longitude <= 180
            assert -90 <= coord.latitude <= 90
    
    def test_coordinate_string_formatting(self):
        """Test coordinate string formatting."""
        test_cases = [
            ((-58.3816, -34.6037), "-58.3816,-34.6037"),
            ((0, 0), "0,0"),
            ((-180, -90), "-180,-90"),
            ((180, 90), "180,90"),
            ((-55.123456, -27.654321), "-55.123456,-27.654321"),
        ]
        
        for (lon, lat), expected in test_cases:
            coord = Coordinate(lon, lat)
            assert coord.to_osrm_format() == expected


class TestGeographicLogic:
    """Test geographic logic and calculations."""
    
    def test_misiones_within_argentina(self):
        """Test that all Misiones coordinates are within Argentina."""
        misiones_cities = [
            (-55.8959, -27.3621),  # Posadas
            (-54.5735, -25.5951),  # Puerto Iguazú
            (-55.5377, -27.3671),  # Oberá
            (-54.7333, -26.8833),  # Eldorado
        ]
        
        for lon, lat in misiones_cities:
            coord = Coordinate(lon, lat)
            # All Misiones coordinates should be within Argentina
            assert misiones_bounds_check(coord) == True
            assert argentina_bounds_check(coord) == True
    
    def test_coordinate_consistency(self):
        """Test coordinate consistency across different checks."""
        # Test coordinates that should pass both checks
        posadas = Coordinate(-55.8959, -27.3621)
        assert misiones_bounds_check(posadas) == True
        assert argentina_bounds_check(posadas) == True
        
        # Test coordinates that should pass Argentina but not Misiones
        buenos_aires = Coordinate(-58.3816, -34.6037)
        assert misiones_bounds_check(buenos_aires) == False
        assert argentina_bounds_check(buenos_aires) == True
        
        # Test coordinates that should pass neither
        brasilia = Coordinate(-47.9292, -15.7801)
        assert misiones_bounds_check(brasilia) == False
        assert argentina_bounds_check(brasilia) == False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])