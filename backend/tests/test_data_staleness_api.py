"""
Tests for data staleness alert API endpoints.
"""
import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import uuid

from app.main import app
from app.models.user import UserRole
from app.services.data_staleness_service import (
    DataStalenessLevel,
    StalenessAlert,
    DataFreshnessReport
)


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_admin_user():
    """Mock admin user."""
    user = MagicMock()
    user.id = str(uuid.uuid4())
    user.role = UserRole.ADMIN
    user.company_id = str(uuid.uuid4())
    return user


@pytest.fixture
def mock_regular_user():
    """Mock regular user (non-admin)."""
    user = MagicMock()
    user.id = str(uuid.uuid4())
    user.role = UserRole.OPERATOR
    user.company_id = str(uuid.uuid4())
    return user


@pytest.fixture
def mock_db():
    """Mock database session."""
    return MagicMock()


@pytest.fixture
def sample_staleness_alert():
    """Sample staleness alert."""
    return StalenessAlert(
        data_type="fuel_price",
        identifier="diesel_500_NEA",
        description="diesel_500 price in NEA",
        level=DataStalenessLevel.STALE,
        days_old=45,
        last_updated=datetime.now() - timedelta(days=45),
        recommended_action="Update fuel price soon",
        fallback_value=150.00
    )


@pytest.fixture
def sample_staleness_report(sample_staleness_alert):
    """Sample staleness report."""
    return DataFreshnessReport(
        report_date=datetime.now(),
        total_alerts=1,
        alerts_by_level={DataStalenessLevel.STALE: 1},
        alerts=[sample_staleness_alert],
        summary="Found 1 data staleness issue: 1 stale.",
        recommendations=["Update 1 stale fuel price(s) within the next few days"]
    )


