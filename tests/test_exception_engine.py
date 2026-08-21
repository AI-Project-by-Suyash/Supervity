import pytest
from app.services.exception_engine import (
    evaluate_amount_mismatch,
    evaluate_quantity_mismatch,
    evaluate_payment_overdue
)
from app.models.exception import Severity, ExceptionType

def test_amount_mismatch_above_threshold():
    # 50,000 vs 62,500 = 25% variance (> 10% threshold) -> HIGH severity (> 15%)
    result = evaluate_amount_mismatch(expected=50000.0, actual=62500.0, threshold=0.10)
    assert result['flagged'] is True
    assert result['type'] == ExceptionType.AMOUNT_MISMATCH
    assert result['severity'] == Severity.HIGH
    assert round(result['variance'], 2) == 0.25
    assert len(result['evidence']['fields']) == 4

def test_amount_mismatch_below_threshold():
    # 50,000 vs 52,000 = 4% variance (< 10% threshold) -> Not flagged
    result = evaluate_amount_mismatch(expected=50000.0, actual=52000.0, threshold=0.10)
    assert result['flagged'] is False

def test_quantity_mismatch_detection():
    # Ordered 100, received 80 (diff = 20) -> HIGH severity (20% diff)
    result = evaluate_quantity_mismatch(expected_qty=100, actual_qty=80)
    assert result['flagged'] is True
    assert result['type'] == ExceptionType.QUANTITY_MISMATCH
    assert result['severity'] == Severity.HIGH
    assert result['difference_quantity'] == 20

def test_quantity_mismatch_missing_actual():
    # Ordered 100, actual is None -> Flagged as HIGH with incomplete evidence
    result = evaluate_quantity_mismatch(expected_qty=100, actual_qty=None)
    assert result['flagged'] is True
    assert result['severity'] == Severity.HIGH
    assert result['evidence']['completeness_score'] < 0.70

def test_payment_overdue_medium_severity():
    # Due on 2026-08-01, evaluated on 2026-08-18 (17 days overdue) -> MEDIUM (8-30 days)
    result = evaluate_payment_overdue(due_date_str='2026-08-01', reference_date_str='2026-08-18')
    assert result['flagged'] is True
    assert result['type'] == ExceptionType.PAYMENT_OVERDUE
    assert result['severity'] == Severity.MEDIUM
    assert result['days_overdue'] == 17

def test_payment_overdue_critical_high():
    # Due on 2026-07-10, evaluated on 2026-08-18 (39 days overdue) -> HIGH (>30 days)
    result = evaluate_payment_overdue(due_date_str='2026-07-10', reference_date_str='2026-08-18')
    assert result['flagged'] is True
    assert result['severity'] == Severity.HIGH
    assert result['days_overdue'] == 39
