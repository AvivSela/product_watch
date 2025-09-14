#!/usr/bin/env python3
"""
Centralized Database Initialization Script

This script initializes all database tables for the Products Watch microservices.
It imports all models from each service and creates the corresponding tables.

Usage:
    python init_database.py

Environment Variables:
    DATABASE_URL: PostgreSQL connection string (default: postgresql://postgres:password@localhost:5432/products_watch)
"""

import sys
from pathlib import Path

# Add src directory to Python path for imports
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from dotenv import load_dotenv
from sqlalchemy import inspect, text

from services.price_service.database import Base as PriceBase
from services.price_service.database import PriceSchema
from services.price_service.database import engine as price_engine
from services.product_service.database import Base as ProductBase
from services.product_service.database import ProductSchema
from services.product_service.database import engine as product_engine
from services.retail_file_service.database import Base as RetailFileBase
from services.retail_file_service.database import RetailFileSchema
from services.retail_file_service.database import engine as retail_file_engine

# Import all service models and engines
from services.store_service.database import Base as StoreBase
from services.store_service.database import StoreSchema
from services.store_service.database import engine as store_engine

# Load environment variables
load_dotenv()


def check_database_connection(engine, service_name):
    """Check if database connection is available."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print(f"✓ {service_name} database connection successful")
        return True
    except Exception as e:
        print(f"✗ {service_name} database connection failed: {e}")
        return False


def get_existing_tables(engine):
    """Get list of existing tables in the database."""
    inspector = inspect(engine)
    return inspector.get_table_names()


def create_tables_for_service(base, engine, service_name, model_class):
    """Create tables for a specific service."""
    try:
        # Get existing tables before creation
        existing_tables_before = get_existing_tables(engine)

        # Create tables
        base.metadata.create_all(bind=engine)

        # Get tables after creation
        existing_tables_after = get_existing_tables(engine)

        # Find newly created tables
        new_tables = set(existing_tables_after) - set(existing_tables_before)

        if new_tables:
            print(f"✓ {service_name}: Created tables: {', '.join(new_tables)}")
        else:
            print(f"✓ {service_name}: All tables already exist")

        return True
    except Exception as e:
        print(f"✗ {service_name}: Failed to create tables: {e}")
        return False


def main():
    """Main initialization function."""
    print("🚀 Starting Products Watch Database Initialization")
    print("=" * 60)

    # Check database connections first
    print("\n📡 Checking database connections...")
    connections_ok = True

    connections_ok &= check_database_connection(store_engine, "Store Service")
    connections_ok &= check_database_connection(product_engine, "Product Service")
    connections_ok &= check_database_connection(price_engine, "Price Service")
    connections_ok &= check_database_connection(
        retail_file_engine, "Retail File Service"
    )

    if not connections_ok:
        print("\n❌ Database connection check failed. Please ensure:")
        print("   - PostgreSQL is running")
        print("   - Database 'products_watch' exists")
        print("   - Connection credentials are correct")
        print(
            "   - DATABASE_URL environment variable is set (if different from default)"
        )
        sys.exit(1)

    print("\n📋 Creating database tables...")

    # Create tables for each service
    success_count = 0
    total_services = 4

    success_count += create_tables_for_service(
        StoreBase, store_engine, "Store Service", StoreSchema
    )
    success_count += create_tables_for_service(
        ProductBase, product_engine, "Product Service", ProductSchema
    )
    success_count += create_tables_for_service(
        PriceBase, price_engine, "Price Service", PriceSchema
    )
    success_count += create_tables_for_service(
        RetailFileBase, retail_file_engine, "Retail File Service", RetailFileSchema
    )

    print("\n" + "=" * 60)

    if success_count == total_services:
        print("🎉 Database initialization completed successfully!")
        print(f"✓ All {total_services} services initialized")
        print("\n📊 Summary of created tables:")

        # Show all tables for each service
        services = [
            ("Store Service", store_engine, StoreBase),
            ("Product Service", product_engine, ProductBase),
            ("Price Service", price_engine, PriceBase),
            ("Retail File Service", retail_file_engine, RetailFileBase),
        ]

        for service_name, engine, base in services:
            tables = get_existing_tables(engine)
            service_tables = [t for t in tables if t in base.metadata.tables]
            print(f"   {service_name}: {', '.join(service_tables)}")

    else:
        print(
            f"⚠️  Database initialization completed with {total_services - success_count} failures"
        )
        print("Please check the error messages above and retry.")
        sys.exit(1)


if __name__ == "__main__":
    main()
