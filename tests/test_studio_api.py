"""Test suite for ProdForge Studio FastAPI REST endpoints."""

from fastapi.testclient import TestClient
from prodforge.studio.server import app

client = TestClient(app)


def test_api_status():
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "detected_provider" in data
    assert "active_model" in data


def test_api_plan():
    response = client.post(
        "/api/plan",
        json={"idea": "Distributed cache with gossip protocol", "constraints": "Python"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "feasibility_score" in data
    assert "markdown_report" in data
    assert data["feasibility_score"] > 0


def test_api_audit_snippet():
    response = client.post(
        "/api/audit",
        json={"raw_code": "API_SECRET = 'secret_key_123456789012'\nprint('Debug output')"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "readiness_score" in data
    assert "findings" in data
    assert len(data["findings"]) >= 1


def test_api_test_generator():
    response = client.post(
        "/api/test",
        json={"raw_code": "def multiply(x: int, y: int) -> int:\n    return x * y\n", "framework": "pytest"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "test_code" in data
    assert "test_multiply" in data["test_code"]


def test_api_feasibility():
    response = client.post(
        "/api/feasibility",
        json={"idea": "Real-time chat service", "target_dau": 25000}
    )
    assert response.status_code == 200
    data = response.json()
    assert "estimated_monthly_cost_usd" in data
    assert data["concurrency_target_rps"] >= 10
