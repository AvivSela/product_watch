from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from database import PriceSchema
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


class Price(BaseEntity):
    """Price entity with detailed price information"""

    chain_id: Optional[str] = Field(None, description="Chain identifier")
    store_id: Optional[int] = Field(None, gt=0, description="Store identifier")
    item_code: Optional[str] = Field(None, description="Unique item code")
    price_amount: Optional[Decimal] = Field(None, ge=0, description="Price amount")
    currency_code: Optional[str] = Field(
        None, min_length=3, max_length=3, description="Currency code (ISO 4217)"
    )
    price_update_date: Optional[datetime] = Field(
        None, description="Date when price was updated"
    )

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_db_model(cls, db_price: PriceSchema) -> "Price":
        """Convert database Price model to Price Pydantic model"""
        return cls(
            id=db_price.id,
            chain_id=db_price.chain_id,
            store_id=db_price.store_id,
            item_code=db_price.item_code,
            price_amount=db_price.price_amount,
            currency_code=db_price.currency_code,
            price_update_date=db_price.price_update_date,
            created_at=db_price.created_at,
            updated_at=db_price.updated_at,
        )

    def to_db_model(self) -> PriceSchema:
        """Convert Price Pydantic model to database Price model"""
        return PriceSchema(
            id=self.id,
            chain_id=self.chain_id,
            store_id=self.store_id,
            item_code=self.item_code,
            price_amount=self.price_amount,
            currency_code=self.currency_code,
            price_update_date=self.price_update_date,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )


class PriceCreate(BaseModel):
    """Model for creating a new price - excludes auto-generated fields"""

    chain_id: Optional[str] = Field(None, description="Chain identifier")
    store_id: Optional[int] = Field(None, gt=0, description="Store identifier")
    item_code: Optional[str] = Field(None, description="Unique item code")
    price_amount: Optional[Decimal] = Field(None, ge=0, description="Price amount")
    currency_code: Optional[str] = Field(
        None, min_length=3, max_length=3, description="Currency code (ISO 4217)"
    )
    price_update_date: Optional[datetime] = Field(
        None, description="Date when price was updated"
    )

    model_config = ConfigDict(
        str_strip_whitespace=True, validate_assignment=True, use_enum_values=True
    )

    def to_db_model(self) -> PriceSchema:
        """Convert PriceCreate Pydantic model to database Price model"""
        return PriceSchema(
            chain_id=self.chain_id,
            store_id=self.store_id,
            item_code=self.item_code,
            price_amount=self.price_amount,
            currency_code=self.currency_code,
            price_update_date=self.price_update_date,
        )


class PriceUpdate(BaseModel):
    """Model for updating price information - all fields optional"""

    chain_id: Optional[str] = Field(None, description="Chain identifier")
    store_id: Optional[int] = Field(None, gt=0, description="Store identifier")
    item_code: Optional[str] = Field(None, description="Unique item code")
    price_amount: Optional[Decimal] = Field(None, ge=0, description="Price amount")
    currency_code: Optional[str] = Field(
        None, min_length=3, max_length=3, description="Currency code (ISO 4217)"
    )
    price_update_date: Optional[datetime] = Field(
        None, description="Date when price was updated"
    )

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
    items: List[Price]
    total: int
    page: int
    size: int
    pages: int
