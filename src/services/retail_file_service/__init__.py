"""
Retail File Service.

This service manages retail file metadata and provides CRUD operations
for retail files in the Products Watch System.
"""

import os
import sys

# Add service directory to Python path for testing
service_dir = os.path.dirname(__file__)
if service_dir not in sys.path:
    sys.path.insert(0, service_dir)

try:
    # Try relative imports first (production)
    from .database import RetailFileSchema, get_db  # type: ignore
    from .models import (  # type: ignore
        PaginatedResponse,
        RetailFile,
        RetailFileCreate,
        RetailFileMessage,
        RetailFileUpdate,
    )
except ImportError:
    # Fallback to absolute imports (testing)
    try:
        from database import RetailFileSchema, get_db  # type: ignore
        from models import (  # type: ignore
            PaginatedResponse,
            RetailFile,
            RetailFileCreate,
            RetailFileMessage,
            RetailFileUpdate,
        )
    except ImportError:
        # Final fallback - set to None for optional imports
        RetailFileSchema = None  # type: ignore
        get_db = None  # type: ignore
        PaginatedResponse = None  # type: ignore
        RetailFile = None  # type: ignore
        RetailFileCreate = None  # type: ignore
        RetailFileMessage = None  # type: ignore
        RetailFileUpdate = None  # type: ignore

__all__ = [
    "RetailFileSchema",
    "get_db",
    "RetailFile",
    "RetailFileCreate",
    "RetailFileUpdate",
    "RetailFileMessage",
    "PaginatedResponse",
]
