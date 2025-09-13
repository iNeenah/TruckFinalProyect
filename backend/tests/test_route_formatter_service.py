"""
Tests for route formatter service.
"""
import pytest
from unittest.mock import MagicMock
from decimal import Decimal
from datetime import datetime
import json

from app.services.route_formatter_service import RouteFormatterService
from app.services.route_optimization_service import OptimizedRoute, RouteOptimizationResponse
from app.services.route_comparison_service import OptimizationSummary
from app.services.osrm_service import Coordinate
from app.schemas.route import Route, CostBreakdown, TollPoint, SavingsAnalysis


@pytest.fixture
def route_formatter():
    """Create route formatter service for testing."""
    return RouteFormatterService()


@pytest.fixture
def mock_optimized_route():
    """Create mock optimized route."""
    route = MagicMock()
    route.osrm_route.distance = 100000  # 100 km
    route.osrm_route.duration = 3600    # 1 hour
    route.geometry = '{"type": "LineString", "coordinates": [[-55.8959, -27.3621], [-54.5735, -25.5951]]}'
    route.route_type = "fastest"
    
    # Mock cost breakdown
    route.cost_breakdown.fuel_cost.total_fuel_cost = Decimal("800.00")
    route.cost_breakdown.fuel_cost.fuel_needed_liters = 15.0
    route.cost_breakdown.total_toll_cost = Decimal("100.00")
    route.cost_breakdown.total_cost = Decimal("900.00")
    
    # Mock tolls
    mock_toll = MagicMock()
    mock_toll.name = "Test Toll"
    mock_toll.coordinate = Coordinate(-55.8959, -27.3621)
    mock_toll.cost = Decimal("100.00")
    mock_toll.road_name = "RN12"
    route.cost_breakdown.tolls = [mock_toll]
    
    return route


@pytest.fixture
def mock_optimization_response(mock_optimized_route):
    """Create mock optimization response."""
    response = MagicMock()
    response.routes = [mock_optimized_route]
    response.recommended_route = mock_optimized_route
    response.total_savings = Decimal("50.00")
    response.calculation_time_ms = 1500
    response.warnings = []
    return response


@pytest.fixture
def mock_analysis_summary(mock_optimized_route):
    """Create mock analysis summary."""
    summary = MagicMock()
    summary.recommended_route = mock_optimized_route
    summary.total_routes_analyzed = 1
    summary.route_scores = {}
    summary.route_comparisons = []
    summary.savings_analysis = MagicMock()
    summary.optimization_insights = []
    summary.warnings = []
    return summary


