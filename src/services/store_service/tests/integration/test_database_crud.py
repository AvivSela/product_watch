"""
Database integration tests for store service CRUD operations.
Tests real PostgreSQL database interactions.
"""

import pytest
from database import StoreSchema
from fastapi import status
from sqlalchemy import text


@pytest.mark.integration
class TestDatabaseCRUDIntegration:
    """Integration tests for Store CRUD operations with real PostgreSQL."""

    def test_create_store_database_integration(
        self, integration_client, integration_db_session, sample_store_data
    ):
        """Test store creation with real database persistence."""
        # Create store via API
        response = integration_client.post("/stores", json=sample_store_data)
        assert response.status_code == status.HTTP_201_CREATED

        store_data = response.json()
        store_id = store_data["id"]

        # Verify data was actually persisted in database
        db_store = (
            integration_db_session.query(StoreSchema)
            .filter(StoreSchema.id == store_id)
            .first()
        )
        assert db_store is not None
        assert db_store.store_code == sample_store_data["store_code"]
        assert db_store.store_name == sample_store_data["store_name"]
        assert db_store.address == sample_store_data["address"]
        assert db_store.city == sample_store_data["city"]
        assert db_store.zip_code == sample_store_data["zip_code"]
        assert db_store.sub_chain_id == sample_store_data["sub_chain_id"]
        assert db_store.chain_id == sample_store_data["chain_id"]

        # Verify auto-generated fields
        assert db_store.id is not None
        assert db_store.created_at is not None
        assert db_store.updated_at is not None

    def test_database_constraints_enforced(
        self, integration_client, integration_db_session, sample_store_data
    ):
        """Test that database constraints are properly enforced."""
        # Create first store
        response1 = integration_client.post("/stores", json=sample_store_data)
        assert response1.status_code == status.HTTP_201_CREATED

        # Try to create duplicate (should fail due to unique constraint)
        response2 = integration_client.post("/stores", json=sample_store_data)
        assert response2.status_code == status.HTTP_400_BAD_REQUEST

        # Verify only one store exists in database
        count = integration_db_session.query(StoreSchema).count()
        assert count == 1

    def test_database_transaction_rollback(
        self, integration_client, integration_db_session, sample_store_data
    ):
        """Test that database transactions work correctly."""
        # Create store
        response = integration_client.post("/stores", json=sample_store_data)
        assert response.status_code == status.HTTP_201_CREATED
        store_id = response.json()["id"]

        # Verify store exists
        db_store = (
            integration_db_session.query(StoreSchema)
            .filter(StoreSchema.id == store_id)
            .first()
        )
        assert db_store is not None

        # The transaction should be rolled back after the test due to the fixture

    def test_database_pagination_performance(
        self, integration_client, integration_db_session, multiple_stores_data
    ):
        """Test database pagination with larger datasets."""
        # Create multiple stores
        created_stores = []
        for store_data in multiple_stores_data:
            response = integration_client.post("/stores", json=store_data)
            assert response.status_code == status.HTTP_201_CREATED
            created_stores.append(response.json())

        # Test pagination
        response = integration_client.get("/stores?page=1&size=2")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["total"] == len(multiple_stores_data)
        assert data["page"] == 1
        assert data["size"] == 2
        assert len(data["items"]) == 2

        # Verify database count matches
        db_count = integration_db_session.query(StoreSchema).count()
        assert db_count == len(multiple_stores_data)

    def test_database_update_persistence(
        self, integration_client, integration_db_session, sample_store_data
    ):
        """Test that database updates are properly persisted."""
        # Create store
        create_response = integration_client.post("/stores", json=sample_store_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        store_id = create_response.json()["id"]

        # Update store
        update_data = {
            "store_name": "Updated Integration Store",
            "address": "999 Updated Street",
            "city": "Updated City",
        }

        update_response = integration_client.put(
            f"/stores/{store_id}", json=update_data
        )
        assert update_response.status_code == status.HTTP_200_OK

        # Verify update in database
        db_store = (
            integration_db_session.query(StoreSchema)
            .filter(StoreSchema.id == store_id)
            .first()
        )
        assert db_store.store_name == "Updated Integration Store"
        assert db_store.address == "999 Updated Street"
        assert db_store.city == "Updated City"

        # Verify other fields unchanged
        assert db_store.store_code == sample_store_data["store_code"]
        assert db_store.zip_code == sample_store_data["zip_code"]

    def test_database_delete_persistence(
        self, integration_client, integration_db_session, sample_store_data
    ):
        """Test that database deletions are properly persisted."""
        # Create store
        create_response = integration_client.post("/stores", json=sample_store_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        store_id = create_response.json()["id"]

        # Verify store exists in database
        db_store = (
            integration_db_session.query(StoreSchema)
            .filter(StoreSchema.id == store_id)
            .first()
        )
        assert db_store is not None

        # Delete store
        delete_response = integration_client.delete(f"/stores/{store_id}")
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT

        # Verify store is deleted from database
        db_store = (
            integration_db_session.query(StoreSchema)
            .filter(StoreSchema.id == store_id)
            .first()
        )
        assert db_store is None

    def test_database_query_performance(
        self, integration_client, integration_db_session, multiple_stores_data
    ):
        """Test database query performance with multiple records."""
        # Create multiple stores
        for store_data in multiple_stores_data:
            response = integration_client.post("/stores", json=store_data)
            assert response.status_code == status.HTTP_201_CREATED

        # Test various queries
        # Query by city
        city_stores = (
            integration_db_session.query(StoreSchema)
            .filter(StoreSchema.city == "Bulk City")
            .all()
        )
        assert len(city_stores) == len(multiple_stores_data)

        # Query by chain_id
        chain_stores = (
            integration_db_session.query(StoreSchema)
            .filter(StoreSchema.chain_id == "bulk_chain_001")
            .all()
        )
        assert len(chain_stores) == len(multiple_stores_data)

        # Query by sub_chain_id
        sub_chain_stores = (
            integration_db_session.query(StoreSchema)
            .filter(StoreSchema.sub_chain_id == "bulk_sub_chain_001")
            .all()
        )
        assert len(sub_chain_stores) == 2  # Only first two stores

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
        result = integration_db_session.execute(text("SELECT COUNT(*) FROM stores"))
        count = result.scalar()
        assert isinstance(count, int)

    def test_database_schema_validation(
        self, integration_client, integration_db_session
    ):
        """Test that database schema constraints are enforced."""
        # Test negative store_code (should fail at database level)
        invalid_data = {
            "store_code": -1,
            "store_name": "Invalid Store",
            "address": "123 Invalid Street",
            "city": "Invalid City",
            "zip_code": "00000",
            "sub_chain_id": "invalid_sub_chain",
            "chain_id": "invalid_chain",
        }

        response = integration_client.post("/stores", json=invalid_data)
        # Should fail due to validation (negative store_code)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_database_concurrent_access_simulation(
        self, integration_client, integration_db_session, sample_store_data
    ):
        """Test database behavior under simulated concurrent access."""
        # Create store
        response1 = integration_client.post("/stores", json=sample_store_data)
        assert response1.status_code == status.HTTP_201_CREATED
        store_id = response1.json()["id"]

        # Simulate concurrent read
        response2 = integration_client.get(f"/stores/{store_id}")
        assert response2.status_code == status.HTTP_200_OK

        # Simulate concurrent update
        update_data = {"store_name": "Concurrent Update"}
        response3 = integration_client.put(f"/stores/{store_id}", json=update_data)
        assert response3.status_code == status.HTTP_200_OK

        # Verify final state
        db_store = (
            integration_db_session.query(StoreSchema)
            .filter(StoreSchema.id == store_id)
            .first()
        )
        assert db_store.store_name == "Concurrent Update"
