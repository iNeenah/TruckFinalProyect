"""
Demo of route comparison and optimization logic.
"""
from decimal import Decimal
from dataclasses import dataclass
from typing import List, Dict, Any
from enum import Enum


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
class RouteData:
    """Route data for comparison."""
    name: str
    distance_km: float
    duration_minutes: float
    fuel_cost: Decimal
    toll_cost: Decimal
    total_cost: Decimal
    route_type: str


@dataclass
class RouteScore:
    """Route scoring information."""
    route_name: str
    total_score: float
    cost_score: float
    time_score: float
    distance_score: float
    toll_score: float
    ranking: RouteRanking


@dataclass
class RouteComparison:
    """Comparison between two routes."""
    route_a: str
    route_b: str
    cost_difference: Decimal
    time_difference: float
    distance_difference: float
    recommendation: str
    confidence: float


def normalize_score(value: float, min_val: float, max_val: float) -> float:
    """Normalize a score to 0-1 range (lower is better)."""
    if max_val == min_val:
        return 0.0
    return (value - min_val) / (max_val - min_val)


def calculate_weighted_score(
    cost_score: float,
    time_score: float,
    distance_score: float,
    toll_score: float,
    criteria: OptimizationCriteria
) -> float:
    """Calculate weighted total score based on criteria."""
    weights = {
        OptimizationCriteria.TOTAL_COST: {"cost": 0.6, "time": 0.2, "distance": 0.1, "toll": 0.1},
        OptimizationCriteria.FUEL_COST: {"cost": 0.7, "time": 0.2, "distance": 0.1, "toll": 0.0},
        OptimizationCriteria.TIME: {"cost": 0.2, "time": 0.6, "distance": 0.1, "toll": 0.1},
        OptimizationCriteria.DISTANCE: {"cost": 0.2, "time": 0.2, "distance": 0.6, "toll": 0.0},
        OptimizationCriteria.TOLL_AVOIDANCE: {"cost": 0.2, "time": 0.2, "distance": 0.1, "toll": 0.5},
        OptimizationCriteria.BALANCED: {"cost": 0.3, "time": 0.3, "distance": 0.2, "toll": 0.2}
    }
    
    weight_set = weights.get(criteria, weights[OptimizationCriteria.BALANCED])
    
    return (
        cost_score * weight_set["cost"] +
        time_score * weight_set["time"] +
        distance_score * weight_set["distance"] +
        toll_score * weight_set["toll"]
    )


def determine_ranking(total_score: float) -> RouteRanking:
    """Determine route ranking based on total score."""
    if total_score <= 0.25:
        return RouteRanking.BEST
    elif total_score <= 0.5:
        return RouteRanking.GOOD
    elif total_score <= 0.75:
        return RouteRanking.ACCEPTABLE
    else:
        return RouteRanking.POOR


def score_routes(routes: List[RouteData], criteria: OptimizationCriteria) -> List[RouteScore]:
    """Score all routes based on criteria."""
    # Extract metrics for normalization
    costs = [float(route.total_cost) for route in routes]
    times = [route.duration_minutes for route in routes]
    distances = [route.distance_km for route in routes]
    toll_costs = [float(route.toll_cost) for route in routes]
    
    # Get min/max for normalization
    min_cost, max_cost = min(costs), max(costs)
    min_time, max_time = min(times), max(times)
    min_distance, max_distance = min(distances), max(distances)
    min_toll, max_toll = min(toll_costs), max(toll_costs)
    
    scores = []
    
    for i, route in enumerate(routes):
        # Normalize scores (0-1, lower is better)
        cost_score = normalize_score(costs[i], min_cost, max_cost)
        time_score = normalize_score(times[i], min_time, max_time)
        distance_score = normalize_score(distances[i], min_distance, max_distance)
        toll_score = normalize_score(toll_costs[i], min_toll, max_toll)
        
        # Calculate weighted total score
        total_score = calculate_weighted_score(
            cost_score, time_score, distance_score, toll_score, criteria
        )
        
        # Determine ranking
        ranking = determine_ranking(total_score)
        
        score = RouteScore(
            route_name=route.name,
            total_score=total_score,
            cost_score=cost_score,
            time_score=time_score,
            distance_score=distance_score,
            toll_score=toll_score,
            ranking=ranking
        )
        scores.append(score)
    
    return scores


