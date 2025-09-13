"""
Route statistics and analytics service.
"""
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
from dataclasses import dataclass
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc

from app.models.calculated_route import CalculatedRoute
from app.models.user import User
from app.models.vehicle import Vehicle
from app.models.company import Company

logger = logging.getLogger(__name__)


@dataclass
class DateRange:
    """Date range for statistics."""
    start: datetime
    end: datetime


@dataclass
class RouteStatistics:
    """Route statistics data."""
    total_routes: int
    total_distance: float
    total_cost: Decimal
    total_savings: Decimal
    average_distance: float
    average_cost: Decimal
    average_savings: Decimal
    most_used_vehicle: Optional[str]
    most_common_origin: Optional[str]
    most_common_destination: Optional[str]
    date_range: DateRange


@dataclass
class CompanyStatistics:
    """Company-wide statistics."""
    company_id: str
    company_name: str
    total_users: int
    total_vehicles: int
    route_statistics: RouteStatistics
    top_users: List[Dict[str, Any]]
    top_vehicles: List[Dict[str, Any]]


@dataclass
class TrendData:
    """Trend data over time."""
    labels: List[str]
    route_counts: List[int]
    total_costs: List[float]
    total_savings: List[float]
    average_distances: List[float]


class RouteStatisticsService:
    """Service for route statistics and analytics."""
    
    def __init__(self, db: Session):
        """
        Initialize route statistics service.
        
        Args:
            db: Database session
        """
        self.db = db
        self.logger = logging.getLogger(__name__)
    
    def get_user_statistics(
        self,
        user_id: str,
        days: int = 30,
        vehicle_id: Optional[str] = None
    ) -> RouteStatistics:
        """
        Get route statistics for a specific user.
        
        Args:
            user_id: User ID
            days: Number of days to analyze
            vehicle_id: Optional vehicle filter
            
        Returns:
            Route statistics
        """
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Build query
            query = self.db.query(CalculatedRoute).filter(
                and_(
                    CalculatedRoute.user_id == user_id,
                    CalculatedRoute.created_at >= start_date,
                    CalculatedRoute.created_at <= end_date
                )
            )
            
            if vehicle_id:
                query = query.filter(CalculatedRoute.vehicle_id == vehicle_id)
            
            # Get all routes
            routes = query.all()
            
            if not routes:
                return self._empty_statistics(DateRange(start_date, end_date))
            
            # Calculate basic statistics
            total_routes = len(routes)
            total_distance = sum(route.distance_km for route in routes)
            total_cost = sum(route.total_cost for route in routes)
            total_savings = sum(route.estimated_savings or Decimal('0') for route in routes)
            
            average_distance = total_distance / total_routes if total_routes > 0 else 0
            average_cost = total_cost / total_routes if total_routes > 0 else Decimal('0')
            average_savings = total_savings / total_routes if total_routes > 0 else Decimal('0')
            
            # Find most used vehicle
            most_used_vehicle = self._get_most_used_vehicle(routes)
            
            # Find most common origin and destination
            most_common_origin = self._get_most_common_location(routes, 'origin')
            most_common_destination = self._get_most_common_location(routes, 'destination')
            
            return RouteStatistics(
                total_routes=total_routes,
                total_distance=total_distance,
                total_cost=total_cost,
                total_savings=total_savings,
                average_distance=average_distance,
                average_cost=average_cost,
                average_savings=average_savings,
                most_used_vehicle=most_used_vehicle,
                most_common_origin=most_common_origin,
                most_common_destination=most_common_destination,
                date_range=DateRange(start_date, end_date)
            )
            
        except Exception as e:
            self.logger.error(f"Error getting user statistics: {e}")
            raise
    
    def get_company_statistics(
        self,
        company_id: str,
        days: int = 30
    ) -> CompanyStatistics:
        """
        Get company-wide route statistics.
        
        Args:
            company_id: Company ID
            days: Number of days to analyze
            
        Returns:
            Company statistics
        """
        try:
            # Get company info
            company = self.db.query(Company).filter(Company.id == company_id).first()
            if not company:
                raise ValueError(f"Company {company_id} not found")
            
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Get all users in company
            users = self.db.query(User).filter(User.company_id == company_id).all()
            user_ids = [user.id for user in users]
            
            # Get all vehicles in company
            vehicles = self.db.query(Vehicle).filter(Vehicle.company_id == company_id).all()
            
            # Get all routes for company users
            routes_query = self.db.query(CalculatedRoute).filter(
                and_(
                    CalculatedRoute.user_id.in_(user_ids),
                    CalculatedRoute.created_at >= start_date,
                    CalculatedRoute.created_at <= end_date
                )
            )
            
            routes = routes_query.all()
            
            # Calculate route statistics
            if routes:
                total_routes = len(routes)
                total_distance = sum(route.distance_km for route in routes)
                total_cost = sum(route.total_cost for route in routes)
                total_savings = sum(route.estimated_savings or Decimal('0') for route in routes)
                
                average_distance = total_distance / total_routes
                average_cost = total_cost / total_routes
                average_savings = total_savings / total_routes
                
                most_used_vehicle = self._get_most_used_vehicle(routes)
                most_common_origin = self._get_most_common_location(routes, 'origin')
                most_common_destination = self._get_most_common_location(routes, 'destination')
            else:
                total_routes = 0
                total_distance = 0
                total_cost = Decimal('0')
                total_savings = Decimal('0')
                average_distance = 0
                average_cost = Decimal('0')
                average_savings = Decimal('0')
                most_used_vehicle = None
                most_common_origin = None
                most_common_destination = None
            
            route_stats = RouteStatistics(
                total_routes=total_routes,
                total_distance=total_distance,
                total_cost=total_cost,
                total_savings=total_savings,
                average_distance=average_distance,
                average_cost=average_cost,
                average_savings=average_savings,
                most_used_vehicle=most_used_vehicle,
                most_common_origin=most_common_origin,
                most_common_destination=most_common_destination,
                date_range=DateRange(start_date, end_date)
            )
            
            # Get top users and vehicles
            top_users = self._get_top_users(user_ids, start_date, end_date)
            top_vehicles = self._get_top_vehicles(company_id, start_date, end_date)
            
            return CompanyStatistics(
                company_id=company_id,
                company_name=company.name,
                total_users=len(users),
                total_vehicles=len(vehicles),
                route_statistics=route_stats,
                top_users=top_users,
                top_vehicles=top_vehicles
            )
            
        except Exception as e:
            self.logger.error(f"Error getting company statistics: {e}")
            raise
    
    def get_trend_data(
        self,
        user_id: Optional[str] = None,
        company_id: Optional[str] = None,
        days: int = 30,
        interval: str = 'daily'
    ) -> TrendData:
        """
        Get trend data over time.
        
        Args:
            user_id: Optional user ID filter
            company_id: Optional company ID filter
            days: Number of days to analyze
            interval: Grouping interval ('daily', 'weekly', 'monthly')
            
        Returns:
            Trend data
        """
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Build base query
            query = self.db.query(CalculatedRoute).filter(
                and_(
                    CalculatedRoute.created_at >= start_date,
                    CalculatedRoute.created_at <= end_date
                )
            )
            
            if user_id:
                query = query.filter(CalculatedRoute.user_id == user_id)
            elif company_id:
                # Get users in company
                user_ids = self.db.query(User.id).filter(User.company_id == company_id).all()
                user_ids = [uid[0] for uid in user_ids]
                query = query.filter(CalculatedRoute.user_id.in_(user_ids))
            
            routes = query.all()
            
            # Group data by interval
            if interval == 'daily':
                grouped_data = self._group_by_day(routes, start_date, end_date)
            elif interval == 'weekly':
                grouped_data = self._group_by_week(routes, start_date, end_date)
            elif interval == 'monthly':
                grouped_data = self._group_by_month(routes, start_date, end_date)
            else:
                raise ValueError(f"Invalid interval: {interval}")
            
            return grouped_data
            
        except Exception as e:
            self.logger.error(f"Error getting trend data: {e}")
            raise
    
    def get_cost_breakdown_analysis(
        self,
        user_id: Optional[str] = None,
        company_id: Optional[str] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get detailed cost breakdown analysis.
        
        Args:
            user_id: Optional user ID filter
            company_id: Optional company ID filter
            days: Number of days to analyze
            
        Returns:
            Cost breakdown analysis
        """
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Build query
            query = self.db.query(CalculatedRoute).filter(
                and_(
                    CalculatedRoute.created_at >= start_date,
                    CalculatedRoute.created_at <= end_date
                )
            )
            
            if user_id:
                query = query.filter(CalculatedRoute.user_id == user_id)
            elif company_id:
                user_ids = self.db.query(User.id).filter(User.company_id == company_id).all()
                user_ids = [uid[0] for uid in user_ids]
                query = query.filter(CalculatedRoute.user_id.in_(user_ids))
            
            routes = query.all()
            
            if not routes:
                return {
                    "total_fuel_cost": 0,
                    "total_toll_cost": 0,
                    "fuel_percentage": 0,
                    "toll_percentage": 0,
                    "average_fuel_per_km": 0,
                    "average_toll_per_km": 0,
                    "routes_with_tolls": 0,
                    "toll_free_routes": 0
                }
            
            # Calculate totals
            total_fuel_cost = sum(route.fuel_cost for route in routes)
            total_toll_cost = sum(route.toll_cost for route in routes)
            total_cost = total_fuel_cost + total_toll_cost
            total_distance = sum(route.distance_km for route in routes)
            
            # Calculate percentages
            fuel_percentage = (float(total_fuel_cost) / float(total_cost) * 100) if total_cost > 0 else 0
            toll_percentage = (float(total_toll_cost) / float(total_cost) * 100) if total_cost > 0 else 0
            
            # Calculate averages per km
            average_fuel_per_km = float(total_fuel_cost) / total_distance if total_distance > 0 else 0
            average_toll_per_km = float(total_toll_cost) / total_distance if total_distance > 0 else 0
            
            # Count routes with/without tolls
            routes_with_tolls = sum(1 for route in routes if route.toll_cost > 0)
            toll_free_routes = len(routes) - routes_with_tolls
            
            return {
                "total_fuel_cost": float(total_fuel_cost),
                "total_toll_cost": float(total_toll_cost),
                "fuel_percentage": fuel_percentage,
                "toll_percentage": toll_percentage,
                "average_fuel_per_km": average_fuel_per_km,
                "average_toll_per_km": average_toll_per_km,
                "routes_with_tolls": routes_with_tolls,
                "toll_free_routes": toll_free_routes,
                "total_routes": len(routes),
                "total_distance": total_distance
            }
            
        except Exception as e:
            self.logger.error(f"Error getting cost breakdown analysis: {e}")
            raise
    
    def _empty_statistics(self, date_range: DateRange) -> RouteStatistics:
        """Return empty statistics structure."""
        return RouteStatistics(
            total_routes=0,
            total_distance=0.0,
            total_cost=Decimal('0'),
            total_savings=Decimal('0'),
            average_distance=0.0,
            average_cost=Decimal('0'),
            average_savings=Decimal('0'),
            most_used_vehicle=None,
            most_common_origin=None,
            most_common_destination=None,
            date_range=date_range
        )
    
    def _get_most_used_vehicle(self, routes: List[CalculatedRoute]) -> Optional[str]:
        """Get the most frequently used vehicle."""
        if not routes:
            return None
        
        vehicle_counts = {}
        for route in routes:
            vehicle_id = route.vehicle_id
            vehicle_counts[vehicle_id] = vehicle_counts.get(vehicle_id, 0) + 1
        
        most_used_vehicle_id = max(vehicle_counts.keys(), key=lambda k: vehicle_counts[k])
        
        # Get vehicle info
        vehicle = self.db.query(Vehicle).filter(Vehicle.id == most_used_vehicle_id).first()
        if vehicle:
            return f"{vehicle.brand} {vehicle.model}" if vehicle.brand else vehicle.model
        
        return most_used_vehicle_id
    
    def _get_most_common_location(self, routes: List[CalculatedRoute], location_type: str) -> Optional[str]:
        """Get the most common origin or destination."""
        if not routes:
            return None
        
        location_counts = {}
        for route in routes:
            if location_type == 'origin':
                location = route.origin_address
            else:
                location = route.destination_address
            
            if location:
                # Simplify address (take first part)
                simplified = location.split(',')[0].strip()
                location_counts[simplified] = location_counts.get(simplified, 0) + 1
        
        if not location_counts:
            return None
        
        return max(location_counts.keys(), key=lambda k: location_counts[k])
    
    def _get_top_users(self, user_ids: List[str], start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Get top users by route count."""
        try:
            # Query route counts by user
            user_stats = self.db.query(
                CalculatedRoute.user_id,
                func.count(CalculatedRoute.id).label('route_count'),
                func.sum(CalculatedRoute.distance_km).label('total_distance'),
                func.sum(CalculatedRoute.total_cost).label('total_cost'),
                func.sum(CalculatedRoute.estimated_savings).label('total_savings')
            ).filter(
                and_(
                    CalculatedRoute.user_id.in_(user_ids),
                    CalculatedRoute.created_at >= start_date,
                    CalculatedRoute.created_at <= end_date
                )
            ).group_by(CalculatedRoute.user_id).order_by(desc('route_count')).limit(5).all()
            
            top_users = []
            for stat in user_stats:
                user = self.db.query(User).filter(User.id == stat.user_id).first()
                if user:
                    top_users.append({
                        "user_id": stat.user_id,
                        "user_name": f"{user.first_name} {user.last_name}",
                        "user_email": user.email,
                        "route_count": stat.route_count,
                        "total_distance": float(stat.total_distance or 0),
                        "total_cost": float(stat.total_cost or 0),
                        "total_savings": float(stat.total_savings or 0)
                    })
            
            return top_users
            
        except Exception as e:
            self.logger.error(f"Error getting top users: {e}")
            return []
    
    def _get_top_vehicles(self, company_id: str, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Get top vehicles by usage."""
        try:
            # Get company users
            user_ids = self.db.query(User.id).filter(User.company_id == company_id).all()
            user_ids = [uid[0] for uid in user_ids]
            
            # Query vehicle usage
            vehicle_stats = self.db.query(
                CalculatedRoute.vehicle_id,
                func.count(CalculatedRoute.id).label('usage_count'),
                func.sum(CalculatedRoute.distance_km).label('total_distance'),
                func.sum(CalculatedRoute.total_cost).label('total_cost')
            ).filter(
                and_(
                    CalculatedRoute.user_id.in_(user_ids),
                    CalculatedRoute.created_at >= start_date,
                    CalculatedRoute.created_at <= end_date
                )
            ).group_by(CalculatedRoute.vehicle_id).order_by(desc('usage_count')).limit(5).all()
            
            top_vehicles = []
            for stat in vehicle_stats:
                vehicle = self.db.query(Vehicle).filter(Vehicle.id == stat.vehicle_id).first()
                if vehicle:
                    top_vehicles.append({
                        "vehicle_id": stat.vehicle_id,
                        "vehicle_name": f"{vehicle.brand} {vehicle.model}" if vehicle.brand else vehicle.model,
                        "license_plate": vehicle.license_plate,
                        "usage_count": stat.usage_count,
                        "total_distance": float(stat.total_distance or 0),
                        "total_cost": float(stat.total_cost or 0)
                    })
            
            return top_vehicles
            
        except Exception as e:
            self.logger.error(f"Error getting top vehicles: {e}")
            return []   
 
    def _group_by_day(self, routes: List[CalculatedRoute], start_date: datetime, end_date: datetime) -> TrendData:
        """Group routes by day."""
        # Create daily buckets
        current_date = start_date.date()
        end_date_only = end_date.date()
        
        daily_data = {}
        labels = []
        
        # Initialize all days with zero values
        while current_date <= end_date_only:
            date_str = current_date.strftime('%Y-%m-%d')
            labels.append(date_str)
            daily_data[date_str] = {
                'routes': [],
                'count': 0,
                'total_cost': 0,
                'total_savings': 0,
                'total_distance': 0
            }
            current_date += timedelta(days=1)
        
        # Group routes by day
        for route in routes:
            date_str = route.created_at.date().strftime('%Y-%m-%d')
            if date_str in daily_data:
                daily_data[date_str]['routes'].append(route)
                daily_data[date_str]['count'] += 1
                daily_data[date_str]['total_cost'] += float(route.total_cost)
                daily_data[date_str]['total_savings'] += float(route.estimated_savings or 0)
                daily_data[date_str]['total_distance'] += route.distance_km
        
        # Create trend data
        route_counts = []
        total_costs = []
        total_savings = []
        average_distances = []
        
        for label in labels:
            data = daily_data[label]
            route_counts.append(data['count'])
            total_costs.append(data['total_cost'])
            total_savings.append(data['total_savings'])
            
            avg_distance = data['total_distance'] / data['count'] if data['count'] > 0 else 0
            average_distances.append(avg_distance)
        
        return TrendData(
            labels=labels,
            route_counts=route_counts,
            total_costs=total_costs,
            total_savings=total_savings,
            average_distances=average_distances
        )
    
    def _group_by_week(self, routes: List[CalculatedRoute], start_date: datetime, end_date: datetime) -> TrendData:
        """Group routes by week."""
        # Find start of first week (Monday)
        days_since_monday = start_date.weekday()
        week_start = start_date - timedelta(days=days_since_monday)
        
        weekly_data = {}
        labels = []
        
        # Initialize weekly buckets
        current_week = week_start
        while current_week <= end_date:
            week_end = current_week + timedelta(days=6)
            week_label = f"{current_week.strftime('%Y-%m-%d')} to {week_end.strftime('%Y-%m-%d')}"
            labels.append(week_label)
            
            weekly_data[week_label] = {
                'start': current_week,
                'end': week_end,
                'routes': [],
                'count': 0,
                'total_cost': 0,
                'total_savings': 0,
                'total_distance': 0
            }
            current_week += timedelta(weeks=1)
        
        # Group routes by week
        for route in routes:
            route_date = route.created_at.date()
            for week_label, week_data in weekly_data.items():
                if week_data['start'].date() <= route_date <= week_data['end'].date():
                    week_data['routes'].append(route)
                    week_data['count'] += 1
                    week_data['total_cost'] += float(route.total_cost)
                    week_data['total_savings'] += float(route.estimated_savings or 0)
                    week_data['total_distance'] += route.distance_km
                    break
        
        # Create trend data
        route_counts = []
        total_costs = []
        total_savings = []
        average_distances = []
        
        for label in labels:
            data = weekly_data[label]
            route_counts.append(data['count'])
            total_costs.append(data['total_cost'])
            total_savings.append(data['total_savings'])
            
            avg_distance = data['total_distance'] / data['count'] if data['count'] > 0 else 0
            average_distances.append(avg_distance)
        
        return TrendData(
            labels=labels,
            route_counts=route_counts,
            total_costs=total_costs,
            total_savings=total_savings,
            average_distances=average_distances
        )
    
    def _group_by_month(self, routes: List[CalculatedRoute], start_date: datetime, end_date: datetime) -> TrendData:
        """Group routes by month."""
        # Find start of first month
        month_start = start_date.replace(day=1)
        
        monthly_data = {}
        labels = []
        
        # Initialize monthly buckets
        current_month = month_start
        while current_month <= end_date:
            # Calculate end of month
            if current_month.month == 12:
                next_month = current_month.replace(year=current_month.year + 1, month=1)
            else:
                next_month = current_month.replace(month=current_month.month + 1)
            
            month_end = next_month - timedelta(days=1)
            month_label = current_month.strftime('%Y-%m')
            labels.append(month_label)
            
            monthly_data[month_label] = {
                'start': current_month,
                'end': month_end,
                'routes': [],
                'count': 0,
                'total_cost': 0,
                'total_savings': 0,
                'total_distance': 0
            }
            current_month = next_month
        
        # Group routes by month
        for route in routes:
            route_date = route.created_at.date()
            for month_label, month_data in monthly_data.items():
                if month_data['start'].date() <= route_date <= month_data['end'].date():
                    month_data['routes'].append(route)
                    month_data['count'] += 1
                    month_data['total_cost'] += float(route.total_cost)
                    month_data['total_savings'] += float(route.estimated_savings or 0)
                    month_data['total_distance'] += route.distance_km
                    break
        
        # Create trend data
        route_counts = []
        total_costs = []
        total_savings = []
        average_distances = []
        
        for label in labels:
            data = monthly_data[label]
            route_counts.append(data['count'])
            total_costs.append(data['total_cost'])
            total_savings.append(data['total_savings'])
            
            avg_distance = data['total_distance'] / data['count'] if data['count'] > 0 else 0
            average_distances.append(avg_distance)
        
        return TrendData(
            labels=labels,
            route_counts=route_counts,
            total_costs=total_costs,
            total_savings=total_savings,
            average_distances=average_distances
        )