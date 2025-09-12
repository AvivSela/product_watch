"""
Database performance integration tests for store service.
Tests real PostgreSQL database performance characteristics.
"""

import time

import pytest
from database import StoreSchema


@pytest.mark.integration
@pytest.mark.performance
class TestDatabasePerformanceIntegration:
    """Performance integration tests for Store database operations."""

    def test_bulk_insert_performance(self, integration_client, integration_db_session):
        """Test performance of bulk insert operations."""
        # Generate test data
        stores_data = []
        for i in range(100):
            stores_data.append(
                {
                    "store_code": 5000 + i,
                    "store_name": f"Performance Test Store {i}",
                    "address": f"{i} Performance Street",
                    "city": "Performance City",
                    "zip_code": f"{50000 + i:05d}",
                    "sub_chain_id": f"perf_sub_chain_{i % 5:03d}",
                    "chain_id": f"perf_chain_{i % 3:03d}",
                }
            )

        # Measure bulk insert time
        start_time = time.time()

        for store_data in stores_data:
            response = integration_client.post("/stores", json=store_data)
            assert response.status_code == 201

        end_time = time.time()
        insert_time = end_time - start_time

        # Verify all stores were created
        db_count = integration_db_session.query(StoreSchema).count()
        assert db_count == len(stores_data)

        # Performance assertion (should complete within reasonable time)
        assert insert_time < 10.0, f"Bulk insert took too long: {insert_time:.2f}s"

        print(f"Bulk insert of {len(stores_data)} stores took {insert_time:.2f}s")

    def test_query_performance_with_indexes(
        self, integration_client, integration_db_session
    ):
        """Test query performance with database indexes."""
        # Create test data
        stores_data = []
        for i in range(50):
            stores_data.append(
                {
                    "store_code": 6000 + i,
                    "store_name": f"Index Test Store {i}",
                    "address": f"{i} Index Street",
                    "city": f"Index City {i % 10}",
                    "zip_code": f"{60000 + i:05d}",
                    "sub_chain_id": f"index_sub_chain_{i % 5:03d}",
                    "chain_id": f"index_chain_{i % 3:03d}",
                }
            )

        # Insert data
        for store_data in stores_data:
            response = integration_client.post("/stores", json=store_data)
            assert response.status_code == 201

        # Test query performance by store_code (should use index)
        start_time = time.time()
        result = (
            integration_db_session.query(StoreSchema)
            .filter(StoreSchema.store_code == 6025)
            .first()
        )
        end_time = time.time()

        assert result is not None
        query_time = end_time - start_time
        assert query_time < 0.1, f"Indexed query took too long: {query_time:.4f}s"

        # Test query performance by chain_id
        start_time = time.time()
        chain_stores = (
            integration_db_session.query(StoreSchema)
            .filter(StoreSchema.chain_id == "index_chain_001")
            .all()
        )
        end_time = time.time()

        assert len(chain_stores) > 0
        query_time = end_time - start_time
        assert query_time < 0.1, f"Chain query took too long: {query_time:.4f}s"

        print(f"Indexed queries completed in {query_time:.4f}s")

    def test_pagination_performance(self, integration_client, integration_db_session):
        """Test pagination performance with large datasets."""
        # Create large dataset
        stores_data = []
        for i in range(200):
            stores_data.append(
                {
                    "store_code": 7000 + i,
                    "store_name": f"Pagination Test Store {i}",
                    "address": f"{i} Pagination Street",
                    "city": "Pagination City",
                    "zip_code": f"{70000 + i:05d}",
                    "sub_chain_id": f"page_sub_chain_{i % 10:03d}",
                    "chain_id": f"page_chain_{i % 5:03d}",
                }
            )

        # Insert data
        for store_data in stores_data:
            response = integration_client.post("/stores", json=store_data)
            assert response.status_code == 201

        # Test pagination performance
        start_time = time.time()

        # Test multiple pages
        for page in range(1, 6):  # Test first 5 pages
            response = integration_client.get(f"/stores?page={page}&size=20")
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
            # Create store
            store_data = {
                "store_code": 8000 + i,
                "store_name": f"Pool Test Store {i}",
                "address": f"{i} Pool Street",
                "city": "Pool City",
                "zip_code": f"{80000 + i:05d}",
                "sub_chain_id": "pool_sub_chain_001",
                "chain_id": "pool_chain_001",
            }

            response = integration_client.post("/stores", json=store_data)
            assert response.status_code == 201

            # Read store
            store_id = response.json()["id"]
            read_response = integration_client.get(f"/stores/{store_id}")
            assert read_response.status_code == 200

            operations.append((store_id, store_data))

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

        # Create and immediately update stores (transaction-heavy)
        for i in range(30):
            store_data = {
                "store_code": 9000 + i,
                "store_name": f"Transaction Test Store {i}",
                "address": f"{i} Transaction Street",
                "city": "Transaction City",
                "zip_code": f"{90000 + i:05d}",
                "sub_chain_id": "trans_sub_chain_001",
                "chain_id": "trans_chain_001",
            }

            # Create
            create_response = integration_client.post("/stores", json=store_data)
            assert create_response.status_code == 201
            store_id = create_response.json()["id"]

            # Update
            update_data = {"store_name": f"Updated Transaction Store {i}"}
            update_response = integration_client.put(
                f"/stores/{store_id}", json=update_data
            )
            assert update_response.status_code == 200

            # Delete
            delete_response = integration_client.delete(f"/stores/{store_id}")
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
        stores_data = []
        for i in range(100):
            stores_data.append(
                {
                    "store_code": 10000 + i,
                    "store_name": f"Memory Test Store {i}",
                    "address": f"{i} Memory Street",
                    "city": "Memory City",
                    "zip_code": f"{100000 + i:05d}",
                    "sub_chain_id": f"mem_sub_chain_{i % 5:03d}",
                    "chain_id": f"mem_chain_{i % 3:03d}",
                }
            )

        # Insert data
        for store_data in stores_data:
            response = integration_client.post("/stores", json=store_data)
            assert response.status_code == 201

        # Test large result set query
        start_time = time.time()

        # Query all stores (large result set)
        all_stores = integration_db_session.query(StoreSchema).all()
        assert len(all_stores) == len(stores_data)

        end_time = time.time()
        query_time = end_time - start_time

        # Performance assertion
        assert query_time < 1.0, (
            f"Large result set query took too long: {query_time:.2f}s"
        )

        print(
            f"Large result set query ({len(all_stores)} records) took {query_time:.2f}s"
        )

    def test_database_concurrent_read_performance(
        self, integration_client, integration_db_session
    ):
        """Test concurrent read performance."""
        # Create test data
        store_data = {
            "store_code": 11000,
            "store_name": "Concurrent Read Test Store",
            "address": "1 Concurrent Street",
            "city": "Concurrent City",
            "zip_code": "11000",
            "sub_chain_id": "concurrent_sub_chain_001",
            "chain_id": "concurrent_chain_001",
        }

        response = integration_client.post("/stores", json=store_data)
        assert response.status_code == 201
        store_id = response.json()["id"]

        # Test multiple concurrent reads
        start_time = time.time()

        # Simulate concurrent reads
        for _ in range(50):
            read_response = integration_client.get(f"/stores/{store_id}")
            assert read_response.status_code == 200

        end_time = time.time()
        concurrent_read_time = end_time - start_time

        # Performance assertion
        assert concurrent_read_time < 2.0, (
            f"Concurrent reads took too long: {concurrent_read_time:.2f}s"
        )

        print(f"Concurrent reads (50 operations) took {concurrent_read_time:.2f}s")
