"""
Simplified database performance integration tests for retail file service.
Tests critical PostgreSQL database performance characteristics.
"""

import time
from datetime import datetime, timezone

import pytest

from ...database import RetailFileSchema


@pytest.mark.integration
@pytest.mark.performance
class TestDatabasePerformanceIntegration:
    """Simplified performance integration tests for RetailFile database operations."""

    def test_bulk_insert_performance(self, integration_client, integration_db_session):
        """Test performance of bulk insert operations."""
        # Generate test data
        retail_files_data = []
        for i in range(100):
            retail_files_data.append(
                {
                    "chain_id": f"perf_chain_{i % 5:03d}",
                    "store_id": 5000 + i,
                    "file_name": f"performance_test_file_{i}.csv",
                    "file_path": f"/data/performance/performance_test_file_{i}.csv",
                    "file_size": 1024 + i,
                    "upload_date": datetime.now(timezone.utc).isoformat(),
                    "is_processed": i % 2 == 0,
                }
            )

        # Measure bulk insert time
        start_time = time.time()

        for retail_file_data in retail_files_data:
            response = integration_client.post("/retail-files", json=retail_file_data)
            assert response.status_code == 201

        end_time = time.time()
        insert_time = end_time - start_time

        # Verify all retail files were created
        db_count = integration_db_session.query(RetailFileSchema).count()
        assert db_count == len(retail_files_data)

        # Performance assertion (should complete within reasonable time)
        assert insert_time < 10.0, f"Bulk insert took too long: {insert_time:.2f}s"

        print(
            f"Bulk insert of {len(retail_files_data)} retail files took {insert_time:.2f}s"
        )

    def test_query_performance_with_indexes(
        self, integration_client, integration_db_session
    ):
        """Test query performance with database indexes."""
        # Create test data
        retail_files_data = []
        for i in range(50):
            retail_files_data.append(
                {
                    "chain_id": f"index_chain_{i % 3:03d}",
                    "store_id": 6000 + i,
                    "file_name": f"index_test_file_{i}.csv",
                    "file_path": f"/data/index/index_test_file_{i}.csv",
                    "file_size": 1024 + i,
                    "upload_date": datetime.now(timezone.utc).isoformat(),
                    "is_processed": i % 2 == 0,
                }
            )

        # Insert data
        for retail_file_data in retail_files_data:
            response = integration_client.post("/retail-files", json=retail_file_data)
            assert response.status_code == 201

        # Test query performance by store_id (should use index)
        start_time = time.time()
        result = (
            integration_db_session.query(RetailFileSchema)
            .filter(RetailFileSchema.store_id == 6025)
            .first()
        )
        end_time = time.time()

        assert result is not None
        query_time = end_time - start_time
        assert query_time < 0.1, f"Indexed query took too long: {query_time:.4f}s"

        # Test query performance by chain_id
        start_time = time.time()
        chain_retail_files = (
            integration_db_session.query(RetailFileSchema)
            .filter(RetailFileSchema.chain_id == "index_chain_001")
            .all()
        )
        end_time = time.time()

        assert len(chain_retail_files) > 0
        query_time = end_time - start_time
        assert query_time < 0.1, f"Chain query took too long: {query_time:.4f}s"

        print(f"Indexed queries completed in {query_time:.4f}s")

    def test_pagination_performance(self, integration_client, integration_db_session):
        """Test pagination performance with large datasets."""
        # Create large dataset
        retail_files_data = []
        for i in range(200):
            retail_files_data.append(
                {
                    "chain_id": f"page_chain_{i % 5:03d}",
                    "store_id": 7000 + i,
                    "file_name": f"pagination_test_file_{i}.csv",
                    "file_path": f"/data/pagination/pagination_test_file_{i}.csv",
                    "file_size": 1024 + i,
                    "upload_date": datetime.now(timezone.utc).isoformat(),
                    "is_processed": i % 2 == 0,
                }
            )

        # Insert data
        for retail_file_data in retail_files_data:
            response = integration_client.post("/retail-files", json=retail_file_data)
            assert response.status_code == 201

        # Test pagination performance
        start_time = time.time()

        # Test multiple pages
        for page in range(1, 6):  # Test first 5 pages
            response = integration_client.get(f"/retail-files?page={page}&size=20")
            assert response.status_code == 200

            data = response.json()
            assert len(data["items"]) <= 20
            assert data["page"] == page

        end_time = time.time()
        pagination_time = end_time - start_time

        # Performance assertion
        assert pagination_time < 2.0, (
            f"Pagination took too long: {pagination_time:.2f}s"
        )

        print(f"Pagination of 5 pages took {pagination_time:.2f}s")
