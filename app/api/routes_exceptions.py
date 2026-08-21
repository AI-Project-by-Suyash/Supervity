import json
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.exception_repository import ExceptionRepository
from app.schemas.exception import ExceptionSummary, ExceptionDetail

router = APIRouter()

@router.get('/exceptions')
def list_exceptions(
    status: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    type: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    repo = ExceptionRepository(db)
    items = repo.list_with_filters(status=status, severity=severity, exception_type=type)
    
    summaries = []
    for item in items:
        summaries.append({
            'id': item.id,
            'transaction_id': item.transaction_id,
            'reference_number': item.transaction.reference_number if item.transaction else 'N/A',
            'vendor': item.transaction.vendor if item.transaction else 'Unknown',
            'type': item.type.value,
            'severity': item.severity.value,
            'status': item.status.value,
            'title': item.title,
            'difference': item.difference,
            'created_at': item.created_at.isoformat()
        })
    return {'items': summaries, 'total': len(summaries)}

@router.get('/exceptions/{exception_id}')
def get_exception_detail(exception_id: str, db: Session = Depends(get_db)):
    repo = ExceptionRepository(db)
    item = repo.get_by_id(exception_id)
    if not item:
        raise HTTPException(status_code=404, detail='Exception not found')

    txn_dict = None
    if item.transaction:
        txn = item.transaction
        txn_dict = {
            'id': txn.id,
            'reference_number': txn.reference_number,
            'transaction_type': txn.transaction_type,
            'vendor': txn.vendor,
            'expected_amount': txn.expected_amount,
            'actual_amount': txn.actual_amount,
            'expected_quantity': txn.expected_quantity,
            'actual_quantity': txn.actual_quantity,
            'due_date': txn.due_date,
            'reference_date': txn.reference_date,
            'currency': txn.currency,
            'metadata': json.loads(txn.metadata_json) if txn.metadata_json else {}
        }

    evidence_dict = json.loads(item.evidence_json) if item.evidence_json else {}
    
    # Latest resolution if any
    res_dict = None
    if item.resolutions:
        latest = sorted(item.resolutions, key=lambda r: r.created_at, reverse=True)[0]
        res_dict = {
            'suggested_action': latest.suggested_action.value,
            'reason': latest.reason,
            'confidence': latest.confidence,
            'score_breakdown': json.loads(latest.score_breakdown) if latest.score_breakdown else {},
            'safety_gates_passed': latest.safety_gates_passed,
            'execution_mode': latest.execution_mode,
            'executed_by': latest.executed_by,
            'created_at': latest.created_at.isoformat()
        }

    return {
        'id': item.id,
        'transaction_id': item.transaction_id,
        'transaction': txn_dict,
        'type': item.type.value,
        'severity': item.severity.value,
        'status': item.status.value,
        'title': item.title,
        'description': item.description,
        'expected_value': item.expected_value,
        'actual_value': item.actual_value,
        'difference': item.difference,
        'threshold': item.threshold,
        'evidence': evidence_dict,
        'resolution': res_dict,
        'created_at': item.created_at.isoformat(),
        'updated_at': item.updated_at.isoformat(),
        'resolved_at': item.resolved_at.isoformat() if item.resolved_at else None
    }
