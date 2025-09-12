"""
Database performance integration tests for retail file service.
Tests real PostgreSQL database performance characteristics.
"""

import time
from datetime import datetime, timezone

import pytest
from database import RetailFileSchema


@pytest.mark.integration
@pytest.mark.performance
class TestDatabasePerformanceIntegration:
    """Performance integration tests for RetailFile database operations."""

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

    def test_database_connection_pool_performance(
        self, integration_client, integration_db_session
    ):
        """Test database connection pool performance."""
        # Test multiple concurrent-like operations
        start_time = time.time()

        # Simulate multiple concurrent operations
        operations = []
        for i in range(20):
            # Create retail file
            retail_file_data = {
                "chain_id": "pool_chain_001",
                "store_id": 8000 + i,
                "file_name": f"pool_test_file_{i}.csv",
                "file_path": f"/data/pool/pool_test_file_{i}.csv",
                "file_size": 1024 + i,
                "upload_date": datetime.now(timezone.utc).isoformat(),
                "is_processed": i % 2 == 0,
            }

            response = integration_client.post("/retail-files", json=retail_file_data)
            assert response.status_code == 201

            # Read retail file
            retail_file_id = response.json()["id"]
            read_response = integration_client.get(f"/retail-files/{retail_file_id}")
            assert read_response.status_code == 200

            operations.append((retail_file_id, retail_file_data))

        end_time = time.time()
        operations_time = end_time - start_time

        # Performance assertion
        assert operations_time < 5.0, (
            f"Connection pool operations took too long: {operations_time:.2f}s"
        )

        print(f"Connection pool operations took {operations_time:.2f}s")

    def test_database_transaction_performance(
        self, integration_client, integration_db_session
    ):
        """Test database transaction performance."""
        # Test transaction-heavy operations
        start_time = time.time()

        # Create and immediately update retail files (transaction-heavy)
        for i in range(30):
            retail_file_data = {
                "chain_id": "trans_chain_001",
                "store_id": 9000 + i,
                "file_name": f"transaction_test_file_{i}.csv",
                "file_path": f"/data/transaction/transaction_test_file_{i}.csv",
                "file_size": 1024 + i,
                "upload_date": datetime.now(timezone.utc).isoformat(),
                "is_processed": False,
            }

            # Create
            create_response = integration_client.post(
                "/retail-files", json=retail_file_data
            )
            assert create_response.status_code == 201
            retail_file_id = create_response.json()["id"]

            # Update
            update_data = {
                "file_name": f"updated_transaction_file_{i}.csv",
                "is_processed": True,
            }
            update_response = integration_client.put(
                f"/retail-files/{retail_file_id}", json=update_data
            )
            assert update_response.status_code == 200

            # Delete
            delete_response = integration_client.delete(
                f"/retail-files/{retail_file_id}"
            )
            assert delete_response.status_code == 204

        end_time = time.time()
        transaction_time = end_time - start_time

        # Performance assertion
        assert transaction_time < 8.0, (
            f"Transaction operations took too long: {transaction_time:.2f}s"
        )

        print(f"Transaction operations took {transaction_time:.2f}s")

    def test_database_memory_usage(self, integration_client, integration_db_session):
        """Test database memory usage with large result sets."""
        # Create test data
        retail_files_data = []
        for i in range(100):
            retail_files_data.append(
                {
                    "chain_id": f"mem_chain_{i % 3:03d}",
                    "store_id": 10000 + i,
                    "file_name": f"memory_test_file_{i}.csv",
                    "file_path": f"/data/memory/memory_test_file_{i}.csv",
                    "file_size": 1024 + i,
                    "upload_date": datetime.now(timezone.utc).isoformat(),
                    "is_processed": i % 2 == 0,
                }
            )

        # Insert data
        for retail_file_data in retail_files_data:
            response = integration_client.post("/retail-files", json=retail_file_data)
            assert response.status_code == 201

        # Test large result set query
        start_time = time.time()

        # Query all retail files (large result set)
        all_retail_files = integration_db_session.query(RetailFileSchema).all()
        assert len(all_retail_files) == len(retail_files_data)

        end_time = time.time()
        query_time = end_time - start_time

        # Performance assertion
        assert query_time < 1.0, (
            f"Large result set query took too long: {query_time:.2f}s"
        )

        print(
            f"Large result set query ({len(all_retail_files)} records) took {query_time:.2f}s"
        )

    def test_database_concurrent_read_performance(
        self, integration_client, integration_db_session
    ):
        """Test concurrent read performance."""
        # Create test data
        retail_file_data = {
            "chain_id": "concurrent_chain_001",
            "store_id": 11000,
            "file_name": "concurrent_read_test_file.csv",
            "file_path": "/data/concurrent/concurrent_read_test_file.csv",
            "file_size": 1024,
            "upload_date": datetime.now(timezone.utc).isoformat(),
            "is_processed": False,
        }

        response = integration_client.post("/retail-files", json=retail_file_data)
        assert response.status_code == 201
        retail_file_id = response.json()["id"]

        # Test multiple concurrent reads
        start_time = time.time()

        # Simulate concurrent reads
        for _ in range(50):
            read_response = integration_client.get(f"/retail-files/{retail_file_id}")
            assert read_response.status_code == 200

        end_time = time.time()
        concurrent_read_time = end_time - start_time

        # Performance assertion
        assert concurrent_read_time < 2.0, (
            f"Concurrent reads took too long: {concurrent_read_time:.2f}s"
        )

        print(f"Concurrent reads (50 operations) took {concurrent_read_time:.2f}s")

    def test_database_file_size_query_performance(
        self, integration_client, integration_db_session
    ):
        """Test query performance filtering by file size."""
        # Create test data with varying file sizes
        retail_files_data = []
        for i in range(50):
            retail_files_data.append(
                {
                    "chain_id": f"size_chain_{i % 2:03d}",
                    "store_id": 12000 + i,
                    "file_name": f"size_test_file_{i}.csv",
                    "file_path": f"/data/size/size_test_file_{i}.csv",
                    "file_size": 1000 + (i * 100),  # Varying sizes
                    "upload_date": datetime.now(timezone.utc).isoformat(),
                    "is_processed": i % 2 == 0,
                }
            )

        # Insert data
        for retail_file_data in retail_files_data:
            response = integration_client.post("/retail-files", json=retail_file_data)
            assert response.status_code == 201

        # Test query performance by file size range
        start_time = time.time()
        large_files = (
            integration_db_session.query(RetailFileSchema)
            .filter(RetailFileSchema.file_size > 3000)
            .all()
        )
        end_time = time.time()

        assert len(large_files) > 0
        query_time = end_time - start_time
        assert query_time < 0.1, f"File size query took too long: {query_time:.4f}s"

        print(f"File size query completed in {query_time:.4f}s")

    def test_database_processed_status_query_performance(
        self, integration_client, integration_db_session
    ):
        """Test query performance filtering by processed status."""
        # Create test data with varying processed status
        retail_files_data = []
        for i in range(50):
            retail_files_data.append(
                {
                    "chain_id": f"status_chain_{i % 2:03d}",
                    "store_id": 13000 + i,
                    "file_name": f"status_test_file_{i}.csv",
                    "file_path": f"/data/status/status_test_file_{i}.csv",
                    "file_size": 1024 + i,
                    "upload_date": datetime.now(timezone.utc).isoformat(),
                    "is_processed": i % 3 == 0,  # Every third file is processed
                }
            )

        # Insert data
        for retail_file_data in retail_files_data:
            response = integration_client.post("/retail-files", json=retail_file_data)
            assert response.status_code == 201

        # Test query performance by processed status
        start_time = time.time()
        processed_files = (
            integration_db_session.query(RetailFileSchema)
            .filter(RetailFileSchema.is_processed == True)
            .all()
        )
        end_time = time.time()

        assert len(processed_files) > 0
        query_time = end_time - start_time
        assert query_time < 0.1, (
            f"Processed status query took too long: {query_time:.4f}s"
        )

        print(f"Processed status query completed in {query_time:.4f}s")
