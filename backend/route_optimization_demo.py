"""
Simplified demo of route optimization concepts.
"""
from decimal import Decimal
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Coordinate:
    """Geographic coordinate."""
    longitude: float
    latitude: float
    
    def to_osrm_format(self) -> str:
        return f"{self.longitude},{self.latitude}"


@dataclass
class Vehicle:
    """Vehicle information."""
    model: str
    fuel_consumption: Decimal  # L/100km
    fuel_type: str
    max_weight: int


@dataclass
class FuelCostInfo:
    """Fuel cost calculation result."""
    distance_km: float
    fuel_needed_liters: float
    fuel_price_per_liter: Decimal
    total_fuel_cost: Decimal


@dataclass
class TollInfo:
    """Toll information."""
    name: str
    cost: Decimal
    road_name: str


def calculate_fuel_cost(distance_km: float, vehicle: Vehicle, fuel_price: Decimal) -> FuelCostInfo:
    """Calculate fuel cost for a route."""
    fuel_needed = (distance_km / 100) * float(vehicle.fuel_consumption)
    total_cost = Decimal(str(fuel_needed)) * fuel_price
    
    return FuelCostInfo(
        distance_km=distance_km,
        fuel_needed_liters=fuel_needed,
        fuel_price_per_liter=fuel_price,
        total_fuel_cost=total_cost
    )


def get_vehicle_category(vehicle: Vehicle) -> str:
    """Determine vehicle category for toll calculation."""
    if vehicle.max_weight > 3500:
        return "truck"
    elif "moto" in vehicle.model.lower():
        return "motorcycle"
    else:
        return "car"


def get_toll_cost(toll_costs: dict, vehicle_category: str) -> Decimal:
    """Get toll cost for vehicle category."""
    return toll_costs.get(vehicle_category, Decimal('0'))


def main():
    """Run route optimization demo."""
    print("🚀 Route Optimization Demo")
    print("=" * 40)
    
    # Sample data
    origin = Coordinate(-55.8959, -27.3621)  # Posadas
    destination = Coordinate(-54.5735, -25.5951)  # Puerto Iguazú
    
    vehicle = Vehicle(
        model="Ford Transit",
        fuel_consumption=Decimal("18.5"),
        fuel_type="diesel_500",
        max_weight=3500
    )
    
    # Route data (simulated)
    routes = [
        {"name": "Fastest Route", "distance": 295.2, "duration": 225, "tolls": 1},
        {"name": "Alternative Route", "distance": 312.8, "duration": 250, "tolls": 0},
        {"name": "Scenic Route", "distance": 328.5, "duration": 280, "tolls": 2}
    ]
    
    fuel_price = Decimal("155.50")  # ARS per liter
    toll_costs = {
        "car": Decimal("45.00"),
        "truck": Decimal("90.00"),
        "motorcycle": Decimal("22.50")
    }
    
    print(f"📍 Origin: Posadas {origin.to_osrm_format()}")
    print(f"📍 Destination: Puerto Iguazú {destination.to_osrm_format()}")
    print(f"🚐 Vehicle: {vehicle.model} ({vehicle.fuel_consumption} L/100km)")
    print(f"⛽ Fuel Price: ARS ${fuel_price}/L")
    
    vehicle_category = get_vehicle_category(vehicle)
    toll_cost_per_toll = get_toll_cost(toll_costs, vehicle_category)
    
    print(f"🏷️  Vehicle Category: {vehicle_category}")
    print(f"🛣️  Toll Cost: ARS ${toll_cost_per_toll} per toll")
    
    print("\n📊 Route Analysis:")
    print(f"{'Route':<20} {'Distance':<10} {'Duration':<10} {'Fuel Cost':<12} {'Toll Cost':<12} {'Total Cost':<12}")
    print("-" * 90)
    
    best_route = None
    best_cost = float('inf')
    
    for route in routes:
        # Calculate fuel cost
        fuel_cost_info = calculate_fuel_cost(route["distance"], vehicle, fuel_price)
        
        # Calculate toll cost
        total_toll_cost = toll_cost_per_toll * route["tolls"]
        
        # Calculate total cost
        total_cost = fuel_cost_info.total_fuel_cost + total_toll_cost
        
        # Format duration
        hours = route["duration"] // 60
        minutes = route["duration"] % 60
        duration_str = f"{hours}h {minutes}m"
        
        print(f"{route['name']:<20} {route['distance']:<10.1f} {duration_str:<10} "
              f"${fuel_cost_info.total_fuel_cost:<11.2f} ${total_toll_cost:<11.2f} ${total_cost:<11.2f}")
        
        # Track best route
        if float(total_cost) < best_cost:
            best_cost = float(total_cost)
            best_route = route
            best_route['total_cost'] = total_cost
            best_route['fuel_cost'] = fuel_cost_info.total_fuel_cost
            best_route['toll_cost'] = total_toll_cost
    
    print("\n🎯 Recommended Route Analysis:")
    print(f"  Best Route: {best_route['name']}")
    print(f"  Distance: {best_route['distance']:.1f} km")
    print(f"  Fuel Cost: ARS ${best_route['fuel_cost']:.2f}")
    print(f"  Toll Cost: ARS ${best_route['toll_cost']:.2f}")
    print(f"  Total Cost: ARS ${best_route['total_cost']:.2f}")
    
    # Calculate savings vs fastest route
    fastest_route = routes[0]
    fastest_fuel_cost = calculate_fuel_cost(fastest_route["distance"], vehicle, fuel_price)
    fastest_toll_cost = toll_cost_per_toll * fastest_route["tolls"]
    fastest_total_cost = fastest_fuel_cost.total_fuel_cost + fastest_toll_cost
    
    if best_route['name'] != fastest_route['name']:
        savings = fastest_total_cost - best_route['total_cost']
        print(f"  Savings vs Fastest: ARS ${savings:.2f}")
    else:
        print("  This is already the fastest route!")
    
    print("\n💡 Optimization Insights:")
    
    # Fuel efficiency tips
    fuel_per_100km = float(vehicle.fuel_consumption)
    if fuel_per_100km > 20:
        print("  ⚠️  High fuel consumption - consider route optimization")
    elif fuel_per_100km < 10:
        print("  ✅ Excellent fuel efficiency")
    else:
        print("  👍 Good fuel efficiency")
    
    # Toll analysis
    total_tolls = sum(route["tolls"] for route in routes)
    if total_tolls > 0:
        print(f"  🛣️  {total_tolls} tolls detected across all routes")
        print(f"  💰 Potential toll savings: ARS ${toll_cost_per_toll * max(route['tolls'] for route in routes):.2f}")
    
    print("\n✅ Route optimization completed!")


if __name__ == "__main__":
    main()