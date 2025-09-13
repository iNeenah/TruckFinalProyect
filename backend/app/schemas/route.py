"""
Pydantic schemas for route calculation and response.
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union, Tuple
from datetime import datetime
from uuid import UUID
from decimal import Decimal


class Coordinates(BaseModel):
    """Geographic coordinates."""
    longitude: float = Field(..., ge=-180, le=180)
    latitude: float = Field(..., ge=-90, le=90)


class RouteRequest(BaseModel):
    """Schema for route calculation request."""
    origin: Union[str, Coordinates] = Field(..., description="Origin address or coordinates")
    destination: Union[str, Coordinates] = Field(..., description="Destination address or coordinates")
    vehicle_id: UUID = Field(..., description="Vehicle ID for cost calculation")
    alternatives: int = Field(default=3, ge=1, le=5, description="Number of route alternatives")
    avoid_tolls: bool = Field(default=False, description="Try to avoid toll roads")
    optimize_for: str = Field(default="cost", description="Optimization criteria: cost, time, distance")

    @validator('optimize_for')
    def validate_optimize_for(cls, v):
        """Validate optimization criteria."""
        allowed = ['cost', 'time', 'distance']
        if v not in allowed:
            raise ValueError(f'optimize_for must be one of: {allowed}')
        return v


class TollPoint(BaseModel):
    """Toll point information in route."""
    toll_id: UUID
    name: str
    coordinates: Coordinates
    tariff: Decimal
    route_code: Optional[str]


class CostBreakdown(BaseModel):
    """Cost breakdown for a route."""
    fuel_cost: Decimal = Field(..., description="Fuel cost in ARS")
    toll_cost: Decimal = Field(..., description="Toll cost in ARS")
    total_cost: Decimal = Field(..., description="Total cost in ARS")
    fuel_liters: float = Field(..., description="Fuel consumption in liters")
    toll_count: int = Field(..., description="Number of tolls on route")


class Route(BaseModel):
    """Individual route information."""
    id: str = Field(..., description="Route identifier")
    geometry: Dict[str, Any] = Field(..., description="GeoJSON LineString geometry")
    distance: float = Field(..., description="Distance in kilometers")
    duration: int = Field(..., description="Duration in minutes")
    cost_breakdown: CostBreakdown
    toll_points: List[TollPoint]
    route_type: str = Field(..., description="Route type: fastest, cheapest, balanced")


class SavingsAnalysis(BaseModel):
    """Savings analysis comparing routes."""
    recommended_route_id: str
    fastest_route_cost: Optional[Decimal]
    cheapest_route_cost: Decimal
    savings_amount: Optional[Decimal]
    savings_percentage: Optional[float]
    comparison_summary: str


class RouteResponse(BaseModel):
    """Schema for route calculation response."""
    request_id: str = Field(..., description="Unique request identifier")
    recommended_route: Route
    alternative_routes: List[Route]
    savings_analysis: SavingsAnalysis
    calculation_time_ms: int
    timestamp: datetime


class RouteCalculation(BaseModel):
    """Schema for storing route calculation results."""
    id: UUID
    user_id: UUID
    vehicle_id: UUID
    company_id: UUID
    origin_address: Optional[str]
    destination_address: Optional[str]
    origin_coordinates: Coordinates
    destination_coordinates: Coordinates
    selected_route: Route
    total_distance: float
    total_duration: int
    fuel_cost: Decimal
    toll_cost: Decimal
    total_cost: Decimal
    savings_amount: Optional[Decimal]
    created_at: datetime

    class Config:
        from_attributes = True


class RouteHistoryResponse(BaseModel):
    """Schema for route history responses."""
    routes: List[RouteCalculation]
    total: int
    page: int
    size: int
    pages: int


class RouteReportRequest(BaseModel):
    """Schema for route report generation request."""
    route_id: UUID
    report_type: str = Field(default="complete", description="Report type: complete, simple")
    include_map: bool = Field(default=True, description="Include map in report")
    format: str = Field(default="pdf", description="Report format: pdf, html")

    @validator('report_type')
    def validate_report_type(cls, v):
        """Validate report type."""
        allowed = ['complete', 'simple']
        if v not in allowed:
            raise ValueError(f'report_type must be one of: {allowed}')
        return v

    @validator('format')
    def validate_format(cls, v):
        """Validate report format."""
        allowed = ['pdf', 'html']
        if v not in allowed:
            raise ValueError(f'format must be one of: {allowed}')
        return v


class RouteReportResponse(BaseModel):
    """Schema for route report response."""
    report_id: str
    download_url: str
    expires_at: datetime
    file_size: int
    format: str


class RouteStatistics(BaseModel):
    """Schema for route statistics."""
    total_routes: int
    total_distance: float
    total_cost: Decimal
    total_savings: Decimal
    average_distance: float
    average_cost: Decimal
    most_used_vehicle: Optional[str]
    most_common_origin: Optional[str]
    most_common_destination: Optional[str]
    date_range: Dict[str, datetime]


class GeocodingResult(BaseModel):
    """Schema for geocoding results."""
    address: str
    coordinates: Coordinates
    formatted_address: str
    confidence: float
    place_type: str


class GeocodingResponse(BaseModel):
    """Schema for geocoding API response."""
    results: List[GeocodingResult]
    status: str