class TestDataHealthEndpoints:
    """Test cases for data health endpoints."""
    
    @patch('app.api.admin.get_current_active_user')
    @patch('app.api.admin.get_db')
    @patch('app.api.admin.DataStalenessService')
    def test_get_data_health_summary_success(
        self,
        mock_staleness_service,
        mock_get_db,
        mock_get_user,
        client,
        mock_admin_user,
        mock_db
    ):
        """Test successful data health summary retrieval."""
        mock_get_user.return_value = mock_admin_user
        mock_get_db.return_value = mock_db
        
        # Mock service response
        mock_service_instance = MagicMock()
        mock_health_summary = {
            "health_status": "good",
            "overall_freshness_percentage": 85.5,
            "fuel_prices": {
                "total": 10,
                "fresh": 8,
                "freshness_percentage": 80.0
            },
            "tolls": {
                "total": 20,
                "fresh": 18,
                "freshness_percentage": 90.0
            },
            "last_checked": datetime.now().isoformat()
        }
        mock_service_instance.get_data_health_summary.return_value = mock_health_summary
        mock_staleness_service.return_value = mock_service_instance
        
        response = client.get("/api/admin/data-health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["health_status"] == "good"
        assert data["overall_freshness_percentage"] == 85.5
        assert data["fuel_prices"]["total"] == 10
        assert data["tolls"]["total"] == 20
    
    @patch('app.api.admin.get_current_active_user')
    @patch('app.api.admin.get_db')
    def test_get_data_health_summary_non_admin_forbidden(
        self,
        mock_get_db,
        mock_get_user,
        client,
        mock_regular_user,
        mock_db
    ):
        """Test data health summary access denied for non-admin users."""
        mock_get_user.return_value = mock_regular_user
        mock_get_db.return_value = mock_db
        
        response = client.get("/api/admin/data-health")
        assert response.status_code == 403
        assert "Admin access required" in response.json()["detail"]
    
    @patch('app.api.admin.get_current_active_user')
    @patch('app.api.admin.get_db')
    @patch('app.api.admin.DataStalenessService')
    def test_get_staleness_report_success(
        self,
        mock_staleness_service,
        mock_get_db,
        mock_get_user,
        client,
        mock_admin_user,
        mock_db,
        sample_staleness_report
    ):
        """Test successful staleness report retrieval."""
        mock_get_user.return_value = mock_admin_user
        mock_get_db.return_value = mock_db
        
        # Mock service response
        mock_service_instance = MagicMock()
        mock_service_instance.generate_staleness_report.return_value = sample_staleness_report
        mock_staleness_service.return_value = mock_service_instance
        
        response = client.get("/api/admin/staleness-report?fuel_price_threshold=30&toll_threshold=180")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_alerts"] == 1
        assert "stale" in data["alerts_by_level"]
        assert data["alerts_by_level"]["stale"] == 1
        assert len(data["alerts"]) == 1
        assert data["alerts"][0]["data_type"] == "fuel_price"
        assert data["alerts"][0]["level"] == "stale"
    
    @patch('app.api.admin.get_current_active_user')
    @patch('app.api.admin.get_db')
    @patch('app.api.admin.DataStalenessService')
    def test_get_fuel_price_alerts_success(
        self,
        mock_staleness_service,
        mock_get_db,
        mock_get_user,
        client,
        mock_admin_user,
        mock_db,
        sample_staleness_alert
    ):
        """Test successful fuel price alerts retrieval."""
        mock_get_user.return_value = mock_admin_user
        mock_get_db.return_value = mock_db
        
        # Mock service response
        mock_service_instance = MagicMock()
        mock_service_instance.check_fuel_price_staleness.return_value = [sample_staleness_alert]
        mock_staleness_service.return_value = mock_service_instance
        
        response = client.get("/api/admin/alerts/fuel-prices?threshold_days=30&fuel_type=diesel_500")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["data_type"] == "fuel_price"
        assert data[0]["identifier"] == "diesel_500_NEA"
        assert data[0]["level"] == "stale"
        assert data[0]["days_old"] == 45
    
    @patch('app.api.admin.get_current_active_user')
    @patch('app.api.admin.get_db')
    @patch('app.api.admin.DataStalenessService')
    def test_get_fuel_price_alerts_with_level_filter(
        self,
        mock_staleness_service,
        mock_get_db,
        mock_get_user,
        client,
        mock_admin_user,
        mock_db
    ):
        """Test fuel price alerts with level filtering."""
        mock_get_user.return_value = mock_admin_user
        mock_get_db.return_value = mock_db
        
        # Create alerts with different levels
        stale_alert = StalenessAlert(
            data_type="fuel_price",
            identifier="diesel_500_NEA",
            description="diesel_500 price in NEA",
            level=DataStalenessLevel.STALE,
            days_old=45,
            last_updated=datetime.now(),
            recommended_action="Update soon"
        )
        
        critical_alert = StalenessAlert(
            data_type="fuel_price",
            identifier="diesel_premium_NEA",
            description="diesel_premium price in NEA",
            level=DataStalenessLevel.CRITICAL,
            days_old=70,
            last_updated=datetime.now(),
            recommended_action="Update immediately"
        )
        
        # Mock service response
        mock_service_instance = MagicMock()
        mock_service_instance.check_fuel_price_staleness.return_value = [stale_alert, critical_alert]
        mock_staleness_service.return_value = mock_service_instance
        
        # Test filtering by critical level
        response = client.get("/api/admin/alerts/fuel-prices?level=critical")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["level"] == "critical"
        assert data[0]["identifier"] == "diesel_premium_NEA"
    
    @patch('app.api.admin.get_current_active_user')
    @patch('app.api.admin.get_db')
    @patch('app.api.admin.DataStalenessService')
    def test_get_toll_alerts_success(
        self,
        mock_staleness_service,
        mock_get_db,
        mock_get_user,
        client,
        mock_admin_user,
        mock_db
    ):
        """Test successful toll alerts retrieval."""
        mock_get_user.return_value = mock_admin_user
        mock_get_db.return_value = mock_db
        
        toll_alert = StalenessAlert(
            data_type="toll",
            identifier="RN12_Peaje Posadas",
            description="Peaje Posadas on RN12",
            level=DataStalenessLevel.STALE,
            days_old=200,
            last_updated=datetime.now() - timedelta(days=200),
            recommended_action="Review toll information",
            fallback_value=90.00
        )
        
        # Mock service response
        mock_service_instance = MagicMock()
        mock_service_instance.check_toll_staleness.return_value = [toll_alert]
        mock_staleness_service.return_value = mock_service_instance
        
        response = client.get("/api/admin/alerts/tolls?threshold_days=180&road_name=RN12")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["data_type"] == "toll"
        assert data[0]["identifier"] == "RN12_Peaje Posadas"
        assert data[0]["level"] == "stale"
        assert data[0]["days_old"] == 200
    
    @patch('app.api.admin.get_current_active_user')
    @patch('app.api.admin.get_db')
    @patch('app.api.admin.DataStalenessService')
    def test_get_fallback_values_success(
        self,
        mock_staleness_service,
        mock_get_db,
        mock_get_user,
        client,
        mock_admin_user,
        mock_db
    ):
        """Test successful fallback values retrieval."""
        mock_get_user.return_value = mock_admin_user
        mock_get_db.return_value = mock_db
        
        # Mock service instance with default values
        mock_service_instance = MagicMock()
        mock_service_instance.default_fuel_prices = {
            "diesel_500": 150.00,
            "diesel_premium": 165.00
        }
        mock_service_instance.default_toll_tariff = 90.00
        mock_service_instance.thresholds = {
            "fuel_price": {
                DataStalenessLevel.WARNING: 15,
                DataStalenessLevel.STALE: 30,
                DataStalenessLevel.CRITICAL: 60
            }
        }
        mock_staleness_service.return_value = mock_service_instance
        
        response = client.get("/api/admin/fallback-values")
        
        assert response.status_code == 200
        data = response.json()
        assert "fuel_prices" in data
        assert "toll_tariff" in data
        assert "staleness_thresholds" in data
        assert data["fuel_prices"]["diesel_500"] == 150.00
        assert data["toll_tariff"] == 90.00
    
    @patch('app.api.admin.get_current_active_user')
    @patch('app.api.admin.get_db')
    def test_acknowledge_alerts_success(
        self,
        mock_get_db,
        mock_get_user,
        client,
        mock_admin_user,
        mock_db
    ):
        """Test successful alert acknowledgment."""
        mock_get_user.return_value = mock_admin_user
        mock_get_db.return_value = mock_db
        
        alert_identifiers = ["diesel_500_NEA", "RN12_Peaje Posadas"]
        
        response = client.post("/api/admin/alerts/acknowledge", json=alert_identifiers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["acknowledged_alerts"] == alert_identifiers
        assert data["acknowledged_by"] == str(mock_admin_user.id)
        assert "Acknowledged 2 alerts" in data["message"]
    
    @patch('app.api.admin.get_current_active_user')
    @patch('app.api.admin.get_db')
    def test_trigger_data_refresh_success(
        self,
        mock_get_db,
        mock_get_user,
        client,
        mock_admin_user,
        mock_db
    ):
        """Test successful data refresh trigger."""
        mock_get_user.return_value = mock_admin_user
        mock_get_db.return_value = mock_db
        
        data_types = ["fuel_prices", "tolls"]
        
        response = client.post("/api/admin/data-refresh/trigger", json=data_types)
        
        assert response.status_code == 200
        data = response.json()
        assert "Data refresh triggered" in data["message"]
        assert data["triggered_by"] == str(mock_admin_user.id)
        assert "refresh_results" in data
        assert "fuel_prices" in data["refresh_results"]
        assert "tolls" in data["refresh_results"]
    
    @patch('app.api.admin.get_current_active_user')
    @patch('app.api.admin.get_db')
    def test_trigger_data_refresh_all_types(
        self,
        mock_get_db,
        mock_get_user,
        client,
        mock_admin_user,
        mock_db
    ):
        """Test data refresh trigger for all data types."""
        mock_get_user.return_value = mock_admin_user
        mock_get_db.return_value = mock_db
        
        data_types = ["all"]
        
        response = client.post("/api/admin/data-refresh/trigger", json=data_types)
        
        assert response.status_code == 200
        data = response.json()
        assert "refresh_results" in data
        assert "fuel_prices" in data["refresh_results"]
        assert "tolls" in data["refresh_results"]
    
    @patch('app.api.admin.get_current_active_user')
    @patch('app.api.admin.get_db')
    def test_alerts_endpoints_non_admin_forbidden(
        self,
        mock_get_db,
        mock_get_user,
        client,
        mock_regular_user,
        mock_db
    ):
        """Test that all alert endpoints deny access to non-admin users."""
        mock_get_user.return_value = mock_regular_user
        mock_get_db.return_value = mock_db
        
        endpoints = [
            "/api/admin/staleness-report",
            "/api/admin/alerts/fuel-prices",
            "/api/admin/alerts/tolls",
            "/api/admin/fallback-values"
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == 403
            assert "Admin access required" in response.json()["detail"]
        
        # Test POST endpoints
        post_endpoints = [
            ("/api/admin/alerts/acknowledge", ["alert1"]),
            ("/api/admin/data-refresh/trigger", ["fuel_prices"])
        ]
        
        for endpoint, data in post_endpoints:
            response = client.post(endpoint, json=data)
            assert response.status_code == 403
            assert "Admin access required" in response.json()["detail"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])