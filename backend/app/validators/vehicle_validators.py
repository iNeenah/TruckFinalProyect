"""
Vehicle-specific data validators.
"""
import re
from typing import List, Dict, Any, Optional
from decimal import Decimal
from fastapi import HTTPException, status

from app.models.vehicle import FuelType


class VehicleValidator:
    """Validator for vehicle data."""
    
    # Argentina license plate patterns
    ARGENTINA_PLATE_PATTERNS = [
        r'^[A-Z]{3}\d{3}$',  # Old format: ABC123
        r'^[A-Z]{2}\d{3}[A-Z]{2}$',  # New format: AB123CD
        r'^\d{3}[A-Z]{3}$',  # Alternative old format: 123ABC
    ]
    
    # Reasonable ranges for vehicle specifications
    FUEL_CONSUMPTION_RANGE = (5.0, 80.0)  # L/100km
    HEIGHT_RANGE = (1.5, 4.5)  # meters
    WIDTH_RANGE = (1.5, 3.0)   # meters
    LENGTH_RANGE = (3.0, 25.0)  # meters
    WEIGHT_RANGE = (500, 50000)  # kg
    YEAR_RANGE = (1980, 2030)
    
    @classmethod
    def validate_license_plate(cls, license_plate: str) -> str:
        """
        Validate Argentina license plate format.
        
        Args:
            license_plate: License plate to validate
            
        Returns:
            Normalized license plate
            
        Raises:
            HTTPException: If license plate is invalid
        """
        if not license_plate or not license_plate.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="License plate cannot be empty"
            )
        
        # Normalize: remove spaces, convert to uppercase
        normalized = license_plate.strip().upper().replace(' ', '').replace('-', '')
        
        # Check against Argentina patterns
        for pattern in cls.ARGENTINA_PLATE_PATTERNS:
            if re.match(pattern, normalized):
                return normalized
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Argentina license plate format. Expected formats: ABC123, AB123CD, or 123ABC"
        )
    
    @classmethod
    def validate_fuel_consumption(cls, consumption: Decimal) -> Decimal:
        """
        Validate fuel consumption value.
        
        Args:
            consumption: Fuel consumption in L/100km
            
        Returns:
            Validated consumption value
            
        Raises:
            HTTPException: If consumption is invalid
        """
        if consumption <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Fuel consumption must be greater than 0"
            )
        
        min_consumption, max_consumption = cls.FUEL_CONSUMPTION_RANGE
        if not (min_consumption <= float(consumption) <= max_consumption):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Fuel consumption must be between {min_consumption} and {max_consumption} L/100km"
            )
        
        return consumption
    
    @classmethod
    def validate_fuel_type(cls, fuel_type: str) -> FuelType:
        """
        Validate fuel type.
        
        Args:
            fuel_type: Fuel type string
            
        Returns:
            Validated FuelType enum
            
        Raises:
            HTTPException: If fuel type is invalid
        """
        try:
            return FuelType(fuel_type)
        except ValueError:
            valid_types = [ft.value for ft in FuelType]
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid fuel type. Must be one of: {', '.join(valid_types)}"
            )
    
    @classmethod
    def validate_dimensions(
        cls, 
        height: Optional[Decimal] = None,
        width: Optional[Decimal] = None,
        length: Optional[Decimal] = None
    ) -> Dict[str, Optional[Decimal]]:
        """
        Validate vehicle dimensions.
        
        Args:
            height: Vehicle height in meters
            width: Vehicle width in meters
            length: Vehicle length in meters
            
        Returns:
            Dictionary of validated dimensions
            
        Raises:
            HTTPException: If dimensions are invalid
        """
        validated = {}
        
        if height is not None:
            min_height, max_height = cls.HEIGHT_RANGE
            if not (min_height <= float(height) <= max_height):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Vehicle height must be between {min_height} and {max_height} meters"
                )
            validated['height'] = height
        
        if width is not None:
            min_width, max_width = cls.WIDTH_RANGE
            if not (min_width <= float(width) <= max_width):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Vehicle width must be between {min_width} and {max_width} meters"
                )
            validated['width'] = width
        
        if length is not None:
            min_length, max_length = cls.LENGTH_RANGE
            if not (min_length <= float(length) <= max_length):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Vehicle length must be between {min_length} and {max_length} meters"
                )
            validated['length'] = length
        
        return validated
    
    @classmethod
    def validate_weights(
        cls,
        max_weight: Optional[int] = None,
        empty_weight: Optional[int] = None
    ) -> Dict[str, Optional[int]]:
        """
        Validate vehicle weights.
        
        Args:
            max_weight: Maximum weight capacity in kg
            empty_weight: Empty vehicle weight in kg
            
        Returns:
            Dictionary of validated weights
            
        Raises:
            HTTPException: If weights are invalid
        """
        validated = {}
        min_weight, max_weight_limit = cls.WEIGHT_RANGE
        
        if max_weight is not None:
            if not (min_weight <= max_weight <= max_weight_limit):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Maximum weight must be between {min_weight} and {max_weight_limit} kg"
                )
            validated['max_weight'] = max_weight
        
        if empty_weight is not None:
            if not (min_weight <= empty_weight <= max_weight_limit):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Empty weight must be between {min_weight} and {max_weight_limit} kg"
                )
            validated['empty_weight'] = empty_weight
        
        # Cross-validation: empty weight should be less than max weight
        if (max_weight is not None and empty_weight is not None and 
            empty_weight >= max_weight):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty weight must be less than maximum weight"
            )
        
        return validated
    
    @classmethod
    def validate_year(cls, year: Optional[int] = None) -> Optional[int]:
        """
        Validate vehicle year.
        
        Args:
            year: Vehicle year
            
        Returns:
            Validated year
            
        Raises:
            HTTPException: If year is invalid
        """
        if year is None:
            return None
        
        min_year, max_year = cls.YEAR_RANGE
        if not (min_year <= year <= max_year):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Vehicle year must be between {min_year} and {max_year}"
            )
        
        return year
    
    @classmethod
    def validate_model_and_brand(cls, model: str, brand: Optional[str] = None) -> Dict[str, str]:
        """
        Validate vehicle model and brand.
        
        Args:
            model: Vehicle model
            brand: Vehicle brand
            
        Returns:
            Dictionary of validated model and brand
            
        Raises:
            HTTPException: If model/brand are invalid
        """
        if not model or not model.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vehicle model cannot be empty"
            )
        
        # Clean and validate model
        model = model.strip()
        if len(model) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vehicle model must be at least 2 characters long"
            )
        
        validated = {'model': model}
        
        # Validate brand if provided
        if brand:
            brand = brand.strip()
            if len(brand) < 2:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Vehicle brand must be at least 2 characters long"
                )
            validated['brand'] = brand
        
        return validated
    
    @classmethod
    def validate_complete_vehicle(cls, vehicle_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform complete validation of vehicle data.
        
        Args:
            vehicle_data: Dictionary of vehicle data
            
        Returns:
            Dictionary of validated vehicle data
            
        Raises:
            HTTPException: If any validation fails
        """
        validated = {}
        validation_errors = []
        
        try:
            # License plate validation
            if 'license_plate' in vehicle_data:
                validated['license_plate'] = cls.validate_license_plate(vehicle_data['license_plate'])
        except HTTPException as e:
            validation_errors.append(f"License plate: {e.detail}")
        
        try:
            # Model and brand validation
            if 'model' in vehicle_data:
                model_brand = cls.validate_model_and_brand(
                    vehicle_data['model'], 
                    vehicle_data.get('brand')
                )
                validated.update(model_brand)
        except HTTPException as e:
            validation_errors.append(f"Model/Brand: {e.detail}")
        
        try:
            # Year validation
            if 'year' in vehicle_data:
                validated['year'] = cls.validate_year(vehicle_data['year'])
        except HTTPException as e:
            validation_errors.append(f"Year: {e.detail}")
        
        try:
            # Fuel consumption validation
            if 'fuel_consumption' in vehicle_data:
                validated['fuel_consumption'] = cls.validate_fuel_consumption(
                    vehicle_data['fuel_consumption']
                )
        except HTTPException as e:
            validation_errors.append(f"Fuel consumption: {e.detail}")
        
        try:
            # Fuel type validation
            if 'fuel_type' in vehicle_data:
                validated['fuel_type'] = cls.validate_fuel_type(vehicle_data['fuel_type'])
        except HTTPException as e:
            validation_errors.append(f"Fuel type: {e.detail}")
        
        try:
            # Dimensions validation
            dimensions = cls.validate_dimensions(
                vehicle_data.get('height'),
                vehicle_data.get('width'),
                vehicle_data.get('length')
            )
            validated.update(dimensions)
        except HTTPException as e:
            validation_errors.append(f"Dimensions: {e.detail}")
        
        try:
            # Weights validation
            weights = cls.validate_weights(
                vehicle_data.get('max_weight'),
                vehicle_data.get('empty_weight')
            )
            validated.update(weights)
        except HTTPException as e:
            validation_errors.append(f"Weights: {e.detail}")
        
        try:
            # Notes validation
            if 'notes' in vehicle_data and vehicle_data['notes']:
                notes = vehicle_data['notes'].strip()
                if len(notes) > 1000:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Notes cannot exceed 1000 characters"
                    )
                validated['notes'] = notes
        except HTTPException as e:
            validation_errors.append(f"Notes: {e.detail}")
        
        # If there are validation errors, raise a comprehensive error
        if validation_errors:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Vehicle validation failed",
                    "errors": validation_errors
                }
            )
        
        return validated
    
    @classmethod
    def validate_fuel_efficiency_range(cls, fuel_consumption: Decimal, vehicle_type: Optional[str] = None) -> bool:
        """
        Validate fuel consumption against expected ranges for different vehicle types.
        
        Args:
            fuel_consumption: Fuel consumption in L/100km
            vehicle_type: Optional vehicle type for more specific validation
            
        Returns:
            True if consumption is within expected range
        """
        # Define expected ranges by vehicle type
        type_ranges = {
            'car': (5.0, 15.0),
            'van': (8.0, 20.0),
            'truck': (15.0, 50.0),
            'bus': (20.0, 80.0),
            'motorcycle': (3.0, 8.0)
        }
        
        if vehicle_type and vehicle_type.lower() in type_ranges:
            min_consumption, max_consumption = type_ranges[vehicle_type.lower()]
            return min_consumption <= float(fuel_consumption) <= max_consumption
        
        # Default range if no specific type
        return cls.FUEL_CONSUMPTION_RANGE[0] <= float(fuel_consumption) <= cls.FUEL_CONSUMPTION_RANGE[1]
    
    @classmethod
    def validate_vehicle_compatibility(cls, vehicle_data: Dict[str, Any]) -> List[str]:
        """
        Check for logical inconsistencies in vehicle data.
        
        Args:
            vehicle_data: Dictionary of vehicle data
            
        Returns:
            List of warning messages about potential issues
        """
        warnings = []
        
        # Check fuel type vs consumption compatibility
        if 'fuel_type' in vehicle_data and 'fuel_consumption' in vehicle_data:
            fuel_type = vehicle_data['fuel_type']
            consumption = float(vehicle_data['fuel_consumption'])
            
            # Diesel vehicles typically have better fuel efficiency
            if fuel_type in ['diesel_500', 'diesel_premium'] and consumption > 40:
                warnings.append("High fuel consumption for diesel vehicle - please verify")
            
            # Gasoline vehicles typically consume more
            if fuel_type == 'gasoline' and consumption < 8:
                warnings.append("Very low fuel consumption for gasoline vehicle - please verify")
        
        # Check dimensions consistency
        dimensions = ['height', 'width', 'length']
        dim_values = {dim: vehicle_data.get(dim) for dim in dimensions if vehicle_data.get(dim)}
        
        if len(dim_values) >= 2:
            # Check for unrealistic dimension ratios
            if 'height' in dim_values and 'width' in dim_values:
                if float(dim_values['height']) > float(dim_values['width']) * 2:
                    warnings.append("Vehicle height seems very high relative to width")
            
            if 'length' in dim_values and 'width' in dim_values:
                if float(dim_values['length']) < float(dim_values['width']):
                    warnings.append("Vehicle length is less than width - please verify")
        
        # Check weight consistency
        if 'max_weight' in vehicle_data and 'empty_weight' in vehicle_data:
            max_weight = vehicle_data['max_weight']
            empty_weight = vehicle_data['empty_weight']
            
            if max_weight and empty_weight:
                payload_capacity = max_weight - empty_weight
                if payload_capacity < max_weight * 0.1:  # Less than 10% payload capacity
                    warnings.append("Very low payload capacity relative to total weight")
        
        # Check year vs fuel consumption (newer vehicles should be more efficient)
        if 'year' in vehicle_data and 'fuel_consumption' in vehicle_data:
            year = vehicle_data['year']
            consumption = float(vehicle_data['fuel_consumption'])
            
            if year and year > 2015 and consumption > 25:
                warnings.append("High fuel consumption for a relatively new vehicle")
        
        return warnings