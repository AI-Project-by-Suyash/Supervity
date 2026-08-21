import pytest
from app.services.confidence_engine import confidence_engine
from app.models.exception import ExceptionType

def test_high_confidence_calculation():
    evidence = {
        "completeness_score": 1.0,
        "fields": [
            {"name": "invoice.amount", "value": 62500.0},
            {"name": "purchase_order.amount", "value": 50000.0}
        ]
    }
    result = confidence_engine.calculate_confidence(
        exception_type=ExceptionType.AMOUNT_MISMATCH.value,
        evidence_data=evidence,
        ai_score=0.95
    )
    # Expected: 0.30*1.0 + 0.30*0.95 + 0.20*1.0 + 0.20*0.95 = 0.30 + 0.285 + 0.20 + 0.19 = 0.975
    assert result["confidence"] >= 0.90
    assert result["safety_gates_passed"] is True
    assert result["recommended_decision"] == "AUTO_RESOLVE"
    assert result["score_breakdown"]["evidence_score"] == 1.0

def test_medium_confidence_calculation():
    evidence = {
        "completeness_score": 0.85,
        "fields": [
            {"name": "invoice.amount", "value": 134400.0},
            {"name": "purchase_order.amount", "value": 120000.0}
        ]
    }
    result = confidence_engine.calculate_confidence(
        exception_type=ExceptionType.AMOUNT_MISMATCH.value,
        evidence_data=evidence,
        ai_score=0.80
    )
    assert 0.70 <= result["confidence"] < 0.90
    assert result["recommended_decision"] == "HUMAN_REVIEW"

def test_low_confidence_missing_evidence_safety_gate():
    evidence = {
        "completeness_score": 0.50,
        "fields": [
            {"name": "purchase_order.quantity", "value": 100},
            {"name": "goods_receipt.quantity", "value": None}  # null mandatory field
        ]
    }
    result = confidence_engine.calculate_confidence(
        exception_type=ExceptionType.QUANTITY_MISMATCH.value,
        evidence_data=evidence,
        ai_score=0.60
    )
    assert result["confidence"] < 0.70
    assert result["safety_gates_passed"] is False
    assert result["recommended_decision"] == "ESCALATE"
