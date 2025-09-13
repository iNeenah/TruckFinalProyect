"""
Vehicle management API endpoints.
"""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.vehicle import (
    VehicleCreate, 
    VehicleUpdate, 
    VehicleResponse, 
    VehicleListResponse,
    VehicleFuelCostCalculation,
    VehicleFuelCostResponse
)
from app.services.vehicle_service import VehicleService
from app.auth.dependencies import get_current_active_user
from app.auth.decorators import require_vehicle_access
from app.models.user import User

router = APIRouter(prefix="/vehicles", tags=["vehicles"])


@router.post("/", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED)
async def create_vehicle(
    vehicle_data: VehicleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_vehicle_access())
):
    """
    Create a new vehicle.
    
    Creates a new vehicle in the fleet management system.
    """
    vehicle_service = VehicleService(db)
    vehicle = vehicle_service.create_vehicle(vehicle_data, current_user)
    return VehicleResponse.from_orm(vehicle)


@router.get("/", response_model=VehicleListResponse)
async def get_vehicles(
    company_id: Optional[UUID] = Query(None, description="Filter by company ID"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    fuel_type: Optional[str] = Query(None, description="Filter by fuel type"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_vehicle_access())
):
    """
    Get vehicles with filtering and pagination.
    
    Returns a paginated list of vehicles with optional filtering.
    """
    vehicle_service = VehicleService(db)
    skip = (page - 1) * size
    
    result = vehicle_service.get_vehicles(
        current_user=current_user,
        company_id=company_id,
        is_active=is_active,
        fuel_type=fuel_type,
        skip=skip,
        limit=size
    )
    
    return VehicleListResponse(
        vehicles=[VehicleResponse.from_orm(v) for v in result["vehicles"]],
        total=result["total"],
        page=result["page"],
        size=result["size"],
        pages=result["pages"]
    )


@router.get("/{vehicle_id}", response_model=VehicleResponse)
async def get_vehicle(
    vehicle_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_vehicle_access())
):
    """
    Get a specific vehicle by ID.
    
    Returns detailed information about a vehicle.
    """
    vehicle_service = VehicleService(db)
    vehicle = vehicle_service.get_vehicle(vehicle_id, current_user)
    return VehicleResponse.from_orm(vehicle)


@router.put("/{vehicle_id}", response_model=VehicleResponse)
async def update_vehicle(
    vehicle_id: UUID,
    vehicle_data: VehicleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_vehicle_access())
):
    """
    Update a vehicle.
    
    Updates vehicle information and returns the updated vehicle.
    """
    vehicle_service = VehicleService(db)
    vehicle = vehicle_service.update_vehicle(vehicle_id, vehicle_data, current_user)
    return VehicleResponse.from_orm(vehicle)


@router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vehicle(
    vehicle_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_vehicle_access())
):
    """
    Delete a vehicle.
    
    Soft deletes a vehicle (sets is_active=False) if it has associated data,
    or hard deletes if no associated data exists.
    """
    vehicle_service = VehicleService(db)
    vehicle_service.delete_vehicle(vehicle_id, current_user)


@router.get("/company/{company_id}", response_model=list[VehicleResponse])
async def get_company_vehicles(
    company_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_vehicle_access())
):
    """
    Get all active vehicles for a specific company.
    
    Returns all active vehicles belonging to the specified company.
    """
    vehicle_service = VehicleService(db)
    vehicles = vehicle_service.get_company_vehicles(company_id, current_user)
    return [VehicleResponse.from_orm(v) for v in vehicles]


@router.post("/calculate-fuel-cost", response_model=VehicleFuelCostResponse)
async def calculate_fuel_cost(
    calculation_data: VehicleFuelCostCalculation,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_vehicle_access())
):
    """
    Calculate fuel cost for a vehicle and distance.
    
    Calculates the fuel cost based on vehicle consumption and distance.
    """
    vehicle_service = VehicleService(db)
    result = vehicle_service.calculate_fuel_cost(calculation_data, current_user)
    return VehicleFuelCostResponse(**result)


@router.get("/statistics/summary")
async def get_vehicle_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_vehicle_access())
):
    """
    Get vehicle statistics.
    
    Returns statistics about vehicles for the user's company.
    """
    vehicle_service = VehicleService(db)
    stats = vehicle_service.get_vehicle_statistics(current_user)
    return stats


@router.post("/validate")
async def validate_vehicle_data(
    vehicle_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_vehicle_access())
):
    """
    Validate vehicle data without creating a vehicle.
    
    Returns validation results including errors and warnings.
    """
    vehicle_service = VehicleService(db)
    validation_result = vehicle_service.validate_vehicle_data(vehicle_data)
    return validation_result


@router.get("/health")
async def vehicle_health_check():
    """
    Health check endpoint for vehicle service.
    """
    return {"status": "healthy", "service": "vehicles"}