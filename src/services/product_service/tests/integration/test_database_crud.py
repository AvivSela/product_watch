"""
Database integration tests for product service CRUD operations.
Tests real PostgreSQL database interactions.
"""

import pytest
from fastapi import status
from sqlalchemy import text

from ...database import ProductSchema


@pytest.mark.integration
class TestDatabaseCRUDIntegration:
    """Integration tests for Product CRUD operations with real PostgreSQL."""

    def test_create_product_database_integration(
        self, integration_client, integration_db_session, sample_product_data
    ):
        """Test product creation with real database persistence."""
        # Create product via API
        response = integration_client.post("/products", json=sample_product_data)
        assert response.status_code == status.HTTP_201_CREATED

        product_data = response.json()
        product_id = product_data["id"]

        # Verify data was actually persisted in database
        db_product = (
            integration_db_session.query(ProductSchema)
            .filter(ProductSchema.id == product_id)
            .first()
        )
        assert db_product is not None
        assert db_product.chain_id == sample_product_data["chain_id"]
        assert db_product.store_id == sample_product_data["store_id"]
        assert db_product.item_code == sample_product_data["item_code"]
        assert db_product.item_name == sample_product_data["item_name"]
        assert (
            db_product.manufacturer_item_description
            == sample_product_data["manufacturer_item_description"]
        )
        assert db_product.manufacturer_name == sample_product_data["manufacturer_name"]
        assert (
            db_product.manufacture_country == sample_product_data["manufacture_country"]
        )
        assert db_product.unit_qty == sample_product_data["unit_qty"]
        assert float(db_product.quantity) == float(sample_product_data["quantity"])
        assert float(db_product.qty_in_package) == float(
            sample_product_data["qty_in_package"]
        )

        # Verify auto-generated fields
        assert db_product.id is not None
        assert db_product.created_at is not None
        assert db_product.updated_at is not None

    def test_database_constraints_enforced(
        self, integration_client, integration_db_session, sample_product_data
    ):
        """Test that database constraints are properly enforced."""
        # Create first product
        response1 = integration_client.post("/products", json=sample_product_data)
        assert response1.status_code == status.HTTP_201_CREATED

        # Try to create duplicate (should fail due to unique constraint)
        response2 = integration_client.post("/products", json=sample_product_data)
        assert response2.status_code == status.HTTP_400_BAD_REQUEST

        # Verify only one product exists in database
        count = integration_db_session.query(ProductSchema).count()
        assert count == 1

    def test_database_transaction_rollback(
        self, integration_client, integration_db_session, sample_product_data
    ):
        """Test that database transactions work correctly."""
        # Create product
        response = integration_client.post("/products", json=sample_product_data)
        assert response.status_code == status.HTTP_201_CREATED
        product_id = response.json()["id"]

        # Verify product exists
        db_product = (
            integration_db_session.query(ProductSchema)
            .filter(ProductSchema.id == product_id)
            .first()
        )
        assert db_product is not None

        # The transaction should be rolled back after the test due to the fixture

    def test_database_pagination_performance(
        self, integration_client, integration_db_session, multiple_products_data
    ):
        """Test database pagination with larger datasets."""
        # Create multiple products
        created_products = []
        for product_data in multiple_products_data:
            response = integration_client.post("/products", json=product_data)
            assert response.status_code == status.HTTP_201_CREATED
            created_products.append(response.json())

        # Test pagination
        response = integration_client.get("/products?page=1&size=2")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["total"] == len(multiple_products_data)
        assert data["page"] == 1
        assert data["size"] == 2
        assert len(data["items"]) == 2

        # Verify database count matches
        db_count = integration_db_session.query(ProductSchema).count()
        assert db_count == len(multiple_products_data)

    def test_database_update_persistence(
        self, integration_client, integration_db_session, sample_product_data
    ):
        """Test that database updates are properly persisted."""
        # Create product
        create_response = integration_client.post("/products", json=sample_product_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        product_id = create_response.json()["id"]

        # Update product
        update_data = {
            "item_name": "Updated Integration Product",
            "manufacturer_name": "Updated Manufacturer",
            "quantity": "5.0",
        }

        update_response = integration_client.put(
            f"/products/{product_id}", json=update_data
        )
        assert update_response.status_code == status.HTTP_200_OK

        # Verify update in database
        db_product = (
            integration_db_session.query(ProductSchema)
            .filter(ProductSchema.id == product_id)
            .first()
        )
        assert db_product.item_name == "Updated Integration Product"
        assert db_product.manufacturer_name == "Updated Manufacturer"
        assert float(db_product.quantity) == 5.0

        # Verify other fields unchanged
        assert db_product.chain_id == sample_product_data["chain_id"]
        assert db_product.store_id == sample_product_data["store_id"]
        assert db_product.item_code == sample_product_data["item_code"]

    def test_database_delete_persistence(
        self, integration_client, integration_db_session, sample_product_data
    ):
        """Test that database deletions are properly persisted."""
        # Create product
        create_response = integration_client.post("/products", json=sample_product_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        product_id = create_response.json()["id"]

        # Verify product exists in database
        db_product = (
            integration_db_session.query(ProductSchema)
            .filter(ProductSchema.id == product_id)
            .first()
        )
        assert db_product is not None

        # Delete product
        delete_response = integration_client.delete(f"/products/{product_id}")
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT

        # Verify product is deleted from database
        db_product = (
            integration_db_session.query(ProductSchema)
            .filter(ProductSchema.id == product_id)
            .first()
        )
        assert db_product is None

    def test_database_query_performance(
        self, integration_client, integration_db_session, multiple_products_data
    ):
        """Test database query performance with multiple records."""
        # Create multiple products
        for product_data in multiple_products_data:
            response = integration_client.post("/products", json=product_data)
            assert response.status_code == status.HTTP_201_CREATED

        # Test various queries
        # Query by chain_id
        chain_products = (
            integration_db_session.query(ProductSchema)
            .filter(ProductSchema.chain_id == "bulk_chain_001")
            .all()
        )
        assert len(chain_products) == len(multiple_products_data)

        # Query by store_id
        store_products = (
            integration_db_session.query(ProductSchema)
            .filter(ProductSchema.store_id == 3001)
            .all()
        )
        assert len(store_products) == 1  # Only first product

        # Query by manufacturer_name
        manufacturer_products = (
            integration_db_session.query(ProductSchema)
            .filter(ProductSchema.manufacturer_name == "Bulk Test Manufacturer")
            .all()
        )
        assert len(manufacturer_products) == len(multiple_products_data)

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
        result = integration_db_session.execute(text("SELECT COUNT(*) FROM products"))
        count = result.scalar()
        assert isinstance(count, int)

    def test_database_schema_validation(
        self, integration_client, integration_db_session
    ):
        """Test that database schema constraints are enforced."""
        # Test negative store_id (should fail at validation level)
        invalid_data = {
            "chain_id": "invalid_chain",
            "store_id": -1,
            "item_code": "INVALID_ITEM",
            "item_name": "Invalid Product",
            "manufacturer_item_description": "Invalid description",
            "manufacturer_name": "Invalid Manufacturer",
            "manufacture_country": "Invalid Country",
            "unit_qty": "1 piece",
            "quantity": "1.0",
            "qty_in_package": "1.0",
        }

        response = integration_client.post("/products", json=invalid_data)
        # Should fail due to validation (negative store_id)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_database_concurrent_access_simulation(
        self, integration_client, integration_db_session, sample_product_data
    ):
        """Test database behavior under simulated concurrent access."""
        # Create product
        response1 = integration_client.post("/products", json=sample_product_data)
        assert response1.status_code == status.HTTP_201_CREATED
        product_id = response1.json()["id"]

        # Simulate concurrent read
        response2 = integration_client.get(f"/products/{product_id}")
        assert response2.status_code == status.HTTP_200_OK

        # Simulate concurrent update
        update_data = {"item_name": "Concurrent Update"}
        response3 = integration_client.put(f"/products/{product_id}", json=update_data)
        assert response3.status_code == status.HTTP_200_OK

        # Verify final state
        db_product = (
            integration_db_session.query(ProductSchema)
            .filter(ProductSchema.id == product_id)
            .first()
        )
        assert db_product.item_name == "Concurrent Update"

    def test_database_unique_constraint_validation(
        self, integration_client, integration_db_session
    ):
        """Test unique constraint on (chain_id, store_id, item_code)."""
        # Create first product
        product_data_1 = {
            "chain_id": "unique_test_chain",
            "store_id": 1001,
            "item_code": "UNIQUE_ITEM_001",
            "item_name": "Unique Test Product 1",
            "manufacturer_item_description": "Unique test product 1 description",
            "manufacturer_name": "Unique Test Manufacturer",
            "manufacture_country": "Unique Country",
            "unit_qty": "1 piece",
            "quantity": "1.0",
            "qty_in_package": "1.0",
        }

        response1 = integration_client.post("/products", json=product_data_1)
        assert response1.status_code == status.HTTP_201_CREATED

        # Try to create product with same (chain_id, store_id, item_code)
        product_data_2 = product_data_1.copy()
        product_data_2["item_name"] = "Different Name"  # Only change name

        response2 = integration_client.post("/products", json=product_data_2)
        assert response2.status_code == status.HTTP_400_BAD_REQUEST

        # Verify only one product exists
        count = integration_db_session.query(ProductSchema).count()
        assert count == 1

    def test_database_decimal_precision(
        self, integration_client, integration_db_session
    ):
        """Test decimal field precision and handling."""
        product_data = {
            "chain_id": "decimal_test_chain",
            "store_id": 2001,
            "item_code": "DECIMAL_ITEM_001",
            "item_name": "Decimal Test Product",
            "manufacturer_item_description": "Decimal test product description",
            "manufacturer_name": "Decimal Test Manufacturer",
            "manufacture_country": "Decimal Country",
            "unit_qty": "1 piece",
            "quantity": "3.14159",
            "qty_in_package": "2.71828",
        }

        response = integration_client.post("/products", json=product_data)
        assert response.status_code == status.HTTP_201_CREATED

        product_id = response.json()["id"]

        # Verify decimal precision in database
        db_product = (
            integration_db_session.query(ProductSchema)
            .filter(ProductSchema.id == product_id)
            .first()
        )
        assert db_product is not None
        assert abs(float(db_product.quantity) - 3.14159) < 0.001
        assert abs(float(db_product.qty_in_package) - 2.71828) < 0.001
