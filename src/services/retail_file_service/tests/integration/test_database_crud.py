"""
Database integration tests for retail file service CRUD operations.
Tests real PostgreSQL database interactions.
"""

import os

# Import database model
import sys

import pytest
from fastapi import status
from sqlalchemy import text

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from ...database import RetailFileSchema


@pytest.mark.integration
class TestDatabaseCRUDIntegration:
    """Integration tests for RetailFile CRUD operations with real PostgreSQL."""

    def test_create_retail_file_database_integration(
        self, integration_client, integration_db_session, sample_retail_file_data
    ):
        """Test retail file creation with real database persistence."""
        # Create retail file via API
        response = integration_client.post(
            "/retail-files", json=sample_retail_file_data
        )
        assert response.status_code == status.HTTP_201_CREATED

        retail_file_data = response.json()
        retail_file_id = retail_file_data["id"]

        # Verify data was actually persisted in database
        db_retail_file = (
            integration_db_session.query(RetailFileSchema)
            .filter(RetailFileSchema.id == retail_file_id)
            .first()
        )
        assert db_retail_file is not None
        assert db_retail_file.chain_id == sample_retail_file_data["chain_id"]
        assert db_retail_file.store_id == sample_retail_file_data["store_id"]
        assert db_retail_file.file_name == sample_retail_file_data["file_name"]
        assert db_retail_file.file_path == sample_retail_file_data["file_path"]
        assert db_retail_file.file_size == sample_retail_file_data["file_size"]
        assert db_retail_file.is_processed == sample_retail_file_data["is_processed"]

        # Verify auto-generated fields
        assert db_retail_file.id is not None
        assert db_retail_file.created_at is not None
        assert db_retail_file.updated_at is not None

    def test_database_constraints_enforced(
        self, integration_client, integration_db_session, sample_retail_file_data
    ):
        """Test that database constraints are properly enforced."""
        # Create first retail file
        response1 = integration_client.post(
            "/retail-files", json=sample_retail_file_data
        )
        assert response1.status_code == status.HTTP_201_CREATED

        # Try to create duplicate (should fail due to unique constraint)
        response2 = integration_client.post(
            "/retail-files", json=sample_retail_file_data
        )
        assert response2.status_code == status.HTTP_400_BAD_REQUEST

        # Verify only one retail file exists in database
        count = integration_db_session.query(RetailFileSchema).count()
        assert count == 1

    def test_database_transaction_rollback(
        self, integration_client, integration_db_session, sample_retail_file_data
    ):
        """Test that database transactions work correctly."""
        # Create retail file
        response = integration_client.post(
            "/retail-files", json=sample_retail_file_data
        )
        assert response.status_code == status.HTTP_201_CREATED
        retail_file_id = response.json()["id"]

        # Verify retail file exists
        db_retail_file = (
            integration_db_session.query(RetailFileSchema)
            .filter(RetailFileSchema.id == retail_file_id)
            .first()
        )
        assert db_retail_file is not None

        # The transaction should be rolled back after the test due to the fixture

    def test_database_pagination_performance(
        self, integration_client, integration_db_session, multiple_retail_files_data
    ):
        """Test database pagination with larger datasets."""
        # Create multiple retail files
        created_retail_files = []
        for retail_file_data in multiple_retail_files_data:
            response = integration_client.post("/retail-files", json=retail_file_data)
            assert response.status_code == status.HTTP_201_CREATED
            created_retail_files.append(response.json())

        # Test pagination
        response = integration_client.get("/retail-files?page=1&size=2")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["total"] == len(multiple_retail_files_data)
        assert data["page"] == 1
        assert data["size"] == 2
        assert len(data["items"]) == 2

        # Verify database count matches
        db_count = integration_db_session.query(RetailFileSchema).count()
        assert db_count == len(multiple_retail_files_data)

    def test_database_update_persistence(
        self, integration_client, integration_db_session, sample_retail_file_data
    ):
        """Test that database updates are properly persisted."""
        # Create retail file
        create_response = integration_client.post(
            "/retail-files", json=sample_retail_file_data
        )
        assert create_response.status_code == status.HTTP_201_CREATED
        retail_file_id = create_response.json()["id"]

        # Update retail file
        update_data = {
            "file_name": "updated_integration_file.csv",
            "file_path": "/data/updated/updated_integration_file.csv",
            "file_size": 2048,
            "is_processed": True,
        }

        update_response = integration_client.put(
            f"/retail-files/{retail_file_id}", json=update_data
        )
        assert update_response.status_code == status.HTTP_200_OK

        # Verify update in database
        db_retail_file = (
            integration_db_session.query(RetailFileSchema)
            .filter(RetailFileSchema.id == retail_file_id)
            .first()
        )
        assert db_retail_file.file_name == "updated_integration_file.csv"
        assert db_retail_file.file_path == "/data/updated/updated_integration_file.csv"
        assert db_retail_file.file_size == 2048
        assert db_retail_file.is_processed == True

        # Verify other fields unchanged
        assert db_retail_file.chain_id == sample_retail_file_data["chain_id"]
        assert db_retail_file.store_id == sample_retail_file_data["store_id"]

    def test_database_delete_persistence(
        self, integration_client, integration_db_session, sample_retail_file_data
    ):
        """Test that database deletions are properly persisted."""
        # Create retail file
        create_response = integration_client.post(
            "/retail-files", json=sample_retail_file_data
        )
        assert create_response.status_code == status.HTTP_201_CREATED
        retail_file_id = create_response.json()["id"]

        # Verify retail file exists in database
        db_retail_file = (
            integration_db_session.query(RetailFileSchema)
            .filter(RetailFileSchema.id == retail_file_id)
            .first()
        )
        assert db_retail_file is not None

        # Delete retail file
        delete_response = integration_client.delete(f"/retail-files/{retail_file_id}")
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT

        # Verify retail file is deleted from database
        db_retail_file = (
            integration_db_session.query(RetailFileSchema)
            .filter(RetailFileSchema.id == retail_file_id)
            .first()
        )
        assert db_retail_file is None

    def test_database_query_performance(
        self, integration_client, integration_db_session, multiple_retail_files_data
    ):
        """Test database query performance with multiple records."""
        # Create multiple retail files
        for retail_file_data in multiple_retail_files_data:
            response = integration_client.post("/retail-files", json=retail_file_data)
            assert response.status_code == status.HTTP_201_CREATED

        # Test various queries
        # Query by chain_id
        chain_retail_files = (
            integration_db_session.query(RetailFileSchema)
            .filter(RetailFileSchema.chain_id == "bulk_chain_001")
            .all()
        )
        # Only first two retail files have bulk_chain_001, third has bulk_chain_002
        assert len(chain_retail_files) == 2

        # Query by store_id
        store_retail_files = (
            integration_db_session.query(RetailFileSchema)
            .filter(RetailFileSchema.store_id == 3001)
            .all()
        )
        assert len(store_retail_files) == 1  # Only first retail file

        # Query by is_processed
        processed_retail_files = (
            integration_db_session.query(RetailFileSchema)
            .filter(RetailFileSchema.is_processed == True)
            .all()
        )
        assert len(processed_retail_files) == 1  # Only second retail file

    def test_database_connection_handling(
        self, integration_client, integration_db_session
    ):
        """Test database connection handling and error scenarios."""
        # Test database health check
        response = integration_client.get("/health/db")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"

        # Test that we can execute raw SQL
        result = integration_db_session.execute(
            text("SELECT COUNT(*) FROM retail_files")
        )
        count = result.scalar()
        assert isinstance(count, int)

    def test_database_schema_validation(
        self, integration_client, integration_db_session
    ):
        """Test that database schema constraints are enforced."""
        # Test missing required field (should fail at validation level)
        invalid_data = {
            "chain_id": "invalid_chain",
            "store_id": 1001,
            # Missing file_name - should cause validation error
            "file_path": "/data/invalid/invalid_file.csv",
            "file_size": 1024,
            "upload_date": "2024-01-01T12:00:00Z",
            "is_processed": False,
        }

        response = integration_client.post("/retail-files", json=invalid_data)
        # Should fail due to validation (missing required field)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_database_concurrent_access_simulation(
        self, integration_client, integration_db_session, sample_retail_file_data
    ):
        """Test database behavior under simulated concurrent access."""
        # Create retail file
        response1 = integration_client.post(
            "/retail-files", json=sample_retail_file_data
        )
        assert response1.status_code == status.HTTP_201_CREATED
        retail_file_id = response1.json()["id"]

        # Simulate concurrent read
        response2 = integration_client.get(f"/retail-files/{retail_file_id}")
        assert response2.status_code == status.HTTP_200_OK

        # Simulate concurrent update
        update_data = {"file_name": "concurrent_update_file.csv"}
        response3 = integration_client.put(
            f"/retail-files/{retail_file_id}", json=update_data
        )
        assert response3.status_code == status.HTTP_200_OK

        # Verify final state
        db_retail_file = (
            integration_db_session.query(RetailFileSchema)
            .filter(RetailFileSchema.id == retail_file_id)
            .first()
        )
        assert db_retail_file.file_name == "concurrent_update_file.csv"

    def test_database_unique_constraint_with_null_store_id(
        self, integration_client, integration_db_session
    ):
        """Test unique constraint behavior with null store_id."""
        # Create retail file without store_id
        retail_file_data_1 = {
            "chain_id": "test_chain",
            "file_name": "test_file.csv",
            "file_path": "/data/test/test_file.csv",
            "file_size": 1024,
            "upload_date": "2024-01-01T12:00:00Z",
            "is_processed": False,
        }

        response1 = integration_client.post("/retail-files", json=retail_file_data_1)
        assert response1.status_code == status.HTTP_201_CREATED

        # Try to create another with same chain_id and file_name but no store_id
        retail_file_data_2 = {
            "chain_id": "test_chain",
            "file_name": "test_file.csv",
            "file_path": "/data/test/test_file_2.csv",
            "file_size": 2048,
            "upload_date": "2024-01-01T12:00:00Z",
            "is_processed": True,
        }

        response2 = integration_client.post("/retail-files", json=retail_file_data_2)
        # Should fail due to unique constraint (chain_id, store_id=NULL, file_name)
        assert response2.status_code == status.HTTP_400_BAD_REQUEST

        # Verify only one retail file exists
        count = integration_db_session.query(RetailFileSchema).count()
        assert count == 1
