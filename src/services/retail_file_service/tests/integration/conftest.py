"""
Integration test configuration and fixtures for retail file service.
Tests real PostgreSQL database interactions.
"""

import os
import subprocess

# Import the main app and database components
import sys
import time
from contextlib import contextmanager
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Set testing environment variable to enable fallback imports
os.environ["TESTING"] = "true"

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
# Add shared directory to path
sys.path.insert(
    0,
    os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "..", ".."
    ),
)

from ...database import Base, get_db
from ...main import app


class PostgreSQLTestManager:
    """Manages PostgreSQL test database lifecycle."""

    def __init__(self):
        self.host = os.getenv("POSTGRES_TEST_HOST", "localhost")
        self.port = os.getenv(
            "POSTGRES_TEST_PORT", "5433"
        )  # Different port to avoid conflicts
        self.user = os.getenv("POSTGRES_TEST_USER", "postgres")
        self.password = os.getenv("POSTGRES_TEST_PASSWORD", "password")
        self.database = os.getenv("POSTGRES_TEST_DB", "products_watch_test")
        self.container_name = "products_watch_test_postgres"

    def start_postgres_container(self):
        """Start PostgreSQL test container."""
        try:
            # Check if container already exists
            result = subprocess.run(
                [
                    "docker",
                    "ps",
                    "-a",
                    "--filter",
                    f"name={self.container_name}",
                    "--format",
                    "{{.Names}}",
                ],
                capture_output=True,
                text=True,
                check=True,
            )

            if self.container_name in result.stdout:
                # Container exists, start it
                subprocess.run(["docker", "start", self.container_name], check=True)
            else:
                # Create new container
                subprocess.run(
                    [
                        "docker",
                        "run",
                        "-d",
                        "--name",
                        self.container_name,
                        "-p",
                        f"{self.port}:5432",
                        "-e",
                        f"POSTGRES_DB={self.database}",
                        "-e",
                        f"POSTGRES_USER={self.user}",
                        "-e",
                        f"POSTGRES_PASSWORD={self.password}",
                        "postgres:15-alpine",
                    ],
                    check=True,
                )

            # Wait for PostgreSQL to be ready
            self._wait_for_postgres()

        except subprocess.CalledProcessError as e:
            pytest.skip(f"Could not start PostgreSQL container: {e}")

    def stop_postgres_container(self):
        """Stop PostgreSQL test container."""
        try:
            subprocess.run(["docker", "stop", self.container_name], check=True)
        except subprocess.CalledProcessError:
            pass  # Container might not be running

    def _wait_for_postgres(self, timeout=30):
        """Wait for PostgreSQL to be ready."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                engine = create_engine(
                    f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
                )
                with engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                return
            except Exception:
                time.sleep(1)
        raise Exception("PostgreSQL did not become ready in time")

    def get_database_url(self):
        """Get database URL for tests."""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


@pytest.fixture(scope="session")
def postgres_manager():
    """Session-scoped PostgreSQL manager."""
    manager = PostgreSQLTestManager()
    manager.start_postgres_container()
    yield manager
    manager.stop_postgres_container()


@pytest.fixture(scope="session")
def integration_engine(postgres_manager):
    """Session-scoped database engine for integration tests."""
    database_url = postgres_manager.get_database_url()
    engine = create_engine(
        database_url,
        poolclass=StaticPool,
        pool_pre_ping=True,
        echo=False,  # Set to True for SQL debugging
    )

    # Create all tables
    Base.metadata.create_all(bind=engine)

    yield engine

    # Clean up
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def integration_db_session(integration_engine):
    """Function-scoped database session with transaction rollback."""
    connection = integration_engine.connect()
    transaction = connection.begin()

    # Create session bound to the transaction
    TestingSessionLocal = sessionmaker(bind=connection)
    session = TestingSessionLocal()

    yield session

    # Rollback transaction and close connection
    # Check if transaction is still active before rolling back
    if transaction.is_active:
        transaction.rollback()
    session.close()
    connection.close()


@pytest.fixture(scope="function")
def integration_client(integration_db_session):
    """Create a test client with real PostgreSQL database."""
    app.dependency_overrides[get_db] = lambda: integration_db_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_retail_file_data():
    """Sample retail file data for integration testing."""
    return {
        "chain_id": "integration_chain_001",
        "store_id": 2001,
        "file_name": "integration_test_file.csv",
        "file_path": "/data/integration/integration_test_file.csv",
        "file_size": 1024,
        "upload_date": datetime.now(timezone.utc).isoformat(),
        "is_processed": False,
    }


@pytest.fixture
def sample_retail_file_data_2():
    """Second sample retail file data for integration testing."""
    return {
        "chain_id": "integration_chain_001",
        "store_id": 2002,
        "file_name": "integration_test_file_2.csv",
        "file_path": "/data/integration/integration_test_file_2.csv",
        "file_size": 2048,
        "upload_date": datetime.now(timezone.utc).isoformat(),
        "is_processed": True,
    }


@pytest.fixture
def multiple_retail_files_data():
    """Multiple retail files data for bulk testing."""
    return [
        {
            "chain_id": "bulk_chain_001",
            "store_id": 3001,
            "file_name": "bulk_test_file_1.csv",
            "file_path": "/data/bulk/bulk_test_file_1.csv",
            "file_size": 1024,
            "upload_date": datetime.now(timezone.utc).isoformat(),
            "is_processed": False,
        },
        {
            "chain_id": "bulk_chain_001",
            "store_id": 3002,
            "file_name": "bulk_test_file_2.csv",
            "file_path": "/data/bulk/bulk_test_file_2.csv",
            "file_size": 2048,
            "upload_date": datetime.now(timezone.utc).isoformat(),
            "is_processed": True,
        },
        {
            "chain_id": "bulk_chain_002",
            "store_id": 3003,
            "file_name": "bulk_test_file_3.csv",
            "file_path": "/data/bulk/bulk_test_file_3.csv",
            "file_size": 4096,
            "upload_date": datetime.now(timezone.utc).isoformat(),
            "is_processed": False,
        },
    ]


@contextmanager
def database_transaction(db_session):
    """Context manager for database transactions in tests."""
    try:
        yield db_session
        db_session.commit()
    except Exception:
        db_session.rollback()
        raise


@pytest.fixture
def mock_kafka_producer():
    """Mock Kafka producer for testing."""
    from unittest.mock import AsyncMock, MagicMock

    mock_producer = MagicMock()
    mock_producer.is_connected = True
    mock_producer.send_message = AsyncMock(return_value=True)
    mock_producer.connect = AsyncMock()
    mock_producer.disconnect = AsyncMock()

    return mock_producer


@pytest.fixture
def kafka_test_config():
    """Kafka test configuration."""
    return {
        "bootstrap_servers": os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
        "topic": os.getenv("KAFKA_TOPIC_RETAIL_FILES", "retail_files"),
    }
