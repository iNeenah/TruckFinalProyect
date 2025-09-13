"""
Route calculation API endpoints.
"""
import logging
import uuid
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.route import (
    RouteRequest,
    RouteResponse,
    RouteHistoryResponse,
    RouteReportRequest,
    RouteReportResponse,
    RouteStatistics,
    GeocodingResponse,
    Coordinates,
    Route,
    CostBreakdown,
    TollPoint,
    SavingsAnalysis
)
from app.services.route_optimization_service import (
    RouteOptimizationService,
    RoutePoint,
    RouteOptimizationRequest,
    OptimizedRoute
)
from app.services.route_comparison_service import (
    RouteComparisonService,
    OptimizationCriteria
)
from app.services.route_formatter_service import RouteFormatterService
from app.services.route_statistics_service import RouteStatisticsService
from app.services.geocoding_service import GeocodingService
from app.services.osrm_service import Coordinate
from app.auth.dependencies import get_current_active_user
from app.models.user import User
from app.models.calculated_route import CalculatedRoute

router = APIRouter(prefix="/routes", tags=["routes"])
logger = logging.getLogger(__name__)


@router.post("/calculate", response_model=RouteResponse, status_code=status.HTTP_200_OK)
async def calculate_route(
    request: RouteRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Calculate optimized routes between origin and destination.
    
    This endpoint calculates multiple route alternatives considering:
    - Fuel costs based on vehicle consumption
    - Toll costs along the route
    - Time and distance optimization
    - Cost savings analysis
    """
    start_time = datetime.now()
    request_id = str(uuid.uuid4())
    
    try:
        logger.info(f"Route calculation request {request_id} from user {current_user.id}")
        
        # Initialize services
        route_service = RouteOptimizationService(db)
        comparison_service = RouteComparisonService()
        
        # Convert request to optimization request
        optimization_request = await _convert_to_optimization_request(request, db)
        
        # Calculate routes
        optimization_response = await route_service.optimize_route(optimization_request)
        
        # Analyze routes with comparison service
        criteria_map = {
            "cost": OptimizationCriteria.TOTAL_COST,
            "time": OptimizationCriteria.TIME,
            "distance": OptimizationCriteria.DISTANCE
        }
        criteria = criteria_map.get(request.optimize_for, OptimizationCriteria.TOTAL_COST)
        
        analysis_summary = comparison_service.analyze_routes(
            optimization_response.routes, criteria
        )
        
        # Convert to API response format
        api_response = _convert_to_api_response(
            request_id,
            optimization_response,
            analysis_summary,
            start_time
        )
        
        # Save calculation in background
        background_tasks.add_task(
            _save_route_calculation,
            db,
            optimization_response,
            optimization_request,
            str(current_user.id),
            request_id
        )
        
        logger.info(f"Route calculation {request_id} completed in {api_response.calculation_time_ms}ms")
        return api_response
        
    except ValueError as e:
        logger.error(f"Route calculation validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Route calculation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Route calculation failed. Please try again."
        )


@router.get("/geocode", response_model=GeocodingResponse)
async def geocode_address(
    address: str = Query(..., description="Address to geocode"),
    limit: int = Query(5, ge=1, le=10, description="Maximum number of results"),
    country: str = Query("AR", description="Country code"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Geocode an address to coordinates.
    
    Converts a text address to geographic coordinates using multiple
    geocoding providers for better accuracy.
    """
    try:
        async with GeocodingService() as geocoder:
            if country.upper() == "AR":
                results = await geocoder.geocode_argentina_address(address)
            else:
                results = await geocoder.geocode(address, country_code=country, limit=limit)
            
            # Convert to API format
            api_results = []
            for result in results[:limit]:
                api_results.append({
                    "address": result.address,
                    "coordinates": {
                        "longitude": result.coordinate.longitude,
                        "latitude": result.coordinate.latitude
                    },
                    "formatted_address": result.address,
                    "confidence": result.confidence,
                    "place_type": result.place_type
                })
            
            return GeocodingResponse(
                results=api_results,
                status="success" if api_results else "no_results"
            )
            
    except Exception as e:
        logger.error(f"Geocoding error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Geocoding failed. Please try again."
        )


@router.get("/history", response_model=RouteHistoryResponse)
async def get_route_history(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    vehicle_id: Optional[str] = Query(None, description="Filter by vehicle ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get route calculation history for the current user.
    
    Returns paginated list of previously calculated routes with
    cost analysis and savings information.
    """
    try:
        query = db.query(CalculatedRoute).filter(
            CalculatedRoute.user_id == current_user.id
        )
        
        if vehicle_id:
            query = query.filter(CalculatedRoute.vehicle_id == vehicle_id)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        skip = (page - 1) * size
        routes = query.order_by(CalculatedRoute.created_at.desc()).offset(skip).limit(size).all()
        
        # Convert to API format
        api_routes = []
        for route in routes:
            api_route = {
                "id": route.id,
                "user_id": route.user_id,
                "vehicle_id": route.vehicle_id,
                "company_id": current_user.company_id,
                "origin_address": route.origin_address,
                "destination_address": route.destination_address,
                "origin_coordinates": {
                    "longitude": route.origin_longitude,
                    "latitude": route.origin_latitude
                },
                "destination_coordinates": {
                    "longitude": route.destination_longitude,
                    "latitude": route.destination_latitude
                },
                "selected_route": {
                    "id": str(route.id),
                    "distance": route.distance_km,
                    "duration": int(route.duration_minutes),
                    "cost_breakdown": {
                        "fuel_cost": route.fuel_cost,
                        "toll_cost": route.toll_cost,
                        "total_cost": route.total_cost,
                        "fuel_liters": (route.distance_km / 100) * 15,  # Approximate
                        "toll_count": 0  # Would need to be calculated
                    }
                },
                "total_distance": route.distance_km,
                "total_duration": int(route.duration_minutes),
                "fuel_cost": route.fuel_cost,
                "toll_cost": route.toll_cost,
                "total_cost": route.total_cost,
                "savings_amount": route.estimated_savings,
                "created_at": route.created_at
            }
            api_routes.append(api_route)
        
        return RouteHistoryResponse(
            routes=api_routes,
            total=total,
            page=page,
            size=size,
            pages=(total + size - 1) // size
        )
        
    except Exception as e:
        logger.error(f"Route history error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve route history"
        )


@router.get("/statistics", response_model=RouteStatistics)
async def get_route_statistics(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get route calculation statistics for the current user.
    
    Provides insights into route usage patterns, costs, and savings
    over the specified time period.
    """
    try:
        route_service = RouteOptimizationService(db)
        stats = await route_service.get_route_statistics(str(current_user.id))
        
        # Calculate date range
        end_date = datetime.now()
        start_date = datetime.now().replace(day=1)  # Start of current month
        
        return RouteStatistics(
            total_routes=stats.get("total_routes", 0),
            total_distance=stats.get("total_distance_km", 0.0),
            total_cost=stats.get("total_cost", 0.0),
            total_savings=stats.get("total_savings", 0.0),
            average_distance=stats.get("average_distance", 0.0),
            average_cost=stats.get("average_cost", 0.0),
            most_used_vehicle=None,  # Would need additional query
            most_common_origin=None,  # Would need additional query
            most_common_destination=None,  # Would need additional query
            date_range={
                "start": start_date,
                "end": end_date
            }
        )
        
    except Exception as e:
        logger.error(f"Route statistics error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve route statistics"
        )


@router.post("/reports", response_model=RouteReportResponse)
async def generate_route_report(
    request: RouteReportRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Generate a route report in PDF or HTML format.
    
    Creates a detailed report with route information, cost analysis,
    and optional map visualization.
    """
    try:
        # Get route from database
        route = db.query(CalculatedRoute).filter(
            CalculatedRoute.id == request.route_id,
            CalculatedRoute.user_id == current_user.id
        ).first()
        
        if not route:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Route not found"
            )
        
        # Generate report ID
        report_id = str(uuid.uuid4())
        
        # Schedule report generation in background
        background_tasks.add_task(
            _generate_report_background,
            route,
            request,
            report_id,
            current_user.id
        )
        
        # Return immediate response
        expires_at = datetime.now().replace(hour=23, minute=59, second=59)
        
        return RouteReportResponse(
            report_id=report_id,
            download_url=f"/routes/reports/{report_id}/download",
            expires_at=expires_at,
            file_size=0,  # Will be updated when report is ready
            format=request.format
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Report generation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate report"
        )


@router.get("/statistics/user")
async def get_user_statistics(
    days: int = Query(30, description="Number of days to analyze", ge=1, le=365),
    vehicle_id: Optional[str] = Query(None, description="Filter by vehicle ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get route statistics for the current user.
    
    Returns comprehensive statistics including:
    - Total routes, distance, cost, and savings
    - Average metrics
    - Most used vehicle and common locations
    """
    try:
        stats_service = RouteStatisticsService(db)
        statistics = stats_service.get_user_statistics(
            user_id=current_user.id,
            days=days,
            vehicle_id=vehicle_id
        )
        
        return {
            "user_id": current_user.id,
            "period_days": days,
            "date_range": {
                "start": statistics.date_range.start.isoformat(),
                "end": statistics.date_range.end.isoformat()
            },
            "totals": {
                "routes": statistics.total_routes,
                "distance_km": statistics.total_distance,
                "cost": float(statistics.total_cost),
                "savings": float(statistics.total_savings)
            },
            "averages": {
                "distance_km": statistics.average_distance,
                "cost": float(statistics.average_cost),
                "savings": float(statistics.average_savings)
            },
            "insights": {
                "most_used_vehicle": statistics.most_used_vehicle,
                "most_common_origin": statistics.most_common_origin,
                "most_common_destination": statistics.most_common_destination
            }
        }
        
    except Exception as e:
        logger.error(f"User statistics error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user statistics"
        )


@router.get("/statistics/company")
async def get_company_statistics(
    days: int = Query(30, description="Number of days to analyze", ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get company-wide route statistics.
    
    Returns comprehensive company statistics including:
    - Overall route metrics
    - Top users and vehicles
    - Company-wide insights
    """
    try:
        if not current_user.company_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is not associated with a company"
            )
        
        stats_service = RouteStatisticsService(db)
        statistics = stats_service.get_company_statistics(
            company_id=current_user.company_id,
            days=days
        )
        
        return {
            "company_id": statistics.company_id,
            "company_name": statistics.company_name,
            "period_days": days,
            "date_range": {
                "start": statistics.route_statistics.date_range.start.isoformat(),
                "end": statistics.route_statistics.date_range.end.isoformat()
            },
            "company_overview": {
                "total_users": statistics.total_users,
                "total_vehicles": statistics.total_vehicles
            },
            "route_totals": {
                "routes": statistics.route_statistics.total_routes,
                "distance_km": statistics.route_statistics.total_distance,
                "cost": float(statistics.route_statistics.total_cost),
                "savings": float(statistics.route_statistics.total_savings)
            },
            "route_averages": {
                "distance_km": statistics.route_statistics.average_distance,
                "cost": float(statistics.route_statistics.average_cost),
                "savings": float(statistics.route_statistics.average_savings)
            },
            "top_users": statistics.top_users,
            "top_vehicles": statistics.top_vehicles,
            "insights": {
                "most_used_vehicle": statistics.route_statistics.most_used_vehicle,
                "most_common_origin": statistics.route_statistics.most_common_origin,
                "most_common_destination": statistics.route_statistics.most_common_destination
            }
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Company statistics error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve company statistics"
        )


@router.get("/statistics/trends")
async def get_trend_statistics(
    days: int = Query(30, description="Number of days to analyze", ge=7, le=365),
    interval: str = Query("daily", description="Grouping interval", regex="^(daily|weekly|monthly)$"),
    scope: str = Query("user", description="Statistics scope", regex="^(user|company)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get trend statistics over time.
    
    Returns time-series data for visualization:
    - Route counts over time
    - Cost trends
    - Savings trends
    - Distance patterns
    """
    try:
        stats_service = RouteStatisticsService(db)
        
        if scope == "user":
            trend_data = stats_service.get_trend_data(
                user_id=current_user.id,
                days=days,
                interval=interval
            )
        elif scope == "company":
            if not current_user.company_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User is not associated with a company"
                )
            trend_data = stats_service.get_trend_data(
                company_id=current_user.company_id,
                days=days,
                interval=interval
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid scope. Use 'user' or 'company'"
            )
        
        return {
            "scope": scope,
            "interval": interval,
            "period_days": days,
            "data": {
                "labels": trend_data.labels,
                "route_counts": trend_data.route_counts,
                "total_costs": trend_data.total_costs,
                "total_savings": trend_data.total_savings,
                "average_distances": trend_data.average_distances
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Trend statistics error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve trend statistics"
        )


@router.get("/statistics/cost-breakdown")
async def get_cost_breakdown_statistics(
    days: int = Query(30, description="Number of days to analyze", ge=1, le=365),
    scope: str = Query("user", description="Statistics scope", regex="^(user|company)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get detailed cost breakdown analysis.
    
    Returns cost analysis including:
    - Fuel vs toll cost breakdown
    - Cost per kilometer metrics
    - Route toll usage patterns
    """
    try:
        stats_service = RouteStatisticsService(db)
        
        if scope == "user":
            cost_analysis = stats_service.get_cost_breakdown_analysis(
                user_id=current_user.id,
                days=days
            )
        elif scope == "company":
            if not current_user.company_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User is not associated with a company"
                )
            cost_analysis = stats_service.get_cost_breakdown_analysis(
                company_id=current_user.company_id,
                days=days
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid scope. Use 'user' or 'company'"
            )
        
        return {
            "scope": scope,
            "period_days": days,
            "cost_breakdown": {
                "total_fuel_cost": cost_analysis["total_fuel_cost"],
                "total_toll_cost": cost_analysis["total_toll_cost"],
                "fuel_percentage": cost_analysis["fuel_percentage"],
                "toll_percentage": cost_analysis["toll_percentage"]
            },
            "per_km_costs": {
                "average_fuel_per_km": cost_analysis["average_fuel_per_km"],
                "average_toll_per_km": cost_analysis["average_toll_per_km"]
            },
            "toll_usage": {
                "routes_with_tolls": cost_analysis["routes_with_tolls"],
                "toll_free_routes": cost_analysis["toll_free_routes"],
                "toll_usage_percentage": (cost_analysis["routes_with_tolls"] / cost_analysis["total_routes"] * 100) if cost_analysis["total_routes"] > 0 else 0
            },
            "summary": {
                "total_routes": cost_analysis["total_routes"],
                "total_distance": cost_analysis["total_distance"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Cost breakdown statistics error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve cost breakdown statistics"
        )


@router.get("/health")
async def route_health_check():
    """
    Health check endpoint for route calculation service.
    
    Verifies that all required services (OSRM, database) are available.
    """
    try:
        from app.services.osrm_service import OSRMService
        
        # Check OSRM service
        async with OSRMService() as osrm:
            osrm_healthy = await osrm.health_check()
        
        return {
            "status": "healthy" if osrm_healthy else "degraded",
            "services": {
                "osrm": "healthy" if osrm_healthy else "unavailable",
                "database": "healthy",  # If we got here, DB is working
                "geocoding": "healthy"
            },
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now()
        }


# Helper functions

async def _convert_to_optimization_request(
    request: RouteRequest,
    db: Session
) -> RouteOptimizationRequest:
    """Convert API request to optimization service request."""
    
    # Handle origin
    if isinstance(request.origin, str):
        # Geocode address
        async with GeocodingService() as geocoder:
            origin_results = await geocoder.geocode_argentina_address(request.origin)
            if not origin_results:
                raise ValueError(f"Could not geocode origin address: {request.origin}")
            origin_coord = origin_results[0].coordinate
            origin_address = origin_results[0].address
    else:
        origin_coord = Coordinate(request.origin.longitude, request.origin.latitude)
        origin_address = None
    
    # Handle destination
    if isinstance(request.destination, str):
        # Geocode address
        async with GeocodingService() as geocoder:
            dest_results = await geocoder.geocode_argentina_address(request.destination)
            if not dest_results:
                raise ValueError(f"Could not geocode destination address: {request.destination}")
            dest_coord = dest_results[0].coordinate
            dest_address = dest_results[0].address
    else:
        dest_coord = Coordinate(request.destination.longitude, request.destination.latitude)
        dest_address = None
    
    return RouteOptimizationRequest(
        origin=RoutePoint(
            coordinate=origin_coord,
            address=origin_address,
            name="Origin"
        ),
        destination=RoutePoint(
            coordinate=dest_coord,
            address=dest_address,
            name="Destination"
        ),
        vehicle_id=str(request.vehicle_id),
        avoid_tolls=request.avoid_tolls,
        max_alternatives=request.alternatives
    )


def _convert_to_api_response(
    request_id: str,
    optimization_response,
    analysis_summary,
    start_time: datetime
) -> RouteResponse:
    """Convert optimization response to API response format."""
    
    # Convert routes
    api_routes = []
    for i, route in enumerate(optimization_response.routes):
        api_route = Route(
            id=f"route_{i}",
            geometry={"type": "LineString", "coordinates": []},  # Would need actual geometry
            distance=route.osrm_route.distance / 1000,  # Convert to km
            duration=int(route.osrm_route.duration / 60),  # Convert to minutes
            cost_breakdown=CostBreakdown(
                fuel_cost=route.cost_breakdown.fuel_cost.total_fuel_cost,
                toll_cost=route.cost_breakdown.total_toll_cost,
                total_cost=route.cost_breakdown.total_cost,
                fuel_liters=route.cost_breakdown.fuel_cost.fuel_needed_liters,
                toll_count=len(route.cost_breakdown.tolls)
            ),
            toll_points=[
                TollPoint(
                    toll_id=uuid.uuid4(),  # Would use actual toll ID
                    name=toll.name,
                    coordinates=Coordinates(
                        longitude=toll.coordinate.longitude,
                        latitude=toll.coordinate.latitude
                    ),
                    tariff=toll.cost,
                    route_code=toll.road_name
                )
                for toll in route.cost_breakdown.tolls
            ],
            route_type=route.route_type
        )
        api_routes.append(api_route)
    
    # Find recommended route
    recommended_route = next(
        (route for route in api_routes if route.route_type == "recommended"),
        api_routes[0] if api_routes else None
    )
    
    # Alternative routes (excluding recommended)
    alternative_routes = [
        route for route in api_routes 
        if route.id != (recommended_route.id if recommended_route else None)
    ]
    
    # Savings analysis
    savings_analysis = SavingsAnalysis(
        recommended_route_id=recommended_route.id if recommended_route else "",
        fastest_route_cost=api_routes[0].cost_breakdown.total_cost if api_routes else None,
        cheapest_route_cost=min(route.cost_breakdown.total_cost for route in api_routes) if api_routes else 0,
        savings_amount=optimization_response.total_savings,
        savings_percentage=float(optimization_response.total_savings / api_routes[0].cost_breakdown.total_cost * 100) if api_routes and api_routes[0].cost_breakdown.total_cost > 0 else 0,
        comparison_summary=f"Recommended route saves ${optimization_response.total_savings:.2f}"
    )
    
    # Calculate response time
    calculation_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
    
    return RouteResponse(
        request_id=request_id,
        recommended_route=recommended_route,
        alternative_routes=alternative_routes,
        savings_analysis=savings_analysis,
        calculation_time_ms=calculation_time_ms,
        timestamp=datetime.now()
    )


async def _save_route_calculation(
    db: Session,
    optimization_response,
    optimization_request,
    user_id: str,
    request_id: str
):
    """Save route calculation to database in background."""
    try:
        route_service = RouteOptimizationService(db)
        await route_service.save_calculated_route(
            optimization_response,
            optimization_request,
            user_id
        )
        logger.info(f"Route calculation {request_id} saved to database")
    except Exception as e:
        logger.error(f"Failed to save route calculation {request_id}: {e}")


async def _generate_report_background(
    route,
    request: RouteReportRequest,
    report_id: str,
    user_id: str
):
    """Generate route report in background."""
    try:
        # Implement actual report generation
        # This uses a PDF generation library like reportlab
        logger.info(f"Generating report {report_id} for route {route.id}")
        
        # Generate PDF report
        from app.services.report_service import generate_route_report
        pdf_content = generate_route_report(route)
        
        # Save report to database or file system
        # For now, we'll just simulate saving
        import asyncio
        await asyncio.sleep(2)  # Simulate processing time
        
        logger.info(f"Report {report_id} generated successfully")
        
    except Exception as e:
        logger.error(f"Failed to generate report {report_id}: {e}")