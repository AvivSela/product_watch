from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestHealthEndpoints:
    """Test health check endpoints"""

    def test_health_check(self):
        """Test basic health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "file-processor-service"
        assert "timestamp" in data

    def test_health_check_ready(self):
        """Test readiness check endpoint"""
        response = client.get("/health/ready")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "ready"
        assert data["service"] == "file-processor-service"
        assert "timestamp" in data

    def test_health_check_live(self):
        """Test liveness check endpoint"""
        response = client.get("/health/live")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "alive"
        assert data["service"] == "file-processor-service"
        assert "timestamp" in data
