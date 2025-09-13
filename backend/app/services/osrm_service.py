"""
OSRM (Open Source Routing Machine) service integration.
"""
import httpx
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from app.config import get_settings
from app.validators.common_validators import validate_coordinates

settings = get_settings()
logger = logging.getLogger(__name__)


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


@dataclass
class Coordinate:
    """Geographic coordinate."""
    longitude: float
    latitude: float
    
    def __post_init__(self):
        """Validate coordinates after initialization."""
        validate_coordinates(self.longitude, self.latitude)
    
    def to_osrm_format(self) -> str:
        """Convert to OSRM coordinate format (lon,lat)."""
        return f"{self.longitude},{self.latitude}"


@dataclass
class RouteStep:
    """Individual step in a route."""
    distance: float  # meters
    duration: float  # seconds
    geometry: str
    name: str
    instruction: str


@dataclass
class RouteLeg:
    """Leg of a route between two waypoints."""
    distance: float  # meters
    duration: float  # seconds
    steps: List[RouteStep]


@dataclass
class Route:
    """Complete route information."""
    distance: float  # meters
    duration: float  # seconds
    geometry: str
    legs: List[RouteLeg]
    weight: Optional[float] = None
    weight_name: Optional[str] = None


@dataclass
class OSRMResponse:
    """OSRM API response."""
    code: str
    routes: List[Route]
    waypoints: List[Dict[str, Any]]
    message: Optional[str] = None


