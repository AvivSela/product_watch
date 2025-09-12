"""
Health check unit tests for store service.
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
        assert data["service"] == "store-service"
        assert "timestamp" in data

    def test_health_check_db_success(self, client):
        """Test database health check endpoint."""
        response = client.get("/health/db")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["status"] == "healthy"
        assert data["service"] == "store-service"
        assert data["database"] == "connected"
        assert "timestamp" in data

    def test_health_check_db_with_data(self, client, sample_store_data):
        """Test database health check with existing data."""
        # Create a store to ensure database is working
        create_response = client.post("/stores", json=sample_store_data)
        assert create_response.status_code == status.HTTP_201_CREATED

        # Test health check
        response = client.get("/health/db")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["status"] == "healthy"
        assert data["database"] == "connected"
