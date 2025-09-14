"""
Pytest configuration and fixtures for product service tests.
"""


# Import the main app and database components

import pytest
from database import Base, get_db
from fastapi.testclient import TestClient
from main import app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Test database configuration
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    # Create tables
    Base.metadata.create_all(bind=engine)

    # Create session
    session = TestingSessionLocal()

    yield session

    # Clean up
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database override."""
    app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_product_data():
    """Sample product data for testing."""
    return {
        "chain_id": "test_chain_001",
        "store_id": 1,
        "item_code": "TEST_ITEM_001",
        "item_name": "Test Product",
        "manufacturer_item_description": "A test product for unit testing",
        "manufacturer_name": "Test Manufacturer Inc.",
        "manufacture_country": "USA",
        "unit_qty": "1 piece",
        "quantity": 10.5,
        "qty_in_package": 1.0,
    }


@pytest.fixture
def sample_product_data_2():
    """Second sample product data for testing."""
    return {
        "chain_id": "test_chain_001",
        "store_id": 2,
        "item_code": "TEST_ITEM_002",
        "item_name": "Another Test Product",
        "manufacturer_item_description": "Another test product for unit testing",
        "manufacturer_name": "Another Test Manufacturer",
        "manufacture_country": "Canada",
        "unit_qty": "2 pieces",
        "quantity": 5.0,
        "qty_in_package": 2.0,
    }
