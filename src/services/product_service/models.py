from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from database import ProductSchema
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


class Product(BaseEntity):
    """Product entity with detailed item information"""

    chain_id: str = Field(..., description="Chain identifier")
    store_id: int = Field(..., gt=0, description="Store identifier")
    item_code: str = Field(..., description="Unique item code")
    item_name: str = Field(..., description="Product name")
    manufacturer_item_description: str = Field(
        ..., description="Manufacturer's product description"
    )
    manufacturer_name: str = Field(..., description="Manufacturer name")
    manufacture_country: str = Field(..., description="Country of manufacture")
    unit_qty: str = Field(..., description="Unit quantity description")
    quantity: Decimal = Field(..., gt=0, description="Product quantity")
    qty_in_package: Decimal = Field(..., gt=0, description="Quantity in package")

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_db_model(cls, db_product: ProductSchema) -> "Product":
        """Convert database Product model to Product Pydantic model"""
        return cls(
            id=db_product.id,
            chain_id=db_product.chain_id,
            store_id=db_product.store_id,
            item_code=db_product.item_code,
            item_name=db_product.item_name,
            manufacturer_item_description=db_product.manufacturer_item_description,
            manufacturer_name=db_product.manufacturer_name,
            manufacture_country=db_product.manufacture_country,
            unit_qty=db_product.unit_qty,
            quantity=db_product.quantity,
            qty_in_package=db_product.qty_in_package,
            created_at=db_product.created_at,
            updated_at=db_product.updated_at,
        )

    def to_db_model(self) -> ProductSchema:
        """Convert Product Pydantic model to database Product model"""
        return ProductSchema(
            id=self.id,
            chain_id=self.chain_id,
            store_id=self.store_id,
            item_code=self.item_code,
            item_name=self.item_name,
            manufacturer_item_description=self.manufacturer_item_description,
            manufacturer_name=self.manufacturer_name,
            manufacture_country=self.manufacture_country,
            unit_qty=self.unit_qty,
            quantity=self.quantity,
            qty_in_package=self.qty_in_package,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )


class ProductCreate(BaseModel):
    """Model for creating a new product - excludes auto-generated fields"""

    chain_id: str = Field(..., description="Chain identifier")
    store_id: int = Field(..., gt=0, description="Store identifier")
    item_code: str = Field(..., description="Unique item code")
    item_name: str = Field(..., description="Product name")
    manufacturer_item_description: str = Field(
        ..., description="Manufacturer's product description"
    )
    manufacturer_name: str = Field(..., description="Manufacturer name")
    manufacture_country: str = Field(..., description="Country of manufacture")
    unit_qty: str = Field(..., description="Unit quantity description")
    quantity: Decimal = Field(..., gt=0, description="Product quantity")
    qty_in_package: Decimal = Field(..., gt=0, description="Quantity in package")

    model_config = ConfigDict(
        str_strip_whitespace=True, validate_assignment=True, use_enum_values=True
    )

    def to_db_model(self) -> ProductSchema:
        """Convert ProductCreate Pydantic model to database Product model"""
        return ProductSchema(
            chain_id=self.chain_id,
            store_id=self.store_id,
            item_code=self.item_code,
            item_name=self.item_name,
            manufacturer_item_description=self.manufacturer_item_description,
            manufacturer_name=self.manufacturer_name,
            manufacture_country=self.manufacture_country,
            unit_qty=self.unit_qty,
            quantity=self.quantity,
            qty_in_package=self.qty_in_package,
        )


class ProductUpdate(BaseModel):
    """Model for updating product information - all fields optional"""

    chain_id: str = Field(None, description="Chain identifier")
    store_id: int = Field(None, gt=0, description="Store identifier")
    item_code: str = Field(None, description="Unique item code")
    item_name: str = Field(None, description="Product name")
    manufacturer_item_description: str = Field(
        None, description="Manufacturer's product description"
    )
    manufacturer_name: str = Field(None, description="Manufacturer name")
    manufacture_country: str = Field(None, description="Country of manufacture")
    unit_qty: str = Field(None, description="Unit quantity description")
    quantity: Decimal = Field(None, gt=0, description="Product quantity")
    qty_in_package: Decimal = Field(None, gt=0, description="Quantity in package")

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
    items: List[Product]
    total: int
    page: int
    size: int
    pages: int
