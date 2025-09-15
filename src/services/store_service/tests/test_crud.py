"""
CRUD unit tests for store service.
"""

import pytest
from fastapi import status


@pytest.mark.unit
class TestStoreCRUD:
    """Test class for Store CRUD operations."""

    def test_create_store_success(self, client, sample_store_data):
        """Test successful store creation."""
        response = client.post("/stores", json=sample_store_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        # Check that all fields are present and correct
        assert data["store_code"] == sample_store_data["store_code"]
        assert data["store_name"] == sample_store_data["store_name"]
        assert data["address"] == sample_store_data["address"]
        assert data["city"] == sample_store_data["city"]
        assert data["zip_code"] == sample_store_data["zip_code"]
        assert data["sub_chain_id"] == sample_store_data["sub_chain_id"]
        assert data["chain_id"] == sample_store_data["chain_id"]

        # Check that auto-generated fields are present
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_store_duplicate_fails(self, client, sample_store_data):
        """Test that creating duplicate stores fails."""
        # Create first store
        response1 = client.post("/stores", json=sample_store_data)
        assert response1.status_code == status.HTTP_201_CREATED

        # Try to create duplicate (same store_code and chain_id)
        response2 = client.post("/stores", json=sample_store_data)
        assert response2.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in response2.json()["detail"]

    def test_create_store_different_chain_succeeds(
        self, client, sample_store_data, sample_store_data_2
    ):
        """Test that same store_code in different chain succeeds."""
        # Create first store
        response1 = client.post("/stores", json=sample_store_data)
        assert response1.status_code == status.HTTP_201_CREATED

        # Create store with same store_code but different chain_id
        sample_store_data_2["store_code"] = sample_store_data[
            "store_code"
        ]  # Same store_code
        sample_store_data_2["chain_id"] = "chain_002"  # Different chain_id
        response2 = client.post("/stores", json=sample_store_data_2)
        assert response2.status_code == status.HTTP_201_CREATED

    def test_create_store_validation_errors(self, client):
        """Test store creation with validation errors."""
        # Test missing required fields
        invalid_data = {
            "store_code": 1001,
            "store_name": "Test Store",
            # Missing address
            "city": "New York",
        }

        response = client.post("/stores", json=invalid_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_store_negative_store_code_fails(self, client):
        """Test that negative store_code fails."""
        invalid_data = {
            "store_code": -1,  # Negative store_code
            "store_name": "Test Store",
            "address": "123 Main Street",
            "city": "New York",
            "zip_code": "10001",
            "sub_chain_id": "sub_chain_001",
            "chain_id": "chain_001",
        }

        response = client.post("/stores", json=invalid_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_store_zero_store_code_fails(self, client):
        """Test that zero store_code fails."""
        invalid_data = {
            "store_code": 0,  # Zero store_code
            "store_name": "Test Store",
            "address": "123 Main Street",
            "city": "New York",
            "zip_code": "10001",
            "sub_chain_id": "sub_chain_001",
            "chain_id": "chain_001",
        }

        response = client.post("/stores", json=invalid_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_store_success(self, client, sample_store_data):
        """Test successful store retrieval."""
        # Create store first
        create_response = client.post("/stores", json=sample_store_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        store_id = create_response.json()["id"]

        # Get store
        response = client.get(f"/stores/{store_id}")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["id"] == store_id
        assert data["store_name"] == sample_store_data["store_name"]

    def test_get_store_not_found(self, client):
        """Test getting non-existent store returns 404."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.get(f"/stores/{fake_id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_stores_pagination(
        self, client, sample_store_data, sample_store_data_2
    ):
        """Test store listing with pagination."""
        # Create two stores
        client.post("/stores", json=sample_store_data)
        client.post("/stores", json=sample_store_data_2)

        # Test pagination
        response = client.get("/stores?page=1&size=1")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["page"] == 1
        assert data["size"] == 1
        assert data["total"] == 2
        assert data["pages"] == 2
        assert len(data["items"]) == 1

    def test_get_stores_empty_list(self, client):
        """Test getting stores when none exist."""
        response = client.get("/stores")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []
        assert data["page"] == 1
        assert data["size"] == 10
        assert data["pages"] == 0

    def test_update_store_success(self, client, sample_store_data):
        """Test successful store update."""
        # Create store first
        create_response = client.post("/stores", json=sample_store_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        store_id = create_response.json()["id"]

        # Update store
        update_data = {
            "store_name": "Updated Store Name",
            "address": "456 Updated Street",
        }

        response = client.put(f"/stores/{store_id}", json=update_data)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["store_name"] == "Updated Store Name"
        assert data["address"] == "456 Updated Street"
        # Other fields should remain unchanged
        assert data["store_code"] == sample_store_data["store_code"]
        assert data["chain_id"] == sample_store_data["chain_id"]

    def test_update_store_not_found(self, client):
        """Test updating non-existent store returns 404."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        update_data = {"store_name": "Updated Name"}

        response = client.put(f"/stores/{fake_id}", json=update_data)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_store_duplicate_constraint(
        self, client, sample_store_data, sample_store_data_2
    ):
        """Test that updating to create duplicate constraint fails."""
        # Create two stores
        client.post("/stores", json=sample_store_data)
        response2 = client.post("/stores", json=sample_store_data_2)

        store2_id = response2.json()["id"]

        # Try to update store2 to have same store_code and chain_id as store1
        update_data = {
            "store_code": sample_store_data["store_code"],
            "chain_id": sample_store_data["chain_id"],
        }

        response = client.put(f"/stores/{store2_id}", json=update_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in response.json()["detail"]

    def test_delete_store_success(self, client, sample_store_data):
        """Test successful store deletion."""
        # Create store first
        create_response = client.post("/stores", json=sample_store_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        store_id = create_response.json()["id"]

        # Delete store
        response = client.delete(f"/stores/{store_id}")
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify store is deleted
        get_response = client.get(f"/stores/{store_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_store_not_found(self, client):
        """Test deleting non-existent store returns 404."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.delete(f"/stores/{fake_id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_complete_crud_workflow(self, client, sample_store_data):
        """Test complete CRUD workflow."""
        # Create
        create_response = client.post("/stores", json=sample_store_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        store_id = create_response.json()["id"]

        # Read
        get_response = client.get(f"/stores/{store_id}")
        assert get_response.status_code == status.HTTP_200_OK
        assert get_response.json()["store_name"] == sample_store_data["store_name"]

        # Update
        update_data = {"store_name": "Updated Name", "city": "Boston"}
        update_response = client.put(f"/stores/{store_id}", json=update_data)
        assert update_response.status_code == status.HTTP_200_OK
        assert update_response.json()["store_name"] == "Updated Name"

        # Verify update
        get_response = client.get(f"/stores/{store_id}")
        assert get_response.json()["store_name"] == "Updated Name"
        assert get_response.json()["city"] == "Boston"

        # Delete
        delete_response = client.delete(f"/stores/{store_id}")
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT

        # Verify deletion
        get_response = client.get(f"/stores/{store_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
