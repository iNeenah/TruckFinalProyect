"""
Route comparison and optimization logic service.
"""
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
import statistics

from app.services.route_optimization_service import OptimizedRoute, RouteCostBreakdown


class OptimizationCriteria(Enum):
    """Criteria for route optimization."""
    TOTAL_COST = "total_cost"
    FUEL_COST = "fuel_cost"
    TIME = "time"
    DISTANCE = "distance"
    TOLL_AVOIDANCE = "toll_avoidance"
    BALANCED = "balanced"


class RouteRanking(Enum):
    """Route ranking categories."""
    BEST = "best"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    POOR = "poor"


@dataclass
class RouteScore:
    """Scoring information for a route."""
    total_score: float
    cost_score: float
    time_score: float
    distance_score: float
    toll_score: float
    ranking: RouteRanking


@dataclass
class RouteComparison:
    """Comparison between two routes."""
    route_a_id: str
    route_b_id: str
    cost_difference: Decimal
    time_difference: float  # minutes
    distance_difference: float  # km
    toll_difference: Decimal
    recommendation: str
    confidence: float


@dataclass
class SavingsAnalysis:
    """Analysis of potential savings."""
    recommended_route_id: str
    baseline_route_id: str  # Usually fastest route
    absolute_savings: Decimal
    percentage_savings: float
    time_trade_off: float  # Additional minutes for savings
    distance_trade_off: float  # Additional km for savings
    savings_per_minute: Decimal
    savings_per_km: Decimal


@dataclass
class OptimizationSummary:
    """Summary of route optimization results."""
    total_routes_analyzed: int
    recommended_route: OptimizedRoute
    route_scores: Dict[str, RouteScore]
    route_comparisons: List[RouteComparison]
    savings_analysis: SavingsAnalysis
    optimization_insights: List[str]
    warnings: List[str]


