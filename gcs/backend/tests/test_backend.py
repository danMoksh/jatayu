"""
Backend API Unit Tests
Validates root, health, targets, and telemetry endpoints using FastAPI TestClient.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "JATAYU GCS Backend"
    assert data["status"] == "running"


def test_health_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "mavlink_connected" in data


def test_telemetry_endpoint(client):
    response = client.get("/api/telemetry")
    assert response.status_code == 200
    data = response.json()
    assert "lat" in data
    assert "lon" in data
    assert "mode" in data


def test_targets_endpoint(client):
    response = client.get("/api/targets")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
