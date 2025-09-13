"""
Example usage of the Routes API endpoints.
"""
import asyncio
import httpx
import json
from datetime import datetime
import uuid


class RoutesAPIClient:
    """Client for interacting with the Routes API."""
    
    def __init__(self, base_url: str = "http://localhost:8000", token: str = None):
        """
        Initialize API client.
        
        Args:
            base_url: Base URL of the API
            token: JWT authentication token
        """
        self.base_url = base_url
        self.headers = {
            "Content-Type": "application/json"
        }
        if token:
            self.headers["Authorization"] = f"Bearer {token}"
    
    async def calculate_route(self, route_request: dict) -> dict:
        """Calculate route using the API."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/routes/calculate",
                json=route_request,
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
    
    async def geocode_address(self, address: str, limit: int = 5) -> dict:
        """Geocode an address using the API."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/routes/geocode",
                params={"address": address, "limit": limit},
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
    
    async def get_route_history(self, page: int = 1, size: int = 20) -> dict:
        """Get route calculation history."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/routes/history",
                params={"page": page, "size": size},
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
    
    async def get_route_statistics(self, days: int = 30) -> dict:
        """Get route statistics."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/routes/statistics",
                params={"days": days},
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
    
    async def generate_route_report(self, report_request: dict) -> dict:
        """Generate a route report."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/routes/reports",
                json=report_request,
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
    
    async def check_health(self) -> dict:
        """Check API health."""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/api/routes/health")
            response.raise_for_status()
            return response.json()


async def demo_geocoding():
    """Demo geocoding functionality."""
    print("🔍 Geocoding Demo")
    print("-" * 30)
    
    client = RoutesAPIClient()
    
    addresses = [
        "Av. Mitre 1234, Posadas, Misiones",
        "Puerto Iguazú, Misiones",
        "Oberá, Misiones",
        "Eldorado, Misiones"
    ]
    
    for address in addresses:
        try:
            print(f"\n📍 Geocoding: {address}")
            result = await client.geocode_address(address, limit=3)
            
            if result["status"] == "success" and result["results"]:
                for i, geocode_result in enumerate(result["results"]):
                    coords = geocode_result["coordinates"]
                    print(f"  {i+1}. {geocode_result['formatted_address']}")
                    print(f"     Coordinates: {coords['longitude']:.4f}, {coords['latitude']:.4f}")
                    print(f"     Confidence: {geocode_result['confidence']:.2f}")
                    print(f"     Type: {geocode_result['place_type']}")
            else:
                print("  ❌ No results found")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")


async def demo_route_calculation():
    """Demo route calculation functionality."""
    print("\n🛣️  Route Calculation Demo")
    print("-" * 35)
    
    client = RoutesAPIClient()
    
    # Sample route requests
    route_requests = [
        {
            "name": "Address-based Route",
            "request": {
                "origin": "Av. Mitre 1234, Posadas, Misiones",
                "destination": "Av. Victoria Aguirre 567, Puerto Iguazú, Misiones",
                "vehicle_id": str(uuid.uuid4()),
                "alternatives": 3,
                "avoid_tolls": False,
                "optimize_for": "cost"
            }
        },
        {
            "name": "Coordinate-based Route",
            "request": {
                "origin": {"longitude": -55.8959, "latitude": -27.3621},
                "destination": {"longitude": -54.5735, "latitude": -25.5951},
                "vehicle_id": str(uuid.uuid4()),
                "alternatives": 2,
                "avoid_tolls": True,
                "optimize_for": "time"
            }
        },
        {
            "name": "Distance-optimized Route",
            "request": {
                "origin": "Posadas, Misiones",
                "destination": "Oberá, Misiones",
                "vehicle_id": str(uuid.uuid4()),
                "alternatives": 3,
                "avoid_tolls": False,
                "optimize_for": "distance"
            }
        }
    ]
    
    for route_info in route_requests:
        print(f"\n📊 {route_info['name']}:")
        print(f"   Origin: {route_info['request']['origin']}")
        print(f"   Destination: {route_info['request']['destination']}")
        print(f"   Optimize for: {route_info['request']['optimize_for']}")
        print(f"   Avoid tolls: {route_info['request']['avoid_tolls']}")
        
        try:
            # Note: This will fail without authentication and running services
            print("   Status: ⏳ Would calculate route (requires auth & services)")
            
            # Simulated response structure
            print("   Expected response:")
            print("     - request_id: unique identifier")
            print("     - recommended_route: best route with cost breakdown")
            print("     - alternative_routes: other route options")
            print("     - savings_analysis: cost comparison and savings")
            print("     - calculation_time_ms: processing time")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")


async def demo_route_history():
    """Demo route history functionality."""
    print("\n📚 Route History Demo")
    print("-" * 25)
    
    client = RoutesAPIClient()
    
    print("📋 Route History Features:")
    print("  - Paginated list of calculated routes")
    print("  - Filter by vehicle ID")
    print("  - Ordered by calculation date (newest first)")
    print("  - Includes cost breakdown and savings")
    
    print("\n🔍 Sample History Query:")
    print("  GET /api/routes/history?page=1&size=20&vehicle_id=abc123")
    
    print("\n📊 Expected Response Structure:")
    print("  - routes: array of route calculations")
    print("  - total: total number of routes")
    print("  - page: current page number")
    print("  - size: page size")
    print("  - pages: total number of pages")


async def demo_route_statistics():
    """Demo route statistics functionality."""
    print("\n📈 Route Statistics Demo")
    print("-" * 30)
    
    client = RoutesAPIClient()
    
    print("📊 Available Statistics:")
    print("  - Total routes calculated")
    print("  - Total distance traveled")
    print("  - Total cost and savings")
    print("  - Average distance and cost per route")
    print("  - Most used vehicle")
    print("  - Most common origin/destination")
    print("  - Date range analysis")
    
    print("\n🔍 Sample Statistics Query:")
    print("  GET /api/routes/statistics?days=30")
    
    print("\n📊 Expected Response:")
    print("  {")
    print('    "total_routes": 25,')
    print('    "total_distance": 2500.0,')
    print('    "total_cost": 15000.0,')
    print('    "total_savings": 1250.0,')
    print('    "average_distance": 100.0,')
    print('    "average_cost": 600.0,')
    print('    "most_used_vehicle": "Ford Transit",')
    print('    "date_range": {"start": "2024-01-01", "end": "2024-01-31"}')
    print("  }")


async def demo_route_reports():
    """Demo route report generation."""
    print("\n📄 Route Reports Demo")
    print("-" * 25)
    
    client = RoutesAPIClient()
    
    print("📋 Report Generation Features:")
    print("  - PDF and HTML formats")
    print("  - Complete or simple report types")
    print("  - Optional map visualization")
    print("  - Downloadable with expiration")
    
    print("\n🔍 Sample Report Request:")
    report_request = {
        "route_id": str(uuid.uuid4()),
        "report_type": "complete",
        "include_map": True,
        "format": "pdf"
    }
    print(f"  POST /api/routes/reports")
    print(f"  Body: {json.dumps(report_request, indent=2)}")
    
    print("\n📊 Expected Response:")
    print("  {")
    print('    "report_id": "unique-report-id",')
    print('    "download_url": "/routes/reports/unique-report-id/download",')
    print('    "expires_at": "2024-01-31T23:59:59",')
    print('    "file_size": 0,')
    print('    "format": "pdf"')
    print("  }")


async def demo_health_check():
    """Demo health check functionality."""
    print("\n🏥 Health Check Demo")
    print("-" * 25)
    
    client = RoutesAPIClient()
    
    try:
        print("🔍 Checking API health...")
        health = await client.check_health()
        
        print(f"✅ API Status: {health.get('status', 'unknown')}")
        
        services = health.get('services', {})
        for service, status in services.items():
            emoji = "✅" if status == "healthy" else "⚠️" if status == "degraded" else "❌"
            print(f"   {emoji} {service.upper()}: {status}")
        
        print(f"🕐 Timestamp: {health.get('timestamp', 'unknown')}")
        
    except Exception as e:
        print(f"❌ Health check failed: {e}")


async def demo_api_authentication():
    """Demo API authentication requirements."""
    print("\n🔐 Authentication Demo")
    print("-" * 25)
    
    print("🔑 Authentication Requirements:")
    print("  - All endpoints require JWT authentication")
    print("  - Include 'Authorization: Bearer <token>' header")
    print("  - Token obtained from /api/auth/login endpoint")
    
    print("\n📋 Authentication Flow:")
    print("  1. POST /api/auth/login with credentials")
    print("  2. Receive JWT token in response")
    print("  3. Include token in all subsequent requests")
    print("  4. Token expires after configured time (default: 30 minutes)")
    
    print("\n🔍 Sample Login Request:")
    login_request = {
        "email": "user@example.com",
        "password": "secure_password"
    }
    print(f"  POST /api/auth/login")
    print(f"  Body: {json.dumps(login_request, indent=2)}")
    
    print("\n📊 Sample Login Response:")
    print("  {")
    print('    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",')
    print('    "token_type": "bearer",')
    print('    "expires_in": 1800')
    print("  }")


async def main():
    """Run all API demos."""
    print("🚀 Routes API Demo")
    print("=" * 50)
    
    try:
        await demo_health_check()
        await demo_api_authentication()
        await demo_geocoding()
        await demo_route_calculation()
        await demo_route_history()
        await demo_route_statistics()
        await demo_route_reports()
        
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
    
    print("\n✅ API demo completed!")
    print("\n💡 Note: Most endpoints require authentication and running services.")
    print("   Start the API server with: uvicorn main:app --reload")
    print("   Ensure OSRM and database services are running.")


if __name__ == "__main__":
    asyncio.run(main())