"""
Example usage of OSRM service integration.
"""
import asyncio
import logging
from app.services.osrm_service import OSRMService, Coordinate, RouteProfile
from app.services.geocoding_service import GeocodingService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def basic_route_example():
    """Basic route calculation example."""
    print("=== Basic Route Calculation ===")
    
    async with OSRMService() as osrm:
        # Check if OSRM service is available
        if not await osrm.health_check():
            print("❌ OSRM service is not available")
            return
        
        print("✅ OSRM service is healthy")
        
        # Define coordinates (Posadas to Puerto Iguazú)
        posadas = Coordinate(-55.8959, -27.3621)
        puerto_iguazu = Coordinate(-54.5735, -25.5951)
        
        print(f"📍 Origin: Posadas {posadas.to_osrm_format()}")
        print(f"📍 Destination: Puerto Iguazú {puerto_iguazu.to_osrm_format()}")
        
        try:
            # Calculate route
            response = await osrm.route([posadas, puerto_iguazu])
            
            if response.routes:
                route = response.routes[0]
                distance_km = route.distance / 1000
                duration_min = route.duration / 60
                
                print(f"🛣️  Distance: {distance_km:.1f} km")
                print(f"⏱️  Duration: {duration_min:.1f} minutes")
                print(f"📊 Number of legs: {len(route.legs)}")
                
                # Show first few steps if available
                if route.legs and route.legs[0].steps:
                    print("\n📋 First few route steps:")
                    for i, step in enumerate(route.legs[0].steps[:3]):
                        print(f"  {i+1}. {step.instruction} on {step.name} ({step.distance:.0f}m)")
            else:
                print("❌ No route found")
                
        except Exception as e:
            print(f"❌ Error calculating route: {e}")


async def route_alternatives_example():
    """Route alternatives example."""
    print("\n=== Route Alternatives ===")
    
    async with OSRMService() as osrm:
        if not await osrm.health_check():
            print("❌ OSRM service is not available")
            return
        
        # Posadas to Oberá
        posadas = Coordinate(-55.8959, -27.3621)
        obera = Coordinate(-55.5377, -27.3671)
        
        print(f"📍 Finding alternatives from Posadas to Oberá")
        
        try:
            routes = await osrm.get_route_alternatives(
                posadas, obera, max_alternatives=3
            )
            
            print(f"🛣️  Found {len(routes)} route alternatives:")
            
            for i, route in enumerate(routes):
                distance_km = route.distance / 1000
                duration_min = route.duration / 60
                print(f"  Route {i+1}: {distance_km:.1f} km, {duration_min:.1f} min")
                
        except Exception as e:
            print(f"❌ Error getting alternatives: {e}")


async def distance_matrix_example():
    """Distance matrix calculation example."""
    print("\n=== Distance Matrix ===")
    
    async with OSRMService() as osrm:
        if not await osrm.health_check():
            print("❌ OSRM service is not available")
            return
        
        # Multiple cities in Misiones
        cities = {
            "Posadas": Coordinate(-55.8959, -27.3621),
            "Puerto Iguazú": Coordinate(-54.5735, -25.5951),
            "Oberá": Coordinate(-55.5377, -27.3671),
            "Eldorado": Coordinate(-54.7333, -26.8833)
        }
        
        city_names = list(cities.keys())
        coordinates = list(cities.values())
        
        print(f"📊 Calculating distance matrix for {len(cities)} cities")
        
        try:
            matrix = await osrm.table(coordinates)
            
            if matrix.get("code") == "Ok":
                durations = matrix["durations"]
                distances = matrix["distances"]
                
                print("\n⏱️  Duration matrix (minutes):")
                print("     ", end="")
                for name in city_names:
                    print(f"{name[:8]:>8}", end="")
                print()
                
                for i, from_city in enumerate(city_names):
                    print(f"{from_city[:8]:8}", end="")
                    for j, to_city in enumerate(city_names):
                        if i == j:
                            print(f"{'--':>8}", end="")
                        else:
                            duration_min = durations[i][j] / 60
                            print(f"{duration_min:8.0f}", end="")
                    print()
                
                print("\n🛣️  Distance matrix (km):")
                print("     ", end="")
                for name in city_names:
                    print(f"{name[:8]:>8}", end="")
                print()
                
                for i, from_city in enumerate(city_names):
                    print(f"{from_city[:8]:8}", end="")
                    for j, to_city in enumerate(city_names):
                        if i == j:
                            print(f"{'--':>8}", end="")
                        else:
                            distance_km = distances[i][j] / 1000
                            print(f"{distance_km:8.0f}", end="")
                    print()
            else:
                print(f"❌ Matrix calculation failed: {matrix.get('message')}")
                
        except Exception as e:
            print(f"❌ Error calculating matrix: {e}")


