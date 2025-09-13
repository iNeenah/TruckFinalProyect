"""
Seed data for initial fuel prices and major tolls in Misiones/NEA region.
"""
from sqlalchemy.orm import Session
from datetime import date, datetime
from decimal import Decimal

from app.models.fuel_price import FuelPrice
from app.models.toll import Toll
from app.models.vehicle import FuelType


def create_initial_fuel_prices(db: Session):
    """Create initial fuel prices for NEA region."""
    
    # Current approximate fuel prices in Argentina (NEA region) - December 2024
    fuel_prices_data = [
        {
            "fuel_type": FuelType.DIESEL_500.value,
            "region": "NEA",
            "price_per_liter": Decimal("850.00"),
            "effective_date": date.today(),
            "source": "Initial seed data",
            "notes": "Approximate price for Diesel 500 in Northeast Argentina"
        },
        {
            "fuel_type": FuelType.DIESEL_PREMIUM.value,
            "region": "NEA",
            "price_per_liter": Decimal("920.00"),
            "effective_date": date.today(),
            "source": "Initial seed data",
            "notes": "Approximate price for Diesel Premium in Northeast Argentina"
        },
        {
            "fuel_type": FuelType.GASOLINE.value,
            "region": "NEA",
            "price_per_liter": Decimal("780.00"),
            "effective_date": date.today(),
            "source": "Initial seed data",
            "notes": "Approximate price for Gasoline in Northeast Argentina"
        }
    ]
    
    for price_data in fuel_prices_data:
        # Check if price already exists
        existing = db.query(FuelPrice).filter(
            FuelPrice.fuel_type == price_data["fuel_type"],
            FuelPrice.region == price_data["region"],
            FuelPrice.effective_date == price_data["effective_date"]
        ).first()
        
        if not existing:
            fuel_price = FuelPrice(**price_data)
            db.add(fuel_price)
    
    db.commit()
    print("✅ Initial fuel prices created")


def create_initial_tolls(db: Session):
    """Create initial toll data for major routes in Misiones and connecting routes."""
    
    # Major tolls on routes connecting Misiones with the rest of Argentina
    tolls_data = [
        # RN12 - Route connecting Misiones with Buenos Aires
        {
            "name": "Peaje Posadas",
            "longitude": -55.8961,
            "latitude": -27.3676,
            "route_code": "RN12",
            "km_marker": Decimal("1365.0"),
            "tariff": Decimal("450.00"),
            "direction": "both",
            "operator": "Autopistas del Sol",
            "notes": "Main toll entering/exiting Posadas"
        },
        {
            "name": "Peaje Candelaria",
            "longitude": -55.7442,
            "latitude": -27.4614,
            "route_code": "RN12",
            "km_marker": Decimal("1340.0"),
            "tariff": Decimal("380.00"),
            "direction": "both",
            "operator": "Autopistas del Sol",
            "notes": "Toll near Candelaria, Misiones"
        },
        {
            "name": "Peaje Oberá",
            "longitude": -55.1196,
            "latitude": -27.4858,
            "route_code": "RN14",
            "km_marker": Decimal("890.0"),
            "tariff": Decimal("420.00"),
            "direction": "both",
            "operator": "Vialidad Nacional",
            "notes": "Toll near Oberá, connecting to RN14"
        },
        
        # RN14 - Alternative route through Corrientes
        {
            "name": "Peaje Corrientes Norte",
            "longitude": -58.8344,
            "latitude": -27.4696,
            "route_code": "RN14",
            "km_marker": Decimal("780.0"),
            "tariff": Decimal("390.00"),
            "direction": "both",
            "operator": "Corredores Viales",
            "notes": "Northern access to Corrientes city"
        },
        {
            "name": "Peaje Paso de los Libres",
            "longitude": -57.0892,
            "latitude": -29.7133,
            "route_code": "RN14",
            "km_marker": Decimal("650.0"),
            "tariff": Decimal("360.00"),
            "direction": "both",
            "operator": "Corredores Viales",
            "notes": "Toll near Brazilian border"
        },
        
        # RN12 continuation towards Buenos Aires
        {
            "name": "Peaje Resistencia",
            "longitude": -59.0386,
            "latitude": -27.4514,
            "route_code": "RN12",
            "km_marker": Decimal("1200.0"),
            "tariff": Decimal("480.00"),
            "direction": "both",
            "operator": "Autopistas del Sol",
            "notes": "Major toll in Chaco province"
        },
        {
            "name": "Peaje Formosa",
            "longitude": -58.1781,
            "latitude": -26.1775,
            "route_code": "RN11",
            "km_marker": Decimal("1100.0"),
            "tariff": Decimal("410.00"),
            "direction": "both",
            "operator": "Vialidad Nacional",
            "notes": "Toll in Formosa province"
        },
        
        # Additional strategic tolls
        {
            "name": "Peaje Santa Ana",
            "longitude": -55.5731,
            "latitude": -27.3731,
            "route_code": "RP2",
            "km_marker": Decimal("45.0"),
            "tariff": Decimal("280.00"),
            "direction": "both",
            "operator": "Vialidad Provincial",
            "notes": "Provincial toll in Misiones"
        },
        {
            "name": "Peaje Iguazú",
            "longitude": -54.5735,
            "latitude": -25.6953,
            "route_code": "RN12",
            "km_marker": Decimal("1450.0"),
            "tariff": Decimal("520.00"),
            "direction": "both",
            "operator": "Autopistas del Sol",
            "notes": "Toll near Iguazu Falls, tourist area"
        }
    ]
    
    for toll_data in tolls_data:
        # Extract coordinates
        longitude = toll_data.pop("longitude")
        latitude = toll_data.pop("latitude")
        
        # Check if toll already exists at this location
        existing = db.query(Toll).filter(
            Toll.name == toll_data["name"]
        ).first()
        
        if not existing:
            toll = Toll(**toll_data)
            toll.set_coordinates(longitude, latitude)
            db.add(toll)
    
    db.commit()
    print("✅ Initial toll data created")


def create_seed_data(db: Session):
    """Create all seed data."""
    print("🌱 Creating seed data...")
    
    try:
        create_initial_fuel_prices(db)
        create_initial_tolls(db)
        print("✅ All seed data created successfully")
        
    except Exception as e:
        print(f"❌ Error creating seed data: {e}")
        db.rollback()
        raise


if __name__ == "__main__":
    # For running seed data creation directly
    from app.database import SessionLocal
    
    db = SessionLocal()
    try:
        create_seed_data(db)
    finally:
        db.close()