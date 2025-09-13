"""
Tests for route comparison service.
"""
import pytest
from unittest.mock import MagicMock
from decimal import Decimal

from app.services.route_comparison_service import (
    RouteComparisonService,
    OptimizationCriteria,
    RouteRanking,
    RouteScore,
    RouteComparison,
    SavingsAnalysis
)


@pytest.fixture
def route_comparison_service():
    """Create route comparison service for testing."""
    return RouteComparisonService()


@pytest.fixture
def mock_routes():
    """Create mock routes for testing."""
    routes = []
    
    # Route 1: Fast but expensive (with tolls)
    route1 = MagicMock()
    route1.osrm_route.distance = 100000  # 100 km
    route1.osrm_route.duration = 3600    # 1 hour
    route1.cost_breakdown.total_cost = Decimal("1000.00")
    route1.cost_breakdown.fuel_cost.total_fuel_cost = Decimal("800.00")
    route1.cost_breakdown.total_toll_cost = Decimal("200.00")
    route1.route_type = "fastest"
    routes.append(route1)
    
    # Route 2: Slower but cheaper (no tolls)
    route2 = MagicMock()
    route2.osrm_route.distance = 120000  # 120 km
    route2.osrm_route.duration = 4800    # 1.33 hours
    route2.cost_breakdown.total_cost = Decimal("900.00")
    route2.cost_breakdown.fuel_cost.total_fuel_cost = Decimal("900.00")
    route2.cost_breakdown.total_toll_cost = Decimal("0.00")
    route2.route_type = "alternative"
    routes.append(route2)
    
    # Route 3: Longest but scenic
    route3 = MagicMock()
    route3.osrm_route.distance = 150000  # 150 km
    route3.osrm_route.duration = 6000    # 1.67 hours
    route3.cost_breakdown.total_cost = Decimal("1200.00")
    route3.cost_breakdown.fuel_cost.total_fuel_cost = Decimal("1100.00")
    route3.cost_breakdown.total_toll_cost = Decimal("100.00")
    route3.route_type = "scenic"
    routes.append(route3)
    
    return routes


