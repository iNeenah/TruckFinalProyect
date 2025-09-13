"""
Tests for administrative panel API endpoints.
"""
import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from datetime import datetime, date, timedelta
from decimal import Decimal
import uuid

from app.main import app
from app.models.user import UserRole


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
def sample_fuel_price():
    """Sample fuel price object."""
    price = MagicMock()
    price.id = 1
    price.fuel_type = "diesel_500"
    price.region = "NEA"
    price.price_per_liter = Decimal("150.00")
    price.effective_date = date.today()
    price.is_active = True
    price.created_at = datetime.now()
    price.updated_at = datetime.now()
    price.updated_by = "admin-user-id"
    return price


class TestFuelPriceManagementEndpoints:
    """Test cases for fuel price management endpoints."""
    
    @patch('app.api.admin.get_current_active_user')
    @patch('app.api.admin.get_db')
    def test_get_fuel_prices_success(
        self,
        mock_get_db,
        mock_get_user,
        client,
        mock_admin_user,
        mock_db,
        sample_fuel_price
    ):
        """Test successful fuel prices retrieval."""
        mock_get_user.return_value = mock_admin_user
        mock_get_db.return_value = mock_db
        
        # Mock database query
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = [sample_fuel_price]
        mock_db.query.return_value = mock_query
        
        response = client.get("/api/admin/fuel-prices")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["fuel_type"] == "diesel_500"
        assert data[0]["region"] == "NEA"
        assert float(data[0]["price_per_liter"]) == 150.00
    
    @patch('app.api.admin.get_current_active_user')
    @patch('app.api.admin.get_db')
    def test_get_fuel_prices_non_admin_forbidden(
        self,
        mock_get_db,
        mock_get_user,
        client,
        mock_regular_user,
        mock_db
    ):
        """Test fuel prices access denied for non-admin users."""
        mock_get_user.return_value = mock_regular_user
        mock_get_db.return_value = mock_db
        
        response = client.get("/api/admin/fuel-prices")
        assert response.status_code == 403
        assert "Admin access required" in response.json()["detail"]
    
    @patch('app.api.admin.get_current_active_user')
    @patch('app.api.admin.get_db')
    def test_get_fuel_prices_with_filters(
        self,
        mock_get_db,
        mock_get_user,
        client,
        mock_admin_user,
        mock_db,
        sample_fuel_price
    ):
        """Test fuel prices retrieval with filters."""
        mock_get_user.return_value = mock_admin_user
        mock_get_db.return_value = mock_db
        
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = [sample_fuel_price]
        mock_db.query.return_value = mock_query
        
        response = client.get("/api/admin/fuel-prices?fuel_type=diesel_500&region=NEA&active_only=true")
        
        assert response.status_code == 200
        # Verify filters were applied
        assert mock_query.filter.call_count >= 3  # fuel_type, region, active_only
    
    @patch('app.api.admin.get_current_active_user')
    @patch('app.api.admin.get_db')
    def test_update_fuel_price_success(
        self,
        mock_get_db,
        mock_get_user,
        client,
        mock_admin_user,
        mock_db,
        sample_fuel_price
    ):
        """Test successful fuel price update."""
        mock_get_user.return_value = mock_admin_user
        mock_get_db.return_value = mock_db
        
        # Mock database query to find existing price
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = sample_fuel_price
        mock_db.query.return_value = mock_query
        
        update_data = {
            "price_per_liter": 155.50,
            "effective_date": date.today().isoformat(),
            "is_active": True
        }
        
        response = client.put("/api/admin/fuel-prices/1", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert float(data["price_per_liter"]) == 155.50
        
        # Verify database operations
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
    
    @patch('app.api.admin.get_current_active_user')
    @patch('app.api.admin.get_db')
    def test_update_fuel_price_not_found(
        self,
        mock_get_db,
        mock_get_user,
        client,
        mock_admin_user,
        mock_db
    ):
        """Test fuel price update for non-existent price."""
        mock_get_user.return_value = mock_admin_user
        mock_get_db.return_value = mock_db
        
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None  # Price not found
        mock_db.query.return_value = mock_query
        
        update_data = {
            "price_per_liter": 155.50,
            "effective_date": date.today().isoformat()
        }
        
        response = client.put("/api/admin/fuel-prices/999", json=update_data)
        assert response.status_code == 404
        assert "Fuel price not found" in response.json()["detail"]
    
    @patch('app.api.admin.get_current_active_user')
    @patch('app.api.admin.get_db')
    def test_update_fuel_price_invalid_data(
        self,
        mock_get_db,
        mock_get_user,
        client,
        mock_admin_user,
        mock_db,
        sample_fuel_price
    ):
        """Test fuel price update with invalid data."""
        mock_get_user.return_value = mock_admin_user
        mock_get_db.return_value = mock_db
        
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = sample_fuel_price
        mock_db.query.return_value = mock_query
        
        # Invalid price (negative)
        update_data = {
            "price_per_liter": -10.00,
            "effective_date": date.today().isoformat()
        }
        
        response = client.put("/api/admin/fuel-prices/1", json=update_data)
        assert response.status_code == 400
        assert "must be greater than zero" in response.json()["detail"]
    
    @patch('app.api.admin.get_current_active_user')
    @patch('app.api.admin.get_db')
    def test_get_fuel_price_history_success(
        self,
        mock_get_db,
        mock_get_user,
        client,
        mock_admin_user,
        mock_db,
        sample_fuel_price
    ):
        """Test successful fuel price history retrieval."""
        mock_get_user.return_value = mock_admin_user
        mock_get_db.return_value = mock_db
        
        # Mock finding the fuel price
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = sample_fuel_price
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = [sample_fuel_price]
        mock_db.query.return_value = mock_query
        
        response = client.get("/api/admin/fuel-prices/1/history?days=30")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == 1
        assert float(data[0]["price_per_liter"]) == 150.00
    
    @patch('app.api.admin.get_current_active_user')
    @patch('app.api.admin.get_db')
    def test_get_audit_log_success(
        self,
        mock_get_db,
        mock_get_user,
        client,
        mock_admin_user,
        mock_db,
        sample_fuel_price
    ):
        """Test successful audit log retrieval."""
        mock_get_user.return_value = mock_admin_user
        mock_get_db.return_value = mock_db
        
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = [sample_fuel_price]
        mock_db.query.return_value = mock_query
        
        response = client.get("/api/admin/fuel-prices/audit-log?days=30")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["action"] == "UPDATE"
        assert data[0]["fuel_type"] == "diesel_500"
    
    @patch('app.api.admin.get_current_active_user')
    @patch('app.api.admin.get_db')
    def test_check_staleness_success(
        self,
        mock_get_db,
        mock_get_user,
        client,
        mock_admin_user,
        mock_db
    ):
        """Test successful staleness check."""
        mock_get_user.return_value = mock_admin_user
        mock_get_db.return_value = mock_db
        
        # Mock stale price (older than threshold)
        stale_price = MagicMock()
        stale_price.id = 1
        stale_price.fuel_type = "diesel_500"
        stale_price.region = "NEA"
        stale_price.price_per_liter = Decimal("150.00")
        stale_price.effective_date = date.today() - timedelta(days=45)  # 45 days old
        stale_price.is_active = True
        
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [stale_price]
        mock_db.query.return_value = mock_query
        
        response = client.get("/api/admin/fuel-prices/staleness-check?threshold_days=30")
        
        assert response.status_code == 200
        data = response.json()
        assert data["threshold_days"] == 30
        assert data["total_stale_prices"] == 1
        assert len(data["recommendations"]) > 0
        assert "default_fallback_values" in data
    
    @patch('app.api.admin.get_current_active_user')
    @patch('app.api.admin.get_db')
    def test_bulk_update_success(
        self,
        mock_get_db,
        mock_get_user,
        client,
        mock_admin_user,
        mock_db,
        sample_fuel_price
    ):
        """Test successful bulk fuel price update."""
        mock_get_user.return_value = mock_admin_user
        mock_get_db.return_value = mock_db
        
        # Mock database query to find existing prices
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = sample_fuel_price
        mock_db.query.return_value = mock_query
        
        bulk_updates = [
            {
                "price_id": 1,
                "price_per_liter": 155.50,
                "effective_date": date.today().isoformat(),
                "is_active": True
            }
        ]
        
        response = client.post("/api/admin/fuel-prices/bulk-update", json=bulk_updates)
        
        assert response.status_code == 200
        data = response.json()
        assert data["updated_count"] == 1
        assert "Successfully updated" in data["message"]
        
        # Verify database operations
        mock_db.commit.assert_called_once()
    
    @patch('app.api.admin.get_current_active_user')
    @patch('app.api.admin.get_db')
    def test_bulk_update_empty_list(
        self,
        mock_get_db,
        mock_get_user,
        client,
        mock_admin_user,
        mock_db
    ):
        """Test bulk update with empty list."""
        mock_get_user.return_value = mock_admin_user
        mock_get_db.return_value = mock_db
        
        response = client.post("/api/admin/fuel-prices/bulk-update", json=[])
        assert response.status_code == 400
        assert "No updates provided" in response.json()["detail"]
    
    @patch('app.api.admin.get_current_active_user')
    @patch('app.api.admin.get_db')
    def test_bulk_update_too_many_items(
        self,
        mock_get_db,
        mock_get_user,
        client,
        mock_admin_user,
        mock_db
    ):
        """Test bulk update with too many items."""
        mock_get_user.return_value = mock_admin_user
        mock_get_db.return_value = mock_db
        
        # Create 51 updates (over the limit of 50)
        bulk_updates = [
            {
                "price_id": i,
                "price_per_liter": 150.00,
                "effective_date": date.today().isoformat()
            }
            for i in range(51)
        ]
        
        response = client.post("/api/admin/fuel-prices/bulk-update", json=bulk_updates)
        assert response.status_code == 400
        assert "Too many updates" in response.json()["detail"]
    
    @patch('app.api.admin.get_current_active_user')
    @patch('app.api.admin.get_db')
    def test_bulk_update_missing_price_id(
        self,
        mock_get_db,
        mock_get_user,
        client,
        mock_admin_user,
        mock_db
    ):
        """Test bulk update with missing price_id."""
        mock_get_user.return_value = mock_admin_user
        mock_get_db.return_value = mock_db
        
        bulk_updates = [
            {
                # Missing price_id
                "price_per_liter": 150.00,
                "effective_date": date.today().isoformat()
            }
        ]
        
        response = client.post("/api/admin/fuel-prices/bulk-update", json=bulk_updates)
        assert response.status_code == 400
        assert "Missing price_id" in response.json()["detail"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])