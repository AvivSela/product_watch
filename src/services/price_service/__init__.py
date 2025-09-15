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
    from .database import PriceSchema, get_db  # type: ignore
    from .models import (  # type: ignore
        PaginatedResponse,
        Price,
        PriceCreate,
        PriceUpdate,
    )
except ImportError:
    # Fallback to absolute imports (testing)
    try:
        from database import PriceSchema, get_db  # type: ignore
        from models import (  # type: ignore
            PaginatedResponse,
            Price,
            PriceCreate,
            PriceUpdate,
        )
    except ImportError:
        # Final fallback - set to None for optional imports
        PriceSchema = None  # type: ignore
        get_db = None  # type: ignore
        PaginatedResponse = None  # type: ignore
        Price = None  # type: ignore
        PriceCreate = None  # type: ignore
        PriceUpdate = None  # type: ignore

__all__ = [
    "PriceSchema",
    "get_db",
    "Price",
    "PriceCreate",
    "PriceUpdate",
    "PaginatedResponse",
]
