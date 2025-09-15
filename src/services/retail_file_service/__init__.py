"""
Retail File Service.

This service manages retail file metadata and provides CRUD operations
for retail files in the Products Watch System.
"""

from .database import RetailFileSchema, get_db
from .models import (
    PaginatedResponse,
    RetailFile,
    RetailFileCreate,
    RetailFileMessage,
    RetailFileUpdate,
)

__all__ = [
    "RetailFileSchema",
    "get_db",
    "RetailFile",
    "RetailFileCreate",
    "RetailFileUpdate",
    "RetailFileMessage",
    "PaginatedResponse",
]
