# Standard library imports
import os
from datetime import datetime, timezone
from uuid import UUID

# Third-party imports
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy.orm import Session

# Local application imports with conditional import strategy
if os.getenv("PYTEST_CURRENT_TEST") or os.getenv("TESTING"):
    # Test environment - use absolute imports
    import sys

    sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
    from database import ProductSchema, get_db
    from models import PaginatedResponse, ProductCreate, ProductUpdate
    from models import Product as ProductModel
else:
    # Production environment - use relative imports
    from .database import ProductSchema, get_db
    from .models import PaginatedResponse, ProductCreate, ProductUpdate
    from .models import Product as ProductModel

# Initialize FastAPI app
app = FastAPI(
    title="Product Service API",
    description="A simple FastAPI Product Service for managing products",
    version="1.0.0",
)


@app.get("/health")
def health_check():
    """Health check endpoint for monitoring service status"""
    return {
        "status": "healthy",
        "service": "product-service",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/health/db")
def health_check_db(db: Session = Depends(get_db)):
    """Health check endpoint that verifies database connectivity"""
    try:
        # Simple database query to verify connection
        db.query(ProductSchema).limit(1).all()
        return {
            "status": "healthy",
            "service": "product-service",
            "database": "connected",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "service": "product-service",
                "database": "disconnected",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )


@app.get("/products", response_model=PaginatedResponse)
def get_products(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Products per page"),
    db: Session = Depends(get_db),
):
    """Get all products with pagination from PostgreSQL database"""
    # Calculate offset
    offset = (page - 1) * size

    # Get total count
    total = db.query(ProductSchema).count()

    # Get paginated products
    products = db.query(ProductSchema).offset(offset).limit(size).all()

    # Calculate total pages
    pages = (total + size - 1) // size

    # Convert to Product models
    product_models = [ProductModel.from_db_model(product) for product in products]

    return PaginatedResponse(
        items=product_models, total=total, page=page, size=size, pages=pages
    )


@app.get("/products/{product_id}", response_model=ProductModel)
def get_product(product_id: UUID, db: Session = Depends(get_db)):
    """Get a specific product by ID"""
    product = db.query(ProductSchema).filter(ProductSchema.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return ProductModel.from_db_model(product)


@app.post("/products", response_model=ProductModel, status_code=201)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    """Create a new product"""
    # Check if product with same chain_id, store_id, and item_code already exists
    existing_product = (
        db.query(ProductSchema)
        .filter(
            ProductSchema.chain_id == product.chain_id,
            ProductSchema.store_id == product.store_id,
            ProductSchema.item_code == product.item_code,
        )
        .first()
    )
    if existing_product:
        raise HTTPException(
            status_code=400,
            detail="Product with this chain ID, store ID, and item code already exists",
        )

    # Create new product
    db_product = product.to_db_model()

    db.add(db_product)
    db.commit()
    db.refresh(db_product)

    return ProductModel.from_db_model(db_product)


@app.put("/products/{product_id}", response_model=ProductModel)
def update_product(
    product_id: UUID, product_update: ProductUpdate, db: Session = Depends(get_db)
):
    """Update an existing product"""
    # Find the product
    product = db.query(ProductSchema).filter(ProductSchema.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Check if chain_id, store_id, and item_code combination is being updated and if it conflicts with existing products
    if (
        (product_update.chain_id and product_update.chain_id != product.chain_id)
        or (product_update.store_id and product_update.store_id != product.store_id)
        or (product_update.item_code and product_update.item_code != product.item_code)
    ):
        chain_id_to_check = (
            product_update.chain_id if product_update.chain_id else product.chain_id
        )
        store_id_to_check = (
            product_update.store_id if product_update.store_id else product.store_id
        )
        item_code_to_check = (
            product_update.item_code if product_update.item_code else product.item_code
        )

        existing_product = (
            db.query(ProductSchema)
            .filter(
                ProductSchema.chain_id == chain_id_to_check,
                ProductSchema.store_id == store_id_to_check,
                ProductSchema.item_code == item_code_to_check,
                ProductSchema.id != product_id,
            )
            .first()
        )
        if existing_product:
            raise HTTPException(
                status_code=400,
                detail="Product with this chain ID, store ID, and item code combination already exists",
            )

    # Update fields
    update_data = product_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)

    product.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(product)

    return ProductModel.from_db_model(product)


@app.delete("/products/{product_id}", status_code=204)
def delete_product(product_id: UUID, db: Session = Depends(get_db)):
    """Delete a product"""
    product = db.query(ProductSchema).filter(ProductSchema.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(product)
    db.commit()

    return None


if __name__ == "__main__":
    import uvicorn

    # Run the FastAPI application using uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)  # noqa: S104