class OSRMService:
    """Service for interacting with OSRM routing engine."""
    
    def __init__(self, base_url: str = None):
        """
        Initialize OSRM service.
        
        Args:
            base_url: OSRM server base URL
        """
        self.base_url = base_url or getattr(settings, 'osrm_url', 'http://localhost:5000')
        self.client = httpx.AsyncClient(timeout=30.0)
        self.logger = logging.getLogger(__name__)
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.client.aclose()
    
    async def health_check(self) -> bool:
        """
        Check if OSRM service is healthy.
        
        Returns:
            True if service is healthy
        """
        try:
            response = await self.client.get(f"{self.base_url}/health")
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"OSRM health check failed: {e}")
            return False
    
    async def route(
        self,
        coordinates: List[Coordinate],
        profile: RouteProfile = RouteProfile.DRIVING,
        alternatives: bool = True,
        steps: bool = True,
        geometries: RouteGeometry = RouteGeometry.GEOJSON,
        overview: str = "full",
        continue_straight: Optional[bool] = None
    ) -> OSRMResponse:
        """
        Calculate route between coordinates.
        
        Args:
            coordinates: List of coordinates (minimum 2)
            profile: Routing profile
            alternatives: Whether to return alternative routes
            steps: Whether to return turn-by-turn instructions
            geometries: Geometry format
            overview: Level of detail in route geometry
            continue_straight: Force route to go straight at waypoints
            
        Returns:
            OSRM response with route information
            
        Raises:
            ValueError: If coordinates are invalid
            httpx.HTTPError: If OSRM request fails
        """
        if len(coordinates) < 2:
            raise ValueError("At least 2 coordinates are required")
        
        # Build coordinate string
        coord_string = ";".join(coord.to_osrm_format() for coord in coordinates)
        
        # Build URL
        url = f"{self.base_url}/route/v1/{profile.value}/{coord_string}"
        
        # Build query parameters
        params = {
            "alternatives": str(alternatives).lower(),
            "steps": str(steps).lower(),
            "geometries": geometries.value,
            "overview": overview
        }
        
        if continue_straight is not None:
            params["continue_straight"] = str(continue_straight).lower()
        
        try:
            self.logger.info(f"OSRM route request: {url} with params: {params}")
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("code") != "Ok":
                raise ValueError(f"OSRM error: {data.get('message', 'Unknown error')}")
            
            return self._parse_route_response(data)
            
        except httpx.HTTPError as e:
            self.logger.error(f"OSRM request failed: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error parsing OSRM response: {e}")
            raise
    
    async def table(
        self,
        coordinates: List[Coordinate],
        sources: Optional[List[int]] = None,
        destinations: Optional[List[int]] = None,
        profile: RouteProfile = RouteProfile.DRIVING
    ) -> Dict[str, Any]:
        """
        Calculate distance/duration matrix between coordinates.
        
        Args:
            coordinates: List of coordinates
            sources: Indices of source coordinates
            destinations: Indices of destination coordinates
            profile: Routing profile
            
        Returns:
            Distance/duration matrix
        """
        if len(coordinates) < 2:
            raise ValueError("At least 2 coordinates are required")
        
        coord_string = ";".join(coord.to_osrm_format() for coord in coordinates)
        url = f"{self.base_url}/table/v1/{profile.value}/{coord_string}"
        
        params = {}
        if sources:
            params["sources"] = ";".join(map(str, sources))
        if destinations:
            params["destinations"] = ";".join(map(str, destinations))
        
        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("code") != "Ok":
                raise ValueError(f"OSRM error: {data.get('message', 'Unknown error')}")
            
            return data
            
        except httpx.HTTPError as e:
            self.logger.error(f"OSRM table request failed: {e}")
            raise
    
    async def nearest(
        self,
        coordinate: Coordinate,
        number: int = 1,
        profile: RouteProfile = RouteProfile.DRIVING
    ) -> Dict[str, Any]:
        """
        Find nearest road segments to a coordinate.
        
        Args:
            coordinate: Target coordinate
            number: Number of nearest segments to return
            profile: Routing profile
            
        Returns:
            Nearest segments information
        """
        coord_string = coordinate.to_osrm_format()
        url = f"{self.base_url}/nearest/v1/{profile.value}/{coord_string}"
        
        params = {"number": number}
        
        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("code") != "Ok":
                raise ValueError(f"OSRM error: {data.get('message', 'Unknown error')}")
            
            return data
            
        except httpx.HTTPError as e:
            self.logger.error(f"OSRM nearest request failed: {e}")
            raise
    
    async def match(
        self,
        coordinates: List[Coordinate],
        timestamps: Optional[List[int]] = None,
        radiuses: Optional[List[int]] = None,
        profile: RouteProfile = RouteProfile.DRIVING
    ) -> Dict[str, Any]:
        """
        Match GPS coordinates to road network.
        
        Args:
            coordinates: List of GPS coordinates
            timestamps: Optional timestamps for each coordinate
            radiuses: Search radius for each coordinate
            profile: Routing profile
            
        Returns:
            Map-matched route
        """
        if len(coordinates) < 2:
            raise ValueError("At least 2 coordinates are required")
        
        coord_string = ";".join(coord.to_osrm_format() for coord in coordinates)
        url = f"{self.base_url}/match/v1/{profile.value}/{coord_string}"
        
        params = {}
        if timestamps:
            params["timestamps"] = ";".join(map(str, timestamps))
        if radiuses:
            params["radiuses"] = ";".join(map(str, radiuses))
        
        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("code") != "Ok":
                raise ValueError(f"OSRM error: {data.get('message', 'Unknown error')}")
            
            return data
            
        except httpx.HTTPError as e:
            self.logger.error(f"OSRM match request failed: {e}")
            raise
    
    def _parse_route_response(self, data: Dict[str, Any]) -> OSRMResponse:
        """
        Parse OSRM route response.
        
        Args:
            data: Raw OSRM response data
            
        Returns:
            Parsed OSRM response
        """
        routes = []
        
        for route_data in data.get("routes", []):
            legs = []
            
            for leg_data in route_data.get("legs", []):
                steps = []
                
                for step_data in leg_data.get("steps", []):
                    step = RouteStep(
                        distance=step_data.get("distance", 0),
                        duration=step_data.get("duration", 0),
                        geometry=step_data.get("geometry", ""),
                        name=step_data.get("name", ""),
                        instruction=step_data.get("maneuver", {}).get("instruction", "")
                    )
                    steps.append(step)
                
                leg = RouteLeg(
                    distance=leg_data.get("distance", 0),
                    duration=leg_data.get("duration", 0),
                    steps=steps
                )
                legs.append(leg)
            
            route = Route(
                distance=route_data.get("distance", 0),
                duration=route_data.get("duration", 0),
                geometry=route_data.get("geometry", ""),
                legs=legs,
                weight=route_data.get("weight"),
                weight_name=route_data.get("weight_name")
            )
            routes.append(route)
        
        return OSRMResponse(
            code=data.get("code", ""),
            routes=routes,
            waypoints=data.get("waypoints", []),
            message=data.get("message")
        )
    
    async def get_route_alternatives(
        self,
        origin: Coordinate,
        destination: Coordinate,
        max_alternatives: int = 3
    ) -> List[Route]:
        """
        Get multiple route alternatives between two points.
        
        Args:
            origin: Starting coordinate
            destination: Ending coordinate
            max_alternatives: Maximum number of alternatives
            
        Returns:
            List of route alternatives
        """
        response = await self.route(
            coordinates=[origin, destination],
            alternatives=True,
            steps=True
        )
        
        # Limit to requested number of alternatives
        return response.routes[:max_alternatives]
    
    async def calculate_route_matrix(
        self,
        origins: List[Coordinate],
        destinations: List[Coordinate]
    ) -> Dict[str, Any]:
        """
        Calculate distance/duration matrix between origins and destinations.
        
        Args:
            origins: List of origin coordinates
            destinations: List of destination coordinates
            
        Returns:
            Matrix with distances and durations
        """
        # Combine all coordinates
        all_coords = origins + destinations
        
        # Create source and destination indices
        source_indices = list(range(len(origins)))
        dest_indices = list(range(len(origins), len(all_coords)))
        
        return await self.table(
            coordinates=all_coords,
            sources=source_indices,
            destinations=dest_indices
        )


