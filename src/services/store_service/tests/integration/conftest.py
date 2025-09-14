"""
Integration test configuration and fixtures for store service.
Tests real PostgreSQL database interactions.
"""

import os
import subprocess

# Import the main app and database components
import time
from contextlib import contextmanager

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
def sample_store_data():
    """Sample store data for integration testing."""
    return {
        "store_code": 2001,
        "store_name": "Integration Test Store Downtown",
        "address": "123 Integration Street",
        "city": "Test City",
        "zip_code": "20001",
        "sub_chain_id": "integration_sub_chain_001",
        "chain_id": "integration_chain_001",
    }


@pytest.fixture
def sample_store_data_2():
    """Second sample store data for integration testing."""
    return {
        "store_code": 2002,
        "store_name": "Integration Test Store Uptown",
        "address": "456 Integration Avenue",
        "city": "Test City",
        "zip_code": "20002",
        "sub_chain_id": "integration_sub_chain_001",
        "chain_id": "integration_chain_001",
    }


@pytest.fixture
def multiple_stores_data():
    """Multiple stores data for bulk testing."""
    return [
        {
            "store_code": 3001,
            "store_name": "Bulk Test Store 1",
            "address": "111 Bulk Street",
            "city": "Bulk City",
            "zip_code": "30001",
            "sub_chain_id": "bulk_sub_chain_001",
            "chain_id": "bulk_chain_001",
        },
        {
            "store_code": 3002,
            "store_name": "Bulk Test Store 2",
            "address": "222 Bulk Street",
            "city": "Bulk City",
            "zip_code": "30002",
            "sub_chain_id": "bulk_sub_chain_001",
            "chain_id": "bulk_chain_001",
        },
        {
            "store_code": 3003,
            "store_name": "Bulk Test Store 3",
            "address": "333 Bulk Street",
            "city": "Bulk City",
            "zip_code": "30003",
            "sub_chain_id": "bulk_sub_chain_002",
            "chain_id": "bulk_chain_001",
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
