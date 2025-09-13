"""
Tests for data staleness monitoring service.
"""
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, date, timedelta
from decimal import Decimal

from app.services.data_staleness_service import (
    DataStalenessService,
    DataStalenessLevel,
    StalenessAlert,
    DataFreshnessReport
)


@pytest.fixture
def mock_db():
    """Mock database session."""
    return MagicMock()


@pytest.fixture
def staleness_service(mock_db):
    """Create staleness service with mock database."""
    return DataStalenessService(mock_db)


@pytest.fixture
def sample_stale_fuel_price():
    """Sample stale fuel price."""
    price = MagicMock()
    price.id = 1
    price.fuel_type = "diesel_500"
    price.region = "NEA"
    price.price_per_liter = Decimal("150.00")
    price.effective_date = date.today() - timedelta(days=45)  # 45 days old
    price.is_active = True
    price.updated_at = datetime.now() - timedelta(days=45)
    return price


@pytest.fixture
def sample_stale_toll():
    """Sample stale toll."""
    toll = MagicMock()
    toll.id = 1
    toll.name = "Peaje Posadas"
    toll.road_name = "RN12"
    toll.latitude = -27.3621
    toll.longitude = -55.8959
    toll.tariff = Decimal("90.00")
    toll.region = "NEA"
    toll.is_active = True
    toll.created_at = datetime.now() - timedelta(days=200)
    toll.updated_at = datetime.now() - timedelta(days=200)  # 200 days old
    return toll


