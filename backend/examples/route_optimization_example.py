"""
Example usage of route optimization service.
"""
import asyncio
import logging
from decimal import Decimal
from unittest.mock import MagicMock

from app.services.route_optimization_service import (
    RouteOptimizationService,
    RoutePoint,
    RouteOptimizationRequest
)
from app.services.osrm_service import Coordinate
from app.models.vehicle import Vehicle, FuelType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_mock_db_session():
    """Create a mock database session for the example."""
    mock_db = MagicMock()
    
    # Mock vehicle
    mock_vehicle = MagicMock(spec=Vehicle)
    mock_vehicle.id = "example-vehicle-id"
    mock_vehicle.fuel_consumption = Decimal("18.5")  # L/100km
    mock_vehicle.fuel_type = FuelType.DIESEL_500
    mock_vehicle.max_weight = 3500
    mock_vehicle.model = "Ford Transit"
    mock_vehicle.brand = "Ford"
    
    # Mock fuel price
    mock_fuel_price = MagicMock()
    mock_fuel_price.price_per_liter = Decimal("155.50")
    mock_fuel_price.fuel_type = "diesel_500"
    mock_fuel_price.is_active = True
    
    # Mock toll
    mock_toll = MagicMock()
    mock_toll.id = "toll-rn12-posadas"
    mock_toll.name = "Peaje RN12 Posadas"
    mock_toll.longitude = -55.8959
    mock_toll.latitude = -27.3621
    mock_toll.cost_car = Decimal("45.00")
    mock_toll.cost_truck = Decimal("90.00")
    mock_toll.cost_motorcycle = Decimal("22.50")
    mock_toll.road_name = "RN12"
    mock_toll.is_active = True
    
    # Configure mock queries
    def mock_query_side_effect(model):
        mock_query = MagicMock()
        if model == Vehicle:
            mock_query.filter.return_value.first.return_value = mock_vehicle
        elif hasattr(model, '__name__') and 'FuelPrice' in model.__name__:
            mock_query.filter.return_value.order_by.return_value.first.return_value = mock_fuel_price
        elif hasattr(model, '__name__') and 'Toll' in model.__name__:
            mock_query.filter.return_value.all.return_value = [mock_toll]
        return mock_query
    
    mock_db.query.side_effect = mock_query_side_effect
    
    return mock_db


async def basic_route_optimization_example():
    """Basic route optimization example."""
    print("=== Basic Route Optimization ===")
    
    # Create mock database session
    mock_db = create_mock_db_session()
    
    # Create route optimization service
    service = RouteOptimizationService(mock_db)
    
    # Define route points
    origin = RoutePoint(
        coordinate=Coordinate(-55.8959, -27.3621),  # Posadas
        address="Av. Mitre 1234, Posadas, Misiones",
        name="Depósito Central"
    )
    
    destination = RoutePoint(
        coordinate=Coordinate(-54.5735, -25.5951),  # Puerto Iguazú
        address="Av. Victoria Aguirre 567, Puerto Iguazú, Misiones",
        name="Cliente Puerto Iguazú"
    )
    
    # Create optimization request
    request = RouteOptimizationRequest(
        origin=origin,
        destination=destination,
        vehicle_id="example-vehicle-id",
        avoid_tolls=False,
        max_alternatives=3
    )
    
    print(f"📍 Origin: {origin.name} ({origin.coordinate.to_osrm_format()})")
    print(f"📍 Destination: {destination.name} ({destination.coordinate.to_osrm_format()})")
    print(f"🚐 Vehicle: Ford Transit (18.5 L/100km)")
    
    try:
        # Note: This would normally require a running OSRM service
        # For this example, we'll simulate the optimization process
        print("\n🔄 Optimizing route...")
        print("⚠️  Note: This example simulates route optimization without OSRM")
        
        # Simulate route optimization results
        print("\n✅ Route optimization completed!")
        print("\n📊 Results:")
        print("  Route 1 (Fastest):")
        print("    - Distance: 295.2 km")
        print("    - Duration: 3h 45min")
        print("    - Fuel cost: ARS $847.50 (54.6L × $155.50/L)")
        print("    - Toll cost: ARS $45.00 (1 toll)")
        print("    - Total cost: ARS $892.50")
        
        print("\n  Route 2 (Alternative):")
        print("    - Distance: 312.8 km")
        print("    - Duration: 4h 10min")
        print("    - Fuel cost: ARS $897.20 (57.9L × $155.50/L)")
        print("    - Toll cost: ARS $0.00 (toll-free)")
        print("    - Total cost: ARS $897.20")
        
        print("\n🎯 Recommended Route: Route 1 (Fastest)")
        print("💰 Estimated Savings: ARS $4.70 vs Alternative")
        
    except Exception as e:
        print(f"❌ Error during optimization: {e}")


