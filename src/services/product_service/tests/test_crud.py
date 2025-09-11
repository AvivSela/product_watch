"""
CRUD unit tests for product service.
"""

from fastapi import status


class TestProductCRUD:
    """Test class for Product CRUD operations."""

    def test_create_product_success(self, client, sample_product_data):
        """Test successful product creation."""
        response = client.post("/products", json=sample_product_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        # Check that all fields are present and correct
        assert data["chain_id"] == sample_product_data["chain_id"]
        assert data["store_id"] == sample_product_data["store_id"]
        assert data["item_code"] == sample_product_data["item_code"]
        assert data["item_name"] == sample_product_data["item_name"]
        assert (
            data["manufacturer_item_description"]
            == sample_product_data["manufacturer_item_description"]
        )
        assert data["manufacturer_name"] == sample_product_data["manufacturer_name"]
        assert data["manufacture_country"] == sample_product_data["manufacture_country"]
        assert data["unit_qty"] == sample_product_data["unit_qty"]
        assert float(data["quantity"]) == sample_product_data["quantity"]
        assert float(data["qty_in_package"]) == sample_product_data["qty_in_package"]

        # Check that auto-generated fields are present
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_product_duplicate_fails(self, client, sample_product_data):
        """Test that creating duplicate products fails."""
        # Create first product
        response1 = client.post("/products", json=sample_product_data)
        assert response1.status_code == status.HTTP_201_CREATED

        # Try to create duplicate (same chain_id, store_id, item_code)
        response2 = client.post("/products", json=sample_product_data)
        assert response2.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in response2.json()["detail"]

    def test_create_product_different_store_succeeds(
        self, client, sample_product_data, sample_product_data_2
    ):
        """Test that same item_code in different store succeeds."""
        # Create first product
        response1 = client.post("/products", json=sample_product_data)
        assert response1.status_code == status.HTTP_201_CREATED

        # Create product with same item_code but different store_id
        sample_product_data_2["item_code"] = sample_product_data[
            "item_code"
        ]  # Same item_code
        response2 = client.post("/products", json=sample_product_data_2)
        assert response2.status_code == status.HTTP_201_CREATED

    def test_create_product_validation_errors(self, client):
        """Test product creation with validation errors."""
        # Test missing required fields
        invalid_data = {
            "chain_id": "test_chain",
            "store_id": 1,
            # Missing item_code
            "item_name": "Test Product",
        }

        response = client.post("/products", json=invalid_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_product_negative_values_fail(self, client):
        """Test that negative values for quantity and qty_in_package fail."""
        invalid_data = {
            "chain_id": "test_chain",
            "store_id": 1,
            "item_code": "TEST_ITEM",
            "item_name": "Test Product",
            "manufacturer_item_description": "Test description",
            "manufacturer_name": "Test Manufacturer",
            "manufacture_country": "USA",
            "unit_qty": "1 piece",
            "quantity": -1.0,  # Negative quantity
            "qty_in_package": 1.0,
        }

        response = client.post("/products", json=invalid_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_product_success(self, client, sample_product_data):
        """Test successful product retrieval."""
        # Create product first
        create_response = client.post("/products", json=sample_product_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        product_id = create_response.json()["id"]

        # Get product
        response = client.get(f"/products/{product_id}")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["id"] == product_id
        assert data["item_name"] == sample_product_data["item_name"]

    def test_get_product_not_found(self, client):
        """Test getting non-existent product returns 404."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.get(f"/products/{fake_id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_products_pagination(
        self, client, sample_product_data, sample_product_data_2
    ):
        """Test product listing with pagination."""
        # Create two products
        client.post("/products", json=sample_product_data)
        client.post("/products", json=sample_product_data_2)

        # Test pagination
        response = client.get("/products?page=1&size=1")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["page"] == 1
        assert data["size"] == 1
        assert data["total"] == 2
        assert data["pages"] == 2
        assert len(data["items"]) == 1

    def test_get_products_empty_list(self, client):
        """Test getting products when none exist."""
        response = client.get("/products")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []
        assert data["page"] == 1
        assert data["size"] == 10
        assert data["pages"] == 0

    def test_update_product_success(self, client, sample_product_data):
        """Test successful product update."""
        # Create product first
        create_response = client.post("/products", json=sample_product_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        product_id = create_response.json()["id"]

        # Update product
        update_data = {
            "item_name": "Updated Product Name",
            "quantity": 15.0,
        }

        response = client.put(f"/products/{product_id}", json=update_data)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["item_name"] == "Updated Product Name"
        assert float(data["quantity"]) == 15.0
        # Other fields should remain unchanged
        assert data["chain_id"] == sample_product_data["chain_id"]
        assert data["store_id"] == sample_product_data["store_id"]

    def test_update_product_not_found(self, client):
        """Test updating non-existent product returns 404."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        update_data = {"item_name": "Updated Name"}

        response = client.put(f"/products/{fake_id}", json=update_data)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_product_duplicate_constraint(
        self, client, sample_product_data, sample_product_data_2
    ):
        """Test that updating to create duplicate constraint fails."""
        # Create two products
        response1 = client.post("/products", json=sample_product_data)
        response2 = client.post("/products", json=sample_product_data_2)

        product2_id = response2.json()["id"]

        # Try to update product2 to have same chain_id, store_id, item_code as product1
        update_data = {
            "chain_id": sample_product_data["chain_id"],
            "store_id": sample_product_data["store_id"],
            "item_code": sample_product_data["item_code"],
        }

        response = client.put(f"/products/{product2_id}", json=update_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in response.json()["detail"]

    def test_delete_product_success(self, client, sample_product_data):
        """Test successful product deletion."""
        # Create product first
        create_response = client.post("/products", json=sample_product_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        product_id = create_response.json()["id"]

        # Delete product
        response = client.delete(f"/products/{product_id}")
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify product is deleted
        get_response = client.get(f"/products/{product_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_product_not_found(self, client):
        """Test deleting non-existent product returns 404."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.delete(f"/products/{fake_id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_complete_crud_workflow(self, client, sample_product_data):
        """Test complete CRUD workflow."""
        # Create
        create_response = client.post("/products", json=sample_product_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        product_id = create_response.json()["id"]

        # Read
        get_response = client.get(f"/products/{product_id}")
        assert get_response.status_code == status.HTTP_200_OK
        assert get_response.json()["item_name"] == sample_product_data["item_name"]

        # Update
        update_data = {"item_name": "Updated Name", "quantity": 20.0}
        update_response = client.put(f"/products/{product_id}", json=update_data)
        assert update_response.status_code == status.HTTP_200_OK
        assert update_response.json()["item_name"] == "Updated Name"

        # Verify update
        get_response = client.get(f"/products/{product_id}")
        assert get_response.json()["item_name"] == "Updated Name"
        assert float(get_response.json()["quantity"]) == 20.0

        # Delete
        delete_response = client.delete(f"/products/{product_id}")
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT

        # Verify deletion
        get_response = client.get(f"/products/{product_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
