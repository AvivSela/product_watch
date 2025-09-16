# Standard library imports
import uuid
from os import getenv

# Third-party imports
from dotenv import load_dotenv
from sqlalchemy import (
    TIMESTAMP,
    Column,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    create_engine,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

# Database configuration
DATABASE_URL = getenv(
    "DATABASE_URL", "postgresql://postgres:password@localhost:5432/products_watch"
)

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()


# Database-agnostic UUID column type
def UUIDColumn(*args, **kwargs):
    """Create a UUID column that works with both PostgreSQL and SQLite."""
    if engine.dialect.name == "postgresql":
        return Column(PostgresUUID(as_uuid=True), *args, **kwargs)
    else:
        # For SQLite and other databases, use String(36) to store UUID as string
        return Column(String(36), *args, **kwargs)


# Database model
class ProductSchema(Base):
    __tablename__ = "products"
    __table_args__ = (
        UniqueConstraint(
            "chain_id", "store_id", "item_code", name="uix_chain_store_item"
        ),
    )

    id = UUIDColumn(primary_key=True, default=uuid.uuid4, index=True)
    chain_id = Column(String(100), nullable=False)
    store_id = Column(Integer, nullable=False)
    item_code = Column(String(100), nullable=False)
    item_name = Column(String(255), nullable=False)
    manufacturer_item_description = Column(String(1000), nullable=False)
    manufacturer_name = Column(String(255), nullable=False)
    manufacture_country = Column(String(100), nullable=False)
    unit_qty = Column(String(100), nullable=False)
    quantity = Column(Numeric(10, 3), nullable=False)
    qty_in_package = Column(Numeric(10, 3), nullable=False)
    created_at = Column(TIMESTAMP, default=func.now())
    updated_at = Column(TIMESTAMP, default=func.now(), onupdate=func.now())


# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")
