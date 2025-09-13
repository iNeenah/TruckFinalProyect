"""
Data staleness monitoring service.

This service checks for outdated data and provides alerts and fallback values.
"""
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, date, timedelta
from decimal import Decimal
from dataclasses import dataclass
from enum import Enum
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from app.models.fuel_price import FuelPrice
from app.models.toll import Toll


logger = logging.getLogger(__name__)


class DataStalenessLevel(str, Enum):
    """Data staleness severity levels."""
    FRESH = "fresh"
    WARNING = "warning"
    STALE = "stale"
    CRITICAL = "critical"


@dataclass
class StalenessAlert:
    """Data staleness alert information."""
    data_type: str
    identifier: str
    description: str
    level: DataStalenessLevel
    days_old: int
    last_updated: Optional[datetime]
    recommended_action: str
    fallback_value: Optional[Any] = None


@dataclass
class DataFreshnessReport:
    """Complete data freshness report."""
    report_date: datetime
    total_alerts: int
    alerts_by_level: Dict[DataStalenessLevel, int]
    alerts: List[StalenessAlert]
    summary: str
    recommendations: List[str]


class DataStalenessService:
    """Service for monitoring data staleness and providing alerts."""
    
    def __init__(self, db: Session):
        """
        Initialize data staleness service.
        
        Args:
            db: Database session
        """
        self.db = db
        self.logger = logging.getLogger(__name__)
        
        # Staleness thresholds (in days)
        self.thresholds = {
            "fuel_price": {
                DataStalenessLevel.WARNING: 15,
                DataStalenessLevel.STALE: 30,
                DataStalenessLevel.CRITICAL: 60
            },
            "toll": {
                DataStalenessLevel.WARNING: 90,
                DataStalenessLevel.STALE: 180,
                DataStalenessLevel.CRITICAL: 365
            }
        }
        
        # Default fallback values
        self.default_fuel_prices = {
            "diesel_500": Decimal("150.00"),
            "diesel_premium": Decimal("165.00"),
            "gasoline_regular": Decimal("140.00"),
            "gasoline_premium": Decimal("155.00")
        }
        
        self.default_toll_tariff = Decimal("90.00")
    
    def check_fuel_price_staleness(
        self, 
        threshold_days: int = 30,
        fuel_type: Optional[str] = None,
        region: Optional[str] = None
    ) -> List[StalenessAlert]:
        """
        Check for stale fuel price data.
        
        Args:
            threshold_days: Days threshold for staleness
            fuel_type: Filter by fuel type
            region: Filter by region
            
        Returns:
            List of staleness alerts
        """
        try:
            staleness_date = date.today() - timedelta(days=threshold_days)
            
            query = self.db.query(FuelPrice).filter(
                and_(
                    FuelPrice.effective_date < staleness_date,
                    FuelPrice.is_active == True
                )
            )
            
            if fuel_type:
                query = query.filter(FuelPrice.fuel_type == fuel_type)
            
            if region:
                query = query.filter(FuelPrice.region == region)
            
            stale_prices = query.all()
            
            alerts = []
            for price in stale_prices:
                days_old = (date.today() - price.effective_date).days
                level = self._get_staleness_level("fuel_price", days_old)
                
                fallback_value = self.default_fuel_prices.get(
                    price.fuel_type, 
                    self.default_fuel_prices.get("diesel_500")
                )
                
                alert = StalenessAlert(
                    data_type="fuel_price",
                    identifier=f"{price.fuel_type}_{price.region}",
                    description=f"{price.fuel_type} price in {price.region}",
                    level=level,
                    days_old=days_old,
                    last_updated=price.updated_at,
                    recommended_action=self._get_fuel_price_recommendation(level, days_old),
                    fallback_value=float(fallback_value)
                )
                alerts.append(alert)
            
            self.logger.info(f"Found {len(alerts)} stale fuel price alerts")
            return alerts
            
        except Exception as e:
            self.logger.error(f"Error checking fuel price staleness: {e}")
            return []
    
    def check_toll_staleness(
        self, 
        threshold_days: int = 180,
        road_name: Optional[str] = None,
        region: Optional[str] = None
    ) -> List[StalenessAlert]:
        """
        Check for stale toll data.
        
        Args:
            threshold_days: Days threshold for staleness
            road_name: Filter by road name
            region: Filter by region
            
        Returns:
            List of staleness alerts
        """
        try:
            staleness_date = date.today() - timedelta(days=threshold_days)
            
            query = self.db.query(Toll).filter(
                and_(
                    Toll.updated_at < datetime.combine(staleness_date, datetime.min.time()),
                    Toll.is_active == True
                )
            )
            
            if road_name:
                query = query.filter(Toll.road_name.ilike(f"%{road_name}%"))
            
            if region:
                query = query.filter(Toll.region == region)
            
            stale_tolls = query.all()
            
            alerts = []
            for toll in stale_tolls:
                if toll.updated_at:
                    days_old = (datetime.now() - toll.updated_at).days
                else:
                    days_old = (datetime.now() - toll.created_at).days
                
                level = self._get_staleness_level("toll", days_old)
                
                alert = StalenessAlert(
                    data_type="toll",
                    identifier=f"{toll.road_name}_{toll.name}",
                    description=f"{toll.name} on {toll.road_name}",
                    level=level,
                    days_old=days_old,
                    last_updated=toll.updated_at or toll.created_at,
                    recommended_action=self._get_toll_recommendation(level, days_old),
                    fallback_value=float(self.default_toll_tariff)
                )
                alerts.append(alert)
            
            self.logger.info(f"Found {len(alerts)} stale toll alerts")
            return alerts
            
        except Exception as e:
            self.logger.error(f"Error checking toll staleness: {e}")
            return []
    
    def generate_staleness_report(
        self,
        fuel_price_threshold: int = 30,
        toll_threshold: int = 180
    ) -> DataFreshnessReport:
        """
        Generate comprehensive data staleness report.
        
        Args:
            fuel_price_threshold: Fuel price staleness threshold in days
            toll_threshold: Toll staleness threshold in days
            
        Returns:
            Complete data freshness report
        """
        try:
            # Get all alerts
            fuel_alerts = self.check_fuel_price_staleness(fuel_price_threshold)
            toll_alerts = self.check_toll_staleness(toll_threshold)
            
            all_alerts = fuel_alerts + toll_alerts
            
            # Count alerts by level
            alerts_by_level = {
                DataStalenessLevel.WARNING: 0,
                DataStalenessLevel.STALE: 0,
                DataStalenessLevel.CRITICAL: 0
            }
            
            for alert in all_alerts:
                if alert.level in alerts_by_level:
                    alerts_by_level[alert.level] += 1
            
            # Generate summary
            total_alerts = len(all_alerts)
            if total_alerts == 0:
                summary = "All data is fresh and up to date."
            else:
                critical_count = alerts_by_level[DataStalenessLevel.CRITICAL]
                stale_count = alerts_by_level[DataStalenessLevel.STALE]
                warning_count = alerts_by_level[DataStalenessLevel.WARNING]
                
                summary_parts = []
                if critical_count > 0:
                    summary_parts.append(f"{critical_count} critical")
                if stale_count > 0:
                    summary_parts.append(f"{stale_count} stale")
                if warning_count > 0:
                    summary_parts.append(f"{warning_count} warning")
                
                summary = f"Found {total_alerts} data staleness issues: {', '.join(summary_parts)}."
            
            # Generate recommendations
            recommendations = self._generate_recommendations(all_alerts)
            
            report = DataFreshnessReport(
                report_date=datetime.now(),
                total_alerts=total_alerts,
                alerts_by_level=alerts_by_level,
                alerts=all_alerts,
                summary=summary,
                recommendations=recommendations
            )
            
            self.logger.info(f"Generated staleness report with {total_alerts} alerts")
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating staleness report: {e}")
            return DataFreshnessReport(
                report_date=datetime.now(),
                total_alerts=0,
                alerts_by_level={},
                alerts=[],
                summary="Error generating report",
                recommendations=["Check system logs for errors"]
            )
    
    def get_fallback_fuel_price(
        self, 
        fuel_type: str, 
        region: str = "NEA"
    ) -> Decimal:
        """
        Get fallback fuel price when current data is stale.
        
        Args:
            fuel_type: Type of fuel
            region: Region code
            
        Returns:
            Fallback fuel price
        """
        try:
            # Try to get most recent price even if stale
            recent_price = self.db.query(FuelPrice).filter(
                and_(
                    FuelPrice.fuel_type == fuel_type,
                    FuelPrice.region == region
                )
            ).order_by(FuelPrice.effective_date.desc()).first()
            
            if recent_price:
                days_old = (date.today() - recent_price.effective_date).days
                if days_old <= 90:  # Use recent price if not too old
                    self.logger.warning(
                        f"Using {days_old}-day-old price for {fuel_type} in {region}: "
                        f"${recent_price.price_per_liter}"
                    )
                    return recent_price.price_per_liter
            
            # Use default fallback
            fallback_price = self.default_fuel_prices.get(
                fuel_type, 
                self.default_fuel_prices["diesel_500"]
            )
            
            self.logger.warning(
                f"Using default fallback price for {fuel_type} in {region}: ${fallback_price}"
            )
            return fallback_price
            
        except Exception as e:
            self.logger.error(f"Error getting fallback fuel price: {e}")
            return self.default_fuel_prices["diesel_500"]
    
    def get_fallback_toll_tariff(self, road_name: str, region: str = "NEA") -> Decimal:
        """
        Get fallback toll tariff when current data is stale.
        
        Args:
            road_name: Road name
            region: Region code
            
        Returns:
            Fallback toll tariff
        """
        try:
            # Try to get average tariff for similar roads
            avg_tariff = self.db.query(func.avg(Toll.tariff)).filter(
                and_(
                    Toll.road_name == road_name,
                    Toll.is_active == True
                )
            ).scalar()
            
            if avg_tariff and avg_tariff > 0:
                self.logger.warning(
                    f"Using average tariff for {road_name}: ${avg_tariff}"
                )
                return Decimal(str(avg_tariff))
            
            # Use default fallback
            self.logger.warning(
                f"Using default fallback tariff for {road_name}: ${self.default_toll_tariff}"
            )
            return self.default_toll_tariff
            
        except Exception as e:
            self.logger.error(f"Error getting fallback toll tariff: {e}")
            return self.default_toll_tariff
    
    def _get_staleness_level(self, data_type: str, days_old: int) -> DataStalenessLevel:
        """
        Determine staleness level based on data type and age.
        
        Args:
            data_type: Type of data
            days_old: Age in days
            
        Returns:
            Staleness level
        """
        thresholds = self.thresholds.get(data_type, self.thresholds["fuel_price"])
        
        if days_old >= thresholds[DataStalenessLevel.CRITICAL]:
            return DataStalenessLevel.CRITICAL
        elif days_old >= thresholds[DataStalenessLevel.STALE]:
            return DataStalenessLevel.STALE
        elif days_old >= thresholds[DataStalenessLevel.WARNING]:
            return DataStalenessLevel.WARNING
        else:
            return DataStalenessLevel.FRESH
    
    def _get_fuel_price_recommendation(self, level: DataStalenessLevel, days_old: int) -> str:
        """Get recommendation for fuel price staleness."""
        if level == DataStalenessLevel.CRITICAL:
            return f"URGENT: Update fuel price immediately (data is {days_old} days old)"
        elif level == DataStalenessLevel.STALE:
            return f"Update fuel price soon (data is {days_old} days old)"
        elif level == DataStalenessLevel.WARNING:
            return f"Consider updating fuel price (data is {days_old} days old)"
        else:
            return "Data is fresh"
    
    def _get_toll_recommendation(self, level: DataStalenessLevel, days_old: int) -> str:
        """Get recommendation for toll staleness."""
        if level == DataStalenessLevel.CRITICAL:
            return f"URGENT: Verify toll information (data is {days_old} days old)"
        elif level == DataStalenessLevel.STALE:
            return f"Review toll information (data is {days_old} days old)"
        elif level == DataStalenessLevel.WARNING:
            return f"Consider reviewing toll information (data is {days_old} days old)"
        else:
            return "Data is fresh"
    
    def _generate_recommendations(self, alerts: List[StalenessAlert]) -> List[str]:
        """
        Generate actionable recommendations based on alerts.
        
        Args:
            alerts: List of staleness alerts
            
        Returns:
            List of recommendations
        """
        if not alerts:
            return ["All data is up to date. No action required."]
        
        recommendations = []
        
        # Count by type and level
        fuel_critical = len([a for a in alerts if a.data_type == "fuel_price" and a.level == DataStalenessLevel.CRITICAL])
        fuel_stale = len([a for a in alerts if a.data_type == "fuel_price" and a.level == DataStalenessLevel.STALE])
        toll_critical = len([a for a in alerts if a.data_type == "toll" and a.level == DataStalenessLevel.CRITICAL])
        toll_stale = len([a for a in alerts if a.data_type == "toll" and a.level == DataStalenessLevel.STALE])
        
        # Priority recommendations
        if fuel_critical > 0:
            recommendations.append(
                f"PRIORITY: Update {fuel_critical} critical fuel price(s) immediately"
            )
        
        if toll_critical > 0:
            recommendations.append(
                f"PRIORITY: Verify {toll_critical} critical toll(s) immediately"
            )
        
        if fuel_stale > 0:
            recommendations.append(
                f"Update {fuel_stale} stale fuel price(s) within the next few days"
            )
        
        if toll_stale > 0:
            recommendations.append(
                f"Review {toll_stale} stale toll(s) when convenient"
            )
        
        # General recommendations
        recommendations.append("Set up automated data refresh processes")
        recommendations.append("Consider implementing data source monitoring")
        recommendations.append("Review data update procedures with team")
        
        return recommendations
    
    def get_data_health_summary(self) -> Dict[str, Any]:
        """
        Get overall data health summary.
        
        Returns:
            Data health summary
        """
        try:
            # Count total records
            total_fuel_prices = self.db.query(FuelPrice).filter(FuelPrice.is_active == True).count()
            total_tolls = self.db.query(Toll).filter(Toll.is_active == True).count()
            
            # Count fresh records (last 30 days for fuel, 90 days for tolls)
            fresh_fuel_date = date.today() - timedelta(days=30)
            fresh_toll_date = datetime.now() - timedelta(days=90)
            
            fresh_fuel_prices = self.db.query(FuelPrice).filter(
                and_(
                    FuelPrice.is_active == True,
                    FuelPrice.effective_date >= fresh_fuel_date
                )
            ).count()
            
            fresh_tolls = self.db.query(Toll).filter(
                and_(
                    Toll.is_active == True,
                    Toll.updated_at >= fresh_toll_date
                )
            ).count()
            
            # Calculate percentages
            fuel_freshness = (fresh_fuel_prices / total_fuel_prices * 100) if total_fuel_prices > 0 else 100
            toll_freshness = (fresh_tolls / total_tolls * 100) if total_tolls > 0 else 100
            overall_freshness = (fuel_freshness + toll_freshness) / 2
            
            # Determine health status
            if overall_freshness >= 90:
                health_status = "excellent"
            elif overall_freshness >= 75:
                health_status = "good"
            elif overall_freshness >= 50:
                health_status = "fair"
            else:
                health_status = "poor"
            
            return {
                "health_status": health_status,
                "overall_freshness_percentage": round(overall_freshness, 1),
                "fuel_prices": {
                    "total": total_fuel_prices,
                    "fresh": fresh_fuel_prices,
                    "freshness_percentage": round(fuel_freshness, 1)
                },
                "tolls": {
                    "total": total_tolls,
                    "fresh": fresh_tolls,
                    "freshness_percentage": round(toll_freshness, 1)
                },
                "last_checked": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting data health summary: {e}")
            return {
                "health_status": "unknown",
                "error": str(e),
                "last_checked": datetime.now().isoformat()
            }