"""
Pytest configuration and fixtures for store service tests.
"""

import os

# Import the main app and database components
import sys

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import Base, get_db
from main import app

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
def sample_store_data():
    """Sample store data for testing."""
    return {
        "store_code": 1001,
        "store_name": "Test Store Downtown",
        "address": "123 Main Street",
        "city": "New York",
        "zip_code": "10001",
        "sub_chain_id": "sub_chain_001",
        "chain_id": "chain_001",
    }


@pytest.fixture
def sample_store_data_2():
    """Second sample store data for testing."""
    return {
        "store_code": 1002,
        "store_name": "Test Store Uptown",
        "address": "456 Broadway",
        "city": "New York",
        "zip_code": "10002",
        "sub_chain_id": "sub_chain_001",
        "chain_id": "chain_001",
    }
