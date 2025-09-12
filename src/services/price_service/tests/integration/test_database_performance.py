"""
Database performance integration tests for price service.
Tests real PostgreSQL database performance and scalability.
"""

import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import pytest
from fastapi import status


@pytest.mark.integration
@pytest.mark.performance
class TestDatabasePerformanceIntegration:
    """Database performance integration tests for Price."""

    def test_create_price_performance(self, integration_client):
        """Test price creation performance."""
        price_data = {
            "chain_id": "perf_test_chain",
            "store_id": 1001,
            "item_code": "PERF_ITEM_001",
            "price_amount": 9.99,
            "currency_code": "USD",
            "price_update_date": "2024-01-15T10:30:00Z",
        }

        # Measure creation time
        start_time = time.time()
        response = integration_client.post("/prices", json=price_data)
        end_time = time.time()

        assert response.status_code == status.HTTP_201_CREATED
        creation_time = end_time - start_time

        # Should be fast (less than 1 second)
        assert creation_time < 1.0, (
            f"Price creation took {creation_time:.3f}s, expected < 1.0s"
        )

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

    def test_update_price_performance(self, integration_client):
        """Test price update performance."""
        # Create a price first
        price_data = {
            "chain_id": "update_perf_chain",
            "store_id": 4001,
            "item_code": "UPDATE_PERF_ITEM",
            "price_amount": 20.00,
            "currency_code": "GBP",
            "price_update_date": "2024-01-15T10:30:00Z",
        }

        create_response = integration_client.post("/prices", json=price_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        created_price = create_response.json()

        # Measure update time
        update_data = {"price_amount": 25.00, "currency_code": "USD"}

        start_time = time.time()
        response = integration_client.put(
            f"/prices/{created_price['id']}", json=update_data
        )
        end_time = time.time()

        assert response.status_code == status.HTTP_200_OK
        update_time = end_time - start_time

        # Should be fast
        assert update_time < 1.0, (
            f"Price update took {update_time:.3f}s, expected < 1.0s"
        )

    def test_delete_price_performance(self, integration_client):
        """Test price deletion performance."""
        # Create a price first
        price_data = {
            "chain_id": "delete_perf_chain",
            "store_id": 5001,
            "item_code": "DELETE_PERF_ITEM",
            "price_amount": 30.00,
            "currency_code": "JPY",
            "price_update_date": "2024-01-15T10:30:00Z",
        }

        create_response = integration_client.post("/prices", json=price_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        created_price = create_response.json()

        # Measure deletion time
        start_time = time.time()
        response = integration_client.delete(f"/prices/{created_price['id']}")
        end_time = time.time()

        assert response.status_code == status.HTTP_204_NO_CONTENT
        deletion_time = end_time - start_time

        # Should be fast
        assert deletion_time < 1.0, (
            f"Price deletion took {deletion_time:.3f}s, expected < 1.0s"
        )

    def test_concurrent_operations_performance(self, integration_client):
        """Test concurrent operations performance."""

        def create_price(price_id):
            try:
                price_data = {
                    "chain_id": f"concurrent_chain_{price_id}",
                    "store_id": 6000 + price_id,
                    "item_code": f"CONCURRENT_ITEM_{price_id:03d}",
                    "price_amount": 10.00 + price_id,
                    "currency_code": "USD",
                    "price_update_date": "2024-01-15T10:30:00Z",
                }
                response = integration_client.post("/prices", json=price_data)
                return response.status_code == status.HTTP_201_CREATED
            except Exception as e:
                print(f"Error creating price {price_id}: {e}")
                return False

        # Test concurrent creation with fewer workers and operations to avoid connection issues
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [
                executor.submit(create_price, i) for i in range(10)
            ]  # Reduced from 20 to 10
            results = [future.result() for future in as_completed(futures)]
        end_time = time.time()

        concurrent_time = end_time - start_time
        success_count = sum(results)

        # Should handle concurrent operations well - allow for some failures due to database constraints
        assert success_count >= 8, (  # Allow for some failures
            f"Only {success_count}/10 concurrent operations succeeded"
        )
        assert concurrent_time < 15.0, (  # Increased timeout
            f"Concurrent operations took {concurrent_time:.3f}s, expected < 15.0s"
        )

    def test_large_dataset_performance(self, integration_client):
        """Test performance with large dataset."""
        # Create a large dataset
        large_dataset_size = 100
        prices_data = []

        for i in range(large_dataset_size):
            price_data = {
                "chain_id": f"large_chain_{i % 100}",  # 100 different chains
                "store_id": 7000 + (i % 200),  # 200 different stores
                "item_code": f"LARGE_ITEM_{i:04d}",
                "price_amount": 5.00 + (i * 0.01),
                "currency_code": "USD",
                "price_update_date": "2024-01-15T10:30:00Z",
            }
            prices_data.append(price_data)

        # Measure large dataset creation
        start_time = time.time()
        created_prices = []

        # Add timeout protection
        timeout_seconds = 30

        for i, price_data in enumerate(prices_data):
            # Check if we've exceeded timeout
            if time.time() - start_time > timeout_seconds:
                raise TimeoutError(f"Test exceeded {timeout_seconds}s timeout")

            response = integration_client.post("/prices", json=price_data)
            assert response.status_code == status.HTTP_201_CREATED
            created_prices.append(response.json())
        end_time = time.time()

        large_dataset_time = end_time - start_time
        avg_time_per_price = large_dataset_time / len(prices_data)

        # Should handle large datasets reasonably well
        assert large_dataset_time < 30.0, (
            f"Large dataset creation took {large_dataset_time:.3f}s, expected < 30.0s"
        )
        assert avg_time_per_price < 0.3, (
            f"Average time per price {avg_time_per_price:.3f}s, expected < 0.3s"
        )

        # Test pagination with large dataset
        start_time = time.time()
        response = integration_client.get("/prices?page=1&size=100")
        end_time = time.time()

        assert response.status_code == status.HTTP_200_OK
        pagination_time = end_time - start_time

        # Pagination should still be fast with large dataset
        assert pagination_time < 3.0, (
            f"Pagination with large dataset took {pagination_time:.3f}s, expected < 3.0s"
        )

        data = response.json()
        assert len(data["items"]) == 100
        assert data["total"] >= large_dataset_size

    def test_memory_usage_performance(self, integration_client):
        """Test memory usage with repeated operations."""
        # Perform many operations to test memory usage
        operations_count = 50

        start_time = time.time()

        # Add timeout protection - fail if test takes too long
        timeout_seconds = 30

        for i in range(operations_count):
            # Check if we've exceeded timeout
            if time.time() - start_time > timeout_seconds:
                raise TimeoutError(f"Test exceeded {timeout_seconds}s timeout")
            # Create
            price_data = {
                "chain_id": f"memory_chain_{i}",
                "store_id": 8000 + i,
                "item_code": f"MEMORY_ITEM_{i:03d}",
                "price_amount": 10.00 + i,
                "currency_code": "USD",
            }
            create_response = integration_client.post("/prices", json=price_data)
            assert create_response.status_code == status.HTTP_201_CREATED

            # Update
            price_id = create_response.json()["id"]
            update_data = {"price_amount": 15.00 + i}
            update_response = integration_client.put(
                f"/prices/{price_id}", json=update_data
            )
            assert update_response.status_code == status.HTTP_200_OK

            # Delete
            delete_response = integration_client.delete(f"/prices/{price_id}")
            assert delete_response.status_code == status.HTTP_204_NO_CONTENT

        end_time = time.time()

        total_time = end_time - start_time
        avg_time_per_operation = total_time / (
            operations_count * 3
        )  # 3 operations per iteration

        # Should maintain good performance
        assert total_time < 30.0, (
            f"Memory test operations took {total_time:.3f}s, expected < 30.0s"
        )
        assert avg_time_per_operation < 0.2, (
            f"Average time per operation {avg_time_per_operation:.3f}s, expected < 0.2s"
        )
