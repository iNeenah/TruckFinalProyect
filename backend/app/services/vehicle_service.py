"""
Vehicle service for fleet management operations.
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import HTTPException, status

from app.models.vehicle import Vehicle
from app.models.company import Company
from app.models.user import User, UserRole
from app.schemas.vehicle import VehicleCreate, VehicleUpdate, VehicleFuelCostCalculation
from app.validators.vehicle_validators import VehicleValidator


class VehicleService:
    """Service for vehicle management operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_vehicle(self, vehicle_data: VehicleCreate, current_user: User) -> Vehicle:
        """
        Create a new vehicle.
        
        Args:
            vehicle_data: Vehicle creation data
            current_user: Current authenticated user
            
        Returns:
            Created vehicle object
            
        Raises:
            HTTPException: If creation fails
        """
        # Check if company exists and user has access
        company = self.db.query(Company).filter(Company.id == vehicle_data.company_id).first()
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )
        
        # Check access permissions
        if current_user.role != UserRole.ADMIN and current_user.company_id != vehicle_data.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to create vehicles for this company"
            )
        
        # Validate vehicle data
        vehicle_dict = vehicle_data.dict()
        validated_data = VehicleValidator.validate_complete_vehicle(vehicle_dict)
        
        # Get compatibility warnings
        warnings = VehicleValidator.validate_vehicle_compatibility(vehicle_dict)
        if warnings:
            # Log warnings but don't block creation
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Vehicle compatibility warnings for {validated_data.get('license_plate')}: {warnings}")
        
        # Check if license plate already exists
        existing_vehicle = self.db.query(Vehicle).filter(
            Vehicle.license_plate == validated_data['license_plate']
        ).first()
        if existing_vehicle:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vehicle with this license plate already exists"
            )
        
        # Create vehicle with validated data
        db_vehicle = Vehicle(**validated_data)
        
        self.db.add(db_vehicle)
        self.db.commit()
        self.db.refresh(db_vehicle)
        
        return db_vehicle
    
    def get_vehicle(self, vehicle_id: UUID, current_user: User) -> Vehicle:
        """
        Get a vehicle by ID.
        
        Args:
            vehicle_id: Vehicle ID
            current_user: Current authenticated user
            
        Returns:
            Vehicle object
            
        Raises:
            HTTPException: If vehicle not found or access denied
        """
        vehicle = self.db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
        if not vehicle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehicle not found"
            )
        
        # Check access permissions
        if current_user.role != UserRole.ADMIN and current_user.company_id != vehicle.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this vehicle"
            )
        
        return vehicle
    
    def get_vehicles(
        self, 
        current_user: User,
        company_id: Optional[UUID] = None,
        is_active: Optional[bool] = None,
        fuel_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Get vehicles with filtering and pagination.
        
        Args:
            current_user: Current authenticated user
            company_id: Filter by company ID
            is_active: Filter by active status
            fuel_type: Filter by fuel type
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            Dictionary with vehicles and pagination info
        """
        query = self.db.query(Vehicle)
        
        # Apply access control
        if current_user.role != UserRole.ADMIN:
            # Non-admin users can only see their company's vehicles
            query = query.filter(Vehicle.company_id == current_user.company_id)
        elif company_id:
            # Admin users can filter by specific company
            query = query.filter(Vehicle.company_id == company_id)
        
        # Apply filters
        if is_active is not None:
            query = query.filter(Vehicle.is_active == is_active)
        
        if fuel_type:
            query = query.filter(Vehicle.fuel_type == fuel_type)
        
        # Get total count
        total = query.count()
        
        # Apply pagination and get results
        vehicles = query.offset(skip).limit(limit).all()
        
        return {
            "vehicles": vehicles,
            "total": total,
            "page": (skip // limit) + 1,
            "size": limit,
            "pages": (total + limit - 1) // limit
        }
    
    def update_vehicle(
        self, 
        vehicle_id: UUID, 
        vehicle_data: VehicleUpdate, 
        current_user: User
    ) -> Vehicle:
        """
        Update a vehicle.
        
        Args:
            vehicle_id: Vehicle ID
            vehicle_data: Vehicle update data
            current_user: Current authenticated user
            
        Returns:
            Updated vehicle object
            
        Raises:
            HTTPException: If update fails
        """
        vehicle = self.get_vehicle(vehicle_id, current_user)
        
        # Validate update data
        update_data = vehicle_data.dict(exclude_unset=True)
        if update_data:  # Only validate if there's data to update
            validated_data = VehicleValidator.validate_complete_vehicle(update_data)
            
            # Get compatibility warnings
            warnings = VehicleValidator.validate_vehicle_compatibility(update_data)
            if warnings:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Vehicle compatibility warnings for {vehicle.license_plate}: {warnings}")
            
            # Check if license plate is being changed and if it conflicts
            if 'license_plate' in validated_data and validated_data['license_plate'] != vehicle.license_plate:
                existing_vehicle = self.db.query(Vehicle).filter(
                    and_(
                        Vehicle.license_plate == validated_data['license_plate'],
                        Vehicle.id != vehicle_id
                    )
                ).first()
                if existing_vehicle:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Vehicle with this license plate already exists"
                    )
            
            # Update vehicle fields with validated data
            for field, value in validated_data.items():
                setattr(vehicle, field, value)
        
        self.db.commit()
        self.db.refresh(vehicle)
        
        return vehicle
    
    def delete_vehicle(self, vehicle_id: UUID, current_user: User) -> bool:
        """
        Delete a vehicle (soft delete by setting is_active=False).
        
        Args:
            vehicle_id: Vehicle ID
            current_user: Current authenticated user
            
        Returns:
            True if deleted successfully
            
        Raises:
            HTTPException: If deletion fails
        """
        vehicle = self.get_vehicle(vehicle_id, current_user)
        
        # Check if vehicle has associated routes
        from app.models.calculated_route import CalculatedRoute
        route_count = self.db.query(CalculatedRoute).filter(
            CalculatedRoute.vehicle_id == vehicle_id
        ).count()
        
        if route_count > 0:
            # Soft delete - keep for historical data
            vehicle.is_active = False
            self.db.commit()
        else:
            # Hard delete if no associated data
            self.db.delete(vehicle)
            self.db.commit()
        
        return True
    
    def get_company_vehicles(self, company_id: UUID, current_user: User) -> List[Vehicle]:
        """
        Get all vehicles for a specific company.
        
        Args:
            company_id: Company ID
            current_user: Current authenticated user
            
        Returns:
            List of vehicles
            
        Raises:
            HTTPException: If access denied
        """
        # Check access permissions
        if current_user.role != UserRole.ADMIN and current_user.company_id != company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this company's vehicles"
            )
        
        vehicles = self.db.query(Vehicle).filter(
            and_(
                Vehicle.company_id == company_id,
                Vehicle.is_active == True
            )
        ).all()
        
        return vehicles
    
    def calculate_fuel_cost(
        self, 
        calculation_data: VehicleFuelCostCalculation,
        current_user: User
    ) -> Dict[str, Any]:
        """
        Calculate fuel cost for a vehicle and distance.
        
        Args:
            calculation_data: Fuel cost calculation data
            current_user: Current authenticated user
            
        Returns:
            Fuel cost calculation result
            
        Raises:
            HTTPException: If calculation fails
        """
        vehicle = self.get_vehicle(calculation_data.vehicle_id, current_user)
        
        fuel_cost = vehicle.calculate_fuel_cost(
            calculation_data.distance_km,
            calculation_data.fuel_price_per_liter
        )
        
        fuel_needed = (calculation_data.distance_km / 100) * float(vehicle.fuel_consumption)
        
        return {
            "vehicle_id": str(vehicle.id),
            "distance_km": calculation_data.distance_km,
            "fuel_consumption": vehicle.fuel_consumption,
            "fuel_needed_liters": fuel_needed,
            "fuel_price_per_liter": calculation_data.fuel_price_per_liter,
            "total_fuel_cost": fuel_cost,
            "fuel_type": vehicle.fuel_type
        }
    
    def get_vehicle_statistics(self, current_user: User) -> Dict[str, Any]:
        """
        Get vehicle statistics for the user's company.
        
        Args:
            current_user: Current authenticated user
            
        Returns:
            Vehicle statistics
        """
        query = self.db.query(Vehicle)
        
        # Apply access control
        if current_user.role != UserRole.ADMIN:
            query = query.filter(Vehicle.company_id == current_user.company_id)
        
        total_vehicles = query.count()
        active_vehicles = query.filter(Vehicle.is_active == True).count()
        inactive_vehicles = total_vehicles - active_vehicles
        
        # Fuel type distribution
        fuel_type_stats = {}
        from app.models.vehicle import FuelType
        for fuel_type in FuelType:
            count = query.filter(Vehicle.fuel_type == fuel_type).count()
            fuel_type_stats[fuel_type.value] = count
        
        return {
            "total_vehicles": total_vehicles,
            "active_vehicles": active_vehicles,
            "inactive_vehicles": inactive_vehicles,
            "fuel_type_distribution": fuel_type_stats
        }
    
    def validate_vehicle_data(self, vehicle_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate vehicle data and return validation results with warnings.
        
        Args:
            vehicle_data: Vehicle data to validate
            
        Returns:
            Dictionary with validation results and warnings
        """
        try:
            validated_data = VehicleValidator.validate_complete_vehicle(vehicle_data)
            warnings = VehicleValidator.validate_vehicle_compatibility(vehicle_data)
            
            return {
                "valid": True,
                "validated_data": validated_data,
                "warnings": warnings,
                "errors": []
            }
        except HTTPException as e:
            error_detail = e.detail
            if isinstance(error_detail, dict) and "errors" in error_detail:
                errors = error_detail["errors"]
            else:
                errors = [str(error_detail)]
            
            return {
                "valid": False,
                "validated_data": {},
                "warnings": [],
                "errors": errors
            }