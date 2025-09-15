"""
Price Service.

This service manages pricing data and provides CRUD operations
for prices in the Products Watch System.
"""

from .database import PriceSchema, get_db
from .main import app
from .models import PaginatedResponse, Price, PriceCreate, PriceUpdate

__all__ = [
    "app",
    "PriceSchema",
    "get_db",
    "Price",
    "PriceCreate",
    "PriceUpdate",
    "PaginatedResponse",
]