class RouteComparisonService:
    """Service for comparing and optimizing routes."""
    
    def __init__(self):
        """Initialize route comparison service."""
        self.logger = logging.getLogger(__name__)
    
    def analyze_routes(
        self,
        routes: List[OptimizedRoute],
        criteria: OptimizationCriteria = OptimizationCriteria.TOTAL_COST,
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> OptimizationSummary:
        """
        Analyze and compare multiple routes.
        
        Args:
            routes: List of optimized routes to analyze
            criteria: Primary optimization criteria
            user_preferences: Optional user preferences
            
        Returns:
            Comprehensive optimization summary
        """
        if not routes:
            raise ValueError("No routes provided for analysis")
        
        user_preferences = user_preferences or {}
        
        # Score all routes
        route_scores = self._score_routes(routes, criteria, user_preferences)
        
        # Find recommended route
        recommended_route = self._select_recommended_route(routes, route_scores, criteria)
        
        # Generate pairwise comparisons
        route_comparisons = self._generate_route_comparisons(routes)
        
        # Analyze savings
        savings_analysis = self._analyze_savings(routes, recommended_route)
        
        # Generate insights and warnings
        insights = self._generate_optimization_insights(routes, recommended_route, criteria)
        warnings = self._generate_warnings(routes, recommended_route)
        
        return OptimizationSummary(
            total_routes_analyzed=len(routes),
            recommended_route=recommended_route,
            route_scores=route_scores,
            route_comparisons=route_comparisons,
            savings_analysis=savings_analysis,
            optimization_insights=insights,
            warnings=warnings
        )
    
    def _score_routes(
        self,
        routes: List[OptimizedRoute],
        criteria: OptimizationCriteria,
        user_preferences: Dict[str, Any]
    ) -> Dict[str, RouteScore]:
        """
        Score routes based on multiple criteria.
        
        Args:
            routes: Routes to score
            criteria: Primary optimization criteria
            user_preferences: User preferences
            
        Returns:
            Dictionary mapping route IDs to scores
        """
        scores = {}
        
        # Extract metrics for normalization
        costs = [float(route.cost_breakdown.total_cost) for route in routes]
        times = [route.osrm_route.duration / 60 for route in routes]  # Convert to minutes
        distances = [route.osrm_route.distance / 1000 for route in routes]  # Convert to km
        toll_costs = [float(route.cost_breakdown.total_toll_cost) for route in routes]
        
        # Normalize metrics (0-1 scale, lower is better)
        min_cost, max_cost = min(costs), max(costs)
        min_time, max_time = min(times), max(times)
        min_distance, max_distance = min(distances), max(distances)
        min_toll, max_toll = min(toll_costs), max(toll_costs)
        
        for i, route in enumerate(routes):
            # Normalize individual scores (0-1, lower is better)
            cost_score = self._normalize_score(costs[i], min_cost, max_cost)
            time_score = self._normalize_score(times[i], min_time, max_time)
            distance_score = self._normalize_score(distances[i], min_distance, max_distance)
            toll_score = self._normalize_score(toll_costs[i], min_toll, max_toll)
            
            # Calculate weighted total score based on criteria
            total_score = self._calculate_weighted_score(
                cost_score, time_score, distance_score, toll_score,
                criteria, user_preferences
            )
            
            # Determine ranking
            ranking = self._determine_ranking(total_score)
            
            route_id = f"route_{i}"
            scores[route_id] = RouteScore(
                total_score=total_score,
                cost_score=cost_score,
                time_score=time_score,
                distance_score=distance_score,
                toll_score=toll_score,
                ranking=ranking
            )
        
        return scores
    
    def _normalize_score(self, value: float, min_val: float, max_val: float) -> float:
        """Normalize a score to 0-1 range."""
        if max_val == min_val:
            return 0.0
        return (value - min_val) / (max_val - min_val)
    
    def _calculate_weighted_score(
        self,
        cost_score: float,
        time_score: float,
        distance_score: float,
        toll_score: float,
        criteria: OptimizationCriteria,
        user_preferences: Dict[str, Any]
    ) -> float:
        """Calculate weighted total score based on criteria."""
        # Default weights
        weights = {
            OptimizationCriteria.TOTAL_COST: {"cost": 0.6, "time": 0.2, "distance": 0.1, "toll": 0.1},
            OptimizationCriteria.FUEL_COST: {"cost": 0.7, "time": 0.2, "distance": 0.1, "toll": 0.0},
            OptimizationCriteria.TIME: {"cost": 0.2, "time": 0.6, "distance": 0.1, "toll": 0.1},
            OptimizationCriteria.DISTANCE: {"cost": 0.2, "time": 0.2, "distance": 0.6, "toll": 0.0},
            OptimizationCriteria.TOLL_AVOIDANCE: {"cost": 0.2, "time": 0.2, "distance": 0.1, "toll": 0.5},
            OptimizationCriteria.BALANCED: {"cost": 0.3, "time": 0.3, "distance": 0.2, "toll": 0.2}
        }
        
        # Get weights for criteria
        weight_set = weights.get(criteria, weights[OptimizationCriteria.BALANCED])
        
        # Apply user preference adjustments
        if user_preferences.get("prioritize_cost"):
            weight_set["cost"] += 0.1
            weight_set["time"] -= 0.05
            weight_set["distance"] -= 0.05
        
        if user_preferences.get("prioritize_time"):
            weight_set["time"] += 0.1
            weight_set["cost"] -= 0.05
            weight_set["distance"] -= 0.05
        
        if user_preferences.get("avoid_tolls"):
            weight_set["toll"] += 0.2
            weight_set["cost"] -= 0.1
            weight_set["time"] -= 0.1
        
        # Calculate weighted score
        total_score = (
            cost_score * weight_set["cost"] +
            time_score * weight_set["time"] +
            distance_score * weight_set["distance"] +
            toll_score * weight_set["toll"]
        )
        
        return total_score
    
    def _determine_ranking(self, total_score: float) -> RouteRanking:
        """Determine route ranking based on total score."""
        if total_score <= 0.25:
            return RouteRanking.BEST
        elif total_score <= 0.5:
            return RouteRanking.GOOD
        elif total_score <= 0.75:
            return RouteRanking.ACCEPTABLE
        else:
            return RouteRanking.POOR
    
    def _select_recommended_route(
        self,
        routes: List[OptimizedRoute],
        route_scores: Dict[str, RouteScore],
        criteria: OptimizationCriteria
    ) -> OptimizedRoute:
        """Select the recommended route based on scores."""
        # Find route with lowest (best) total score
        best_route_id = min(route_scores.keys(), key=lambda k: route_scores[k].total_score)
        best_route_index = int(best_route_id.split('_')[1])
        
        recommended_route = routes[best_route_index]
        recommended_route.route_type = "recommended"
        
        return recommended_route
    
    def _generate_route_comparisons(self, routes: List[OptimizedRoute]) -> List[RouteComparison]:
        """Generate pairwise route comparisons."""
        comparisons = []
        
        for i in range(len(routes)):
            for j in range(i + 1, len(routes)):
                route_a = routes[i]
                route_b = routes[j]
                
                comparison = self._compare_two_routes(route_a, route_b, f"route_{i}", f"route_{j}")
                comparisons.append(comparison)
        
        return comparisons
    
    def _compare_two_routes(
        self,
        route_a: OptimizedRoute,
        route_b: OptimizedRoute,
        route_a_id: str,
        route_b_id: str
    ) -> RouteComparison:
        """Compare two routes and generate recommendation."""
        # Calculate differences
        cost_diff = route_b.cost_breakdown.total_cost - route_a.cost_breakdown.total_cost
        time_diff = (route_b.osrm_route.duration - route_a.osrm_route.duration) / 60  # minutes
        distance_diff = (route_b.osrm_route.distance - route_a.osrm_route.distance) / 1000  # km
        toll_diff = route_b.cost_breakdown.total_toll_cost - route_a.cost_breakdown.total_toll_cost
        
        # Generate recommendation
        if abs(float(cost_diff)) < 10:  # Less than ARS $10 difference
            if time_diff < -5:  # Route B is significantly faster
                recommendation = f"{route_b_id} is faster with similar cost"
                confidence = 0.8
            elif time_diff > 5:  # Route A is significantly faster
                recommendation = f"{route_a_id} is faster with similar cost"
                confidence = 0.8
            else:
                recommendation = "Routes are very similar"
                confidence = 0.6
        elif float(cost_diff) < 0:  # Route A is cheaper
            if time_diff > 30:  # But significantly slower
                recommendation = f"{route_a_id} is cheaper but much slower"
                confidence = 0.7
            else:
                recommendation = f"{route_a_id} is more cost-effective"
                confidence = 0.9
        else:  # Route B is cheaper
            if time_diff < -30:  # And significantly faster
                recommendation = f"{route_b_id} is cheaper and faster"
                confidence = 0.95
            else:
                recommendation = f"{route_b_id} is more cost-effective"
                confidence = 0.9
        
        return RouteComparison(
            route_a_id=route_a_id,
            route_b_id=route_b_id,
            cost_difference=cost_diff,
            time_difference=time_diff,
            distance_difference=distance_diff,
            toll_difference=toll_diff,
            recommendation=recommendation,
            confidence=confidence
        )
    
    def _analyze_savings(
        self,
        routes: List[OptimizedRoute],
        recommended_route: OptimizedRoute
    ) -> SavingsAnalysis:
        """Analyze potential savings of recommended route."""
        # Find fastest route (usually first one)
        fastest_route = routes[0]
        
        # If recommended route is the fastest, compare with most expensive
        if recommended_route == fastest_route:
            baseline_route = max(routes, key=lambda r: r.cost_breakdown.total_cost)
        else:
            baseline_route = fastest_route
        
        # Calculate savings
        absolute_savings = baseline_route.cost_breakdown.total_cost - recommended_route.cost_breakdown.total_cost
        
        if float(baseline_route.cost_breakdown.total_cost) > 0:
            percentage_savings = (float(absolute_savings) / float(baseline_route.cost_breakdown.total_cost)) * 100
        else:
            percentage_savings = 0.0
        
        # Calculate trade-offs
        time_trade_off = (recommended_route.osrm_route.duration - baseline_route.osrm_route.duration) / 60
        distance_trade_off = (recommended_route.osrm_route.distance - baseline_route.osrm_route.distance) / 1000
        
        # Calculate efficiency metrics
        savings_per_minute = absolute_savings / max(abs(time_trade_off), 1) if time_trade_off != 0 else Decimal('0')
        savings_per_km = absolute_savings / max(abs(distance_trade_off), 1) if distance_trade_off != 0 else Decimal('0')
        
        return SavingsAnalysis(
            recommended_route_id="recommended",
            baseline_route_id="baseline",
            absolute_savings=absolute_savings,
            percentage_savings=percentage_savings,
            time_trade_off=time_trade_off,
            distance_trade_off=distance_trade_off,
            savings_per_minute=savings_per_minute,
            savings_per_km=savings_per_km
        )
    
    def _generate_optimization_insights(
        self,
        routes: List[OptimizedRoute],
        recommended_route: OptimizedRoute,
        criteria: OptimizationCriteria
    ) -> List[str]:
        """Generate optimization insights."""
        insights = []
        
        # Cost analysis
        costs = [float(route.cost_breakdown.total_cost) for route in routes]
        cost_range = max(costs) - min(costs)
        
        if cost_range > 100:  # Significant cost difference
            insights.append(f"Route costs vary by up to ARS ${cost_range:.2f} - optimization can provide significant savings")
        elif cost_range < 20:
            insights.append("All routes have similar costs - consider time or convenience factors")
        
        # Time analysis
        times = [route.osrm_route.duration / 60 for route in routes]
        time_range = max(times) - min(times)
        
        if time_range > 30:  # More than 30 minutes difference
            insights.append(f"Route times vary by up to {time_range:.0f} minutes - consider time vs cost trade-offs")
        
        # Toll analysis
        toll_routes = [route for route in routes if route.cost_breakdown.total_toll_cost > 0]
        toll_free_routes = [route for route in routes if route.cost_breakdown.total_toll_cost == 0]
        
        if toll_routes and toll_free_routes:
            avg_toll_cost = statistics.mean([float(route.cost_breakdown.total_toll_cost) for route in toll_routes])
            insights.append(f"Toll-free alternatives available - average toll cost is ARS ${avg_toll_cost:.2f}")
        
        # Fuel efficiency insights
        fuel_costs = [float(route.cost_breakdown.fuel_cost.total_fuel_cost) for route in routes]
        fuel_range = max(fuel_costs) - min(fuel_costs)
        
        if fuel_range > 200:  # Significant fuel cost difference
            insights.append(f"Fuel costs vary by ARS ${fuel_range:.2f} - shorter routes provide better fuel efficiency")
        
        # Distance insights
        distances = [route.osrm_route.distance / 1000 for route in routes]
        distance_range = max(distances) - min(distances)
        
        if distance_range > 50:  # More than 50km difference
            insights.append(f"Route distances vary by {distance_range:.1f} km - consider vehicle wear and maintenance costs")
        
        # Criteria-specific insights
        if criteria == OptimizationCriteria.TOTAL_COST:
            insights.append("Optimization focused on total cost - recommended route minimizes fuel and toll expenses")
        elif criteria == OptimizationCriteria.TIME:
            insights.append("Optimization focused on time - recommended route prioritizes speed over cost")
        elif criteria == OptimizationCriteria.TOLL_AVOIDANCE:
            insights.append("Optimization focused on toll avoidance - recommended route minimizes toll expenses")
        
        return insights
    
    def _generate_warnings(
        self,
        routes: List[OptimizedRoute],
        recommended_route: OptimizedRoute
    ) -> List[str]:
        """Generate warnings about route optimization."""
        warnings = []
        
        # Check for very high costs
        if float(recommended_route.cost_breakdown.total_cost) > 5000:
            warnings.append("High route cost detected - verify fuel prices and vehicle efficiency")
        
        # Check for very long routes
        if recommended_route.osrm_route.distance > 1000000:  # More than 1000km
            warnings.append("Very long route detected - consider overnight stops or driver rest requirements")
        
        # Check for very long times
        if recommended_route.osrm_route.duration > 28800:  # More than 8 hours
            warnings.append("Long driving time detected - consider driver fatigue and legal driving limits")
        
        # Check for toll-heavy routes
        if float(recommended_route.cost_breakdown.total_toll_cost) > float(recommended_route.cost_breakdown.fuel_cost.total_fuel_cost):
            warnings.append("Toll costs exceed fuel costs - consider toll-free alternatives")
        
        # Check for minimal savings
        if recommended_route.estimated_savings and float(recommended_route.estimated_savings) < 10:
            warnings.append("Minimal cost savings detected - fastest route may be more practical")
        
        # Check for data freshness (would need database access in real implementation)
        warnings.append("Verify fuel prices and toll costs are current for accurate optimization")
        
        return warnings
    
    def rank_routes_by_criteria(
        self,
        routes: List[OptimizedRoute],
        criteria: OptimizationCriteria
    ) -> List[Tuple[OptimizedRoute, float]]:
        """
        Rank routes by specific criteria.
        
        Args:
            routes: Routes to rank
            criteria: Ranking criteria
            
        Returns:
            List of (route, score) tuples sorted by score
        """
        scored_routes = []
        
        for route in routes:
            if criteria == OptimizationCriteria.TOTAL_COST:
                score = float(route.cost_breakdown.total_cost)
            elif criteria == OptimizationCriteria.FUEL_COST:
                score = float(route.cost_breakdown.fuel_cost.total_fuel_cost)
            elif criteria == OptimizationCriteria.TIME:
                score = route.osrm_route.duration
            elif criteria == OptimizationCriteria.DISTANCE:
                score = route.osrm_route.distance
            elif criteria == OptimizationCriteria.TOLL_AVOIDANCE:
                score = float(route.cost_breakdown.total_toll_cost)
            else:  # BALANCED
                # Weighted combination
                cost_norm = float(route.cost_breakdown.total_cost) / 1000  # Normalize to similar scale
                time_norm = route.osrm_route.duration / 3600  # Hours
                distance_norm = route.osrm_route.distance / 100000  # 100km units
                score = cost_norm + time_norm + distance_norm
            
            scored_routes.append((route, score))
        
        # Sort by score (lower is better for all criteria)
        scored_routes.sort(key=lambda x: x[1])
        
        return scored_routes
    
    def calculate_route_efficiency_metrics(self, route: OptimizedRoute) -> Dict[str, float]:
        """
        Calculate efficiency metrics for a route.
        
        Args:
            route: Route to analyze
            
        Returns:
            Dictionary of efficiency metrics
        """
        distance_km = route.osrm_route.distance / 1000
        duration_hours = route.osrm_route.duration / 3600
        
        metrics = {
            "cost_per_km": float(route.cost_breakdown.total_cost) / distance_km if distance_km > 0 else 0,
            "cost_per_hour": float(route.cost_breakdown.total_cost) / duration_hours if duration_hours > 0 else 0,
            "fuel_efficiency": float(route.cost_breakdown.fuel_cost.fuel_consumption_per_100km),
            "average_speed_kmh": distance_km / duration_hours if duration_hours > 0 else 0,
            "toll_density": float(route.cost_breakdown.total_toll_cost) / distance_km if distance_km > 0 else 0,
            "fuel_cost_ratio": float(route.cost_breakdown.fuel_cost.total_fuel_cost) / float(route.cost_breakdown.total_cost) if float(route.cost_breakdown.total_cost) > 0 else 0,
            "toll_cost_ratio": float(route.cost_breakdown.total_toll_cost) / float(route.cost_breakdown.total_cost) if float(route.cost_breakdown.total_cost) > 0 else 0
        }
        
        return metrics