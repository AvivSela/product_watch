"""
Price Service.

This service manages pricing data and provides CRUD operations
for prices in the Products Watch System.
"""

import os
import sys

# Add service directory to Python path for testing
service_dir = os.path.dirname(__file__)
if service_dir not in sys.path:
    sys.path.insert(0, service_dir)

try:
    # Try relative imports first (production)
    from .database import PriceSchema, get_db
    from .models import PaginatedResponse, Price, PriceCreate, PriceUpdate
except ImportError:
    # Fallback to absolute imports (testing)
    try:
        from database import PriceSchema, get_db
        from models import PaginatedResponse, Price, PriceCreate, PriceUpdate
    except ImportError:
        # Final fallback - set to None for optional imports
        PriceSchema = None
        get_db = None
        PaginatedResponse = None
        Price = None
        PriceCreate = None
        PriceUpdate = None

__all__ = [
    "PriceSchema",
    "get_db",
    "Price",
    "PriceCreate",
    "PriceUpdate",
    "PaginatedResponse",
]
