"""
Store Service.

This service manages store information and provides CRUD operations
for stores in the Products Watch System.
"""

import os
import sys

# Add service directory to Python path for testing
service_dir = os.path.dirname(__file__)
if service_dir not in sys.path:
    sys.path.insert(0, service_dir)

try:
    # Try relative imports first (production)
    from .database import StoreSchema, get_db  # type: ignore
    from .models import (  # type: ignore
        PaginatedResponse,
        Store,
        StoreCreate,
        StoreUpdate,
    )
except ImportError:
    # Fallback to absolute imports (testing)
    try:
        from database import StoreSchema, get_db  # type: ignore
        from models import (  # type: ignore
            PaginatedResponse,
            Store,
            StoreCreate,
            StoreUpdate,
        )
    except ImportError:
        # Final fallback - set to None for optional imports
        StoreSchema = None  # type: ignore
        get_db = None  # type: ignore
        PaginatedResponse = None  # type: ignore
        Store = None  # type: ignore
        StoreCreate = None  # type: ignore
        StoreUpdate = None  # type: ignore

__all__ = [
    "StoreSchema",
    "get_db",
    "Store",
    "StoreCreate",
    "StoreUpdate",
    "PaginatedResponse",
]
