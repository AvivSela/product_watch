"""
Retail File Service.

This service manages retail file metadata and provides CRUD operations
for retail files in the Products Watch System.
"""

from .database import RetailFileSchema, get_db
from .main import app
from .models import (
    PaginatedResponse,
    RetailFile,
    RetailFileCreate,
    RetailFileMessage,
    RetailFileUpdate,
)

__all__ = [
    "app",
    "RetailFileSchema",
    "get_db",
    "RetailFile",
    "RetailFileCreate",
    "RetailFileUpdate",
    "RetailFileMessage",
    "PaginatedResponse",
]
