import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.seed.seed_data import seed_database
from app.core.database import SessionLocal, engine
from app.models.base import Base

client = TestClient(app)



def test_health_check_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data

def test_list_exceptions_api():
    response = client.get("/api/exceptions")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert data["total"] == 12

def test_filter_exceptions_by_severity():
    response = client.get("/api/exceptions?severity=HIGH")
    assert response.status_code == 200
    items = response.json()["items"]
    assert len(items) > 0
    assert all(i["severity"] == "HIGH" for i in items)

def test_get_exception_detail():
    response = client.get("/api/exceptions/EXC-1001")
    assert response.status_code == 200
    detail = response.json()
    assert detail["id"] == "EXC-1001"
    assert "evidence" in detail
    assert "fields" in detail["evidence"]

def test_ai_explain_endpoint():
    response = client.post("/api/exceptions/EXC-1001/explain")
    assert response.status_code == 200
    data = response.json()
    assert "explanation" in data
    assert len(data["evidence_fields"]) > 0

def test_ai_suggest_endpoint():
    response = client.post("/api/exceptions/EXC-1001/suggest")
    assert response.status_code == 200
    data = response.json()
    assert "suggested_action" in data
    assert "confidence" in data
    assert "score_breakdown" in data

def test_audit_trail_endpoint():
    # Trigger an explanation first to add an audit event
    client.post("/api/exceptions/EXC-1001/explain")
    response = client.get("/api/exceptions/EXC-1001/audit")
    assert response.status_code == 200
    events = response.json()
    assert len(events) >= 2  # INIT + EXPLAIN
    assert any(e["actor"] == "AI_EMPLOYEE" for e in events)