class TestRouteComparisonService:
    """Test cases for RouteComparisonService."""
    
    def test_normalize_score(self, route_comparison_service):
        """Test score normalization."""
        # Test normal case
        assert route_comparison_service._normalize_score(5, 0, 10) == 0.5
        assert route_comparison_service._normalize_score(0, 0, 10) == 0.0
        assert route_comparison_service._normalize_score(10, 0, 10) == 1.0
        
        # Test edge case where min == max
        assert route_comparison_service._normalize_score(5, 5, 5) == 0.0
    
    def test_determine_ranking(self, route_comparison_service):
        """Test route ranking determination."""
        assert route_comparison_service._determine_ranking(0.1) == RouteRanking.BEST
        assert route_comparison_service._determine_ranking(0.3) == RouteRanking.GOOD
        assert route_comparison_service._determine_ranking(0.6) == RouteRanking.ACCEPTABLE
        assert route_comparison_service._determine_ranking(0.9) == RouteRanking.POOR
    
    def test_calculate_weighted_score_total_cost(self, route_comparison_service):
        """Test weighted score calculation for total cost criteria."""
        score = route_comparison_service._calculate_weighted_score(
            cost_score=0.5,
            time_score=0.3,
            distance_score=0.2,
            toll_score=0.1,
            criteria=OptimizationCriteria.TOTAL_COST,
            user_preferences={}
        )
        
        # Should prioritize cost (weight 0.6)
        expected = 0.5 * 0.6 + 0.3 * 0.2 + 0.2 * 0.1 + 0.1 * 0.1
        assert abs(score - expected) < 0.001
    
    def test_calculate_weighted_score_time(self, route_comparison_service):
        """Test weighted score calculation for time criteria."""
        score = route_comparison_service._calculate_weighted_score(
            cost_score=0.5,
            time_score=0.3,
            distance_score=0.2,
            toll_score=0.1,
            criteria=OptimizationCriteria.TIME,
            user_preferences={}
        )
        
        # Should prioritize time (weight 0.6)
        expected = 0.5 * 0.2 + 0.3 * 0.6 + 0.2 * 0.1 + 0.1 * 0.1
        assert abs(score - expected) < 0.001
    
    def test_calculate_weighted_score_with_preferences(self, route_comparison_service):
        """Test weighted score calculation with user preferences."""
        score = route_comparison_service._calculate_weighted_score(
            cost_score=0.5,
            time_score=0.3,
            distance_score=0.2,
            toll_score=0.1,
            criteria=OptimizationCriteria.BALANCED,
            user_preferences={"prioritize_cost": True, "avoid_tolls": True}
        )
        
        # Should have adjusted weights for cost and toll preferences
        assert isinstance(score, float)
        assert 0 <= score <= 1
    
    def test_score_routes(self, route_comparison_service, mock_routes):
        """Test route scoring."""
        scores = route_comparison_service._score_routes(
            mock_routes,
            OptimizationCriteria.TOTAL_COST,
            {}
        )
        
        assert len(scores) == 3
        assert "route_0" in scores
        assert "route_1" in scores
        assert "route_2" in scores
        
        # Check score structure
        for route_id, score in scores.items():
            assert isinstance(score, RouteScore)
            assert 0 <= score.total_score <= 1
            assert 0 <= score.cost_score <= 1
            assert 0 <= score.time_score <= 1
            assert 0 <= score.distance_score <= 1
            assert 0 <= score.toll_score <= 1
            assert isinstance(score.ranking, RouteRanking)
    
    def test_select_recommended_route(self, route_comparison_service, mock_routes):
        """Test recommended route selection."""
        # Create mock scores where route_1 has the best (lowest) score
        mock_scores = {
            "route_0": MagicMock(total_score=0.8),
            "route_1": MagicMock(total_score=0.3),  # Best score
            "route_2": MagicMock(total_score=0.9)
        }
        
        recommended = route_comparison_service._select_recommended_route(
            mock_routes, mock_scores, OptimizationCriteria.TOTAL_COST
        )
        
        assert recommended == mock_routes[1]  # Should select route_1
        assert recommended.route_type == "recommended"
    
    def test_compare_two_routes(self, route_comparison_service, mock_routes):
        """Test comparison between two routes."""
        route_a = mock_routes[0]  # Fast but expensive
        route_b = mock_routes[1]  # Slower but cheaper
        
        comparison = route_comparison_service._compare_two_routes(
            route_a, route_b, "route_0", "route_1"
        )
        
        assert isinstance(comparison, RouteComparison)
        assert comparison.route_a_id == "route_0"
        assert comparison.route_b_id == "route_1"
        assert comparison.cost_difference == Decimal("-100.00")  # Route B is cheaper
        assert comparison.time_difference == 20.0  # Route B is 20 minutes slower
        assert comparison.distance_difference == 20.0  # Route B is 20 km longer
        assert comparison.toll_difference == Decimal("-200.00")  # Route B has no tolls
        assert isinstance(comparison.recommendation, str)
        assert 0 <= comparison.confidence <= 1
    
    def test_generate_route_comparisons(self, route_comparison_service, mock_routes):
        """Test generation of all pairwise route comparisons."""
        comparisons = route_comparison_service._generate_route_comparisons(mock_routes)
        
        # Should have 3 comparisons for 3 routes: (0,1), (0,2), (1,2)
        assert len(comparisons) == 3
        
        # Check that all comparisons are present
        comparison_pairs = {(c.route_a_id, c.route_b_id) for c in comparisons}
        expected_pairs = {("route_0", "route_1"), ("route_0", "route_2"), ("route_1", "route_2")}
        assert comparison_pairs == expected_pairs
    
    def test_analyze_savings(self, route_comparison_service, mock_routes):
        """Test savings analysis."""
        recommended_route = mock_routes[1]  # Cheaper route
        
        savings_analysis = route_comparison_service._analyze_savings(
            mock_routes, recommended_route
        )
        
        assert isinstance(savings_analysis, SavingsAnalysis)
        assert savings_analysis.recommended_route_id == "recommended"
        assert savings_analysis.baseline_route_id == "baseline"
        assert savings_analysis.absolute_savings == Decimal("100.00")  # 1000 - 900
        assert savings_analysis.percentage_savings == 10.0  # 100/1000 * 100
        assert savings_analysis.time_trade_off == 20.0  # 20 minutes slower
        assert savings_analysis.distance_trade_off == 20.0  # 20 km longer
    
    def test_generate_optimization_insights(self, route_comparison_service, mock_routes):
        """Test optimization insights generation."""
        recommended_route = mock_routes[1]
        
        insights = route_comparison_service._generate_optimization_insights(
            mock_routes, recommended_route, OptimizationCriteria.TOTAL_COST
        )
        
        assert isinstance(insights, list)
        assert len(insights) > 0
        assert all(isinstance(insight, str) for insight in insights)
        
        # Should contain cost-related insight
        cost_insights = [i for i in insights if "cost" in i.lower()]
        assert len(cost_insights) > 0
    
    def test_generate_warnings(self, route_comparison_service, mock_routes):
        """Test warnings generation."""
        recommended_route = mock_routes[0]
        
        warnings = route_comparison_service._generate_warnings(
            mock_routes, recommended_route
        )
        
        assert isinstance(warnings, list)
        assert all(isinstance(warning, str) for warning in warnings)
        
        # Should always include data freshness warning
        data_warnings = [w for w in warnings if "fuel prices" in w.lower()]
        assert len(data_warnings) > 0
    
    def test_analyze_routes_complete(self, route_comparison_service, mock_routes):
        """Test complete route analysis."""
        summary = route_comparison_service.analyze_routes(
            mock_routes,
            OptimizationCriteria.TOTAL_COST,
            {"prioritize_cost": True}
        )
        
        assert summary.total_routes_analyzed == 3
        assert summary.recommended_route in mock_routes
        assert len(summary.route_scores) == 3
        assert len(summary.route_comparisons) == 3
        assert isinstance(summary.savings_analysis, SavingsAnalysis)
        assert isinstance(summary.optimization_insights, list)
        assert isinstance(summary.warnings, list)
    
    def test_analyze_routes_empty_list(self, route_comparison_service):
        """Test route analysis with empty route list."""
        with pytest.raises(ValueError, match="No routes provided for analysis"):
            route_comparison_service.analyze_routes([], OptimizationCriteria.TOTAL_COST)
    
    def test_rank_routes_by_criteria_total_cost(self, route_comparison_service, mock_routes):
        """Test ranking routes by total cost."""
        ranked_routes = route_comparison_service.rank_routes_by_criteria(
            mock_routes, OptimizationCriteria.TOTAL_COST
        )
        
        assert len(ranked_routes) == 3
        
        # Should be sorted by cost (ascending)
        costs = [float(route.cost_breakdown.total_cost) for route, score in ranked_routes]
        assert costs == sorted(costs)
        
        # Check that scores match costs
        for route, score in ranked_routes:
            assert score == float(route.cost_breakdown.total_cost)
    
    def test_rank_routes_by_criteria_time(self, route_comparison_service, mock_routes):
        """Test ranking routes by time."""
        ranked_routes = route_comparison_service.rank_routes_by_criteria(
            mock_routes, OptimizationCriteria.TIME
        )
        
        assert len(ranked_routes) == 3
        
        # Should be sorted by time (ascending)
        times = [route.osrm_route.duration for route, score in ranked_routes]
        assert times == sorted(times)
    
    def test_rank_routes_by_criteria_distance(self, route_comparison_service, mock_routes):
        """Test ranking routes by distance."""
        ranked_routes = route_comparison_service.rank_routes_by_criteria(
            mock_routes, OptimizationCriteria.DISTANCE
        )
        
        assert len(ranked_routes) == 3
        
        # Should be sorted by distance (ascending)
        distances = [route.osrm_route.distance for route, score in ranked_routes]
        assert distances == sorted(distances)
    
    def test_calculate_route_efficiency_metrics(self, route_comparison_service, mock_routes):
        """Test route efficiency metrics calculation."""
        route = mock_routes[0]
        
        metrics = route_comparison_service.calculate_route_efficiency_metrics(route)
        
        expected_metrics = [
            "cost_per_km", "cost_per_hour", "fuel_efficiency", "average_speed_kmh",
            "toll_density", "fuel_cost_ratio", "toll_cost_ratio"
        ]
        
        for metric in expected_metrics:
            assert metric in metrics
            assert isinstance(metrics[metric], (int, float))
            assert metrics[metric] >= 0
        
        # Test specific calculations
        assert metrics["cost_per_km"] == 10.0  # 1000 / 100
        assert metrics["average_speed_kmh"] == 100.0  # 100 km / 1 hour
        assert metrics["fuel_cost_ratio"] == 0.8  # 800 / 1000
        assert metrics["toll_cost_ratio"] == 0.2  # 200 / 1000


class TestOptimizationCriteria:
    """Test cases for OptimizationCriteria enum."""
    
    def test_optimization_criteria_values(self):
        """Test optimization criteria enum values."""
        assert OptimizationCriteria.TOTAL_COST.value == "total_cost"
        assert OptimizationCriteria.FUEL_COST.value == "fuel_cost"
        assert OptimizationCriteria.TIME.value == "time"
        assert OptimizationCriteria.DISTANCE.value == "distance"
        assert OptimizationCriteria.TOLL_AVOIDANCE.value == "toll_avoidance"
        assert OptimizationCriteria.BALANCED.value == "balanced"


class TestRouteRanking:
    """Test cases for RouteRanking enum."""
    
    def test_route_ranking_values(self):
        """Test route ranking enum values."""
        assert RouteRanking.BEST.value == "best"
        assert RouteRanking.GOOD.value == "good"
        assert RouteRanking.ACCEPTABLE.value == "acceptable"
        assert RouteRanking.POOR.value == "poor"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])