async def fuel_cost_calculation_example():
    """Example of fuel cost calculation."""
    print("\n=== Fuel Cost Calculation ===")
    
    mock_db = create_mock_db_session()
    service = RouteOptimizationService(mock_db)
    
    # Mock vehicle data
    mock_vehicle = MagicMock()
    mock_vehicle.fuel_consumption = Decimal("18.5")
    mock_vehicle.fuel_type = FuelType.DIESEL_500
    
    distances = [50, 100, 200, 500]  # km
    fuel_price = Decimal("155.50")   # ARS per liter
    
    print(f"🚐 Vehicle consumption: 18.5 L/100km")
    print(f"⛽ Fuel price: ARS $155.50/L")
    print("\n📊 Fuel cost by distance:")
    print(f"{'Distance (km)':<15} {'Fuel (L)':<10} {'Cost (ARS)':<12}")
    print("-" * 40)
    
    for distance in distances:
        fuel_cost_info = service._calculate_fuel_cost(distance, mock_vehicle, fuel_price)
        
        print(f"{distance:<15} {fuel_cost_info.fuel_needed_liters:<10.1f} ${fuel_cost_info.total_fuel_cost:<11.2f}")


async def vehicle_category_example():
    """Example of vehicle categorization for tolls."""
    print("\n=== Vehicle Categorization ===")
    
    mock_db = create_mock_db_session()
    service = RouteOptimizationService(mock_db)
    
    # Different vehicle types
    vehicles = [
        {"model": "Toyota Corolla", "max_weight": 1500, "expected": "car"},
        {"model": "Ford Transit", "max_weight": 3500, "expected": "car"},
        {"model": "Mercedes Sprinter", "max_weight": 5000, "expected": "truck"},
        {"model": "Honda Moto", "max_weight": 200, "expected": "motorcycle"},
        {"model": "Yamaha Scooter", "max_weight": 150, "expected": "motorcycle"},
    ]
    
    print("🚗 Vehicle categorization for toll calculation:")
    print(f"{'Vehicle':<20} {'Weight (kg)':<12} {'Category':<12} {'Expected':<12}")
    print("-" * 60)
    
    for vehicle_data in vehicles:
        mock_vehicle = MagicMock()
        mock_vehicle.model = vehicle_data["model"]
        mock_vehicle.max_weight = vehicle_data["max_weight"]
        
        category = service._get_vehicle_category(mock_vehicle)
        status = "✅" if category == vehicle_data["expected"] else "❌"
        
        print(f"{vehicle_data['model']:<20} {vehicle_data['max_weight']:<12} {category:<12} {vehicle_data['expected']:<12} {status}")


async def toll_cost_example():
    """Example of toll cost calculation."""
    print("\n=== Toll Cost Calculation ===")
    
    mock_db = create_mock_db_session()
    service = RouteOptimizationService(mock_db)
    
    # Mock toll
    mock_toll = MagicMock()
    mock_toll.name = "Peaje RN12 Posadas"
    mock_toll.cost_car = Decimal("45.00")
    mock_toll.cost_truck = Decimal("90.00")
    mock_toll.cost_motorcycle = Decimal("22.50")
    
    # Different vehicles
    vehicles = [
        {"name": "Toyota Corolla", "max_weight": 1500, "model": "Corolla"},
        {"name": "Ford Transit", "max_weight": 3500, "model": "Transit"},
        {"name": "Mercedes Truck", "max_weight": 8000, "model": "Actros"},
        {"name": "Honda Motorcycle", "max_weight": 200, "model": "Honda Moto"},
    ]
    
    print(f"🛣️  Toll: {mock_toll.name}")
    print(f"{'Vehicle':<20} {'Category':<12} {'Toll Cost (ARS)':<15}")
    print("-" * 50)
    
    for vehicle_data in vehicles:
        mock_vehicle = MagicMock()
        mock_vehicle.model = vehicle_data["model"]
        mock_vehicle.max_weight = vehicle_data["max_weight"]
        
        category = service._get_vehicle_category(mock_vehicle)
        cost = service._get_toll_cost_for_vehicle(mock_toll, mock_vehicle)
        
        print(f"{vehicle_data['name']:<20} {category:<12} ${cost:<14.2f}")


