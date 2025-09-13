"""
Geocoding service for converting addresses to coordinates.
"""
import httpx
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from app.config import get_settings
from app.services.osrm_service import Coordinate

settings = get_settings()
logger = logging.getLogger(__name__)


class GeocodingProvider(Enum):
    """Supported geocoding providers."""
    NOMINATIM = "nominatim"
    MAPBOX = "mapbox"
    GOOGLE = "google"


@dataclass
class GeocodingResult:
    """Geocoding result."""
    address: str
    coordinate: Coordinate
    confidence: float
    place_type: str
    country: str
    region: str
    locality: str
    postal_code: Optional[str] = None
    street: Optional[str] = None
    house_number: Optional[str] = None


@dataclass
class ReverseGeocodingResult:
    """Reverse geocoding result."""
    coordinate: Coordinate
    address: str
    country: str
    region: str
    locality: str
    postal_code: Optional[str] = None
    street: Optional[str] = None
    house_number: Optional[str] = None


class GeocodingService:
    """Service for geocoding and reverse geocoding."""
    
    def __init__(self, provider: GeocodingProvider = GeocodingProvider.NOMINATIM):
        """
        Initialize geocoding service.
        
        Args:
            provider: Geocoding provider to use
        """
        self.provider = provider
        self.client = httpx.AsyncClient(timeout=10.0)
        self.logger = logging.getLogger(__name__)
        
        # Provider-specific configuration
        self._setup_provider()
    
    def _setup_provider(self):
        """Setup provider-specific configuration."""
        if self.provider == GeocodingProvider.NOMINATIM:
            self.base_url = "https://nominatim.openstreetmap.org"
            self.headers = {
                "User-Agent": "OptimizadorRutas/1.0 (contact@example.com)"
            }
        elif self.provider == GeocodingProvider.MAPBOX:
            self.base_url = "https://api.mapbox.com/geocoding/v5/mapbox.places"
            self.api_key = getattr(settings, 'mapbox_access_token', None)
            self.headers = {}
        elif self.provider == GeocodingProvider.GOOGLE:
            self.base_url = "https://maps.googleapis.com/maps/api/geocode/json"
            self.api_key = getattr(settings, 'google_maps_api_key', None)
            self.headers = {}
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.client.aclose()
    
    async def geocode(
        self,
        address: str,
        country_code: str = "AR",
        limit: int = 5,
        bounds: Optional[Tuple[float, float, float, float]] = None
    ) -> List[GeocodingResult]:
        """
        Geocode an address to coordinates.
        
        Args:
            address: Address to geocode
            country_code: Country code to limit search
            limit: Maximum number of results
            bounds: Bounding box (min_lon, min_lat, max_lon, max_lat)
            
        Returns:
            List of geocoding results
        """
        if self.provider == GeocodingProvider.NOMINATIM:
            return await self._geocode_nominatim(address, country_code, limit, bounds)
        elif self.provider == GeocodingProvider.MAPBOX:
            return await self._geocode_mapbox(address, country_code, limit, bounds)
        elif self.provider == GeocodingProvider.GOOGLE:
            return await self._geocode_google(address, country_code, limit, bounds)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    async def reverse_geocode(
        self,
        coordinate: Coordinate,
        language: str = "es"
    ) -> Optional[ReverseGeocodingResult]:
        """
        Reverse geocode coordinates to address.
        
        Args:
            coordinate: Coordinate to reverse geocode
            language: Language for results
            
        Returns:
            Reverse geocoding result or None
        """
        if self.provider == GeocodingProvider.NOMINATIM:
            return await self._reverse_geocode_nominatim(coordinate, language)
        elif self.provider == GeocodingProvider.MAPBOX:
            return await self._reverse_geocode_mapbox(coordinate, language)
        elif self.provider == GeocodingProvider.GOOGLE:
            return await self._reverse_geocode_google(coordinate, language)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    async def _geocode_nominatim(
        self,
        address: str,
        country_code: str,
        limit: int,
        bounds: Optional[Tuple[float, float, float, float]]
    ) -> List[GeocodingResult]:
        """Geocode using Nominatim (OpenStreetMap)."""
        params = {
            "q": address,
            "format": "json",
            "addressdetails": 1,
            "limit": limit,
            "countrycodes": country_code.lower()
        }
        
        if bounds:
            min_lon, min_lat, max_lon, max_lat = bounds
            params["viewbox"] = f"{min_lon},{max_lat},{max_lon},{min_lat}"
            params["bounded"] = 1
        
        try:
            response = await self.client.get(
                f"{self.base_url}/search",
                params=params,
                headers=self.headers
            )
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            for item in data:
                try:
                    coordinate = Coordinate(
                        longitude=float(item["lon"]),
                        latitude=float(item["lat"])
                    )
                    
                    address_parts = item.get("address", {})
                    
                    result = GeocodingResult(
                        address=item.get("display_name", ""),
                        coordinate=coordinate,
                        confidence=float(item.get("importance", 0.5)),
                        place_type=item.get("type", "unknown"),
                        country=address_parts.get("country", ""),
                        region=address_parts.get("state", ""),
                        locality=address_parts.get("city", address_parts.get("town", "")),
                        postal_code=address_parts.get("postcode"),
                        street=address_parts.get("road"),
                        house_number=address_parts.get("house_number")
                    )
                    results.append(result)
                    
                except (ValueError, KeyError) as e:
                    self.logger.warning(f"Error parsing Nominatim result: {e}")
                    continue
            
            return results
            
        except httpx.HTTPError as e:
            self.logger.error(f"Nominatim geocoding failed: {e}")
            return []
    
    async def _geocode_mapbox(
        self,
        address: str,
        country_code: str,
        limit: int,
        bounds: Optional[Tuple[float, float, float, float]]
    ) -> List[GeocodingResult]:
        """Geocode using Mapbox."""
        if not self.api_key:
            self.logger.error("Mapbox API key not configured")
            return []
        
        params = {
            "access_token": self.api_key,
            "country": country_code.lower(),
            "limit": limit,
            "language": "es"
        }
        
        if bounds:
            min_lon, min_lat, max_lon, max_lat = bounds
            params["bbox"] = f"{min_lon},{min_lat},{max_lon},{max_lat}"
        
        try:
            url = f"{self.base_url}/{address}.json"
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            for feature in data.get("features", []):
                try:
                    coordinates = feature["geometry"]["coordinates"]
                    coordinate = Coordinate(
                        longitude=coordinates[0],
                        latitude=coordinates[1]
                    )
                    
                    properties = feature.get("properties", {})
                    context = {item["id"].split(".")[0]: item["text"] 
                              for item in feature.get("context", [])}
                    
                    result = GeocodingResult(
                        address=feature.get("place_name", ""),
                        coordinate=coordinate,
                        confidence=properties.get("accuracy", 0.5),
                        place_type=feature.get("place_type", ["unknown"])[0],
                        country=context.get("country", ""),
                        region=context.get("region", ""),
                        locality=context.get("place", ""),
                        postal_code=context.get("postcode"),
                        street=context.get("address"),
                        house_number=properties.get("address")
                    )
                    results.append(result)
                    
                except (ValueError, KeyError) as e:
                    self.logger.warning(f"Error parsing Mapbox result: {e}")
                    continue
            
            return results
            
        except httpx.HTTPError as e:
            self.logger.error(f"Mapbox geocoding failed: {e}")
            return []
    
    async def _geocode_google(
        self,
        address: str,
        country_code: str,
        limit: int,
        bounds: Optional[Tuple[float, float, float, float]]
    ) -> List[GeocodingResult]:
        """Geocode using Google Maps."""
        if not self.api_key:
            self.logger.error("Google Maps API key not configured")
            return []
        
        params = {
            "address": address,
            "key": self.api_key,
            "region": country_code.lower(),
            "language": "es"
        }
        
        if bounds:
            min_lon, min_lat, max_lon, max_lat = bounds
            params["bounds"] = f"{min_lat},{min_lon}|{max_lat},{max_lon}"
        
        try:
            response = await self.client.get(self.base_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            if data.get("status") != "OK":
                self.logger.warning(f"Google geocoding error: {data.get('status')}")
                return []
            
            for result in data.get("results", [])[:limit]:
                try:
                    location = result["geometry"]["location"]
                    coordinate = Coordinate(
                        longitude=location["lng"],
                        latitude=location["lat"]
                    )
                    
                    address_components = {
                        comp["types"][0]: comp["long_name"]
                        for comp in result.get("address_components", [])
                    }
                    
                    geocoding_result = GeocodingResult(
                        address=result.get("formatted_address", ""),
                        coordinate=coordinate,
                        confidence=1.0,  # Google doesn't provide confidence scores
                        place_type=result.get("types", ["unknown"])[0],
                        country=address_components.get("country", ""),
                        region=address_components.get("administrative_area_level_1", ""),
                        locality=address_components.get("locality", ""),
                        postal_code=address_components.get("postal_code"),
                        street=address_components.get("route"),
                        house_number=address_components.get("street_number")
                    )
                    results.append(geocoding_result)
                    
                except (ValueError, KeyError) as e:
                    self.logger.warning(f"Error parsing Google result: {e}")
                    continue
            
            return results
            
        except httpx.HTTPError as e:
            self.logger.error(f"Google geocoding failed: {e}")
            return []
    
    async def _reverse_geocode_nominatim(
        self,
        coordinate: Coordinate,
        language: str
    ) -> Optional[ReverseGeocodingResult]:
        """Reverse geocode using Nominatim."""
        params = {
            "lat": coordinate.latitude,
            "lon": coordinate.longitude,
            "format": "json",
            "addressdetails": 1,
            "accept-language": language
        }
        
        try:
            response = await self.client.get(
                f"{self.base_url}/reverse",
                params=params,
                headers=self.headers
            )
            response.raise_for_status()
            
            data = response.json()
            
            if "error" in data:
                return None
            
            address_parts = data.get("address", {})
            
            return ReverseGeocodingResult(
                coordinate=coordinate,
                address=data.get("display_name", ""),
                country=address_parts.get("country", ""),
                region=address_parts.get("state", ""),
                locality=address_parts.get("city", address_parts.get("town", "")),
                postal_code=address_parts.get("postcode"),
                street=address_parts.get("road"),
                house_number=address_parts.get("house_number")
            )
            
        except httpx.HTTPError as e:
            self.logger.error(f"Nominatim reverse geocoding failed: {e}")
            return None
    
    async def _reverse_geocode_mapbox(
        self,
        coordinate: Coordinate,
        language: str
    ) -> Optional[ReverseGeocodingResult]:
        """Reverse geocode using Mapbox."""
        if not self.api_key:
            self.logger.error("Mapbox API key not configured")
            return None
        
        params = {
            "access_token": self.api_key,
            "language": language
        }
        
        try:
            url = f"{self.base_url}/{coordinate.longitude},{coordinate.latitude}.json"
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            features = data.get("features", [])
            
            if not features:
                return None
            
            feature = features[0]  # Take the first (most relevant) result
            context = {item["id"].split(".")[0]: item["text"] 
                      for item in feature.get("context", [])}
            
            return ReverseGeocodingResult(
                coordinate=coordinate,
                address=feature.get("place_name", ""),
                country=context.get("country", ""),
                region=context.get("region", ""),
                locality=context.get("place", ""),
                postal_code=context.get("postcode"),
                street=context.get("address"),
                house_number=feature.get("properties", {}).get("address")
            )
            
        except httpx.HTTPError as e:
            self.logger.error(f"Mapbox reverse geocoding failed: {e}")
            return None
    
    async def _reverse_geocode_google(
        self,
        coordinate: Coordinate,
        language: str
    ) -> Optional[ReverseGeocodingResult]:
        """Reverse geocode using Google Maps."""
        if not self.api_key:
            self.logger.error("Google Maps API key not configured")
            return None
        
        params = {
            "latlng": f"{coordinate.latitude},{coordinate.longitude}",
            "key": self.api_key,
            "language": language
        }
        
        try:
            response = await self.client.get(self.base_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("status") != "OK" or not data.get("results"):
                return None
            
            result = data["results"][0]  # Take the first result
            address_components = {
                comp["types"][0]: comp["long_name"]
                for comp in result.get("address_components", [])
            }
            
            return ReverseGeocodingResult(
                coordinate=coordinate,
                address=result.get("formatted_address", ""),
                country=address_components.get("country", ""),
                region=address_components.get("administrative_area_level_1", ""),
                locality=address_components.get("locality", ""),
                postal_code=address_components.get("postal_code"),
                street=address_components.get("route"),
                house_number=address_components.get("street_number")
            )
            
        except httpx.HTTPError as e:
            self.logger.error(f"Google reverse geocoding failed: {e}")
            return None
    
    async def geocode_argentina_address(
        self,
        address: str,
        province: Optional[str] = None
    ) -> List[GeocodingResult]:
        """
        Geocode address specifically in Argentina.
        
        Args:
            address: Address to geocode
            province: Optional province to limit search
            
        Returns:
            List of geocoding results
        """
        # Argentina bounds for better results
        argentina_bounds = (-73.5, -55.1, -53.6, -21.8)
        
        # Enhance address with country and province info
        enhanced_address = address
        if province:
            enhanced_address += f", {province}"
        enhanced_address += ", Argentina"
        
        return await self.geocode(
            address=enhanced_address,
            country_code="AR",
            bounds=argentina_bounds
        )
    
    async def geocode_misiones_address(
        self,
        address: str,
        city: Optional[str] = None
    ) -> List[GeocodingResult]:
        """
        Geocode address specifically in Misiones province.
        
        Args:
            address: Address to geocode
            city: Optional city to limit search
            
        Returns:
            List of geocoding results
        """
        # Misiones bounds for better results
        misiones_bounds = (-56.5, -28.1, -53.6, -25.2)
        
        # Enhance address with location info
        enhanced_address = address
        if city:
            enhanced_address += f", {city}"
        enhanced_address += ", Misiones, Argentina"
        
        return await self.geocode(
            address=enhanced_address,
            country_code="AR",
            bounds=misiones_bounds
        )


# Utility functions
async def quick_geocode(address: str) -> Optional[Coordinate]:
    """
    Quick geocoding function for simple use cases.
    
    Args:
        address: Address to geocode
        
    Returns:
        First coordinate result or None
    """
    async with GeocodingService() as geocoder:
        results = await geocoder.geocode_argentina_address(address)
        return results[0].coordinate if results else None


async def quick_reverse_geocode(coordinate: Coordinate) -> Optional[str]:
    """
    Quick reverse geocoding function for simple use cases.
    
    Args:
        coordinate: Coordinate to reverse geocode
        
    Returns:
        Address string or None
    """
    async with GeocodingService() as geocoder:
        result = await geocoder.reverse_geocode(coordinate)
        return result.address if result else None