class TestRouteFormatterService:
    """Test cases for RouteFormatterService."""
    
    def test_format_single_route(self, route_formatter, mock_optimized_route):
        """Test formatting a single route."""
        formatted_route = route_formatter._format_single_route(mock_optimized_route, "route_1")
        
        assert isinstance(formatted_route, Route)
        assert formatted_route.id == "route_1"
        assert formatted_route.distance == 100.0  # Converted to km
        assert formatted_route.duration == 60     # Converted to minutes
        assert formatted_route.route_type == "fastest"
        
        # Check cost breakdown
        assert formatted_route.cost_breakdown.fuel_cost == Decimal("800.00")
        assert formatted_route.cost_breakdown.toll_cost == Decimal("100.00")
        assert formatted_route.cost_breakdown.total_cost == Decimal("900.00")
        assert formatted_route.cost_breakdown.fuel_liters == 15.0
        assert formatted_route.cost_breakdown.toll_count == 1
        
        # Check toll points
        assert len(formatted_route.toll_points) == 1
        toll_point = formatted_route.toll_points[0]
        assert isinstance(toll_point, TollPoint)
        assert toll_point.name == "Test Toll"
        assert toll_point.tariff == Decimal("100.00")
        assert toll_point.route_code == "RN12"
    
    def test_convert_to_geojson_valid_json(self, route_formatter):
        """Test converting valid GeoJSON string to GeoJSON."""
        geojson_str = '{"type": "LineString", "coordinates": [[-55.8959, -27.3621], [-54.5735, -25.5951]]}'
        
        result = route_formatter._convert_to_geojson(geojson_str)
        
        assert result["type"] == "LineString"
        assert len(result["coordinates"]) == 2
        assert result["coordinates"][0] == [-55.8959, -27.3621]
        assert result["coordinates"][1] == [-54.5735, -25.5951]
    
    def test_convert_to_geojson_invalid_input(self, route_formatter):
        """Test converting invalid geometry to GeoJSON."""
        invalid_geometry = "invalid_geometry_string"
        
        result = route_formatter._convert_to_geojson(invalid_geometry)
        
        # Should return empty LineString as fallback
        assert result["type"] == "LineString"
        assert result["coordinates"] == []
    
    def test_format_toll_points(self, route_formatter):
        """Test formatting toll points."""
        mock_toll = MagicMock()
        mock_toll.name = "Test Toll"
        mock_toll.coordinate = Coordinate(-55.8959, -27.3621)
        mock_toll.cost = Decimal("50.00")
        mock_toll.road_name = "RN12"
        
        toll_points = route_formatter._format_toll_points([mock_toll])
        
        assert len(toll_points) == 1
        toll_point = toll_points[0]
        assert isinstance(toll_point, TollPoint)
        assert toll_point.name == "Test Toll"
        assert toll_point.coordinates.longitude == -55.8959
        assert toll_point.coordinates.latitude == -27.3621
        assert toll_point.tariff == Decimal("50.00")
        assert toll_point.route_code == "RN12"
    
    def test_format_savings_analysis_with_savings(self, route_formatter):
        """Test formatting savings analysis with actual savings."""
        # Create mock routes with different costs
        route1 = MagicMock()
        route1.id = "route_1"
        route1.duration = 60
        route1.cost_breakdown.total_cost = Decimal("1000.00")
        
        route2 = MagicMock()
        route2.id = "route_2"
        route2.duration = 70
        route2.cost_breakdown.total_cost = Decimal("900.00")
        
        formatted_routes = [route1, route2]
        mock_analysis_summary = MagicMock()
        mock_analysis_summary.recommended_route.route_type = "cheapest"
        
        savings_analysis = route_formatter._format_savings_analysis(
            mock_analysis_summary, formatted_routes
        )
        
        assert isinstance(savings_analysis, SavingsAnalysis)
        assert savings_analysis.fastest_route_cost == Decimal("1000.00")  # route1 is faster
        assert savings_analysis.cheapest_route_cost == Decimal("900.00")   # route2 is cheaper
        assert savings_analysis.savings_amount == Decimal("100.00")       # 1000 - 900
        assert savings_analysis.savings_percentage == 10.0                # 100/1000 * 100
        assert "saves ARS $100.00" in savings_analysis.comparison_summary
    
    def test_format_savings_analysis_no_savings(self, route_formatter):
        """Test formatting savings analysis when no savings exist."""
        # Create mock route (only one route, so no savings)
        route1 = MagicMock()
        route1.id = "route_1"
        route1.duration = 60
        route1.cost_breakdown.total_cost = Decimal("1000.00")
        
        formatted_routes = [route1]
        mock_analysis_summary = MagicMock()
        mock_analysis_summary.recommended_route.route_type = "fastest"
        
        savings_analysis = route_formatter._format_savings_analysis(
            mock_analysis_summary, formatted_routes
        )
        
        assert savings_analysis.savings_amount is None
        assert savings_analysis.savings_percentage is None
        assert "fastest route is also the most economical" in savings_analysis.comparison_summary.lower()
    
    def test_generate_comparison_summary_significant_time_difference(self, route_formatter):
        """Test comparison summary with significant time difference."""
        fastest_route = MagicMock()
        fastest_route.duration = 60
        
        cheapest_route = MagicMock()
        cheapest_route.duration = 120  # 60 minutes longer
        
        mock_analysis_summary = MagicMock()
        savings_amount = Decimal("100.00")
        
        summary = route_formatter._generate_comparison_summary(
            mock_analysis_summary, fastest_route, cheapest_route, savings_amount
        )
        
        assert "saves ARS $100.00" in summary
        assert "60 minutes longer" in summary
    
    def test_generate_comparison_summary_minimal_time_difference(self, route_formatter):
        """Test comparison summary with minimal time difference."""
        fastest_route = MagicMock()
        fastest_route.duration = 60
        
        cheapest_route = MagicMock()
        cheapest_route.duration = 65  # Only 5 minutes longer
        
        mock_analysis_summary = MagicMock()
        savings_amount = Decimal("50.00")
        
        summary = route_formatter._generate_comparison_summary(
            mock_analysis_summary, fastest_route, cheapest_route, savings_amount
        )
        
        assert "saves ARS $50.00" in summary
        assert "minimal additional travel time" in summary
    
    def test_create_route_geojson_feature_collection(self, route_formatter):
        """Test creating GeoJSON FeatureCollection."""
        # Create mock routes
        route1 = MagicMock()
        route1.id = "route_1"
        route1.route_type = "fastest"
        route1.distance = 100.0
        route1.duration = 60
        route1.cost_breakdown.total_cost = Decimal("1000.00")
        route1.cost_breakdown.fuel_cost = Decimal("800.00")
        route1.cost_breakdown.toll_cost = Decimal("200.00")
        route1.cost_breakdown.toll_count = 2
        route1.geometry = {"type": "LineString", "coordinates": [[-55.8959, -27.3621], [-54.5735, -25.5951]]}
        route1.toll_points = []
        
        routes = [route1]
        
        feature_collection = route_formatter.create_route_geojson_feature_collection(
            routes, include_toll_markers=False
        )
        
        assert feature_collection["type"] == "FeatureCollection"
        assert len(feature_collection["features"]) == 1
        
        feature = feature_collection["features"][0]
        assert feature["type"] == "Feature"
        assert feature["properties"]["route_id"] == "route_1"
        assert feature["properties"]["route_type"] == "fastest"
        assert feature["properties"]["distance_km"] == 100.0
        assert feature["properties"]["duration_minutes"] == 60
        assert feature["properties"]["total_cost"] == 1000.0
        assert feature["geometry"] == route1.geometry
    
    def test_create_route_geojson_feature_collection_with_tolls(self, route_formatter):
        """Test creating GeoJSON FeatureCollection with toll markers."""
        # Create mock toll point
        mock_toll = MagicMock()
        mock_toll.name = "Test Toll"
        mock_toll.coordinates.longitude = -55.8959
        mock_toll.coordinates.latitude = -27.3621
        mock_toll.tariff = Decimal("50.00")
        mock_toll.route_code = "RN12"
        
        # Create mock route with toll
        route1 = MagicMock()
        route1.id = "route_1"
        route1.route_type = "fastest"
        route1.distance = 100.0
        route1.duration = 60
        route1.cost_breakdown.total_cost = Decimal("1000.00")
        route1.cost_breakdown.fuel_cost = Decimal("800.00")
        route1.cost_breakdown.toll_cost = Decimal("200.00")
        route1.cost_breakdown.toll_count = 1
        route1.geometry = {"type": "LineString", "coordinates": [[-55.8959, -27.3621], [-54.5735, -25.5951]]}
        route1.toll_points = [mock_toll]
        
        routes = [route1]
        
        feature_collection = route_formatter.create_route_geojson_feature_collection(
            routes, include_toll_markers=True
        )
        
        assert len(feature_collection["features"]) == 2  # Route + toll marker
        
        # Check toll marker feature
        toll_feature = feature_collection["features"][1]
        assert toll_feature["type"] == "Feature"
        assert toll_feature["properties"]["type"] == "toll"
        assert toll_feature["properties"]["toll_name"] == "Test Toll"
        assert toll_feature["properties"]["toll_cost"] == 50.0
        assert toll_feature["geometry"]["type"] == "Point"
        assert toll_feature["geometry"]["coordinates"] == [-55.8959, -27.3621]
    
    def test_get_route_color(self, route_formatter):
        """Test route color assignment."""
        # Test known route types
        assert route_formatter._get_route_color("recommended", 0) == "#2ecc71"
        assert route_formatter._get_route_color("fastest", 0) == "#3498db"
        assert route_formatter._get_route_color("cheapest", 0) == "#f39c12"
        
        # Test unknown route type (should use default colors)
        color = route_formatter._get_route_color("unknown", 0)
        assert color.startswith("#")
        assert len(color) == 7
    
    def test_create_route_summary_table(self, route_formatter):
        """Test creating route summary table."""
        # Create mock routes
        route1 = MagicMock()
        route1.route_type = "fastest"
        route1.distance = 100.0
        route1.duration = 90  # 1h 30m
        route1.cost_breakdown.fuel_cost = Decimal("800.00")
        route1.cost_breakdown.toll_cost = Decimal("100.00")
        route1.cost_breakdown.total_cost = Decimal("900.00")
        route1.cost_breakdown.toll_count = 1
        
        route2 = MagicMock()
        route2.route_type = "cheapest"
        route2.distance = 110.0
        route2.duration = 45  # 45m
        route2.cost_breakdown.fuel_cost = Decimal("750.00")
        route2.cost_breakdown.toll_cost = Decimal("0.00")
        route2.cost_breakdown.total_cost = Decimal("750.00")
        route2.cost_breakdown.toll_count = 0
        
        routes = [route1, route2]
        
        table_data = route_formatter.create_route_summary_table(routes)
        
        assert "headers" in table_data
        assert "rows" in table_data
        assert len(table_data["headers"]) == 7
        assert len(table_data["rows"]) == 2
        
        # Check first row
        row1 = table_data["rows"][0]
        assert row1[0] == "Fastest"
        assert row1[1] == "100.0"
        assert row1[2] == "1h 30m"
        assert row1[3] == "$800.00"
        assert row1[4] == "$100.00"
        assert row1[5] == "$900.00"
        assert row1[6] == "1"
        
        # Check second row
        row2 = table_data["rows"][1]
        assert row2[0] == "Cheapest"
        assert row2[2] == "45m"  # No hours
        assert row2[6] == "0"    # No tolls
    
    def test_create_cost_breakdown_chart_data(self, route_formatter):
        """Test creating cost breakdown chart data."""
        # Create mock routes
        route1 = MagicMock()
        route1.route_type = "fastest"
        route1.cost_breakdown.fuel_cost = Decimal("800.00")
        route1.cost_breakdown.toll_cost = Decimal("100.00")
        
        route2 = MagicMock()
        route2.route_type = "cheapest"
        route2.cost_breakdown.fuel_cost = Decimal("750.00")
        route2.cost_breakdown.toll_cost = Decimal("0.00")
        
        routes = [route1, route2]
        
        chart_data = route_formatter.create_cost_breakdown_chart_data(routes)
        
        assert "labels" in chart_data
        assert "datasets" in chart_data
        assert len(chart_data["labels"]) == 2
        assert chart_data["labels"] == ["Fastest", "Cheapest"]
        
        assert len(chart_data["datasets"]) == 2
        fuel_dataset = chart_data["datasets"][0]
        toll_dataset = chart_data["datasets"][1]
        
        assert fuel_dataset["label"] == "Fuel Cost"
        assert fuel_dataset["data"] == [800.0, 750.0]
        
        assert toll_dataset["label"] == "Toll Cost"
        assert toll_dataset["data"] == [100.0, 0.0]
    
    def test_create_savings_visualization_data_with_savings(self, route_formatter):
        """Test creating savings visualization data with actual savings."""
        # Create mock savings analysis
        savings_analysis = MagicMock()
        savings_analysis.savings_amount = Decimal("100.00")
        savings_analysis.savings_percentage = 10.0
        
        # Create mock routes
        fastest_route = MagicMock()
        fastest_route.route_type = "fastest"
        fastest_route.cost_breakdown.total_cost = Decimal("1000.00")
        fastest_route.duration = 60
        fastest_route.distance = 100.0
        
        recommended_route = MagicMock()
        recommended_route.route_type = "recommended"
        recommended_route.cost_breakdown.total_cost = Decimal("900.00")
        recommended_route.duration = 70
        recommended_route.distance = 110.0
        
        routes = [fastest_route, recommended_route]
        
        viz_data = route_formatter.create_savings_visualization_data(savings_analysis, routes)
        
        assert viz_data["type"] == "savings_comparison"
        assert viz_data["savings_amount"] == 100.0
        assert viz_data["savings_percentage"] == 10.0
        assert viz_data["time_trade_off"] == 10  # 70 - 60
        assert viz_data["distance_trade_off"] == 10.0  # 110 - 100
        
        assert viz_data["fastest_route"]["cost"] == 1000.0
        assert viz_data["recommended_route"]["cost"] == 900.0
    
    def test_create_savings_visualization_data_no_savings(self, route_formatter):
        """Test creating savings visualization data with no savings."""
        savings_analysis = MagicMock()
        savings_analysis.savings_amount = Decimal("0.00")
        
        routes = []
        
        viz_data = route_formatter.create_savings_visualization_data(savings_analysis, routes)
        
        assert viz_data["type"] == "no_savings"
        assert "No significant savings" in viz_data["message"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])