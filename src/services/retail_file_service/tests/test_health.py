"""
Health check tests for retail file service.
"""

import pytest
from fastapi import status


@pytest.mark.unit
class TestHealthChecks:
    """Test class for health check endpoints."""

    def test_health_check(self, client):
        """Test basic health check endpoint."""
        response = client.get("/health")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["status"] == "healthy"
        assert data["service"] == "retail-file-service"
        assert "timestamp" in data

    def test_health_check_db(self, client):
        """Test database health check endpoint."""
        response = client.get("/health/db")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["status"] == "healthy"
        assert data["service"] == "retail-file-service"
        assert data["database"] == "connected"
        assert "timestamp" in data
