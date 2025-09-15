"""
Simplified database performance integration tests for store service.
Tests critical PostgreSQL database performance characteristics.
"""

import time

import pytest

from ...database import StoreSchema


@pytest.mark.integration
@pytest.mark.performance
class TestDatabasePerformanceIntegration:
    """Simplified performance integration tests for Store database operations."""

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