async def geocoding_integration_example():
    """Example of integrating geocoding with routing."""
    print("\n=== Geocoding + Routing Integration ===")
    
    # Note: This example uses Nominatim (free) but requires internet
    async with GeocodingService() as geocoder:
        async with OSRMService() as osrm:
            if not await osrm.health_check():
                print("❌ OSRM service is not available")
                return
            
            # Geocode addresses in Misiones
            addresses = [
                "Av. Mitre, Posadas, Misiones, Argentina",
                "Av. Victoria Aguirre, Puerto Iguazú, Misiones, Argentina"
            ]
            
            coordinates = []
            
            print("🔍 Geocoding addresses...")
            for address in addresses:
                try:
                    results = await geocoder.geocode_misiones_address(address)
                    if results:
                        coord = results[0].coordinate
                        coordinates.append(coord)
                        print(f"  ✅ {address[:50]}... -> {coord.to_osrm_format()}")
                    else:
                        print(f"  ❌ Could not geocode: {address}")
                except Exception as e:
                    print(f"  ❌ Geocoding error for {address}: {e}")
            
            if len(coordinates) >= 2:
                print(f"\n🛣️  Calculating route between geocoded addresses...")
                try:
                    response = await osrm.route(coordinates)
                    if response.routes:
                        route = response.routes[0]
                        distance_km = route.distance / 1000
                        duration_min = route.duration / 60
                        print(f"  Distance: {distance_km:.1f} km")
                        print(f"  Duration: {duration_min:.1f} minutes")
                    else:
                        print("  ❌ No route found between geocoded addresses")
                except Exception as e:
                    print(f"  ❌ Routing error: {e}")
            else:
                print("❌ Not enough valid coordinates for routing")


async def bounds_checking_example():
    """Example of coordinate bounds checking."""
    print("\n=== Coordinate Bounds Checking ===")
    
    from app.services.osrm_service import argentina_bounds_check, misiones_bounds_check
    
    test_coordinates = [
        ("Buenos Aires", Coordinate(-58.3816, -34.6037)),
        ("Posadas", Coordinate(-55.8959, -27.3621)),
        ("Puerto Iguazú", Coordinate(-54.5735, -25.5951)),
        ("São Paulo, Brazil", Coordinate(-46.6333, -23.5505)),
        ("Santiago, Chile", Coordinate(-70.6693, -33.4489)),
    ]
    
    print("🗺️  Checking coordinate bounds:")
    print(f"{'Location':<20} {'Argentina':<10} {'Misiones':<10} {'Coordinates'}")
    print("-" * 60)
    
    for name, coord in test_coordinates:
        argentina_ok = "✅" if argentina_bounds_check(coord) else "❌"
        misiones_ok = "✅" if misiones_bounds_check(coord) else "❌"
        coord_str = coord.to_osrm_format()
        
        print(f"{name:<20} {argentina_ok:<10} {misiones_ok:<10} {coord_str}")


async def main():
    """Run all examples."""
    print("🚀 OSRM Service Integration Examples")
    print("=" * 50)
    
    try:
        await basic_route_example()
        await route_alternatives_example()
        await distance_matrix_example()
        await bounds_checking_example()
        
        # Note: Geocoding example requires internet and may be slow
        # Uncomment to test:
        # await geocoding_integration_example()
        
    except KeyboardInterrupt:
        print("\n👋 Examples interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        logger.exception("Unexpected error in examples")
    
    print("\n✅ Examples completed!")


if __name__ == "__main__":
    asyncio.run(main())