# Utility functions for coordinate conversion
def create_coordinate_from_dict(coord_dict: Dict[str, float]) -> Coordinate:
    """
    Create Coordinate from dictionary.
    
    Args:
        coord_dict: Dictionary with 'longitude' and 'latitude' keys
        
    Returns:
        Coordinate object
    """
    return Coordinate(
        longitude=coord_dict["longitude"],
        latitude=coord_dict["latitude"]
    )


def create_coordinates_from_addresses(addresses: List[str]) -> List[Coordinate]:
    """
    Convert addresses to coordinates using geocoding.
    
    Args:
        addresses: List of address strings
        
    Returns:
        List of coordinates
        
    Note:
        This is a placeholder. In production, integrate with a geocoding service
        like Google Maps, Mapbox, or Nominatim.
    """
    # Implement geocoding integration using Nominatim (OpenStreetMap)
    try:
        import requests
        from typing import List
        from app.schemas.location import Location
        
        # Use Nominatim for geocoding (OpenStreetMap)
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": query,
            "format": "json",
            "addressdetails": 1,
            "limit": 5,
            "countrycodes": "AR"  # Limit to Argentina
        }
        
        headers = {
            "User-Agent": "Kiro Route Optimizer/1.0"
        }
        
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        
        results = response.json()
        locations: List[Location] = []
        
        for result in results:
            location = Location(
                name=result.get("display_name", ""),
                latitude=float(result.get("lat", 0)),
                longitude=float(result.get("lon", 0)),
                address=result.get("address", {})
            )
            locations.append(location)
            
        logger.info(f"Geocoding completed for query '{query}'. Found {len(locations)} results.")
        return locations
        
    except Exception as e:
        logger.error(f"Error during geocoding: {e}")
        # Return empty list as fallback
        return []


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
