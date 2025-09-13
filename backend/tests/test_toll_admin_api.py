"""
Tests for toll management admin API endpoints.
"""
import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from datetime import datetime
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
def sample_toll():
    """Sample toll object."""
    toll = MagicMock()
    toll.id = 1
    toll.name = "Peaje Posadas"
    toll.road_name = "RN12"
    toll.latitude = -27.3621
    toll.longitude = -55.8959
    toll.tariff = Decimal("90.00")
    toll.region = "NEA"
    toll.is_active = True
    toll.created_at = datetime.now()
    toll.updated_at = datetime.now()
    toll.updated_by = "admin-user-id"
    return toll


class TestTollManagementEndpoints:
    """Test cases for toll management endpoints."""
    
    @patch('app.api.admin.get_current_active_user')
    @patch('app.api.admin.get_db')
    def test_get_tolls_success(
        self,
        mock_get_db,
        mock_get_user,
        client,
        mock_admin_user,
        mock_db,
        sample_toll
    ):
        """Test successful tolls retrieval."""
        mock_get_user.return_value = mock_admin_user
        mock_get_db.return_value = mock_db
        
        # Mock database query
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = [sample_toll]
        mock_db.query.return_value = mock_query
        
        response = client.get("/api/admin/tolls")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Peaje Posadas"
        assert data[0]["road_name"] == "RN12"
        assert float(data[0]["tariff"]) == 90.00
    
    @patch('app.api.admin.get_current_active_user')
    @patch('app.api.admin.get_db')
    def test_get_tolls_non_admin_forbidden(
        self,
        mock_get_db,
        mock_get_user,
        client,
        mock_regular_user,
        mock_db
    ):
        """Test tolls access denied for non-admin users."""
        mock_get_user.return_value = mock_regular_user
        mock_get_db.return_value = mock_db
        
        response = client.get("/api/admin/tolls")
        assert response.status_code == 403
        assert "Admin access required" in response.json()["detail"]
    
    @patch('app.api.admin.get_current_active_user')
    @patch('app.api.admin.get_db')
    def test_get_tolls_with_filters(
        self,
        mock_get_db,
        mock_get_user,
        client,
        mock_admin_user,
        mock_db,
        sample_toll
    ):
        """Test tolls retrieval with filters."""
        mock_get_user.return_value = mock_admin_user
        mock_get_db.return_value = mock_db
        
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = [sample_toll]
        mock_db.query.return_value = mock_query
        
        response = client.get("/api/admin/tolls?road_name=RN12&region=NEA&active_only=true")
        
        assert response.status_code == 200
        # Verify filters were applied
        assert mock_query.filter.call_count >= 3  # road_name, region, active_only
    
    @patch('app.api.admin.get_current_active_user')
    @patch('app.api.admin.get_db')
    def test_create_toll_success(
        self,
        mock_get_db,
        mock_get_user,
        client,
        mock_admin_user,
        mock_db
    ):
        """Test successful toll creation."""
        mock_get_user.return_value = mock_admin_user
        mock_get_db.return_value = mock_db
        
        # Mock no existing toll at location
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None
        mock_db.query.return_value = mock_query
        
        # Mock new toll creation
        new_toll = MagicMock()
        new_toll.id = 1
        new_toll.name = "Nuevo Peaje"
        new_toll.road_name = "RN14"
        new_toll.latitude = -26.1234
        new_toll.longitude = -54.5678
        new_toll.tariff = Decimal("85.00")
        new_toll.region = "NEA"
        new_toll.is_active = True
        new_toll.created_at = datetime.now()
        new_toll.updated_at = datetime.now()
        new_toll.updated_by = mock_admin_user.id
        
        mock_db.refresh.return_value = None
        mock_db.refresh.side_effect = lambda obj: setattr(obj, 'id', 1)
        
        toll_data = {
            "name": "Nuevo Peaje",
            "road_name": "RN14",
            "latitude": -26.1234,
            "longitude": -54.5678,
            "tariff": 85.00,
            "region": "NEA"
        }
        
        response = client.post("/api/admin/tolls", json=toll_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Nuevo Peaje"
        assert data["road_name"] == "RN14"
        
        # Verify database operations
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
    
    @patch('app.api.admin.get_current_active_user')
    @patch('app.api.admin.get_db')
    def test_create_toll_invalid_coordinates(
        self,
        mock_get_db,
        mock_get_user,
        client,
        mock_admin_user,
        mock_db
    ):
        """Test toll creation with invalid coordinates."""
        mock_get_user.return_value = mock_admin_user
        mock_get_db.return_value = mock_db
        
        toll_data = {
            "name": "Peaje Inválido",
            "road_name": "RN14",
            "latitude": 95.0,  # Invalid latitude
            "longitude": -54.5678,
            "tariff": 85.00,
            "region": "NEA"
        }
        
        response = client.post("/api/admin/tolls", json=toll_data)
        assert response.status_code == 400
        assert "Latitude must be between -90 and 90" in response.json()["detail"]
    
    @patch('app.api.admin.get_current_active_user')
    @patch('app.api.admin.get_db')
    def test_create_toll_duplicate_location(
        self,
        mock_get_db,
        mock_get_user,
        client,
        mock_admin_user,
        mock_db,
        sample_toll
    ):
        """Test toll creation at duplicate location."""
        mock_get_user.return_value = mock_admin_user
        mock_get_db.return_value = mock_db
        
        # Mock existing toll at same location
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = sample_toll
        mock_db.query.return_value = mock_query
        
        toll_data = {
            "name": "Peaje Duplicado",
            "road_name": "RN12",
            "latitude": -27.3621,
            "longitude": -55.8959,
            "tariff": 90.00,
            "region": "NEA"
        }
        
        response = client.post("/api/admin/tolls", json=toll_data)
        assert response.status_code == 400
        assert "already exists at this location" in response.json()["detail"]
    
    @patch('app.api.admin.get_current_active_user')
    @patch('app.api.admin.get_db')
    def test_update_toll_success(
        self,
        mock_get_db,
        mock_get_user,
        client,
        mock_admin_user,
        mock_db,
        sample_toll
    ):
        """Test successful toll update."""
        mock_get_user.return_value = mock_admin_user
        mock_get_db.return_value = mock_db
        
        # Mock database query to find existing toll
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = sample_toll
        mock_db.query.return_value = mock_query
        
        update_data = {
            "name": "Peaje Posadas Actualizado",
            "tariff": 95.00,
            "is_active": True
        }
        
        response = client.put("/api/admin/tolls/1", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        
        # Verify database operations
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
    
    @patch('app.api.admin.get_current_active_user')
    @patch('app.api.admin.get_db')
    def test_update_toll_not_found(
        self,
        mock_get_db,
        mock_get_user,
        client,
        mock_admin_user,
        mock_db
    ):
        """Test toll update for non-existent toll."""
        mock_get_user.return_value = mock_admin_user
        mock_get_db.return_value = mock_db
        
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None  # Toll not found
        mock_db.query.return_value = mock_query
        
        update_data = {
            "name": "Peaje No Existe",
            "tariff": 95.00
        }
        
        response = client.put("/api/admin/tolls/999", json=update_data)
        assert response.status_code == 404
        assert "Toll not found" in response.json()["detail"]
    
    @patch('app.api.admin.get_current_active_user')
    @patch('app.api.admin.get_db')
    def test_delete_toll_success(
        self,
        mock_get_db,
        mock_get_user,
        client,
        mock_admin_user,
        mock_db,
        sample_toll
    ):
        """Test successful toll deletion (soft delete)."""
        mock_get_user.return_value = mock_admin_user
        mock_get_db.return_value = mock_db
        
        # Mock database query to find existing toll
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = sample_toll
        mock_db.query.return_value = mock_query
        
        response = client.delete("/api/admin/tolls/1")
        
        assert response.status_code == 204
        
        # Verify soft delete (is_active set to False)
        assert sample_toll.is_active == False
        mock_db.commit.assert_called_once()
    
    @patch('app.api.admin.get_current_active_user')
    @patch('app.api.admin.get_db')
    def test_import_tolls_csv_success(
        self,
        mock_get_db,
        mock_get_user,
        client,
        mock_admin_user,
        mock_db
    ):
        """Test successful CSV toll import."""
        mock_get_user.return_value = mock_admin_user
        mock_get_db.return_value = mock_db
        
        # Mock no existing tolls at locations
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None
        mock_db.query.return_value = mock_query
        
        csv_data = """name,road_name,latitude,longitude,tariff,region
Peaje Test 1,RN12,-27.1234,-55.5678,85.00,NEA
Peaje Test 2,RN14,-26.9876,-54.3210,90.00,NEA"""
        
        import_request = {
            "csv_data": csv_data,
            "default_region": "NEA"
        }
        
        response = client.post("/api/admin/tolls/import", json=import_request)
        
        assert response.status_code == 200
        data = response.json()
        assert data["imported_count"] == 2
        assert data["skipped_count"] == 0
        assert data["error_count"] == 0
        assert "Import completed" in data["message"]
        
        # Verify database operations
        assert mock_db.add.call_count == 2
        mock_db.commit.assert_called_once()
    
    @patch('app.api.admin.get_current_active_user')
    @patch('app.api.admin.get_db')
    def test_import_tolls_csv_invalid_headers(
        self,
        mock_get_db,
        mock_get_user,
        client,
        mock_admin_user,
        mock_db
    ):
        """Test CSV import with invalid headers."""
        mock_get_user.return_value = mock_admin_user
        mock_get_db.return_value = mock_db
        
        csv_data = """nombre,ruta,lat,lng,precio
Peaje Test,RN12,-27.1234,-55.5678,85.00"""
        
        import_request = {
            "csv_data": csv_data,
            "default_region": "NEA"
        }
        
        response = client.post("/api/admin/tolls/import", json=import_request)
        assert response.status_code == 400
        assert "Missing required CSV columns" in response.json()["detail"]
    
    @patch('app.api.admin.get_current_active_user')
    @patch('app.api.admin.get_db')
    def test_import_tolls_csv_with_errors(
        self,
        mock_get_db,
        mock_get_user,
        client,
        mock_admin_user,
        mock_db
    ):
        """Test CSV import with data errors."""
        mock_get_user.return_value = mock_admin_user
        mock_get_db.return_value = mock_db
        
        # Mock no existing tolls
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None
        mock_db.query.return_value = mock_query
        
        csv_data = """name,road_name,latitude,longitude,tariff,region
Peaje Válido,RN12,-27.1234,-55.5678,85.00,NEA
Peaje Inválido,RN14,95.0,-54.3210,90.00,NEA"""  # Invalid latitude
        
        import_request = {
            "csv_data": csv_data,
            "default_region": "NEA"
        }
        
        response = client.post("/api/admin/tolls/import", json=import_request)
        
        assert response.status_code == 200
        data = response.json()
        assert data["imported_count"] == 1
        assert data["error_count"] == 1
        assert len(data["errors"]) == 1
        assert "Invalid latitude" in data["errors"][0]
    
    @patch('app.api.admin.get_current_active_user')
    @patch('app.api.admin.get_db')
    def test_validate_toll_location_success(
        self,
        mock_get_db,
        mock_get_user,
        client,
        mock_admin_user,
        mock_db
    ):
        """Test successful toll location validation."""
        mock_get_user.return_value = mock_admin_user
        mock_get_db.return_value = mock_db
        
        # Mock no nearby tolls
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = []
        mock_db.query.return_value = mock_query
        
        response = client.get("/api/admin/tolls/validate-location?latitude=-27.3621&longitude=-55.8959")
        
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] == True
        assert data["in_argentina"] == True
        assert data["nearby_tolls_count"] == 0
    
    @patch('app.api.admin.get_current_active_user')
    @patch('app.api.admin.get_db')
    def test_validate_toll_location_invalid_coordinates(
        self,
        mock_get_db,
        mock_get_user,
        client,
        mock_admin_user,
        mock_db
    ):
        """Test toll location validation with invalid coordinates."""
        mock_get_user.return_value = mock_admin_user
        mock_get_db.return_value = mock_db
        
        response = client.get("/api/admin/tolls/validate-location?latitude=95.0&longitude=-55.8959")
        
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] == False
        assert "Invalid latitude" in data["reason"]
    
    @patch('app.api.admin.get_current_active_user')
    @patch('app.api.admin.get_db')
    def test_validate_toll_location_outside_argentina(
        self,
        mock_get_db,
        mock_get_user,
        client,
        mock_admin_user,
        mock_db
    ):
        """Test toll location validation outside Argentina."""
        mock_get_user.return_value = mock_admin_user
        mock_get_db.return_value = mock_db
        
        # Coordinates in Brazil
        response = client.get("/api/admin/tolls/validate-location?latitude=-15.7801&longitude=-47.9292")
        
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] == False
        assert "outside Argentina" in data["reason"]
    
    @patch('app.api.admin.get_current_active_user')
    @patch('app.api.admin.get_db')
    def test_validate_toll_location_with_nearby_tolls(
        self,
        mock_get_db,
        mock_get_user,
        client,
        mock_admin_user,
        mock_db,
        sample_toll
    ):
        """Test toll location validation with nearby existing tolls."""
        mock_get_user.return_value = mock_admin_user
        mock_get_db.return_value = mock_db
        
        # Mock nearby toll
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [sample_toll]
        mock_db.query.return_value = mock_query
        
        response = client.get("/api/admin/tolls/validate-location?latitude=-27.3621&longitude=-55.8959")
        
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] == True
        assert data["nearby_tolls_count"] == 1
        assert len(data["warnings"]) > 0
        assert "existing toll" in data["warnings"][0]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])