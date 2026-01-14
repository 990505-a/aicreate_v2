"""Integration tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient
from app.main import app


class TestWorkflowAPI:
    """Test workflow management API."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    def test_list_workflows(self, client):
        """Test listing all workflows."""
        response = client.get("/api/v1/workflows/")

        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data

    def test_readiness_check(self, client):
        """Test readiness check endpoint."""
        response = client.get("/ready")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"


class TestExecutionAPI:
    """Test workflow execution API."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    def test_list_executions(self, client):
        """Test listing executions."""
        response = client.get("/api/v1/executions/")

        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_list_executions_with_filters(self, client):
        """Test listing executions with status filter."""
        response = client.get("/api/v1/executions/?status=completed")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        for exec_data in data:
            assert exec_data["status"] == "completed"

    def test_list_executions_pagination(self, client):
        """Test listing executions with pagination."""
        response = client.get("/api/v1/executions/?limit=10&offset=0")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Should return at most 10 items
        assert len(data) <= 10

    def test_get_nonexistent_execution(self, client):
        """Test getting non-existent execution."""
        response = client.get("/api/v1/executions/nonexistent-id")

        assert response.status_code == 404

    def test_cancel_nonexistent_execution(self, client):
        """Test cancelling non-existent execution."""
        response = client.post("/api/v1/executions/nonexistent-id/cancel")

        assert response.status_code == 404
