"""
Product Service.

This service manages product information and provides CRUD operations
for products in the Products Watch System.
"""

import os
import sys

# Add service directory to Python path for testing
service_dir = os.path.dirname(__file__)
if service_dir not in sys.path:
    sys.path.insert(0, service_dir)

try:
    # Try relative imports first (production)
    from .database import ProductSchema, get_db
    from .models import PaginatedResponse, Product, ProductCreate, ProductUpdate
except ImportError:
    # Fallback to absolute imports (testing)
    try:
        from database import ProductSchema, get_db
        from models import PaginatedResponse, Product, ProductCreate, ProductUpdate
    except ImportError:
        # Final fallback - set to None for optional imports
        ProductSchema = None
        get_db = None
        PaginatedResponse = None
        Product = None
        ProductCreate = None
        ProductUpdate = None

__all__ = [
    "ProductSchema",
    "get_db",
    "Product",
    "ProductCreate",
    "ProductUpdate",
    "PaginatedResponse",
]
