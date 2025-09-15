"""
Product Service.

This service manages product information and provides CRUD operations
for products in the Products Watch System.
"""

from .database import ProductSchema, get_db
from .models import PaginatedResponse, Product, ProductCreate, ProductUpdate

__all__ = [
    "ProductSchema",
    "get_db",
    "Product",
    "ProductCreate",
    "ProductUpdate",
    "PaginatedResponse",
]