async def default_fuel_prices_example():
    """Example of default fuel prices."""
    print("\n=== Default Fuel Prices ===")
    
    mock_db = create_mock_db_session()
    service = RouteOptimizationService(mock_db)
    
    fuel_types = ["diesel_500", "diesel_premium", "gasoline", "unknown_fuel"]
    
    print("⛽ Default fuel prices (when current prices unavailable):")
    print(f"{'Fuel Type':<15} {'Price (ARS/L)':<15}")
    print("-" * 32)
    
    for fuel_type in fuel_types:
        price = service._get_default_fuel_price(fuel_type)
        print(f"{fuel_type:<15} ${price:<14.2f}")


async def geocoding_simulation_example():
    """Example of geocoding integration (simulated)."""
    print("\n=== Geocoding Integration (Simulated) ===")
    
    addresses = [
        "Av. Mitre 1234, Posadas, Misiones",
        "Av. Victoria Aguirre 567, Puerto Iguazú, Misiones",
        "Ruta Nacional 12 Km 1456, Oberá, Misiones",
        "Centro, Eldorado, Misiones"
    ]
    
    print("🔍 Address geocoding simulation:")
    print(f"{'Address':<40} {'Coordinates':<20} {'Status'}")
    print("-" * 70)
    
    # Simulated coordinates for Misiones locations
    simulated_coords = [
        (-55.8959, -27.3621),  # Posadas
        (-54.5735, -25.5951),  # Puerto Iguazú
        (-55.5377, -27.3671),  # Oberá
        (-54.7333, -26.8833),  # Eldorado
    ]
    
    for i, address in enumerate(addresses):
        if i < len(simulated_coords):
            lon, lat = simulated_coords[i]
            coord_str = f"{lon:.4f}, {lat:.4f}"
            status = "✅ Found"
        else:
            coord_str = "N/A"
            status = "❌ Not found"
        
        print(f"{address[:39]:<40} {coord_str:<20} {status}")


async def route_statistics_example():
    """Example of route statistics."""
    print("\n=== Route Statistics Example ===")
    
    mock_db = create_mock_db_session()
    service = RouteOptimizationService(mock_db)
    
    # Mock statistics data
    mock_db.query.return_value.count.return_value = 25
    
    mock_stats = MagicMock()
    mock_stats.total_distance = 2500.0
    mock_stats.total_savings = 1250.0
    mock_stats.avg_savings = 50.0
    
    mock_db.query.return_value.with_entities.return_value.first.return_value = mock_stats
    
    stats = await service.get_route_statistics()
    
    print("📊 Route calculation statistics:")
    print(f"  Total routes calculated: {stats['total_routes']}")
    print(f"  Total distance: {stats['total_distance_km']:.1f} km")
    print(f"  Total savings: ARS ${stats['total_savings']:.2f}")
    print(f"  Average savings per route: ARS ${stats['average_savings']:.2f}")


async def main():
    """Run all examples."""
    print("🚀 Route Optimization Service Examples")
    print("=" * 50)
    
    try:
        await basic_route_optimization_example()
        await fuel_cost_calculation_example()
        await vehicle_category_example()
        await toll_cost_example()
        await default_fuel_prices_example()
        await geocoding_simulation_example()
        await route_statistics_example()
        
    except KeyboardInterrupt:
        print("\n👋 Examples interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        logger.exception("Unexpected error in examples")
    
    print("\n✅ Examples completed!")
    print("\n💡 Note: These examples use simulated data.")
    print("   In production, connect to real database and OSRM service.")


if __name__ == "__main__":
    asyncio.run(main())