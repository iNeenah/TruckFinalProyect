"""
Tests for vehicle validators.
"""
import pytest
from decimal import Decimal
from fastapi import HTTPException

from app.validators.vehicle_validators import VehicleValidator
from app.models.vehicle import FuelType


class TestVehicleValidator:
    """Test cases for VehicleValidator."""
    
    def test_validate_license_plate_valid_formats(self):
        """Test valid license plate formats."""
        # Old format
        assert VehicleValidator.validate_license_plate("ABC123") == "ABC123"
        assert VehicleValidator.validate_license_plate("abc123") == "ABC123"
        assert VehicleValidator.validate_license_plate("ABC 123") == "ABC123"
        
        # New format
        assert VehicleValidator.validate_license_plate("AB123CD") == "AB123CD"
        assert VehicleValidator.validate_license_plate("ab123cd") == "AB123CD"
        assert VehicleValidator.validate_license_plate("AB 123 CD") == "AB123CD"
        
        # Alternative format
        assert VehicleValidator.validate_license_plate("123ABC") == "123ABC"
        assert VehicleValidator.validate_license_plate("123abc") == "123ABC"
        assert VehicleValidator.validate_license_plate("123 ABC") == "123ABC"
    
    def test_validate_license_plate_invalid_formats(self):
        """Test invalid license plate formats."""
        invalid_plates = [
            "",
            "   ",
            "AB12",
            "ABCD123",
            "AB1234CD",
            "123ABCD",
            "12ABC3",
            "A1B2C3"
        ]
        
        for plate in invalid_plates:
            with pytest.raises(HTTPException) as exc_info:
                VehicleValidator.validate_license_plate(plate)
            assert exc_info.value.status_code == 400
    
    def test_validate_fuel_consumption_valid(self):
        """Test valid fuel consumption values."""
        valid_consumptions = [
            Decimal("10.5"),
            Decimal("25.0"),
            Decimal("50.75"),
            Decimal("5.0"),
            Decimal("80.0")
        ]
        
        for consumption in valid_consumptions:
            result = VehicleValidator.validate_fuel_consumption(consumption)
            assert result == consumption
    
    def test_validate_fuel_consumption_invalid(self):
        """Test invalid fuel consumption values."""
        invalid_consumptions = [
            Decimal("0"),
            Decimal("-5.0"),
            Decimal("100.0"),
            Decimal("4.9"),
            Decimal("80.1")
        ]
        
        for consumption in invalid_consumptions:
            with pytest.raises(HTTPException) as exc_info:
                VehicleValidator.validate_fuel_consumption(consumption)
            assert exc_info.value.status_code == 400
    
    def test_validate_fuel_type_valid(self):
        """Test valid fuel types."""
        assert VehicleValidator.validate_fuel_type("diesel_500") == FuelType.DIESEL_500
        assert VehicleValidator.validate_fuel_type("diesel_premium") == FuelType.DIESEL_PREMIUM
        assert VehicleValidator.validate_fuel_type("gasoline") == FuelType.GASOLINE
    
    def test_validate_fuel_type_invalid(self):
        """Test invalid fuel types."""
        invalid_types = ["diesel", "gas", "electric", "hybrid", ""]
        
        for fuel_type in invalid_types:
            with pytest.raises(HTTPException) as exc_info:
                VehicleValidator.validate_fuel_type(fuel_type)
            assert exc_info.value.status_code == 400
    
    def test_validate_dimensions_valid(self):
        """Test valid vehicle dimensions."""
        result = VehicleValidator.validate_dimensions(
            height=Decimal("2.5"),
            width=Decimal("2.0"),
            length=Decimal("10.0")
        )
        
        assert result["height"] == Decimal("2.5")
        assert result["width"] == Decimal("2.0")
        assert result["length"] == Decimal("10.0")
    
    def test_validate_dimensions_invalid(self):
        """Test invalid vehicle dimensions."""
        # Invalid height
        with pytest.raises(HTTPException):
            VehicleValidator.validate_dimensions(height=Decimal("5.0"))
        
        # Invalid width
        with pytest.raises(HTTPException):
            VehicleValidator.validate_dimensions(width=Decimal("4.0"))
        
        # Invalid length
        with pytest.raises(HTTPException):
            VehicleValidator.validate_dimensions(length=Decimal("30.0"))
    
    def test_validate_weights_valid(self):
        """Test valid vehicle weights."""
        result = VehicleValidator.validate_weights(
            max_weight=5000,
            empty_weight=2000
        )
        
        assert result["max_weight"] == 5000
        assert result["empty_weight"] == 2000
    
    def test_validate_weights_invalid(self):
        """Test invalid vehicle weights."""
        # Empty weight >= max weight
        with pytest.raises(HTTPException):
            VehicleValidator.validate_weights(max_weight=2000, empty_weight=2000)
        
        # Weight out of range
        with pytest.raises(HTTPException):
            VehicleValidator.validate_weights(max_weight=100000)
    
    def test_validate_year_valid(self):
        """Test valid vehicle years."""
        assert VehicleValidator.validate_year(2020) == 2020
        assert VehicleValidator.validate_year(1990) == 1990
        assert VehicleValidator.validate_year(None) is None
    
    def test_validate_year_invalid(self):
        """Test invalid vehicle years."""
        invalid_years = [1970, 2040, 0, -2000]
        
        for year in invalid_years:
            with pytest.raises(HTTPException):
                VehicleValidator.validate_year(year)
    
    def test_validate_model_and_brand_valid(self):
        """Test valid model and brand."""
        result = VehicleValidator.validate_model_and_brand("Sprinter", "Mercedes-Benz")
        assert result["model"] == "Sprinter"
        assert result["brand"] == "Mercedes-Benz"
        
        result = VehicleValidator.validate_model_and_brand("Transit")
        assert result["model"] == "Transit"
        assert "brand" not in result
    
    def test_validate_model_and_brand_invalid(self):
        """Test invalid model and brand."""
        # Empty model
        with pytest.raises(HTTPException):
            VehicleValidator.validate_model_and_brand("")
        
        # Short model
        with pytest.raises(HTTPException):
            VehicleValidator.validate_model_and_brand("A")
        
        # Short brand
        with pytest.raises(HTTPException):
            VehicleValidator.validate_model_and_brand("Transit", "A")
    
    def test_validate_complete_vehicle_valid(self):
        """Test complete vehicle validation with valid data."""
        vehicle_data = {
            "license_plate": "ABC123",
            "model": "Sprinter",
            "brand": "Mercedes-Benz",
            "year": 2020,
            "fuel_consumption": Decimal("15.5"),
            "fuel_type": "diesel_500",
            "height": Decimal("2.5"),
            "width": Decimal("2.0"),
            "length": Decimal("6.0"),
            "max_weight": 3500,
            "empty_weight": 2000,
            "notes": "Company delivery van"
        }
        
        result = VehicleValidator.validate_complete_vehicle(vehicle_data)
        
        assert result["license_plate"] == "ABC123"
        assert result["model"] == "Sprinter"
        assert result["brand"] == "Mercedes-Benz"
        assert result["year"] == 2020
        assert result["fuel_consumption"] == Decimal("15.5")
        assert result["fuel_type"] == FuelType.DIESEL_500
        assert result["height"] == Decimal("2.5")
        assert result["width"] == Decimal("2.0")
        assert result["length"] == Decimal("6.0")
        assert result["max_weight"] == 3500
        assert result["empty_weight"] == 2000
        assert result["notes"] == "Company delivery van"
    
    def test_validate_complete_vehicle_partial_data(self):
        """Test complete vehicle validation with partial data."""
        vehicle_data = {
            "license_plate": "AB123CD",
            "model": "Transit",
            "fuel_consumption": Decimal("12.0"),
            "fuel_type": "diesel_premium"
        }
        
        result = VehicleValidator.validate_complete_vehicle(vehicle_data)
        
        assert result["license_plate"] == "AB123CD"
        assert result["model"] == "Transit"
        assert result["fuel_consumption"] == Decimal("12.0")
        assert result["fuel_type"] == FuelType.DIESEL_PREMIUM
        assert "brand" not in result
        assert "year" not in result
    
    def test_validate_complete_vehicle_multiple_errors(self):
        """Test complete vehicle validation with multiple errors."""
        vehicle_data = {
            "license_plate": "INVALID",
            "model": "",
            "fuel_consumption": Decimal("0"),
            "fuel_type": "invalid_fuel",
            "height": Decimal("10.0"),
            "max_weight": 0
        }
        
        with pytest.raises(HTTPException) as exc_info:
            VehicleValidator.validate_complete_vehicle(vehicle_data)
        
        assert exc_info.value.status_code == 400
        error_detail = exc_info.value.detail
        assert isinstance(error_detail, dict)
        assert "errors" in error_detail
        assert len(error_detail["errors"]) > 1
    
    def test_validate_fuel_efficiency_range(self):
        """Test fuel efficiency range validation."""
        # Test with vehicle type
        assert VehicleValidator.validate_fuel_efficiency_range(Decimal("10.0"), "car") == True
        assert VehicleValidator.validate_fuel_efficiency_range(Decimal("25.0"), "truck") == True
        assert VehicleValidator.validate_fuel_efficiency_range(Decimal("50.0"), "car") == False
        
        # Test without vehicle type (default range)
        assert VehicleValidator.validate_fuel_efficiency_range(Decimal("15.0")) == True
        assert VehicleValidator.validate_fuel_efficiency_range(Decimal("100.0")) == False
    
    def test_validate_vehicle_compatibility_warnings(self):
        """Test vehicle compatibility warnings."""
        # High consumption for diesel
        vehicle_data = {
            "fuel_type": "diesel_500",
            "fuel_consumption": Decimal("45.0")
        }
        warnings = VehicleValidator.validate_vehicle_compatibility(vehicle_data)
        assert any("High fuel consumption for diesel" in w for w in warnings)
        
        # Low consumption for gasoline
        vehicle_data = {
            "fuel_type": "gasoline",
            "fuel_consumption": Decimal("5.0")
        }
        warnings = VehicleValidator.validate_vehicle_compatibility(vehicle_data)
        assert any("Very low fuel consumption for gasoline" in w for w in warnings)
        
        # Dimension inconsistencies
        vehicle_data = {
            "height": Decimal("4.0"),
            "width": Decimal("1.8")
        }
        warnings = VehicleValidator.validate_vehicle_compatibility(vehicle_data)
        assert any("height seems very high" in w for w in warnings)
        
        # Weight inconsistencies
        vehicle_data = {
            "max_weight": 1000,
            "empty_weight": 950
        }
        warnings = VehicleValidator.validate_vehicle_compatibility(vehicle_data)
        assert any("Very low payload capacity" in w for w in warnings)
        
        # Year vs consumption
        vehicle_data = {
            "year": 2020,
            "fuel_consumption": Decimal("30.0")
        }
        warnings = VehicleValidator.validate_vehicle_compatibility(vehicle_data)
        assert any("High fuel consumption for a relatively new vehicle" in w for w in warnings)