"""
Health check unit tests for price service.
"""

import pytest
from fastapi import status


@pytest.mark.unit
class TestHealthChecks:
    """Test class for health check endpoints."""

    def test_health_check_success(self, client):
        """Test basic health check endpoint."""
        response = client.get("/health")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["status"] == "healthy"
        assert data["service"] == "price-service"
        assert "timestamp" in data

    def test_health_check_db_success(self, client):
        """Test database health check endpoint."""
        response = client.get("/health/db")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["status"] == "healthy"
        assert data["service"] == "price-service"
        assert data["database"] == "connected"
        assert "timestamp" in data

    def test_health_check_db_with_data(self, client, sample_price_data):
        """Test database health check with existing data."""
        # Create a price to ensure database is working
        create_response = client.post("/prices", json=sample_price_data)
        assert create_response.status_code == status.HTTP_201_CREATED

        # Test health check
        response = client.get("/health/db")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["status"] == "healthy"
        assert data["database"] == "connected"
