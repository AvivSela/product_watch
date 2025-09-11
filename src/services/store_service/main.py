from datetime import datetime, timezone
from uuid import UUID

from database import StoreSchema, get_db
from fastapi import Depends, FastAPI, HTTPException, Query
from models import PaginatedResponse, StoreCreate, StoreUpdate
from models import Store as StoreModel
from sqlalchemy.orm import Session

# Initialize FastAPI app
app = FastAPI(
    title="Store Service API",
    description="A simple FastAPI Store Service for managing stores",
    version="1.0.0",
)


@app.get("/health")
def health_check():
    """Health check endpoint for monitoring service status"""
    return {
        "status": "healthy",
        "service": "store-service",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/health/db")
def health_check_db(db: Session = Depends(get_db)):
    """Health check endpoint that verifies database connectivity"""
    try:
        # Simple database query to verify connection
        db.query(StoreSchema).limit(1).all()
        return {
            "status": "healthy",
            "service": "store-service",
            "database": "connected",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "service": "store-service",
                "database": "disconnected",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )


@app.get("/stores", response_model=PaginatedResponse)
def get_stores(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Stores per page"),
    db: Session = Depends(get_db),
):
    """Get all stores with pagination from PostgreSQL database"""
    # Calculate offset
    offset = (page - 1) * size

    # Get total count
    total = db.query(StoreSchema).count()

    # Get paginated stores
    stores = db.query(StoreSchema).offset(offset).limit(size).all()

    # Calculate total pages
    pages = (total + size - 1) // size

    # Convert to Store models
    store_models = [StoreModel.from_db_model(store) for store in stores]

    return PaginatedResponse(
        items=store_models, total=total, page=page, size=size, pages=pages
    )


@app.get("/stores/{store_id}", response_model=StoreModel)
def get_store(store_id: UUID, db: Session = Depends(get_db)):
    """Get a specific store by ID"""
    store = db.query(StoreSchema).filter(StoreSchema.id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")

    return StoreModel.from_db_model(store)


@app.post("/stores", response_model=StoreModel, status_code=201)
def create_store(store: StoreCreate, db: Session = Depends(get_db)):
    """Create a new store"""
    # Check if store with same store_code already exists
    existing_store = (
        db.query(StoreSchema).filter(StoreSchema.store_code == store.store_code).first()
    )
    if existing_store:
        raise HTTPException(
            status_code=400, detail="Store with this store code already exists"
        )

    # Create new store
    db_store = store.to_db_model()

    db.add(db_store)
    db.commit()
    db.refresh(db_store)

    return StoreModel.from_db_model(db_store)


@app.put("/stores/{store_id}", response_model=StoreModel)
def update_store(
    store_id: UUID, store_update: StoreUpdate, db: Session = Depends(get_db)
):
    """Update an existing store"""
    # Find the store
    store = db.query(StoreSchema).filter(StoreSchema.id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")

    # Check if store_code is being updated and if it conflicts with existing stores
    if store_update.store_code and store_update.store_code != store.store_code:
        existing_store = (
            db.query(StoreSchema)
            .filter(
                StoreSchema.store_code == store_update.store_code,
                StoreSchema.id != store_id,
            )
            .first()
        )
        if existing_store:
            raise HTTPException(
                status_code=400, detail="Store with this store code already exists"
            )

    # Update fields
    update_data = store_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(store, field, value)

    store.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(store)

    return StoreModel.from_db_model(store)


@app.delete("/stores/{store_id}", status_code=204)
def delete_store(store_id: UUID, db: Session = Depends(get_db)):
    """Delete a store"""
    store = db.query(StoreSchema).filter(StoreSchema.id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")

    db.delete(store)
    db.commit()

    return None


if __name__ == "__main__":
    import uvicorn

    # Run the FastAPI application using uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
