# Standard library imports
from datetime import datetime
from typing import List, Optional
from uuid import UUID

# Local application imports
from database import RetailFileSchema

# Third-party imports
from pydantic import BaseModel, ConfigDict, Field


# Pydantic models for request/response
class BaseEntity(BaseModel):
    """Base model with common fields for all entities"""

    model_config = ConfigDict(
        str_strip_whitespace=True, validate_assignment=True, use_enum_values=True
    )

    id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class RetailFile(BaseEntity):
    """Retail file entity with file information"""

    chain_id: str = Field(..., description="Chain ID")
    store_id: Optional[int] = Field(None, description="Store ID")
    file_name: str = Field(..., description="File name")
    file_path: str = Field(..., description="File path")
    file_size: Optional[int] = Field(None, description="File size in bytes")
    upload_date: datetime = Field(..., description="File upload timestamp")
    is_processed: bool = Field(..., description="Whether the file has been processed")

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_db_model(cls, db_retail_file: RetailFileSchema) -> "RetailFile":
        """Convert database RetailFile model to RetailFile Pydantic model"""
        return cls(
            id=db_retail_file.id,
            chain_id=db_retail_file.chain_id,
            store_id=db_retail_file.store_id,
            file_name=db_retail_file.file_name,
            file_path=db_retail_file.file_path,
            file_size=db_retail_file.file_size,
            upload_date=db_retail_file.upload_date,
            is_processed=db_retail_file.is_processed,
            created_at=db_retail_file.created_at,
            updated_at=db_retail_file.updated_at,
        )

    def to_db_model(self) -> RetailFileSchema:
        """Convert RetailFile Pydantic model to database RetailFile model"""
        return RetailFileSchema(
            id=self.id,
            chain_id=self.chain_id,
            store_id=self.store_id,
            file_name=self.file_name,
            file_path=self.file_path,
            file_size=self.file_size,
            upload_date=self.upload_date,
            is_processed=self.is_processed,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )


class RetailFileCreate(BaseModel):
    """Model for creating a new retail file - excludes auto-generated fields"""

    chain_id: str = Field(..., description="Chain ID")
    store_id: Optional[int] = Field(None, description="Store ID")
    file_name: str = Field(..., description="File name")
    file_path: str = Field(..., description="File path")
    file_size: Optional[int] = Field(None, description="File size in bytes")
    upload_date: datetime = Field(..., description="File upload timestamp")
    is_processed: bool = Field(..., description="Whether the file has been processed")

    model_config = ConfigDict(
        str_strip_whitespace=True, validate_assignment=True, use_enum_values=True
    )

    def to_db_model(self) -> RetailFileSchema:
        """Convert RetailFileCreate Pydantic model to database RetailFile model"""
        return RetailFileSchema(
            chain_id=self.chain_id,
            store_id=self.store_id,
            file_name=self.file_name,
            file_path=self.file_path,
            file_size=self.file_size,
            upload_date=self.upload_date,
            is_processed=self.is_processed,
        )


class RetailFileUpdate(BaseModel):
    """Model for updating retail file information - all fields optional"""

    chain_id: str = Field(None, description="Chain ID")
    store_id: Optional[int] = Field(None, description="Store ID")
    file_name: str = Field(None, description="File name")
    file_path: str = Field(None, description="File path")
    file_size: Optional[int] = Field(None, description="File size in bytes")
    upload_date: datetime = Field(None, description="File upload timestamp")
    is_processed: bool = Field(None, description="Whether the file has been processed")

    model_config = ConfigDict(
        str_strip_whitespace=True, validate_assignment=True, use_enum_values=True
    )


# Pagination models
class PaginationParams(BaseModel):
    page: int = 1
    size: int = 10

    def __init__(self, page: int = 1, size: int = 10, **kwargs):
        super().__init__(page=max(1, page), size=max(1, min(100, size)), **kwargs)


class PaginatedResponse(BaseModel):
    items: List[RetailFile]
    total: int
    page: int
    size: int
    pages: int


class RetailFileMessage(BaseModel):
    event_type: str
    data: RetailFile