def compare_routes(route_a: RouteData, route_b: RouteData) -> RouteComparison:
    """Compare two routes and generate recommendation."""
    cost_diff = route_b.total_cost - route_a.total_cost
    time_diff = route_b.duration_minutes - route_a.duration_minutes
    distance_diff = route_b.distance_km - route_a.distance_km
    
    # Generate recommendation
    if abs(float(cost_diff)) < 50:  # Less than $50 difference
        if time_diff < -10:  # Route B is significantly faster
            recommendation = f"{route_b.name} is faster with similar cost"
            confidence = 0.8
        elif time_diff > 10:  # Route A is significantly faster
            recommendation = f"{route_a.name} is faster with similar cost"
            confidence = 0.8
        else:
            recommendation = "Routes are very similar"
            confidence = 0.6
    elif float(cost_diff) < 0:  # Route A is cheaper
        if time_diff > 30:  # But significantly slower
            recommendation = f"{route_a.name} is cheaper but much slower"
            confidence = 0.7
        else:
            recommendation = f"{route_a.name} is more cost-effective"
            confidence = 0.9
    else:  # Route B is cheaper
        if time_diff < -30:  # And significantly faster
            recommendation = f"{route_b.name} is cheaper and faster"
            confidence = 0.95
        else:
            recommendation = f"{route_b.name} is more cost-effective"
            confidence = 0.9
    
    return RouteComparison(
        route_a=route_a.name,
        route_b=route_b.name,
        cost_difference=cost_diff,
        time_difference=time_diff,
        distance_difference=distance_diff,
        recommendation=recommendation,
        confidence=confidence
    )


def analyze_savings(routes: List[RouteData], recommended_route: RouteData) -> Dict[str, Any]:
    """Analyze potential savings."""
    # Find fastest route (baseline)
    fastest_route = min(routes, key=lambda r: r.duration_minutes)
    
    if recommended_route == fastest_route:
        # Compare with most expensive route
        baseline_route = max(routes, key=lambda r: r.total_cost)
    else:
        baseline_route = fastest_route
    
    absolute_savings = baseline_route.total_cost - recommended_route.total_cost
    percentage_savings = (float(absolute_savings) / float(baseline_route.total_cost)) * 100 if float(baseline_route.total_cost) > 0 else 0
    
    time_trade_off = recommended_route.duration_minutes - baseline_route.duration_minutes
    distance_trade_off = recommended_route.distance_km - baseline_route.distance_km
    
    return {
        "baseline_route": baseline_route.name,
        "recommended_route": recommended_route.name,
        "absolute_savings": absolute_savings,
        "percentage_savings": percentage_savings,
        "time_trade_off": time_trade_off,
        "distance_trade_off": distance_trade_off
    }


def generate_insights(routes: List[RouteData], recommended_route: RouteData) -> List[str]:
    """Generate optimization insights."""
    insights = []
    
    # Cost analysis
    costs = [float(route.total_cost) for route in routes]
    cost_range = max(costs) - min(costs)
    
    if cost_range > 200:
        insights.append(f"Route costs vary by up to ${cost_range:.2f} - optimization provides significant savings")
    elif cost_range < 50:
        insights.append("All routes have similar costs - consider time or convenience factors")
    
    # Time analysis
    times = [route.duration_minutes for route in routes]
    time_range = max(times) - min(times)
    
    if time_range > 30:
        insights.append(f"Route times vary by up to {time_range:.0f} minutes - consider time vs cost trade-offs")
    
    # Toll analysis
    toll_routes = [route for route in routes if route.toll_cost > 0]
    toll_free_routes = [route for route in routes if route.toll_cost == 0]
    
    if toll_routes and toll_free_routes:
        avg_toll_cost = sum(float(route.toll_cost) for route in toll_routes) / len(toll_routes)
        insights.append(f"Toll-free alternatives available - average toll cost is ${avg_toll_cost:.2f}")
    
    # Distance insights
    distances = [route.distance_km for route in routes]
    distance_range = max(distances) - min(distances)
    
    if distance_range > 50:
        insights.append(f"Route distances vary by {distance_range:.1f} km - consider vehicle wear costs")
    
    return insights