class TestDataStalenessService:
    """Test cases for data staleness service."""
    
    def test_init(self, mock_db):
        """Test service initialization."""
        service = DataStalenessService(mock_db)
        
        assert service.db == mock_db
        assert "fuel_price" in service.thresholds
        assert "toll" in service.thresholds
        assert "diesel_500" in service.default_fuel_prices
        assert service.default_toll_tariff > 0
    
    def test_check_fuel_price_staleness_no_stale_data(self, staleness_service, mock_db):
        """Test fuel price staleness check with no stale data."""
        # Mock query returning no stale prices
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = []
        mock_db.query.return_value = mock_query
        
        alerts = staleness_service.check_fuel_price_staleness(threshold_days=30)
        
        assert alerts == []
        mock_db.query.assert_called_once()
    
    def test_check_fuel_price_staleness_with_stale_data(
        self, 
        staleness_service, 
        mock_db, 
        sample_stale_fuel_price
    ):
        """Test fuel price staleness check with stale data."""
        # Mock query returning stale price
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [sample_stale_fuel_price]
        mock_db.query.return_value = mock_query
        
        alerts = staleness_service.check_fuel_price_staleness(threshold_days=30)
        
        assert len(alerts) == 1
        alert = alerts[0]
        assert alert.data_type == "fuel_price"
        assert alert.identifier == "diesel_500_NEA"
        assert alert.level == DataStalenessLevel.STALE
        assert alert.days_old == 45
        assert alert.fallback_value == 150.00
    
    def test_check_toll_staleness_no_stale_data(self, staleness_service, mock_db):
        """Test toll staleness check with no stale data."""
        # Mock query returning no stale tolls
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = []
        mock_db.query.return_value = mock_query
        
        alerts = staleness_service.check_toll_staleness(threshold_days=180)
        
        assert alerts == []
        mock_db.query.assert_called_once()
    
    def test_check_toll_staleness_with_stale_data(
        self, 
        staleness_service, 
        mock_db, 
        sample_stale_toll
    ):
        """Test toll staleness check with stale data."""
        # Mock query returning stale toll
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [sample_stale_toll]
        mock_db.query.return_value = mock_query
        
        alerts = staleness_service.check_toll_staleness(threshold_days=180)
        
        assert len(alerts) == 1
        alert = alerts[0]
        assert alert.data_type == "toll"
        assert alert.identifier == "RN12_Peaje Posadas"
        assert alert.level == DataStalenessLevel.STALE
        assert alert.days_old == 200
        assert alert.fallback_value == 90.00
    
    def test_generate_staleness_report_no_alerts(self, staleness_service):
        """Test staleness report generation with no alerts."""
        with patch.object(staleness_service, 'check_fuel_price_staleness', return_value=[]):
            with patch.object(staleness_service, 'check_toll_staleness', return_value=[]):
                report = staleness_service.generate_staleness_report()
                
                assert report.total_alerts == 0
                assert "All data is fresh" in report.summary
                assert len(report.recommendations) == 1
                assert "No action required" in report.recommendations[0]
    
    def test_generate_staleness_report_with_alerts(
        self, 
        staleness_service,
        sample_stale_fuel_price,
        sample_stale_toll
    ):
        """Test staleness report generation with alerts."""
        # Create mock alerts
        fuel_alert = StalenessAlert(
            data_type="fuel_price",
            identifier="diesel_500_NEA",
            description="diesel_500 price in NEA",
            level=DataStalenessLevel.STALE,
            days_old=45,
            last_updated=datetime.now() - timedelta(days=45),
            recommended_action="Update fuel price soon",
            fallback_value=150.00
        )
        
        toll_alert = StalenessAlert(
            data_type="toll",
            identifier="RN12_Peaje Posadas",
            description="Peaje Posadas on RN12",
            level=DataStalenessLevel.CRITICAL,
            days_old=200,
            last_updated=datetime.now() - timedelta(days=200),
            recommended_action="URGENT: Verify toll information",
            fallback_value=90.00
        )
        
        with patch.object(staleness_service, 'check_fuel_price_staleness', return_value=[fuel_alert]):
            with patch.object(staleness_service, 'check_toll_staleness', return_value=[toll_alert]):
                report = staleness_service.generate_staleness_report()
                
                assert report.total_alerts == 2
                assert report.alerts_by_level[DataStalenessLevel.STALE] == 1
                assert report.alerts_by_level[DataStalenessLevel.CRITICAL] == 1
                assert "2 data staleness issues" in report.summary
                assert len(report.recommendations) > 1
    
    def test_get_staleness_level(self, staleness_service):
        """Test staleness level determination."""
        # Test fuel price levels
        assert staleness_service._get_staleness_level("fuel_price", 10) == DataStalenessLevel.FRESH
        assert staleness_service._get_staleness_level("fuel_price", 20) == DataStalenessLevel.WARNING
        assert staleness_service._get_staleness_level("fuel_price", 40) == DataStalenessLevel.STALE
        assert staleness_service._get_staleness_level("fuel_price", 70) == DataStalenessLevel.CRITICAL
        
        # Test toll levels
        assert staleness_service._get_staleness_level("toll", 60) == DataStalenessLevel.FRESH
        assert staleness_service._get_staleness_level("toll", 120) == DataStalenessLevel.WARNING
        assert staleness_service._get_staleness_level("toll", 200) == DataStalenessLevel.STALE
        assert staleness_service._get_staleness_level("toll", 400) == DataStalenessLevel.CRITICAL
    
    def test_get_fallback_fuel_price_with_recent_data(self, staleness_service, mock_db):
        """Test fallback fuel price with recent data available."""
        # Mock recent price (within 90 days)
        recent_price = MagicMock()
        recent_price.price_per_liter = Decimal("155.00")
        recent_price.effective_date = date.today() - timedelta(days=60)
        
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.first.return_value = recent_price
        mock_db.query.return_value = mock_query
        
        fallback_price = staleness_service.get_fallback_fuel_price("diesel_500", "NEA")
        
        assert fallback_price == Decimal("155.00")
    
    def test_get_fallback_fuel_price_no_recent_data(self, staleness_service, mock_db):
        """Test fallback fuel price with no recent data."""
        # Mock no recent price
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.first.return_value = None
        mock_db.query.return_value = mock_query
        
        fallback_price = staleness_service.get_fallback_fuel_price("diesel_500", "NEA")
        
        assert fallback_price == staleness_service.default_fuel_prices["diesel_500"]
    
    def test_get_fallback_toll_tariff_with_average(self, staleness_service, mock_db):
        """Test fallback toll tariff with average available."""
        # Mock average tariff query
        mock_db.query.return_value.filter.return_value.scalar.return_value = 95.50
        
        fallback_tariff = staleness_service.get_fallback_toll_tariff("RN12", "NEA")
        
        assert fallback_tariff == Decimal("95.50")
    
    def test_get_fallback_toll_tariff_no_average(self, staleness_service, mock_db):
        """Test fallback toll tariff with no average available."""
        # Mock no average tariff
        mock_db.query.return_value.filter.return_value.scalar.return_value = None
        
        fallback_tariff = staleness_service.get_fallback_toll_tariff("RN12", "NEA")
        
        assert fallback_tariff == staleness_service.default_toll_tariff
    
    def test_get_data_health_summary(self, staleness_service, mock_db):
        """Test data health summary generation."""
        # Mock database counts
        mock_db.query.return_value.filter.return_value.count.side_effect = [10, 5, 8, 6]  # total_fuel, fresh_fuel, total_toll, fresh_toll
        
        health_summary = staleness_service.get_data_health_summary()
        
        assert "health_status" in health_summary
        assert "overall_freshness_percentage" in health_summary
        assert "fuel_prices" in health_summary
        assert "tolls" in health_summary
        assert health_summary["fuel_prices"]["total"] == 10
        assert health_summary["fuel_prices"]["fresh"] == 5
        assert health_summary["tolls"]["total"] == 8
        assert health_summary["tolls"]["fresh"] == 6
    
    def test_fuel_price_recommendation_messages(self, staleness_service):
        """Test fuel price recommendation messages."""
        critical_rec = staleness_service._get_fuel_price_recommendation(DataStalenessLevel.CRITICAL, 70)
        assert "URGENT" in critical_rec
        assert "70 days old" in critical_rec
        
        stale_rec = staleness_service._get_fuel_price_recommendation(DataStalenessLevel.STALE, 40)
        assert "Update fuel price soon" in stale_rec
        assert "40 days old" in stale_rec
        
        warning_rec = staleness_service._get_fuel_price_recommendation(DataStalenessLevel.WARNING, 20)
        assert "Consider updating" in warning_rec
        assert "20 days old" in warning_rec
        
        fresh_rec = staleness_service._get_fuel_price_recommendation(DataStalenessLevel.FRESH, 5)
        assert "Data is fresh" in fresh_rec
    
    def test_toll_recommendation_messages(self, staleness_service):
        """Test toll recommendation messages."""
        critical_rec = staleness_service._get_toll_recommendation(DataStalenessLevel.CRITICAL, 400)
        assert "URGENT" in critical_rec
        assert "400 days old" in critical_rec
        
        stale_rec = staleness_service._get_toll_recommendation(DataStalenessLevel.STALE, 200)
        assert "Review toll information" in stale_rec
        assert "200 days old" in stale_rec
        
        warning_rec = staleness_service._get_toll_recommendation(DataStalenessLevel.WARNING, 120)
        assert "Consider reviewing" in warning_rec
        assert "120 days old" in warning_rec
        
        fresh_rec = staleness_service._get_toll_recommendation(DataStalenessLevel.FRESH, 30)
        assert "Data is fresh" in fresh_rec
    
    def test_generate_recommendations_priority_order(self, staleness_service):
        """Test that recommendations are generated in priority order."""
        alerts = [
            StalenessAlert(
                data_type="fuel_price",
                identifier="diesel_500_NEA",
                description="diesel_500 price in NEA",
                level=DataStalenessLevel.CRITICAL,
                days_old=70,
                last_updated=datetime.now(),
                recommended_action="Update immediately"
            ),
            StalenessAlert(
                data_type="toll",
                identifier="RN12_Peaje",
                description="Peaje on RN12",
                level=DataStalenessLevel.STALE,
                days_old=200,
                last_updated=datetime.now(),
                recommended_action="Review soon"
            )
        ]
        
        recommendations = staleness_service._generate_recommendations(alerts)
        
        # Critical fuel price should be first priority
        assert "PRIORITY" in recommendations[0]
        assert "critical fuel price" in recommendations[0]
        
        # Should include general recommendations
        assert any("automated data refresh" in rec for rec in recommendations)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])