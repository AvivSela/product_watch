# Standard library imports
import uuid
from os import getenv

# Third-party imports
from dotenv import load_dotenv
from sqlalchemy import TIMESTAMP, Column, Integer, Numeric, String, create_engine, func
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
class PriceSchema(Base):
    __tablename__ = "prices"

    id = UUIDColumn(primary_key=True, default=uuid.uuid4, index=True)
    chain_id = Column(String(100), nullable=True)
    store_id = Column(Integer, nullable=True)
    item_code = Column(String(100), nullable=True)
    price_amount = Column(Numeric(10, 2), nullable=True)
    currency_code = Column(String(3), nullable=True)
    price_update_date = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP, default=func.now(), nullable=False)
    updated_at = Column(
        TIMESTAMP, default=func.now(), onupdate=func.now(), nullable=False
    )


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
