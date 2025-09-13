"""
Example usage of administrative panel API endpoints.

This script demonstrates how to use the admin endpoints for fuel price management.
"""
import asyncio
import aiohttp
import json
from datetime import date, datetime
from decimal import Decimal


class AdminAPIExample:
    """Example client for admin API endpoints."""
    
    def __init__(self, base_url: str = "http://localhost:8000", admin_token: str = None):
        """
        Initialize admin API client.
        
        Args:
            base_url: Base URL of the API
            admin_token: JWT token for admin authentication
        """
        self.base_url = base_url
        self.admin_token = admin_token
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {admin_token}" if admin_token else ""
        }
    
    async def get_fuel_prices(self, fuel_type: str = None, region: str = None, active_only: bool = True):
        """
        Get current fuel prices.
        
        Args:
            fuel_type: Filter by fuel type
            region: Filter by region
            active_only: Show only active prices
        """
        params = {}
        if fuel_type:
            params["fuel_type"] = fuel_type
        if region:
            params["region"] = region
        params["active_only"] = active_only
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/api/admin/fuel-prices",
                headers=self.headers,
                params=params
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"Retrieved {len(data)} fuel prices:")
                    for price in data:
                        print(f"  {price['fuel_type']} - {price['region']}: "
                              f"${price['price_per_liter']}/L (effective: {price['effective_date']})")
                    return data
                else:
                    error = await response.json()
                    print(f"Error getting fuel prices: {error}")
                    return None
    
    async def update_fuel_price(self, price_id: int, new_price: float, effective_date: str = None):
        """
        Update a specific fuel price.
        
        Args:
            price_id: ID of the price to update
            new_price: New price per liter
            effective_date: Effective date (ISO format)
        """
        update_data = {
            "price_per_liter": new_price,
            "effective_date": effective_date or date.today().isoformat(),
            "is_active": True
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.put(
                f"{self.base_url}/api/admin/fuel-prices/{price_id}",
                headers=self.headers,
                json=update_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"Updated fuel price {price_id}:")
                    print(f"  {data['fuel_type']} - {data['region']}: "
                          f"${data['price_per_liter']}/L")
                    return data
                else:
                    error = await response.json()
                    print(f"Error updating fuel price: {error}")
                    return None
    
    async def get_price_history(self, price_id: int, days: int = 90):
        """
        Get price history for a specific fuel price.
        
        Args:
            price_id: ID of the price
            days: Number of days of history
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/api/admin/fuel-prices/{price_id}/history",
                headers=self.headers,
                params={"days": days}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"Price history for fuel price {price_id} ({len(data)} records):")
                    for record in data:
                        print(f"  {record['effective_date']}: ${record['price_per_liter']}/L "
                              f"(updated: {record['updated_at']})")
                    return data
                else:
                    error = await response.json()
                    print(f"Error getting price history: {error}")
                    return None
    
    async def get_audit_log(self, days: int = 30, fuel_type: str = None):
        """
        Get audit log for fuel price changes.
        
        Args:
            days: Number of days of audit log
            fuel_type: Filter by fuel type
        """
        params = {"days": days}
        if fuel_type:
            params["fuel_type"] = fuel_type
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/api/admin/fuel-prices/audit-log",
                headers=self.headers,
                params=params
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"Audit log ({len(data)} entries):")
                    for entry in data:
                        print(f"  {entry['updated_at']}: {entry['action']} "
                              f"{entry['fuel_type']} - {entry['region']} "
                              f"(${entry['price_per_liter']}/L) by {entry['updated_by']}")
                    return data
                else:
                    error = await response.json()
                    print(f"Error getting audit log: {error}")
                    return None
    
    async def check_staleness(self, threshold_days: int = 30):
        """
        Check for stale fuel price data.
        
        Args:
            threshold_days: Staleness threshold in days
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/api/admin/fuel-prices/staleness-check",
                headers=self.headers,
                params={"threshold_days": threshold_days}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"Staleness check (threshold: {threshold_days} days):")
                    print(f"  Total stale prices: {data['total_stale_prices']}")
                    print(f"  Stale categories: {data['stale_categories']}")
                    
                    if data['stale_prices']:
                        print("  Stale prices by category:")
                        for category, prices in data['stale_prices'].items():
                            print(f"    {category}: {len(prices)} prices")
                            for price in prices:
                                print(f"      ID {price['id']}: {price['days_old']} days old")
                    
                    print("  Recommendations:")
                    for rec in data['recommendations']:
                        print(f"    - {rec}")
                    
                    return data
                else:
                    error = await response.json()
                    print(f"Error checking staleness: {error}")
                    return None
    
    async def bulk_update_prices(self, updates: list):
        """
        Perform bulk update of fuel prices.
        
        Args:
            updates: List of price updates
        """
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/api/admin/fuel-prices/bulk-update",
                headers=self.headers,
                json=updates
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"Bulk update completed:")
                    print(f"  {data['message']}")
                    print(f"  Updated prices:")
                    for price in data['updated_prices']:
                        print(f"    ID {price['id']}: {price['fuel_type']} - "
                              f"{price['region']} = ${price['price_per_liter']}/L")
                    return data
                else:
                    error = await response.json()
                    print(f"Error in bulk update: {error}")
                    return None


