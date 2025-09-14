"""
Pytest configuration and fixtures for file processor service tests.
"""

import os

# Set testing environment variable to enable fallback imports
os.environ["TESTING"] = "true"

# Import the main app components
import sys
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
# Add shared directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", ".."))

from main import app


@pytest.fixture(scope="function")
def mock_kafka_consumer():
    """Mock Kafka consumer to avoid external dependencies in tests."""
    mock_consumer = AsyncMock()
    mock_consumer.connect = AsyncMock()
    mock_consumer.disconnect = AsyncMock()
    mock_consumer.subscribe = AsyncMock()
    mock_consumer.unsubscribe = AsyncMock()
    mock_consumer.getmany = AsyncMock(return_value=[])
    mock_consumer.is_connected = False  # Set to False for unit tests
    return mock_consumer


@pytest.fixture(scope="function")
def mock_kafka_producer():
    """Mock Kafka producer to avoid external dependencies in tests."""
    mock_producer = AsyncMock()
    mock_producer.connect = AsyncMock()
    mock_producer.disconnect = AsyncMock()
    mock_producer.send_message = AsyncMock(return_value=True)
    mock_producer.is_connected = False  # Set to False for unit tests
    return mock_producer


@pytest.fixture(scope="function")
def mock_s3_client():
    """Mock S3 client to avoid external dependencies in tests."""
    mock_s3 = AsyncMock()
    mock_s3.download_file = AsyncMock()
    mock_s3.upload_file = AsyncMock()
    mock_s3.delete_file = AsyncMock()
    mock_s3.file_exists = AsyncMock(return_value=True)
    return mock_s3


@pytest.fixture(scope="function")
def client(mock_kafka_consumer, mock_kafka_producer, mock_s3_client):
    """Create a test client with mocked dependencies."""
    # Mock the global instances
    import main

    original_kafka_consumer = getattr(main, "kafka_consumer", None)
    original_kafka_producer = getattr(main, "kafka_producer", None)
    original_s3_client = getattr(main, "s3_client", None)

    main.kafka_consumer = mock_kafka_consumer
    main.kafka_producer = mock_kafka_producer
    main.s3_client = mock_s3_client

    with TestClient(app) as test_client:
        yield test_client

    # Restore original instances
    main.kafka_consumer = original_kafka_consumer
    main.kafka_producer = original_kafka_producer
    main.s3_client = original_s3_client


@pytest.fixture
def sample_retail_file_data():
    """Sample retail file data for testing."""
    return {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "chain_id": "test_chain_001",
        "store_id": 1,
        "file_name": "test_file.xml",
        "file_path": "/uploads/test_file.xml",
        "file_size": 1024,
        "upload_date": "2024-01-15T10:30:00",
        "is_processed": False,
        "created_at": "2024-01-15T10:30:00",
        "updated_at": "2024-01-15T10:30:00",
    }


@pytest.fixture
def sample_extracted_data():
    """Sample extracted price product data for testing."""
    return [
        {
            "product_id": "PROD001",
            "product_name": "Test Product 1",
            "price": 9.99,
            "currency": "USD",
            "store_id": 1,
            "chain_id": "test_chain_001",
        },
        {
            "product_id": "PROD002",
            "product_name": "Test Product 2",
            "price": 19.99,
            "currency": "USD",
            "store_id": 1,
            "chain_id": "test_chain_001",
        },
    ]
