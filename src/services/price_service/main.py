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
    from database import PriceSchema, get_db
    from models import PaginatedResponse, PriceCreate, PriceUpdate
    from models import Price as PriceModel
else:
    # Production environment - use relative imports
    from .database import PriceSchema, get_db
    from .models import PaginatedResponse, PriceCreate, PriceUpdate
    from .models import Price as PriceModel

# Initialize FastAPI app
app = FastAPI(
    title="Price Service API",
    description="A simple FastAPI Price Service for managing prices",
    version="1.0.0",
)


@app.get("/health")
def health_check():
    """Health check endpoint for monitoring service status"""
    return {
        "status": "healthy",
        "service": "price-service",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/health/db")
def health_check_db(db: Session = Depends(get_db)):
    """Health check endpoint that verifies database connectivity"""
    try:
        # Simple database query to verify connection
        db.query(PriceSchema).limit(1).all()
        return {
            "status": "healthy",
            "service": "price-service",
            "database": "connected",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "service": "price-service",
                "database": "disconnected",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )


@app.get("/prices", response_model=PaginatedResponse)
def get_prices(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Prices per page"),
    db: Session = Depends(get_db),
):
    """Get all prices with pagination from PostgreSQL database"""
    # Calculate offset
    offset = (page - 1) * size

    # Get total count
    total = db.query(PriceSchema).count()

    # Get paginated prices
    prices = db.query(PriceSchema).offset(offset).limit(size).all()

    # Calculate total pages
    pages = (total + size - 1) // size

    # Convert to Price models
    price_models = [PriceModel.from_db_model(price) for price in prices]

    return PaginatedResponse(
        items=price_models, total=total, page=page, size=size, pages=pages
    )


@app.get("/prices/{price_id}", response_model=PriceModel)
def get_price(price_id: UUID, db: Session = Depends(get_db)):
    """Get a specific price by ID"""
    price = db.query(PriceSchema).filter(PriceSchema.id == price_id).first()
    if not price:
        raise HTTPException(status_code=404, detail="Price not found")

    return PriceModel.from_db_model(price)


@app.post("/prices", response_model=PriceModel, status_code=201)
def create_price(price: PriceCreate, db: Session = Depends(get_db)):
    """Create a new price"""
    # Create new price
    db_price = price.to_db_model()

    db.add(db_price)
    db.commit()
    db.refresh(db_price)

    return PriceModel.from_db_model(db_price)


@app.put("/prices/{price_id}", response_model=PriceModel)
def update_price(
    price_id: UUID, price_update: PriceUpdate, db: Session = Depends(get_db)
):
    """Update an existing price"""
    # Find the price
    price = db.query(PriceSchema).filter(PriceSchema.id == price_id).first()
    if not price:
        raise HTTPException(status_code=404, detail="Price not found")

    # Update fields
    update_data = price_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(price, field, value)

    price.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(price)

    return PriceModel.from_db_model(price)


@app.delete("/prices/{price_id}", status_code=204)
def delete_price(price_id: UUID, db: Session = Depends(get_db)):
    """Delete a price"""
    price = db.query(PriceSchema).filter(PriceSchema.id == price_id).first()
    if not price:
        raise HTTPException(status_code=404, detail="Price not found")

    db.delete(price)
    db.commit()

    return None


if __name__ == "__main__":
    import uvicorn

    # Run the FastAPI application using uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)  # noqa: S104
