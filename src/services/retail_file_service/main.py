# Standard library imports
import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from uuid import UUID

# Third-party imports
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy.orm import Session

# Local application imports
# Try relative imports first, fallback to absolute imports if needed
try:
    # Try relative imports first
    from .database import RetailFileSchema, get_db
    from .models import (
        PaginatedResponse,
        RetailFileCreate,
        RetailFileMessage,
        RetailFileUpdate,
    )
    from .models import RetailFile as RetailFileModel
except ImportError:
    # Fallback to absolute imports when running directly
    import os
    import sys

    # Add the current directory to Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)

    # Add the src directory to Python path for shared imports
    src_dir = os.path.join(os.path.dirname(__file__), "..", "..")
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)

    from database import RetailFileSchema, get_db
    from models import (
        PaginatedResponse,
        RetailFileCreate,
        RetailFileMessage,
        RetailFileUpdate,
    )
    from models import RetailFile as RetailFileModel

# Import Kafka producer with fallback
try:
    from ...shared.utils.kafka_producer import KafkaProducer
except ImportError:
    try:
        from shared.utils.kafka_producer import KafkaProducer
    except ImportError:
        # Final fallback - add src to path and try again
        import os
        import sys

        src_dir = os.path.join(os.path.dirname(__file__), "..", "..")
        if src_dir not in sys.path:
            sys.path.insert(0, src_dir)
        from shared.utils.kafka_producer import KafkaProducer

# Kafka configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_TOPIC_RETAIL_FILES = os.getenv("KAFKA_TOPIC_RETAIL_FILES", "retail_files")

