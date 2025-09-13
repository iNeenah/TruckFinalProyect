"""
Example usage of toll management admin API endpoints.

This script demonstrates how to use the admin endpoints for toll management.
"""
import asyncio
import aiohttp
import json
from datetime import datetime
from decimal import Decimal


class TollAdminAPIExample:
    """Example client for toll admin API endpoints."""
    
    def __init__(self, base_url: str = "http://localhost:8000", admin_token: str = None):
        """
        Initialize toll admin API client.
        
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
    
    async def get_tolls(self, road_name: str = None, region: str = None, active_only: bool = True):
        """
        Get toll information.
        
        Args:
            road_name: Filter by road name
            region: Filter by region
            active_only: Show only active tolls
        """
        params = {}
        if road_name:
            params["road_name"] = road_name
        if region:
            params["region"] = region
        params["active_only"] = active_only
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/api/admin/tolls",
                headers=self.headers,
                params=params
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"Retrieved {len(data)} tolls:")
                    for toll in data:
                        print(f"  {toll['name']} ({toll['road_name']}): "
                              f"${toll['tariff']} at ({toll['latitude']}, {toll['longitude']})")
                    return data
                else:
                    error = await response.json()
                    print(f"Error getting tolls: {error}")
                    return None
    
    async def create_toll(self, name: str, road_name: str, latitude: float, longitude: float, 
                         tariff: float, region: str = "NEA"):
        """
        Create a new toll.
        
        Args:
            name: Toll name
            road_name: Road name
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            tariff: Toll tariff in ARS
            region: Region code
        """
        toll_data = {
            "name": name,
            "road_name": road_name,
            "latitude": latitude,
            "longitude": longitude,
            "tariff": tariff,
            "region": region
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/api/admin/tolls",
                headers=self.headers,
                json=toll_data
            ) as response:
                if response.status == 201:
                    data = await response.json()
                    print(f"Created toll:")
                    print(f"  ID: {data['id']}")
                    print(f"  Name: {data['name']}")
                    print(f"  Road: {data['road_name']}")
                    print(f"  Location: ({data['latitude']}, {data['longitude']})")
                    print(f"  Tariff: ${data['tariff']}")
                    return data
                else:
                    error = await response.json()
                    print(f"Error creating toll: {error}")
                    return None
    
    async def update_toll(self, toll_id: int, **updates):
        """
        Update a specific toll.
        
        Args:
            toll_id: ID of the toll to update
            **updates: Fields to update
        """
        async with aiohttp.ClientSession() as session:
            async with session.put(
                f"{self.base_url}/api/admin/tolls/{toll_id}",
                headers=self.headers,
                json=updates
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"Updated toll {toll_id}:")
                    print(f"  Name: {data['name']}")
                    print(f"  Road: {data['road_name']}")
                    print(f"  Tariff: ${data['tariff']}")
                    return data
                else:
                    error = await response.json()
                    print(f"Error updating toll: {error}")
                    return None
    
    async def delete_toll(self, toll_id: int):
        """
        Delete (deactivate) a toll.
        
        Args:
            toll_id: ID of the toll to delete
        """
        async with aiohttp.ClientSession() as session:
            async with session.delete(
                f"{self.base_url}/api/admin/tolls/{toll_id}",
                headers=self.headers
            ) as response:
                if response.status == 204:
                    print(f"Successfully deleted toll {toll_id}")
                    return True
                else:
                    error = await response.json()
                    print(f"Error deleting toll: {error}")
                    return False
    
    async def import_tolls_csv(self, csv_data: str, default_region: str = "NEA"):
        """
        Import tolls from CSV data.
        
        Args:
            csv_data: CSV data as string
            default_region: Default region for tolls without region
        """
        import_request = {
            "csv_data": csv_data,
            "default_region": default_region
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/api/admin/tolls/import",
                headers=self.headers,
                json=import_request
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"CSV Import completed:")
                    print(f"  {data['message']}")
                    print(f"  Imported: {data['imported_count']}")
                    print(f"  Skipped: {data['skipped_count']}")
                    print(f"  Errors: {data['error_count']}")
                    
                    if data['imported_tolls']:
                        print("  Imported tolls:")
                        for toll in data['imported_tolls']:
                            print(f"    Row {toll['row']}: {toll['name']} - ${toll['tariff']}")
                    
                    if data['skipped_tolls']:
                        print("  Skipped tolls:")
                        for toll in data['skipped_tolls']:
                            print(f"    Row {toll['row']}: {toll['name']} - {toll['reason']}")
                    
                    if data['errors']:
                        print("  Errors:")
                        for error in data['errors']:
                            print(f"    {error}")
                    
                    return data
                else:
                    error = await response.json()
                    print(f"Error importing tolls: {error}")
                    return None
    
    async def validate_toll_location(self, latitude: float, longitude: float):
        """
        Validate toll location.
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/api/admin/tolls/validate-location",
                headers=self.headers,
                params={"latitude": latitude, "longitude": longitude}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"Location validation for ({latitude}, {longitude}):")
                    print(f"  Valid: {data['valid']}")
                    
                    if data['valid']:
                        print(f"  In Argentina: {data['in_argentina']}")
                        print(f"  Nearby tolls: {data['nearby_tolls_count']}")
                        
                        if data.get('warnings'):
                            print("  Warnings:")
                            for warning in data['warnings']:
                                print(f"    - {warning}")
                        
                        print("  Suggestions:")
                        for suggestion in data['suggestions']:
                            print(f"    - {suggestion}")
                    else:
                        print(f"  Reason: {data['reason']}")
                        if data.get('suggestions'):
                            print("  Suggestions:")
                            for suggestion in data['suggestions']:
                                print(f"    - {suggestion}")
                    
                    return data
                else:
                    error = await response.json()
                    print(f"Error validating location: {error}")
                    return None


