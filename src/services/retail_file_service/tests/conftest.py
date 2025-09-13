"""
Pytest configuration and fixtures for retail file service tests.
"""

import os

# Import the main app and database components
import sys
from unittest.mock import AsyncMock

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
def mock_kafka_producer():
    """Mock Kafka producer to avoid external dependencies in tests."""
    mock_producer = AsyncMock()
    mock_producer.connect = AsyncMock()
    mock_producer.disconnect = AsyncMock()
    mock_producer.send_message = AsyncMock(return_value=True)
    mock_producer.is_connected = True
    return mock_producer


@pytest.fixture(scope="function")
def client(db_session, mock_kafka_producer):
    """Create a test client with database override and mocked Kafka."""
    app.dependency_overrides[get_db] = lambda: db_session

    # Mock the global kafka_producer
    import main

    original_kafka_producer = getattr(main, "kafka_producer", None)
    main.kafka_producer = mock_kafka_producer

    with TestClient(app) as test_client:
        yield test_client

    # Restore original kafka_producer
    main.kafka_producer = original_kafka_producer
    app.dependency_overrides.clear()


@pytest.fixture
def sample_retail_file_data():
    """Sample retail file data for testing."""
    return {
        "chain_id": "test_chain_001",
        "store_id": 1,
        "file_name": "test_file.csv",
        "file_path": "/uploads/test_file.csv",
        "file_size": 1024,
        "upload_date": "2024-01-15T10:30:00",
        "is_processed": False,
    }


@pytest.fixture
def sample_retail_file_data_2():
    """Second sample retail file data for testing."""
    return {
        "chain_id": "test_chain_001",
        "store_id": 2,
        "file_name": "another_test_file.csv",
        "file_path": "/uploads/another_test_file.csv",
        "file_size": 2048,
        "upload_date": "2024-01-16T14:45:00",
        "is_processed": True,
    }
