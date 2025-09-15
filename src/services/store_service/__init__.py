"""
Store Service.

This service manages store information and provides CRUD operations
for stores in the Products Watch System.
"""

from .database import StoreSchema, get_db
from .main import app
from .models import PaginatedResponse, Store, StoreCreate, StoreUpdate

__all__ = [
    "app",
    "StoreSchema",
    "get_db",
    "Store",
    "StoreCreate",
    "StoreUpdate",
    "PaginatedResponse",
]
