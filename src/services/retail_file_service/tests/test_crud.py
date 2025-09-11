"""
CRUD unit tests for retail file service.
"""

from fastapi import status


class TestRetailFileCRUD:
    """Test class for Retail File CRUD operations."""

    def test_create_retail_file_success(self, client, sample_retail_file_data):
        """Test successful retail file creation."""
        response = client.post("/retail-files", json=sample_retail_file_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        # Check that all fields are present and correct
        assert data["chain_id"] == sample_retail_file_data["chain_id"]
        assert data["store_id"] == sample_retail_file_data["store_id"]
        assert data["file_name"] == sample_retail_file_data["file_name"]
        assert data["file_path"] == sample_retail_file_data["file_path"]
        assert data["file_size"] == sample_retail_file_data["file_size"]
        assert data["upload_date"] == sample_retail_file_data["upload_date"]
        assert data["is_processed"] == sample_retail_file_data["is_processed"]

        # Check that auto-generated fields are present
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_retail_file_duplicate_fails(self, client, sample_retail_file_data):
        """Test that creating duplicate retail files fails."""
        # Create first retail file
        response1 = client.post("/retail-files", json=sample_retail_file_data)
        assert response1.status_code == status.HTTP_201_CREATED

        # Try to create duplicate (same chain_id, store_id, file_name)
        response2 = client.post("/retail-files", json=sample_retail_file_data)
        assert response2.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in response2.json()["detail"]

    def test_create_retail_file_different_store_succeeds(
        self, client, sample_retail_file_data, sample_retail_file_data_2
    ):
        """Test that creating retail files with different stores succeeds."""
        # Create first retail file
        response1 = client.post("/retail-files", json=sample_retail_file_data)
        assert response1.status_code == status.HTTP_201_CREATED

        # Create second retail file with different store_id
        response2 = client.post("/retail-files", json=sample_retail_file_data_2)
        assert response2.status_code == status.HTTP_201_CREATED

        # Verify they have different IDs
        data1 = response1.json()
        data2 = response2.json()
        assert data1["id"] != data2["id"]

    def test_create_retail_file_without_store_id(self, client):
        """Test creating retail file without store_id."""
        retail_file_data = {
            "chain_id": "test_chain_001",
            "file_name": "test_file.csv",
            "file_path": "/uploads/test_file.csv",
            "file_size": 1024,
            "upload_date": "2024-01-15T10:30:00Z",
            "is_processed": False,
        }

        response = client.post("/retail-files", json=retail_file_data)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["store_id"] is None

    def test_get_retail_file_success(self, client, sample_retail_file_data):
        """Test successful retail file retrieval."""
        # Create retail file
        create_response = client.post("/retail-files", json=sample_retail_file_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        created_data = create_response.json()

        # Get retail file
        retail_file_id = created_data["id"]
        response = client.get(f"/retail-files/{retail_file_id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Verify all fields match
        assert data["id"] == created_data["id"]
        assert data["chain_id"] == sample_retail_file_data["chain_id"]
        assert data["store_id"] == sample_retail_file_data["store_id"]
        assert data["file_name"] == sample_retail_file_data["file_name"]
        assert data["file_path"] == sample_retail_file_data["file_path"]
        assert data["file_size"] == sample_retail_file_data["file_size"]
        assert data["upload_date"] == sample_retail_file_data["upload_date"]
        assert data["is_processed"] == sample_retail_file_data["is_processed"]

    def test_get_retail_file_not_found(self, client):
        """Test getting non-existent retail file returns 404."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.get(f"/retail-files/{fake_id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_retail_files_pagination(
        self, client, sample_retail_file_data, sample_retail_file_data_2
    ):
        """Test pagination for getting retail files."""
        # Create two retail files
        client.post("/retail-files", json=sample_retail_file_data)
        client.post("/retail-files", json=sample_retail_file_data_2)

        # Test pagination
        response = client.get("/retail-files?page=1&size=1")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["total"] == 2
        assert data["page"] == 1
        assert data["size"] == 1
        assert data["pages"] == 2
        assert len(data["items"]) == 1

        # Test second page
        response = client.get("/retail-files?page=2&size=1")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["total"] == 2
        assert data["page"] == 2
        assert data["size"] == 1
        assert data["pages"] == 2
        assert len(data["items"]) == 1

    def test_update_retail_file_success(self, client, sample_retail_file_data):
        """Test successful retail file update."""
        # Create retail file
        create_response = client.post("/retail-files", json=sample_retail_file_data)
        created_data = create_response.json()

        # Update retail file
        update_data = {
            "file_name": "updated_file.csv",
            "is_processed": True,
        }
        retail_file_id = created_data["id"]
        response = client.put(f"/retail-files/{retail_file_id}", json=update_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Verify updated fields
        assert data["file_name"] == "updated_file.csv"
        assert data["is_processed"] is True
        # Verify unchanged fields
        assert data["chain_id"] == sample_retail_file_data["chain_id"]
        assert data["store_id"] == sample_retail_file_data["store_id"]

    def test_update_retail_file_not_found(self, client):
        """Test updating non-existent retail file returns 404."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        update_data = {"file_name": "updated_file.csv"}
        response = client.put(f"/retail-files/{fake_id}", json=update_data)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_retail_file_duplicate_fails(
        self, client, sample_retail_file_data, sample_retail_file_data_2
    ):
        """Test that updating to duplicate combination fails."""
        # Create two retail files
        response1 = client.post("/retail-files", json=sample_retail_file_data)
        response2 = client.post("/retail-files", json=sample_retail_file_data_2)

        data1 = response1.json()
        data2 = response2.json()

        # Try to update second retail file to have same chain_id, store_id, file_name as first
        update_data = {
            "chain_id": sample_retail_file_data["chain_id"],
            "store_id": sample_retail_file_data["store_id"],
            "file_name": sample_retail_file_data["file_name"],
        }
        response = client.put(f"/retail-files/{data2['id']}", json=update_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in response.json()["detail"]

    def test_delete_retail_file_success(self, client, sample_retail_file_data):
        """Test successful retail file deletion."""
        # Create retail file
        create_response = client.post("/retail-files", json=sample_retail_file_data)
        created_data = create_response.json()

        # Delete retail file
        retail_file_id = created_data["id"]
        response = client.delete(f"/retail-files/{retail_file_id}")
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify retail file is deleted
        get_response = client.get(f"/retail-files/{retail_file_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_retail_file_not_found(self, client):
        """Test deleting non-existent retail file returns 404."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.delete(f"/retail-files/{fake_id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND
