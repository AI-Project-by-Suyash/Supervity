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

def test_root_dashboard_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "Exception Resolution Workbench" in response.text
    head_resp = client.head("/")
    assert head_resp.status_code == 200

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

def test_analytics_metrics_api():
    response = client.get("/api/analytics/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert "status_distribution" in data
    assert "severity_distribution" in data
    assert "type_distribution" in data
    assert data["summary"]["total_exceptions"] == 12
    assert "total_financial_exposure" in data["summary"]

def test_reset_dataset_api():
    # 1. Resolve an exception
    res_resp = client.post("/api/exceptions/EXC-1001/resolve")
    assert res_resp.status_code == 200
    
    # Verify it is resolved
    exc_resp = client.get("/api/exceptions/EXC-1001")
    assert exc_resp.json()["status"] == "RESOLVED"
    
    # 2. Trigger Reset
    reset_resp = client.post("/api/seed/reset")
    assert reset_resp.status_code == 200
    assert reset_resp.json()["status"] == "success"
    
    # 3. Verify exception is restored to OPEN and resolutions are cleared
    exc_resp2 = client.get("/api/exceptions/EXC-1001")
    assert exc_resp2.json()["status"] == "OPEN"
    
    # 4. Verify analytics metrics are reset
    metrics_resp = client.get("/api/analytics/metrics")
    assert metrics_resp.json()["summary"]["auto_resolved_count"] == 0


