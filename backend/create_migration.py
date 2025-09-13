#!/usr/bin/env python3
"""
Script to create initial database migration.
"""
import os
import sys
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from alembic.config import Config
from alembic import command

def create_initial_migration():
    """Create initial database migration."""
    
    # Set up Alembic configuration
    alembic_cfg = Config("alembic.ini")
    
    # Create initial migration
    try:
        command.revision(
            alembic_cfg, 
            autogenerate=True, 
            message="Initial migration - companies, users, vehicles, fuel_prices, tolls, calculated_routes"
        )
        print("✅ Initial migration created successfully")
        
    except Exception as e:
        print(f"❌ Error creating migration: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = create_initial_migration()
    sys.exit(0 if success else 1)