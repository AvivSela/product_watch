# Standard library imports
from datetime import datetime
from typing import List, Optional
from uuid import UUID

# Local application imports
from database import StoreSchema

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


class Store(BaseEntity):
    store_code: int = Field(..., gt=0, description="Unique store code")
    store_name: str = Field(..., description="Store name")
    address: str = Field(..., description="Store address")
    city: str = Field(..., description="City where store is located")
    zip_code: str = Field(..., description="Postal/ZIP code")
    sub_chain_id: str = Field(..., description="Sub-chain identifier")
    chain_id: str = Field(..., description="Parent chain identifier")

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_db_model(cls, db_store: StoreSchema) -> "Store":
        """Convert database Store model to Store Pydantic model"""
        return cls(
            id=db_store.id,
            store_code=db_store.store_code,
            store_name=db_store.store_name,
            address=db_store.address,
            city=db_store.city,
            zip_code=db_store.zip_code,
            sub_chain_id=db_store.sub_chain_id,
            chain_id=db_store.chain_id,
            created_at=db_store.created_at,
            updated_at=db_store.updated_at,
        )

    def to_db_model(self) -> StoreSchema:
        """Convert Store Pydantic model to database Store model"""
        return StoreSchema(
            id=self.id,
            store_code=self.store_code,
            store_name=self.store_name,
            address=self.address,
            city=self.city,
            zip_code=self.zip_code,
            sub_chain_id=self.sub_chain_id,
            chain_id=self.chain_id,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )


class StoreCreate(BaseModel):
    """Model for creating a new store - excludes auto-generated fields"""

    store_code: int = Field(..., gt=0, description="Unique store code")
    store_name: str = Field(..., description="Store name")
    address: str = Field(..., description="Store address")
    city: str = Field(..., description="City where store is located")
    zip_code: str = Field(..., description="Postal/ZIP code")
    sub_chain_id: str = Field(..., description="Sub-chain identifier")
    chain_id: str = Field(..., description="Parent chain identifier")

    model_config = ConfigDict(
        str_strip_whitespace=True, validate_assignment=True, use_enum_values=True
    )

    def to_db_model(self) -> StoreSchema:
        """Convert StoreCreate Pydantic model to database Store model"""
        return StoreSchema(
            store_code=self.store_code,
            store_name=self.store_name,
            address=self.address,
            city=self.city,
            zip_code=self.zip_code,
            sub_chain_id=self.sub_chain_id,
            chain_id=self.chain_id,
        )


class StoreUpdate(BaseModel):
    """Model for updating store information - all fields optional"""

    store_code: int = Field(None, gt=0, description="Unique store code")
    store_name: str = Field(None, description="Store name")
    address: str = Field(None, description="Store address")
    city: str = Field(None, description="City where store is located")
    zip_code: str = Field(None, description="Postal/ZIP code")
    sub_chain_id: str = Field(None, description="Sub-chain identifier")
    chain_id: str = Field(None, description="Parent chain identifier")

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
    items: List[Store]
    total: int
    page: int
    size: int
    pages: int
