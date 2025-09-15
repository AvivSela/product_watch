"""
Product Service.

This service manages product information and provides CRUD operations
for products in the Products Watch System.
"""

from .database import ProductSchema, get_db
from .main import app
from .models import PaginatedResponse, Product, ProductCreate, ProductUpdate

__all__ = [
    "app",
    "ProductSchema",
    "get_db",
    "Product",
    "ProductCreate",
    "ProductUpdate",
    "PaginatedResponse",
]
