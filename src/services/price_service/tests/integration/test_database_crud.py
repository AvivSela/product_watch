"""
Database CRUD integration tests for price service.
Tests real PostgreSQL database CRUD operations.
"""

from fastapi import status


class TestDatabaseCRUDIntegration:
    """Database CRUD integration tests for Price."""

    def test_create_price_integration(self, integration_client, sample_price_data):
        """Test creating price with real database."""
        response = integration_client.post("/prices", json=sample_price_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        # Verify all fields are correctly stored
        assert data["chain_id"] == sample_price_data["chain_id"]
        assert data["store_id"] == sample_price_data["store_id"]
        assert data["item_code"] == sample_price_data["item_code"]
        assert float(data["price_amount"]) == sample_price_data["price_amount"]
        assert data["currency_code"] == sample_price_data["currency_code"]
        # Note: datetime format may be normalized by the database
        assert data["price_update_date"] is not None

        # Verify auto-generated fields
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_price_with_decimal_precision(self, integration_client):
        """Test creating price with decimal precision handling."""
        price_data = {
            "price_amount": 123.456789,  # More than 2 decimal places
            "currency_code": "USD",
        }

        response = integration_client.post("/prices", json=price_data)
        assert response.status_code == status.HTTP_201_CREATED

        data = response.json()
        # Should be rounded to 2 decimal places
        assert float(data["price_amount"]) == 123.46

    def test_get_price_integration(self, integration_client, sample_price_data):
        """Test retrieving price with real database."""
        # Create a price first
        create_response = integration_client.post("/prices", json=sample_price_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        created_price = create_response.json()

        # Get the price
        price_id = created_price["id"]
        response = integration_client.get(f"/prices/{price_id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["id"] == price_id
        assert data["chain_id"] == sample_price_data["chain_id"]
        assert data["store_id"] == sample_price_data["store_id"]
        assert data["item_code"] == sample_price_data["item_code"]
        assert float(data["price_amount"]) == sample_price_data["price_amount"]
        assert data["currency_code"] == sample_price_data["currency_code"]

    def test_get_prices_pagination_integration(
        self, integration_client, multiple_prices_data
    ):
        """Test pagination with real database."""
        # Create multiple prices
        created_prices = []
        for price_data in multiple_prices_data:
            response = integration_client.post("/prices", json=price_data)
            assert response.status_code == status.HTTP_201_CREATED
            created_prices.append(response.json())

        # Test pagination
        response = integration_client.get("/prices?page=1&size=2")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert len(data["items"]) == 2
        assert data["total"] >= 3  # At least the 3 we created
        assert data["page"] == 1
        assert data["size"] == 2

        # Test second page
        response = integration_client.get("/prices?page=2&size=2")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert len(data["items"]) >= 1  # At least 1 more item
        assert data["page"] == 2
        assert data["size"] == 2

    def test_update_price_integration(self, integration_client, sample_price_data):
        """Test updating price with real database."""
        # Create a price first
        create_response = integration_client.post("/prices", json=sample_price_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        created_price = create_response.json()

        # Update the price
        price_id = created_price["id"]
        update_data = {
            "price_amount": 19.99,
            "currency_code": "EUR",
            "price_update_date": "2024-02-01T12:00:00Z",
        }
        response = integration_client.put(f"/prices/{price_id}", json=update_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["id"] == price_id
        assert float(data["price_amount"]) == 19.99
        assert data["currency_code"] == "EUR"
        # Note: datetime format may be normalized by the database
        assert data["price_update_date"] is not None

        # Other fields should remain unchanged
        assert data["chain_id"] == sample_price_data["chain_id"]
        assert data["store_id"] == sample_price_data["store_id"]
        assert data["item_code"] == sample_price_data["item_code"]

    def test_delete_price_integration(self, integration_client, sample_price_data):
        """Test deleting price with real database."""
        # Create a price first
        create_response = integration_client.post("/prices", json=sample_price_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        created_price = create_response.json()

        # Delete the price
        price_id = created_price["id"]
        response = integration_client.delete(f"/prices/{price_id}")

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify the price is deleted
        get_response = integration_client.get(f"/prices/{price_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_price_not_found_integration(self, integration_client):
        """Test handling of non-existent price."""
        import uuid

        fake_id = str(uuid.uuid4())

        # Test GET
        response = integration_client.get(f"/prices/{fake_id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND

        # Test PUT
        response = integration_client.put(
            f"/prices/{fake_id}", json={"price_amount": 10.00}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

        # Test DELETE
        response = integration_client.delete(f"/prices/{fake_id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_price_validation_integration(self, integration_client):
        """Test price validation with real database."""
        # Test invalid store_id
        invalid_data = {
            "store_id": 0,  # Should be > 0
            "price_amount": 10.00,
            "currency_code": "USD",
        }
        response = integration_client.post("/prices", json=invalid_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Test invalid price_amount
        invalid_data = {
            "price_amount": -5.00,  # Should be >= 0
            "currency_code": "USD",
        }
        response = integration_client.post("/prices", json=invalid_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Test invalid currency_code
        invalid_data = {
            "price_amount": 10.00,
            "currency_code": "US",  # Should be exactly 3 characters
        }
        response = integration_client.post("/prices", json=invalid_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_price_with_null_values_integration(self, integration_client):
        """Test creating price with null values."""
        # Create price with only required fields (all optional in our case)
        minimal_data = {}
        response = integration_client.post("/prices", json=minimal_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        # Verify auto-generated fields are present
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

        # Other fields should be null
        assert data["chain_id"] is None
        assert data["store_id"] is None
        assert data["item_code"] is None
        assert data["price_amount"] is None
        assert data["currency_code"] is None
        assert data["price_update_date"] is None

    def test_price_bulk_operations_integration(
        self, integration_client, multiple_prices_data
    ):
        """Test bulk operations with real database."""
        # Create multiple prices
        created_prices = []
        for price_data in multiple_prices_data:
            response = integration_client.post("/prices", json=price_data)
            assert response.status_code == status.HTTP_201_CREATED
            created_prices.append(response.json())

        # Verify all prices were created
        response = integration_client.get("/prices")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["total"] >= len(multiple_prices_data)

        # Update multiple prices
        for i, price in enumerate(created_prices):
            update_data = {
                "price_amount": float(price["price_amount"]) + 1.00,
                "currency_code": "CAD",  # Change currency
            }
            response = integration_client.put(
                f"/prices/{price['id']}", json=update_data
            )
            assert response.status_code == status.HTTP_200_OK

        # Delete all created prices
        for price in created_prices:
            response = integration_client.delete(f"/prices/{price['id']}")
            assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify all prices are deleted
        for price in created_prices:
            response = integration_client.get(f"/prices/{price['id']}")
            assert response.status_code == status.HTTP_404_NOT_FOUND
