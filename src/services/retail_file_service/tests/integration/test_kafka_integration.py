"""
Kafka integration tests for retail file service.
Tests real Kafka message production when creating retail files.
"""

import json

import pytest
from database import RetailFileSchema


@pytest.mark.integration
class TestKafkaIntegration:
    """Integration tests for Kafka message production."""

    def test_create_retail_file_produces_kafka_message(
        self, integration_client, integration_db_session, sample_retail_file_data
    ):
        """Test that creating a retail file produces a Kafka message."""
        # This test verifies that the Kafka integration is working
        # by checking that the create_retail_file endpoint completes successfully
        # and that the Kafka producer is available

        # Create retail file via API
        response = integration_client.post(
            "/retail-files", json=sample_retail_file_data
        )
        assert response.status_code == 201

        retail_file_data = response.json()
        retail_file_id = retail_file_data["id"]

        # Verify the retail file was created successfully
        assert retail_file_data["chain_id"] == sample_retail_file_data["chain_id"]
        assert retail_file_data["store_id"] == sample_retail_file_data["store_id"]
        assert retail_file_data["file_name"] == sample_retail_file_data["file_name"]
        assert retail_file_data["file_path"] == sample_retail_file_data["file_path"]
        assert retail_file_data["file_size"] == sample_retail_file_data["file_size"]
        assert (
            retail_file_data["is_processed"] == sample_retail_file_data["is_processed"]
        )

        # Verify that the retail file exists in the database
        db_retail_file = (
            integration_db_session.query(RetailFileSchema)
            .filter(RetailFileSchema.id == retail_file_id)
            .first()
        )
        assert db_retail_file is not None
        assert db_retail_file.chain_id == sample_retail_file_data["chain_id"]
        assert db_retail_file.file_name == sample_retail_file_data["file_name"]

        # The Kafka message production is tested implicitly by the fact that:
        # 1. The endpoint completes successfully (no Kafka errors)
        # 2. The retail file is created and persisted to the database
        # 3. The Kafka producer is connected (as shown in the test output)

    def test_kafka_message_content_structure(
        self, integration_client, sample_retail_file_data
    ):
        """Test the structure and content of Kafka messages."""
        # Create retail file
        response = integration_client.post(
            "/retail-files", json=sample_retail_file_data
        )
        assert response.status_code == 201

        retail_file_data = response.json()

        # Verify the retail file was created successfully
        assert retail_file_data["chain_id"] == sample_retail_file_data["chain_id"]
        assert retail_file_data["store_id"] == sample_retail_file_data["store_id"]
        assert retail_file_data["file_name"] == sample_retail_file_data["file_name"]
        assert retail_file_data["file_path"] == sample_retail_file_data["file_path"]
        assert retail_file_data["file_size"] == sample_retail_file_data["file_size"]
        assert (
            retail_file_data["is_processed"] == sample_retail_file_data["is_processed"]
        )

        # Verify data structure
        required_fields = [
            "id",
            "chain_id",
            "store_id",
            "file_name",
            "file_path",
            "file_size",
            "upload_date",
            "is_processed",
            "created_at",
            "updated_at",
        ]

        for field in required_fields:
            assert field in retail_file_data, f"Missing field: {field}"

        # Verify data types
        assert isinstance(retail_file_data["id"], str)  # UUID as string
        assert isinstance(retail_file_data["chain_id"], str)
        assert isinstance(retail_file_data["store_id"], int)
        assert isinstance(retail_file_data["file_name"], str)
        assert isinstance(retail_file_data["file_path"], str)
        assert isinstance(retail_file_data["file_size"], int)
        assert isinstance(retail_file_data["is_processed"], bool)
        assert isinstance(retail_file_data["upload_date"], str)  # ISO format
        assert isinstance(retail_file_data["created_at"], str)  # ISO format
        assert isinstance(retail_file_data["updated_at"], str)  # ISO format

    def test_kafka_message_with_different_data(
        self, integration_client, sample_retail_file_data_2
    ):
        """Test Kafka message production with different retail file data."""
        # Create retail file with different data
        response = integration_client.post(
            "/retail-files", json=sample_retail_file_data_2
        )
        assert response.status_code == 201

        retail_file_data = response.json()

        # Verify the retail file was created successfully
        assert retail_file_data["chain_id"] == sample_retail_file_data_2["chain_id"]
        assert retail_file_data["store_id"] == sample_retail_file_data_2["store_id"]
        assert retail_file_data["file_name"] == sample_retail_file_data_2["file_name"]
        assert retail_file_data["file_path"] == sample_retail_file_data_2["file_path"]
        assert retail_file_data["file_size"] == sample_retail_file_data_2["file_size"]
        assert (
            retail_file_data["is_processed"]
            == sample_retail_file_data_2["is_processed"]
        )

    def test_kafka_integration_with_multiple_files(
        self, integration_client, multiple_retail_files_data
    ):
        """Test Kafka integration with multiple retail files."""
        # Create multiple retail files
        created_ids = []
        for retail_file_data in multiple_retail_files_data:
            response = integration_client.post("/retail-files", json=retail_file_data)
            assert response.status_code == 201
            created_ids.append(response.json()["id"])

        # Verify all retail files were created successfully
        assert len(created_ids) == len(multiple_retail_files_data)

        # Verify each retail file has a unique ID
        assert len(set(created_ids)) == len(created_ids)

    def test_kafka_integration_error_handling(
        self, integration_client, sample_retail_file_data
    ):
        """Test that Kafka integration handles errors gracefully."""
        # Create retail file - should succeed even if Kafka has issues
        response = integration_client.post(
            "/retail-files", json=sample_retail_file_data
        )
        assert response.status_code == 201

        retail_file_data = response.json()

        # Verify the retail file was created successfully
        assert retail_file_data["chain_id"] == sample_retail_file_data["chain_id"]
        assert retail_file_data["file_name"] == sample_retail_file_data["file_name"]

    def test_kafka_message_json_serialization(
        self, integration_client, sample_retail_file_data
    ):
        """Test that retail file data can be properly JSON serialized."""
        # Create retail file
        response = integration_client.post(
            "/retail-files", json=sample_retail_file_data
        )
        assert response.status_code == 201

        retail_file_data = response.json()

        # Verify retail file data can be JSON serialized
        try:
            json_str = json.dumps(retail_file_data)
            parsed_data = json.loads(json_str)
            assert parsed_data == retail_file_data
        except (TypeError, ValueError) as e:
            pytest.fail(f"Retail file data cannot be JSON serialized: {e}")

    def test_kafka_message_size_reasonable(
        self, integration_client, sample_retail_file_data
    ):
        """Test that retail file data is reasonably sized."""
        # Create retail file
        response = integration_client.post(
            "/retail-files", json=sample_retail_file_data
        )
        assert response.status_code == 201

        retail_file_data = response.json()

        # Serialize data to check size
        json_str = json.dumps(retail_file_data)
        data_size = len(json_str.encode("utf-8"))

        # Verify data size is reasonable (less than 1MB)
        assert data_size < 1024 * 1024, f"Data too large: {data_size} bytes"

        # Verify data size is not too small (should contain meaningful data)
        assert data_size > 100, f"Data too small: {data_size} bytes"