def main():
    """Run route comparison demo."""
    print("🚀 Route Comparison and Optimization Demo")
    print("=" * 50)
    
    # Sample route data (Posadas to Puerto Iguazú)
    routes = [
        RouteData(
            name="Fastest Route (RN12)",
            distance_km=295.2,
            duration_minutes=225,  # 3h 45m
            fuel_cost=Decimal("847.50"),
            toll_cost=Decimal("90.00"),
            total_cost=Decimal("937.50"),
            route_type="fastest"
        ),
        RouteData(
            name="Cheapest Route (Secondary Roads)",
            distance_km=312.8,
            duration_minutes=280,  # 4h 40m
            fuel_cost=Decimal("897.20"),
            toll_cost=Decimal("0.00"),
            total_cost=Decimal("897.20"),
            route_type="cheapest"
        ),
        RouteData(
            name="Balanced Route (Mixed)",
            distance_km=305.5,
            duration_minutes=250,  # 4h 10m
            fuel_cost=Decimal("876.80"),
            toll_cost=Decimal("45.00"),
            total_cost=Decimal("921.80"),
            route_type="balanced"
        ),
        RouteData(
            name="Scenic Route (Coastal)",
            distance_km=340.0,
            duration_minutes=300,  # 5h
            fuel_cost=Decimal("975.60"),
            toll_cost=Decimal("45.00"),
            total_cost=Decimal("1020.60"),
            route_type="scenic"
        )
    ]
    
    print("📊 Available Routes:")
    print(f"{'Route':<25} {'Distance':<10} {'Time':<8} {'Fuel':<10} {'Tolls':<8} {'Total':<10}")
    print("-" * 80)
    
    for route in routes:
        hours = int(route.duration_minutes // 60)
        minutes = int(route.duration_minutes % 60)
        time_str = f"{hours}h {minutes}m"
        
        print(f"{route.name:<25} {route.distance_km:<10.1f} {time_str:<8} "
              f"${route.fuel_cost:<9.2f} ${route.toll_cost:<7.2f} ${route.total_cost:<9.2f}")
    
    # Test different optimization criteria
    criteria_list = [
        OptimizationCriteria.TOTAL_COST,
        OptimizationCriteria.TIME,
        OptimizationCriteria.TOLL_AVOIDANCE,
        OptimizationCriteria.BALANCED
    ]
    
    for criteria in criteria_list:
        print(f"\n🎯 Optimization by {criteria.value.replace('_', ' ').title()}:")
        print("-" * 40)
        
        # Score routes
        scores = score_routes(routes, criteria)
        
        # Sort by total score (best first)
        scores.sort(key=lambda s: s.total_score)
        
        print(f"{'Rank':<5} {'Route':<25} {'Score':<8} {'Ranking':<12}")
        print("-" * 55)
        
        for i, score in enumerate(scores):
            rank_emoji = ["🥇", "🥈", "🥉", "4️⃣"][min(i, 3)]
            ranking_emoji = {
                RouteRanking.BEST: "⭐",
                RouteRanking.GOOD: "👍",
                RouteRanking.ACCEPTABLE: "👌",
                RouteRanking.POOR: "⚠️"
            }[score.ranking]
            
            print(f"{rank_emoji:<5} {score.route_name:<25} {score.total_score:<8.3f} "
                  f"{score.ranking.value:<12} {ranking_emoji}")
        
        # Show recommended route
        recommended = scores[0]
        recommended_route = next(r for r in routes if r.name == recommended.route_name)
        
        print(f"\n✅ Recommended: {recommended.route_name}")
        
        # Analyze savings
        savings = analyze_savings(routes, recommended_route)
        if float(savings["absolute_savings"]) > 0:
            print(f"💰 Savings: ${savings['absolute_savings']:.2f} ({savings['percentage_savings']:.1f}%)")
            if savings["time_trade_off"] > 0:
                print(f"⏱️  Trade-off: +{savings['time_trade_off']:.0f} minutes")
        else:
            print("💰 This is already the most economical option")
    
    print(f"\n🔍 Route Comparisons:")
    print("-" * 30)
    
    # Compare first few routes
    comparison = compare_routes(routes[0], routes[1])
    print(f"📊 {comparison.route_a} vs {comparison.route_b}:")
    print(f"   Cost difference: ${comparison.cost_difference:.2f}")
    print(f"   Time difference: {comparison.time_difference:.0f} minutes")
    print(f"   Distance difference: {comparison.distance_difference:.1f} km")
    print(f"   Recommendation: {comparison.recommendation}")
    print(f"   Confidence: {comparison.confidence:.0%}")
    
    print(f"\n💡 Optimization Insights:")
    print("-" * 25)
    
    # Use balanced criteria for insights
    balanced_scores = score_routes(routes, OptimizationCriteria.BALANCED)
    best_balanced = min(balanced_scores, key=lambda s: s.total_score)
    best_route = next(r for r in routes if r.name == best_balanced.route_name)
    
    insights = generate_insights(routes, best_route)
    for i, insight in enumerate(insights, 1):
        print(f"   {i}. {insight}")
    
    print(f"\n🎯 Final Recommendation:")
    print(f"   For balanced optimization: {best_route.name}")
    print(f"   Total cost: ${best_route.total_cost:.2f}")
    print(f"   Travel time: {best_route.duration_minutes/60:.1f} hours")
    print(f"   Distance: {best_route.distance_km:.1f} km")
    
    print("\n✅ Route comparison analysis completed!")


if __name__ == "__main__":
    main()