# Global Kafka producer instance
kafka_producer: KafkaProducer = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage Kafka producer lifecycle"""
    global kafka_producer

    # Skip Kafka connection in test environment
    if os.getenv("PYTEST_CURRENT_TEST") or os.getenv("TESTING"):
        print("Skipping Kafka connection in test environment")
        kafka_producer = None
    else:
        # Startup
        try:
            import asyncio

            kafka_producer = KafkaProducer(
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                request_timeout_ms=5000,  # 5 second timeout
                max_block_ms=5000,  # 5 second max block time
            )
            # Add timeout to connection attempt
            await asyncio.wait_for(kafka_producer.connect(), timeout=5.0)
            print(f"Kafka producer connected to {KAFKA_BOOTSTRAP_SERVERS}")
        except asyncio.TimeoutError:
            print("Kafka connection timeout - continuing without Kafka")
            kafka_producer = None
        except Exception as e:
            print(f"Failed to connect Kafka producer: {e}")
            kafka_producer = None

    yield

    # Shutdown
    if kafka_producer:
        try:
            await kafka_producer.disconnect()
            print("Kafka producer disconnected")
        except Exception as e:
            print(f"Error disconnecting Kafka producer: {e}")
        finally:
            kafka_producer = None


# Initialize FastAPI app
app = FastAPI(
    title="Retail File Service API",
    description="A simple FastAPI Retail File Service for managing retail files",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
def health_check():
    """Health check endpoint for monitoring service status"""
    return {
        "status": "healthy",
        "service": "retail-file-service",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/health/db")
def health_check_db(db: Session = Depends(get_db)):
    """Health check endpoint that verifies database connectivity"""
    try:
        # Simple database query to verify connection
        db.query(RetailFileSchema).limit(1).all()
        return {
            "status": "healthy",
            "service": "retail-file-service",
            "database": "connected",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "service": "retail-file-service",
                "database": "disconnected",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )


@app.get("/retail-files", response_model=PaginatedResponse)
def get_retail_files(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Files per page"),
    db: Session = Depends(get_db),
):
    """Get all retail files with pagination from PostgreSQL database"""
    # Calculate offset
    offset = (page - 1) * size

    # Get total count
    total = db.query(RetailFileSchema).count()

    # Get paginated retail files
    retail_files = db.query(RetailFileSchema).offset(offset).limit(size).all()

    # Calculate total pages
    pages = (total + size - 1) // size

    # Convert to RetailFile models
    retail_file_models = [
        RetailFileModel.from_db_model(retail_file) for retail_file in retail_files
    ]

    return PaginatedResponse(
        items=retail_file_models, total=total, page=page, size=size, pages=pages
    )


@app.get("/retail-files/{retail_file_id}", response_model=RetailFileModel)
def get_retail_file(retail_file_id: UUID, db: Session = Depends(get_db)):
    """Get a specific retail file by ID"""
    retail_file = (
        db.query(RetailFileSchema).filter(RetailFileSchema.id == retail_file_id).first()
    )
    if not retail_file:
        raise HTTPException(status_code=404, detail="Retail file not found")

    return RetailFileModel.from_db_model(retail_file)


@app.post("/retail-files", response_model=RetailFileModel, status_code=201)
async def create_retail_file(
    retail_file: RetailFileCreate, db: Session = Depends(get_db)
):
    """Create a new retail file"""
    # Check if retail file with same chain_id, store_id, and file_name already exists
    existing_retail_file = (
        db.query(RetailFileSchema)
        .filter(
            RetailFileSchema.chain_id == retail_file.chain_id,
            RetailFileSchema.store_id == retail_file.store_id,
            RetailFileSchema.file_name == retail_file.file_name,
        )
        .first()
    )
    if existing_retail_file:
        raise HTTPException(
            status_code=400,
            detail="Retail file with this chain ID, store ID, and file name already exists",
        )

    # Create new retail file
    db_retail_file = retail_file.to_db_model()

    db.add(db_retail_file)
    db.commit()
    db.refresh(db_retail_file)

    # Convert to response model
    retail_file_model = RetailFileModel.from_db_model(db_retail_file)

    # Produce Kafka message
    await produce_Kafka_message(kafka_producer, retail_file_model)

    return retail_file_model


@app.put("/retail-files/{retail_file_id}", response_model=RetailFileModel)
def update_retail_file(
    retail_file_id: UUID,
    retail_file_update: RetailFileUpdate,
    db: Session = Depends(get_db),
):
    """Update an existing retail file"""
    # Find the retail file
    retail_file = (
        db.query(RetailFileSchema).filter(RetailFileSchema.id == retail_file_id).first()
    )
    if not retail_file:
        raise HTTPException(status_code=404, detail="Retail file not found")

    # Check if chain_id, store_id, and file_name combination is being updated and if it conflicts with existing files
    if (
        (
            retail_file_update.chain_id
            and retail_file_update.chain_id != retail_file.chain_id
        )
        or (
            retail_file_update.store_id
            and retail_file_update.store_id != retail_file.store_id
        )
        or (
            retail_file_update.file_name
            and retail_file_update.file_name != retail_file.file_name
        )
    ):
        chain_id_to_check = (
            retail_file_update.chain_id
            if retail_file_update.chain_id
            else retail_file.chain_id
        )
        store_id_to_check = (
            retail_file_update.store_id
            if retail_file_update.store_id
            else retail_file.store_id
        )
        file_name_to_check = (
            retail_file_update.file_name
            if retail_file_update.file_name
            else retail_file.file_name
        )

        existing_retail_file = (
            db.query(RetailFileSchema)
            .filter(
                RetailFileSchema.chain_id == chain_id_to_check,
                RetailFileSchema.store_id == store_id_to_check,
                RetailFileSchema.file_name == file_name_to_check,
                RetailFileSchema.id != retail_file_id,
            )
            .first()
        )
        if existing_retail_file:
            raise HTTPException(
                status_code=400,
                detail="Retail file with this chain ID, store ID, and file name combination already exists",
            )

    # Update fields
    update_data = retail_file_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(retail_file, field, value)

    retail_file.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(retail_file)

    return RetailFileModel.from_db_model(retail_file)


@app.delete("/retail-files/{retail_file_id}", status_code=204)
def delete_retail_file(retail_file_id: UUID, db: Session = Depends(get_db)):
    """Delete a retail file"""
    retail_file = (
        db.query(RetailFileSchema).filter(RetailFileSchema.id == retail_file_id).first()
    )
    if not retail_file:
        raise HTTPException(status_code=404, detail="Retail file not found")

    db.delete(retail_file)
    db.commit()

    return None


async def produce_Kafka_message(
    kafka_producer: KafkaProducer, retail_file_model: RetailFileModel
):
    """Produce a Kafka message"""
    if kafka_producer and kafka_producer.is_connected:
        try:
            message = RetailFileMessage(
                event_type="retail_file_created", data=retail_file_model
            )

            await kafka_producer.send_message(
                KAFKA_TOPIC_RETAIL_FILES,
                message.model_dump_json(),
                key=str(retail_file_model.id),
            )
        except Exception as e:
            # Log the error but don't fail the request
            print(f"Failed to send Kafka message: {e}")
    else:
        print("Kafka producer not available, skipping message production")


if __name__ == "__main__":
    import uvicorn

    # Run the FastAPI application using uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
