"""
Simplified database performance integration tests for price service.
Tests critical PostgreSQL database performance characteristics.
"""

import time

import pytest
from fastapi import status


@pytest.mark.integration
@pytest.mark.performance
class TestDatabasePerformanceIntegration:
    """Simplified performance integration tests for Price database operations."""

    def test_bulk_create_prices_performance(self, integration_client):
        """Test bulk price creation performance."""
        prices_data = []
        for i in range(60):  # Create 60 prices to ensure enough for pagination tests
            price_data = {
                "chain_id": f"bulk_perf_chain_{i % 10}",  # 10 different chains
                "store_id": 2000 + (i % 20),  # 20 different stores
                "item_code": f"BULK_PERF_ITEM_{i:03d}",
                "price_amount": 10.00 + (i * 0.01),  # Varying prices
                "currency_code": "USD",
                "price_update_date": "2024-01-15T10:30:00Z",
            }
            prices_data.append(price_data)

        # Measure bulk creation time
        start_time = time.time()
        created_prices = []

        # Add timeout protection
        timeout_seconds = 20

        for i, price_data in enumerate(prices_data):
            # Check if we've exceeded timeout
            if time.time() - start_time > timeout_seconds:
                raise TimeoutError(f"Test exceeded {timeout_seconds}s timeout")

            response = integration_client.post("/prices", json=price_data)
            assert response.status_code == status.HTTP_201_CREATED
            created_prices.append(response.json())
        end_time = time.time()

        bulk_creation_time = end_time - start_time
        avg_time_per_price = bulk_creation_time / len(prices_data)

        # Should be reasonably fast
        assert bulk_creation_time < 20.0, (
            f"Bulk creation took {bulk_creation_time:.3f}s, expected < 20.0s"
        )
        assert avg_time_per_price < 1.0, (
            f"Average time per price {avg_time_per_price:.3f}s, expected < 1.0s"
        )

        # Return created_prices for use in other tests
        self.created_prices = created_prices

    def test_pagination_performance(self, integration_client):
        """Test pagination performance with large dataset."""
        # First create a large dataset
        self.test_bulk_create_prices_performance(integration_client)

        # Test pagination performance
        start_time = time.time()
        response = integration_client.get("/prices?page=1&size=50")
        end_time = time.time()

        assert response.status_code == status.HTTP_200_OK
        pagination_time = end_time - start_time

        # Pagination should be fast
        assert pagination_time < 2.0, (
            f"Pagination took {pagination_time:.3f}s, expected < 2.0s"
        )

        data = response.json()
        # Should have at least 50 items if there are enough in the database
        assert len(data["items"]) <= 50  # Should not exceed requested size
        assert data["total"] >= 60  # Should have at least the 60 items we created

    def test_get_price_performance(self, integration_client):
        """Test individual price retrieval performance."""
        # Create a price first
        price_data = {
            "chain_id": "get_perf_chain",
            "store_id": 3001,
            "item_code": "GET_PERF_ITEM",
            "price_amount": 15.99,
            "currency_code": "EUR",
            "price_update_date": "2024-01-15T10:30:00Z",
        }

        create_response = integration_client.post("/prices", json=price_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        created_price = create_response.json()

        # Measure retrieval time
        start_time = time.time()
        response = integration_client.get(f"/prices/{created_price['id']}")
        end_time = time.time()

        assert response.status_code == status.HTTP_200_OK
        retrieval_time = end_time - start_time

        # Should be very fast
        assert retrieval_time < 0.5, (
            f"Price retrieval took {retrieval_time:.3f}s, expected < 0.5s"
        )
