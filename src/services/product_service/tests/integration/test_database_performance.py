"""
Simplified database performance integration tests for product service.
Tests critical PostgreSQL database performance characteristics.
"""

import time

import pytest
from database import ProductSchema


@pytest.mark.integration
@pytest.mark.performance
class TestDatabasePerformanceIntegration:
    """Simplified performance integration tests for Product database operations."""

    def test_bulk_insert_performance(self, integration_client, integration_db_session):
        """Test performance of bulk insert operations."""
        # Generate test data
        products_data = []
        for i in range(100):
            products_data.append(
                {
                    "chain_id": f"perf_chain_{i % 5:03d}",
                    "store_id": 5000 + i,
                    "item_code": f"PERF_ITEM_{i:03d}",
                    "item_name": f"Performance Test Product {i}",
                    "manufacturer_item_description": f"Performance test product {i} description",
                    "manufacturer_name": f"Performance Manufacturer {i % 10}",
                    "manufacture_country": f"Performance Country {i % 3}",
                    "unit_qty": f"{i % 5 + 1} pieces",
                    "quantity": f"{i % 10 + 1}.0",
                    "qty_in_package": f"{i % 3 + 1}.0",
                }
            )

        # Measure bulk insert time
        start_time = time.time()

        for product_data in products_data:
            response = integration_client.post("/products", json=product_data)
            assert response.status_code == 201

        end_time = time.time()
        insert_time = end_time - start_time

        # Verify all products were created
        db_count = integration_db_session.query(ProductSchema).count()
        assert db_count == len(products_data)

        # Performance assertion (should complete within reasonable time)
        assert insert_time < 15.0, f"Bulk insert took too long: {insert_time:.2f}s"

        print(f"Bulk insert of {len(products_data)} products took {insert_time:.2f}s")

    def test_query_performance_with_indexes(
        self, integration_client, integration_db_session
    ):
        """Test query performance with database indexes."""
        # Create test data
        products_data = []
        for i in range(50):
            products_data.append(
                {
                    "chain_id": f"index_chain_{i % 3:03d}",
                    "store_id": 6000 + i,
                    "item_code": f"INDEX_ITEM_{i:03d}",
                    "item_name": f"Index Test Product {i}",
                    "manufacturer_item_description": f"Index test product {i} description",
                    "manufacturer_name": f"Index Manufacturer {i % 10}",
                    "manufacture_country": f"Index Country {i % 5}",
                    "unit_qty": f"{i % 5 + 1} pieces",
                    "quantity": f"{i % 10 + 1}.0",
                    "qty_in_package": f"{i % 3 + 1}.0",
                }
            )

        # Insert data
        for product_data in products_data:
            response = integration_client.post("/products", json=product_data)
            assert response.status_code == 201

        # Test query performance by store_id (should use index)
        start_time = time.time()
        result = (
            integration_db_session.query(ProductSchema)
            .filter(ProductSchema.store_id == 6025)
            .first()
        )
        end_time = time.time()

        assert result is not None
        query_time = end_time - start_time
        assert query_time < 0.1, f"Indexed query took too long: {query_time:.4f}s"

        # Test query performance by chain_id
        start_time = time.time()
        chain_products = (
            integration_db_session.query(ProductSchema)
            .filter(ProductSchema.chain_id == "index_chain_001")
            .all()
        )
        end_time = time.time()

        assert len(chain_products) > 0
        query_time = end_time - start_time
        assert query_time < 0.1, f"Chain query took too long: {query_time:.4f}s"

        print(f"Indexed queries completed in {query_time:.4f}s")

    def test_pagination_performance(self, integration_client, integration_db_session):
        """Test pagination performance with large datasets."""
        # Create large dataset
        products_data = []
        for i in range(200):
            products_data.append(
                {
                    "chain_id": f"page_chain_{i % 5:03d}",
                    "store_id": 7000 + i,
                    "item_code": f"PAGE_ITEM_{i:03d}",
                    "item_name": f"Pagination Test Product {i}",
                    "manufacturer_item_description": f"Pagination test product {i} description",
                    "manufacturer_name": f"Pagination Manufacturer {i % 10}",
                    "manufacture_country": f"Pagination Country {i % 3}",
                    "unit_qty": f"{i % 5 + 1} pieces",
                    "quantity": f"{i % 10 + 1}.0",
                    "qty_in_package": f"{i % 3 + 1}.0",
                }
            )

        # Insert data
        for product_data in products_data:
            response = integration_client.post("/products", json=product_data)
            assert response.status_code == 201

        # Test pagination performance
        start_time = time.time()

        # Test multiple pages
        for page in range(1, 6):  # Test first 5 pages
            response = integration_client.get(f"/products?page={page}&size=20")
            assert response.status_code == 200

            data = response.json()
            assert len(data["items"]) <= 20
            assert data["page"] == page

        end_time = time.time()
        pagination_time = end_time - start_time

        # Performance assertion
        assert pagination_time < 3.0, (
            f"Pagination took too long: {pagination_time:.2f}s"
        )

        print(f"Pagination of 5 pages took {pagination_time:.2f}s")
