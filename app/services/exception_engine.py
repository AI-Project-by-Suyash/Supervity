from datetime import datetime
from typing import Optional, Dict, Any
from app.models.exception import ExceptionType, Severity

def evaluate_amount_mismatch(
    expected: Optional[float],
    actual: Optional[float],
    threshold: float = 0.10
) -> Dict[str, Any]:
    if expected is None or actual is None or expected <= 0:
        return {
            'flagged': True,
            'type': ExceptionType.AMOUNT_MISMATCH,
            'severity': Severity.HIGH,
            'variance': 1.0,
            'evidence': {
                'fields': [
                    {'name': 'invoice.amount', 'value': actual, 'source': 'invoice', 'label': 'Invoice Amount'},
                    {'name': 'purchase_order.amount', 'value': expected, 'source': 'purchase_order', 'label': 'PO Amount'}
                ],
                'completeness_score': 0.50
            }
        }

    variance = abs(actual - expected) / expected
    if variance <= threshold:
        return {'flagged': False, 'variance': variance}

    # Severity rules
    if variance > 0.15:
        severity = Severity.HIGH
    elif variance >= 0.05:
        severity = Severity.MEDIUM
    else:
        severity = Severity.LOW

    return {
        'flagged': True,
        'type': ExceptionType.AMOUNT_MISMATCH,
        'severity': severity,
        'variance': variance,
        'expected_value': f'₹{expected:,.2f}',
        'actual_value': f'₹{actual:,.2f}',
        'difference': f'₹{abs(actual - expected):,.2f} ({variance * 100:+.1f}%)',
        'threshold': f'{threshold * 100:.1f}%',
        'evidence': {
            'fields': [
                {'name': 'invoice.amount', 'value': actual, 'source': 'invoice', 'label': 'Invoice Billed Amount'},
                {'name': 'purchase_order.amount', 'value': expected, 'source': 'purchase_order', 'label': 'Approved PO Amount'},
                {'name': 'variance', 'value': variance, 'source': 'exception_engine', 'label': 'Calculated Variance'},
                {'name': 'allowed_variance', 'value': threshold, 'source': 'policy', 'label': 'Allowed Policy Threshold'}
            ],
            'completeness_score': 1.0
        }
    }

def evaluate_quantity_mismatch(
    expected_qty: Optional[int],
    actual_qty: Optional[int]
) -> Dict[str, Any]:
    if expected_qty is None or actual_qty is None:
        return {
            'flagged': True,
            'type': ExceptionType.QUANTITY_MISMATCH,
            'severity': Severity.HIGH,
            'difference_quantity': expected_qty,
            'expected_value': f'{expected_qty} units' if expected_qty else 'Unknown',
            'actual_value': 'null (missing receipt)',
            'difference': f'-{expected_qty} units' if expected_qty else 'Missing data',
            'threshold': '0 discrepancy',
            'evidence': {
                'fields': [
                    {'name': 'purchase_order.quantity', 'value': expected_qty, 'source': 'purchase_order', 'label': 'Ordered Quantity'},
                    {'name': 'goods_receipt.quantity', 'value': actual_qty, 'source': 'goods_receipt', 'label': 'Delivered Quantity'}
                ],
                'completeness_score': 0.50
            }
        }

    diff = abs(actual_qty - expected_qty)
    if diff == 0:
        return {'flagged': False, 'difference_quantity': 0}

    pct = diff / expected_qty if expected_qty > 0 else 1.0
    if pct > 0.15:
        severity = Severity.HIGH
    elif pct >= 0.05:
        severity = Severity.MEDIUM
    else:
        severity = Severity.LOW

    return {
        'flagged': True,
        'type': ExceptionType.QUANTITY_MISMATCH,
        'severity': severity,
        'difference_quantity': diff,
        'expected_value': f'{expected_qty:,} units',
        'actual_value': f'{actual_qty:,} units',
        'difference': f'{actual_qty - expected_qty:+,} units ({pct * 100:.1f}%)',
        'threshold': '0 discrepancy',
        'evidence': {
            'fields': [
                {'name': 'purchase_order.quantity', 'value': expected_qty, 'source': 'purchase_order', 'label': 'Ordered Quantity'},
                {'name': 'goods_receipt.quantity', 'value': actual_qty, 'source': 'goods_receipt', 'label': 'Delivered Quantity'},
                {'name': 'discrepancy_quantity', 'value': diff, 'source': 'exception_engine', 'label': 'Discrepancy Count'}
            ],
            'completeness_score': 1.0
        }
    }

def evaluate_payment_overdue(
    due_date_str: Optional[str],
    reference_date_str: Optional[str]
) -> Dict[str, Any]:
    if not due_date_str or not reference_date_str:
        return {
            'flagged': True,
            'type': ExceptionType.PAYMENT_OVERDUE,
            'severity': Severity.HIGH,
            'days_overdue': 0,
            'expected_value': due_date_str or 'Valid due date required',
            'actual_value': 'null (missing due date)',
            'difference': 'Indeterminate',
            'threshold': '0 days grace',
            'evidence': {
                'fields': [
                    {'name': 'invoice.due_date', 'value': due_date_str, 'source': 'invoice', 'label': 'Invoice Due Date'},
                    {'name': 'evaluation.reference_date', 'value': reference_date_str, 'source': 'system', 'label': 'System Reference Date'}
                ],
                'completeness_score': 0.40
            }
        }

    try:
        due = datetime.strptime(due_date_str, '%Y-%m-%d').date()
        ref = datetime.strptime(reference_date_str, '%Y-%m-%d').date()
        days = (ref - due).days
    except ValueError:
        return {'flagged': False}

    if days <= 0:
        return {'flagged': False, 'days_overdue': 0}

    if days > 30:
        severity = Severity.HIGH
    elif days >= 8:
        severity = Severity.MEDIUM
    else:
        severity = Severity.LOW

    return {
        'flagged': True,
        'type': ExceptionType.PAYMENT_OVERDUE,
        'severity': severity,
        'days_overdue': days,
        'expected_value': f'{due_date_str} (Due Date)',
        'actual_value': f'{reference_date_str} (Reference Date)',
        'difference': f'{days} days overdue',
        'threshold': '0 days grace',
        'evidence': {
            'fields': [
                {'name': 'invoice.due_date', 'value': due_date_str, 'source': 'invoice', 'label': 'Invoice Due Date'},
                {'name': 'evaluation.reference_date', 'value': reference_date_str, 'source': 'system', 'label': 'System Reference Date'},
                {'name': 'days_overdue', 'value': days, 'source': 'exception_engine', 'label': 'Days Past Due'}
            ],
            'completeness_score': 1.0
        }
    }
