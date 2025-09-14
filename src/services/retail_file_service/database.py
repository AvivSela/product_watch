# Standard library imports
import uuid
from os import getenv

# Third-party imports
from dotenv import load_dotenv
from sqlalchemy import TIMESTAMP, Boolean, Column, Integer, String, create_engine, func
from sqlalchemy.dialects.postgresql import UUID
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


# Database model
class RetailFileSchema(Base):
    __tablename__ = "retail_files"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    chain_id = Column(String(100), nullable=False)
    store_id = Column(Integer, nullable=True)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=True)
    upload_date = Column(TIMESTAMP, nullable=False)
    is_processed = Column(Boolean, nullable=False, default=False)
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