async def main():
    """
    Main example function demonstrating toll admin API usage.
    """
    print("=== Toll Admin API Example ===\n")
    
    # Initialize client (you would need a real admin JWT token)
    admin_token = "your-admin-jwt-token-here"
    client = TollAdminAPIExample(admin_token=admin_token)
    
    print("1. Getting all tolls...")
    await client.get_tolls()
    print()
    
    print("2. Getting tolls on RN12...")
    await client.get_tolls(road_name="RN12")
    print()
    
    print("3. Validating a location in Argentina...")
    await client.validate_toll_location(-27.3621, -55.8959)
    print()
    
    print("4. Validating an invalid location...")
    await client.validate_toll_location(95.0, -55.8959)
    print()
    
    # Example of creating a toll (uncomment to test)
    # print("5. Creating a new toll...")
    # await client.create_toll(
    #     name="Peaje Ejemplo",
    #     road_name="RN12",
    #     latitude=-27.1234,
    #     longitude=-55.5678,
    #     tariff=85.00,
    #     region="NEA"
    # )
    # print()
    
    # Example of updating a toll (uncomment to test)
    # print("6. Updating toll tariff...")
    # await client.update_toll(1, tariff=95.00, name="Peaje Actualizado")
    # print()
    
    # Example of CSV import (uncomment to test)
    # print("7. Importing tolls from CSV...")
    # csv_data = """name,road_name,latitude,longitude,tariff,region
    # Peaje Test 1,RN12,-27.1234,-55.5678,85.00,NEA
    # Peaje Test 2,RN14,-26.9876,-54.3210,90.00,NEA"""
    # await client.import_tolls_csv(csv_data)
    # print()
    
    print("=== Example completed ===")


def demo_without_server():
    """
    Demonstrate the API structure without making actual requests.
    """
    print("=== Toll Admin API Structure Demo ===\n")
    
    print("Available Toll Admin Endpoints:")
    print("  GET  /api/admin/tolls")
    print("       - Get toll information with filtering")
    print("       - Query params: road_name, region, active_only")
    print()
    
    print("  POST /api/admin/tolls")
    print("       - Create a new toll")
    print("       - Body: name, road_name, latitude, longitude, tariff, region")
    print()
    
    print("  PUT  /api/admin/tolls/{toll_id}")
    print("       - Update a specific toll")
    print("       - Body: name, road_name, latitude, longitude, tariff, region, is_active")
    print()
    
    print("  DELETE /api/admin/tolls/{toll_id}")
    print("       - Delete (deactivate) a toll")
    print()
    
    print("  POST /api/admin/tolls/import")
    print("       - Import tolls from CSV data")
    print("       - Body: csv_data, default_region")
    print()
    
    print("  GET  /api/admin/tolls/validate-location")
    print("       - Validate toll location coordinates")
    print("       - Query params: latitude, longitude")
    print()
    
    print("Example Request Bodies:")
    print()
    
    print("Create toll:")
    create_example = {
        "name": "Peaje Ejemplo",
        "road_name": "RN12",
        "latitude": -27.3621,
        "longitude": -55.8959,
        "tariff": 90.00,
        "region": "NEA"
    }
    print(json.dumps(create_example, indent=2))
    print()
    
    print("Update toll:")
    update_example = {
        "name": "Peaje Actualizado",
        "tariff": 95.00,
        "is_active": True
    }
    print(json.dumps(update_example, indent=2))
    print()
    
    print("CSV Import:")
    csv_example = {
        "csv_data": "name,road_name,latitude,longitude,tariff,region\\nPeaje Test,RN12,-27.1234,-55.5678,85.00,NEA",
        "default_region": "NEA"
    }
    print(json.dumps(csv_example, indent=2))
    print()
    
    print("Expected CSV Format:")
    print("name,road_name,latitude,longitude,tariff,region")
    print("Peaje Posadas,RN12,-27.3621,-55.8959,90.00,NEA")
    print("Peaje Iguazú,RN12,-25.5951,-54.5735,85.00,NEA")
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