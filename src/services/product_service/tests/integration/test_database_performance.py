"""
Database performance integration tests for product service.
Tests real PostgreSQL database performance characteristics.
"""

import time

from database import ProductSchema


class TestDatabasePerformanceIntegration:
    """Performance integration tests for Product database operations."""

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

    def test_database_connection_pool_performance(
        self, integration_client, integration_db_session
    ):
        """Test database connection pool performance."""
        # Test multiple concurrent-like operations
        start_time = time.time()

        # Simulate multiple concurrent operations
        operations = []
        for i in range(20):
            # Create product
            product_data = {
                "chain_id": f"pool_chain_{i % 3:03d}",
                "store_id": 8000 + i,
                "item_code": f"POOL_ITEM_{i:03d}",
                "item_name": f"Pool Test Product {i}",
                "manufacturer_item_description": f"Pool test product {i} description",
                "manufacturer_name": f"Pool Manufacturer {i % 5}",
                "manufacture_country": f"Pool Country {i % 3}",
                "unit_qty": f"{i % 5 + 1} pieces",
                "quantity": f"{i % 10 + 1}.0",
                "qty_in_package": f"{i % 3 + 1}.0",
            }

            response = integration_client.post("/products", json=product_data)
            assert response.status_code == 201

            # Read product
            product_id = response.json()["id"]
            read_response = integration_client.get(f"/products/{product_id}")
            assert read_response.status_code == 200

            operations.append((product_id, product_data))

        end_time = time.time()
        operations_time = end_time - start_time

        # Performance assertion
        assert operations_time < 8.0, (
            f"Connection pool operations took too long: {operations_time:.2f}s"
        )

        print(f"Connection pool operations took {operations_time:.2f}s")

    def test_database_transaction_performance(
        self, integration_client, integration_db_session
    ):
        """Test database transaction performance."""
        # Test transaction-heavy operations
        start_time = time.time()

        # Create and immediately update products (transaction-heavy)
        for i in range(30):
            product_data = {
                "chain_id": f"trans_chain_{i % 3:03d}",
                "store_id": 9000 + i,
                "item_code": f"TRANS_ITEM_{i:03d}",
                "item_name": f"Transaction Test Product {i}",
                "manufacturer_item_description": f"Transaction test product {i} description",
                "manufacturer_name": f"Transaction Manufacturer {i % 5}",
                "manufacture_country": f"Transaction Country {i % 3}",
                "unit_qty": f"{i % 5 + 1} pieces",
                "quantity": f"{i % 10 + 1}.0",
                "qty_in_package": f"{i % 3 + 1}.0",
            }

            # Create
            create_response = integration_client.post("/products", json=product_data)
            assert create_response.status_code == 201
            product_id = create_response.json()["id"]

            # Update
            update_data = {"item_name": f"Updated Transaction Product {i}"}
            update_response = integration_client.put(
                f"/products/{product_id}", json=update_data
            )
            assert update_response.status_code == 200

            # Delete
            delete_response = integration_client.delete(f"/products/{product_id}")
            assert delete_response.status_code == 204

        end_time = time.time()
        transaction_time = end_time - start_time

        # Performance assertion
        assert transaction_time < 12.0, (
            f"Transaction operations took too long: {transaction_time:.2f}s"
        )

        print(f"Transaction operations took {transaction_time:.2f}s")

    def test_database_memory_usage(self, integration_client, integration_db_session):
        """Test database memory usage with large result sets."""
        # Create test data
        products_data = []
        for i in range(100):
            products_data.append(
                {
                    "chain_id": f"mem_chain_{i % 3:03d}",
                    "store_id": 10000 + i,
                    "item_code": f"MEM_ITEM_{i:03d}",
                    "item_name": f"Memory Test Product {i}",
                    "manufacturer_item_description": f"Memory test product {i} description",
                    "manufacturer_name": f"Memory Manufacturer {i % 10}",
                    "manufacture_country": f"Memory Country {i % 5}",
                    "unit_qty": f"{i % 5 + 1} pieces",
                    "quantity": f"{i % 10 + 1}.0",
                    "qty_in_package": f"{i % 3 + 1}.0",
                }
            )

        # Insert data
        for product_data in products_data:
            response = integration_client.post("/products", json=product_data)
            assert response.status_code == 201

        # Test large result set query
        start_time = time.time()

        # Query all products (large result set)
        all_products = integration_db_session.query(ProductSchema).all()
        assert len(all_products) == len(products_data)

        end_time = time.time()
        query_time = end_time - start_time

        # Performance assertion
        assert query_time < 1.5, (
            f"Large result set query took too long: {query_time:.2f}s"
        )

        print(
            f"Large result set query ({len(all_products)} records) took {query_time:.2f}s"
        )

    def test_database_concurrent_read_performance(
        self, integration_client, integration_db_session
    ):
        """Test concurrent read performance."""
        # Create test data
        product_data = {
            "chain_id": "concurrent_chain_001",
            "store_id": 11000,
            "item_code": "CONCURRENT_ITEM_001",
            "item_name": "Concurrent Read Test Product",
            "manufacturer_item_description": "Concurrent read test product description",
            "manufacturer_name": "Concurrent Manufacturer",
            "manufacture_country": "Concurrent Country",
            "unit_qty": "1 piece",
            "quantity": "1.0",
            "qty_in_package": "1.0",
        }

        response = integration_client.post("/products", json=product_data)
        assert response.status_code == 201
        product_id = response.json()["id"]

        # Test multiple concurrent reads
        start_time = time.time()

        # Simulate concurrent reads
        for _ in range(50):
            read_response = integration_client.get(f"/products/{product_id}")
            assert read_response.status_code == 200

        end_time = time.time()
        concurrent_read_time = end_time - start_time

        # Performance assertion
        assert concurrent_read_time < 3.0, (
            f"Concurrent reads took too long: {concurrent_read_time:.2f}s"
        )

        print(f"Concurrent reads (50 operations) took {concurrent_read_time:.2f}s")

    def test_database_decimal_operations_performance(
        self, integration_client, integration_db_session
    ):
        """Test performance of decimal field operations."""
        # Create products with various decimal values
        products_data = []
        for i in range(50):
            products_data.append(
                {
                    "chain_id": f"decimal_chain_{i % 3:03d}",
                    "store_id": 12000 + i,
                    "item_code": f"DECIMAL_ITEM_{i:03d}",
                    "item_name": f"Decimal Test Product {i}",
                    "manufacturer_item_description": f"Decimal test product {i} description",
                    "manufacturer_name": f"Decimal Manufacturer {i % 5}",
                    "manufacture_country": f"Decimal Country {i % 3}",
                    "unit_qty": f"{i % 5 + 1} pieces",
                    "quantity": f"{i * 0.1 + 1.0:.2f}",
                    "qty_in_package": f"{i * 0.05 + 0.5:.3f}",
                }
            )

        # Measure insert time for decimal operations
        start_time = time.time()

        for product_data in products_data:
            response = integration_client.post("/products", json=product_data)
            assert response.status_code == 201

        end_time = time.time()
        decimal_insert_time = end_time - start_time

        # Test decimal query performance
        start_time = time.time()
        decimal_products = (
            integration_db_session.query(ProductSchema)
            .filter(ProductSchema.quantity > 2.0)
            .all()
        )
        end_time = time.time()

        decimal_query_time = end_time - start_time

        # Performance assertions
        assert decimal_insert_time < 8.0, (
            f"Decimal insert operations took too long: {decimal_insert_time:.2f}s"
        )
        assert decimal_query_time < 0.2, (
            f"Decimal query took too long: {decimal_query_time:.4f}s"
        )

        print(
            f"Decimal operations - Insert: {decimal_insert_time:.2f}s, Query: {decimal_query_time:.4f}s"
        )

    def test_database_text_search_performance(
        self, integration_client, integration_db_session
    ):
        """Test performance of text search operations."""
        # Create products with various text content
        products_data = []
        for i in range(30):
            products_data.append(
                {
                    "chain_id": f"text_chain_{i % 2:03d}",
                    "store_id": 13000 + i,
                    "item_code": f"TEXT_ITEM_{i:03d}",
                    "item_name": f"Text Search Product {i} with long name",
                    "manufacturer_item_description": f"Very long description for text search product {i} with many words and details",
                    "manufacturer_name": f"Text Search Manufacturer {i % 5}",
                    "manufacture_country": f"Text Country {i % 3}",
                    "unit_qty": f"{i % 5 + 1} pieces",
                    "quantity": f"{i % 10 + 1}.0",
                    "qty_in_package": f"{i % 3 + 1}.0",
                }
            )

        # Insert data
        for product_data in products_data:
            response = integration_client.post("/products", json=product_data)
            assert response.status_code == 201

        # Test text search performance
        start_time = time.time()

        # Search by item name
        name_products = (
            integration_db_session.query(ProductSchema)
            .filter(ProductSchema.item_name.like("%Text Search%"))
            .all()
        )

        # Search by manufacturer
        manufacturer_products = (
            integration_db_session.query(ProductSchema)
            .filter(ProductSchema.manufacturer_name.like("%Manufacturer%"))
            .all()
        )

        # Search by description
        description_products = (
            integration_db_session.query(ProductSchema)
            .filter(
                ProductSchema.manufacturer_item_description.like("%long description%")
            )
            .all()
        )

        end_time = time.time()
        text_search_time = end_time - start_time

        # Performance assertion
        assert text_search_time < 0.5, (
            f"Text search operations took too long: {text_search_time:.4f}s"
        )

        # Verify results
        assert len(name_products) > 0
        assert len(manufacturer_products) > 0
        assert len(description_products) > 0

        print(f"Text search operations took {text_search_time:.4f}s")
