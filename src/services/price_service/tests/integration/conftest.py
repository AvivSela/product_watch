"""
Integration test configuration and fixtures for price service.
Tests real PostgreSQL database interactions.
"""

import os
import subprocess
import sys
import time
from contextlib import contextmanager

# Set testing environment variable
os.environ["TESTING"] = "true"

# Add necessary paths for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.insert(
    0,
    os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "..", ".."
    ),
)

import pytest
from database import Base, get_db
from fastapi.testclient import TestClient
from main import app
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


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
        pool_pre_ping=False,  # Disable pre-ping to avoid transaction issues
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
    TestingSessionLocal = sessionmaker(
        bind=connection, autocommit=False, autoflush=False
    )
    session = TestingSessionLocal()

    yield session

    # Rollback transaction and close connection
    # Check if transaction is still active before rolling back
    if transaction.is_active:
        transaction.rollback()
    session.close()
    connection.close()


@pytest.fixture(scope="function")
def integration_client(integration_engine):
    """Create a test client with real PostgreSQL database."""

    def get_db_for_client():
        db = sessionmaker(bind=integration_engine, autocommit=False, autoflush=False)()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = get_db_for_client
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_price_data():
    """Sample price data for integration testing."""
    return {
        "chain_id": "integration_chain_001",
        "store_id": 2001,
        "item_code": "INTEGRATION_ITEM_001",
        "price_amount": 9.99,
        "currency_code": "USD",
        "price_update_date": "2024-01-15T10:30:00Z",
    }


@pytest.fixture
def sample_price_data_2():
    """Second sample price data for integration testing."""
    return {
        "chain_id": "integration_chain_001",
        "store_id": 2002,
        "item_code": "INTEGRATION_ITEM_002",
        "price_amount": 15.50,
        "currency_code": "EUR",
        "price_update_date": "2024-01-16T14:45:00Z",
    }


@pytest.fixture
def multiple_prices_data():
    """Multiple prices data for bulk testing."""
    return [
        {
            "chain_id": "bulk_chain_001",
            "store_id": 3001,
            "item_code": "BULK_ITEM_001",
            "price_amount": 5.99,
            "currency_code": "USD",
            "price_update_date": "2024-01-15T10:30:00Z",
        },
        {
            "chain_id": "bulk_chain_001",
            "store_id": 3002,
            "item_code": "BULK_ITEM_002",
            "price_amount": 12.50,
            "currency_code": "EUR",
            "price_update_date": "2024-01-16T14:45:00Z",
        },
        {
            "chain_id": "bulk_chain_001",
            "store_id": 3003,
            "item_code": "BULK_ITEM_003",
            "price_amount": 8.75,
            "currency_code": "GBP",
            "price_update_date": "2024-01-17T09:15:00Z",
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
