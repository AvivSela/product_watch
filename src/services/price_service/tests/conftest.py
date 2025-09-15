"""
Pytest configuration and fixtures for price service tests.
"""


# Import the main app and database components

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from ..database import Base, get_db
from ..main import app

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
def sample_price_data():
    """Sample price data for testing."""
    return {
        "chain_id": "test_chain_001",
        "store_id": 1,
        "item_code": "TEST_ITEM_001",
        "price_amount": 9.99,
        "currency_code": "USD",
        "price_update_date": "2024-01-15T10:30:00Z",
    }


@pytest.fixture
def sample_price_data_2():
    """Second sample price data for testing."""
    return {
        "chain_id": "test_chain_002",
        "store_id": 2,
        "item_code": "TEST_ITEM_002",
        "price_amount": 15.50,
        "currency_code": "EUR",
        "price_update_date": "2024-01-16T14:45:00Z",
    }
