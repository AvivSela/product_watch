"""
CRUD unit tests for price service.
"""

import pytest
from fastapi import status


@pytest.mark.unit
class TestPriceCRUD:
    """Test class for Price CRUD operations."""

    def test_create_price_success(self, client, sample_price_data):
        """Test successful price creation."""
        response = client.post("/prices", json=sample_price_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        # Check that all fields are present and correct
        assert data["chain_id"] == sample_price_data["chain_id"]
        assert data["store_id"] == sample_price_data["store_id"]
        assert data["item_code"] == sample_price_data["item_code"]
        assert float(data["price_amount"]) == sample_price_data["price_amount"]
        assert data["currency_code"] == sample_price_data["currency_code"]
        # Note: datetime format may be normalized by the database
        assert data["price_update_date"] is not None

        # Check that auto-generated fields are present
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_price_with_minimal_data(self, client):
        """Test creating price with minimal required data."""
        minimal_data = {}
        response = client.post("/prices", json=minimal_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        # Check that auto-generated fields are present
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_price_with_invalid_store_id(self, client):
        """Test creating price with invalid store_id."""
        invalid_data = {
            "store_id": 0,  # Invalid: should be > 0
            "price_amount": 10.50,
            "currency_code": "USD",
        }
        response = client.post("/prices", json=invalid_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_price_with_invalid_price_amount(self, client):
        """Test creating price with invalid price_amount."""
        invalid_data = {
            "price_amount": -5.00,  # Invalid: should be >= 0
            "currency_code": "USD",
        }
        response = client.post("/prices", json=invalid_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_price_with_invalid_currency_code(self, client):
        """Test creating price with invalid currency_code."""
        invalid_data = {
            "price_amount": 10.50,
            "currency_code": "US",  # Invalid: should be exactly 3 characters
        }
        response = client.post("/prices", json=invalid_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_price_success(self, client, sample_price_data):
        """Test successful price retrieval."""
        # Create a price first
        create_response = client.post("/prices", json=sample_price_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        created_price = create_response.json()

        # Get the price
        price_id = created_price["id"]
        response = client.get(f"/prices/{price_id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["id"] == price_id
        assert data["chain_id"] == sample_price_data["chain_id"]
        assert data["store_id"] == sample_price_data["store_id"]
        assert data["item_code"] == sample_price_data["item_code"]
        assert float(data["price_amount"]) == sample_price_data["price_amount"]
        assert data["currency_code"] == sample_price_data["currency_code"]

    def test_get_price_not_found(self, client):
        """Test getting non-existent price."""
        import uuid

        fake_id = str(uuid.uuid4())
        response = client.get(f"/prices/{fake_id}")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"]

    def test_get_prices_pagination(
        self, client, sample_price_data, sample_price_data_2
    ):
        """Test getting prices with pagination."""
        # Create two prices
        client.post("/prices", json=sample_price_data)
        client.post("/prices", json=sample_price_data_2)

        # Get first page
        response = client.get("/prices?page=1&size=1")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert len(data["items"]) == 1
        assert data["total"] == 2
        assert data["page"] == 1
        assert data["size"] == 1
        assert data["pages"] == 2

        # Get second page
        response = client.get("/prices?page=2&size=1")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert len(data["items"]) == 1
        assert data["total"] == 2
        assert data["page"] == 2
        assert data["size"] == 1
        assert data["pages"] == 2

    def test_update_price_success(self, client, sample_price_data):
        """Test successful price update."""
        # Create a price first
        create_response = client.post("/prices", json=sample_price_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        created_price = create_response.json()

        # Update the price
        price_id = created_price["id"]
        update_data = {"price_amount": 12.99, "currency_code": "EUR"}
        response = client.put(f"/prices/{price_id}", json=update_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["id"] == price_id
        assert float(data["price_amount"]) == 12.99
        assert data["currency_code"] == "EUR"
        # Other fields should remain unchanged
        assert data["chain_id"] == sample_price_data["chain_id"]
        assert data["store_id"] == sample_price_data["store_id"]

    def test_update_price_not_found(self, client):
        """Test updating non-existent price."""
        import uuid

        fake_id = str(uuid.uuid4())
        update_data = {"price_amount": 15.00}
        response = client.put(f"/prices/{fake_id}", json=update_data)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"]

    def test_update_price_with_invalid_data(self, client, sample_price_data):
        """Test updating price with invalid data."""
        # Create a price first
        create_response = client.post("/prices", json=sample_price_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        created_price = create_response.json()

        # Try to update with invalid data
        price_id = created_price["id"]
        invalid_update_data = {
            "price_amount": -10.00,  # Invalid: should be >= 0
        }
        response = client.put(f"/prices/{price_id}", json=invalid_update_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_delete_price_success(self, client, sample_price_data):
        """Test successful price deletion."""
        # Create a price first
        create_response = client.post("/prices", json=sample_price_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        created_price = create_response.json()

        # Delete the price
        price_id = created_price["id"]
        response = client.delete(f"/prices/{price_id}")

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify the price is deleted
        get_response = client.get(f"/prices/{price_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_price_not_found(self, client):
        """Test deleting non-existent price."""
        import uuid

        fake_id = str(uuid.uuid4())
        response = client.delete(f"/prices/{fake_id}")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"]