async def main():
    """
    Main example function demonstrating admin API usage.
    """
    print("=== Admin API Example ===\n")
    
    # Initialize client (you would need a real admin JWT token)
    admin_token = "your-admin-jwt-token-here"
    client = AdminAPIExample(admin_token=admin_token)
    
    print("1. Getting current fuel prices...")
    await client.get_fuel_prices()
    print()
    
    print("2. Getting diesel prices only...")
    await client.get_fuel_prices(fuel_type="diesel_500")
    print()
    
    print("3. Checking for stale prices...")
    await client.check_staleness(threshold_days=30)
    print()
    
    print("4. Getting audit log...")
    await client.get_audit_log(days=7)
    print()
    
    # Example of updating a price (uncomment to test)
    # print("5. Updating fuel price...")
    # await client.update_fuel_price(
    #     price_id=1,
    #     new_price=155.50,
    #     effective_date=date.today().isoformat()
    # )
    # print()
    
    # Example of bulk update (uncomment to test)
    # print("6. Bulk updating prices...")
    # bulk_updates = [
    #     {
    #         "price_id": 1,
    #         "price_per_liter": 152.00,
    #         "effective_date": date.today().isoformat(),
    #         "is_active": True
    #     },
    #     {
    #         "price_id": 2,
    #         "price_per_liter": 167.50,
    #         "effective_date": date.today().isoformat(),
    #         "is_active": True
    #     }
    # ]
    # await client.bulk_update_prices(bulk_updates)
    # print()
    
    print("=== Example completed ===")


def demo_without_server():
    """
    Demonstrate the API structure without making actual requests.
    """
    print("=== Admin API Structure Demo ===\n")
    
    print("Available Admin Endpoints:")
    print("  GET  /api/admin/fuel-prices")
    print("       - Get current fuel prices with filtering")
    print("       - Query params: fuel_type, region, active_only")
    print()
    
    print("  PUT  /api/admin/fuel-prices/{price_id}")
    print("       - Update a specific fuel price")
    print("       - Body: price_per_liter, effective_date, is_active")
    print()
    
    print("  GET  /api/admin/fuel-prices/{price_id}/history")
    print("       - Get price history for a specific fuel price")
    print("       - Query params: days")
    print()
    
    print("  GET  /api/admin/fuel-prices/audit-log")
    print("       - Get audit log of price changes")
    print("       - Query params: days, fuel_type, updated_by")
    print()
    
    print("  GET  /api/admin/fuel-prices/staleness-check")
    print("       - Check for stale price data")
    print("       - Query params: threshold_days")
    print()
    
    print("  POST /api/admin/fuel-prices/bulk-update")
    print("       - Bulk update multiple fuel prices")
    print("       - Body: array of price updates")
    print()
    
    print("Example Request Bodies:")
    print()
    
    print("Update fuel price:")
    update_example = {
        "price_per_liter": 155.50,
        "effective_date": "2024-01-15",
        "is_active": True
    }
    print(json.dumps(update_example, indent=2))
    print()
    
    print("Bulk update:")
    bulk_example = [
        {
            "price_id": 1,
            "price_per_liter": 152.00,
            "effective_date": "2024-01-15",
            "is_active": True
        },
        {
            "price_id": 2,
            "price_per_liter": 167.50,
            "effective_date": "2024-01-15",
            "is_active": True
        }
    ]
    print(json.dumps(bulk_example, indent=2))
    print()
    
    print("=== Demo completed ===")


if __name__ == "__main__":
    print("Choose demo mode:")
    print("1. Structure demo (no server required)")
    print("2. Live API demo (requires running server and admin token)")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        demo_without_server()
    elif choice == "2":
        asyncio.run(main())
    else:
        print("Invalid choice. Running structure demo...")
        demo_without_server()