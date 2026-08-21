import json
from pathlib import Path
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models.base import Base
from app.models.transaction import Transaction
from app.models.exception import ExceptionRecord, ExceptionType, Severity, ExceptionStatus
from app.models.audit import AuditEventRecord, ActorType

def seed_database(db: Session = None, reset: bool = True):
    should_close = False
    if db is None:
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        should_close = True

    try:
        if reset:
            db.query(AuditEventRecord).delete()
            db.query(ExceptionRecord).delete()
            db.query(Transaction).delete()
            db.commit()

        # Load mock json
        json_path = Path('data/mock_exceptions.json')
        if not json_path.exists():
            return 0

        data = json.loads(json_path.read_text(encoding='utf-8'))
        count = 0
        for item in data:
            txn = Transaction(
                id=item['id'],
                reference_number=item['reference_number'],
                transaction_type=item['transaction_type'],
                vendor=item['vendor'],
                expected_amount=item.get('expected_amount'),
                actual_amount=item.get('actual_amount'),
                expected_quantity=item.get('expected_quantity'),
                actual_quantity=item.get('actual_quantity'),
                due_date=item.get('due_date'),
                reference_date=item.get('reference_date'),
                currency=item.get('currency', 'INR'),
                metadata_json=json.dumps(item.get('metadata', {}))
            )
            db.add(txn)
            db.flush()

            exc_data = item['exception']
            exc = ExceptionRecord(
                id=exc_data['id'],
                transaction_id=txn.id,
                type=ExceptionType(exc_data['type']),
                severity=Severity(exc_data['severity']),
                status=ExceptionStatus.OPEN,
                title=exc_data['title'],
                description=exc_data['description'],
                expected_value=exc_data.get('expected_value'),
                actual_value=exc_data.get('actual_value'),
                difference=exc_data.get('difference'),
                threshold=exc_data.get('threshold'),
                evidence_json=json.dumps(exc_data['evidence'])
            )
            db.add(exc)
            db.flush()

            # Seed initial audit event
            audit = AuditEventRecord(
                id=f'AUD-{exc.id}-INIT',
                exception_id=exc.id,
                actor=ActorType.SYSTEM,
                action='EXCEPTION_CREATED',
                reason='Deterministic exception detection engine flagged transaction discrepancy.',
                metadata_json=json.dumps({'source': 'deterministic_engine', 'severity': exc.severity.value})
            )
            db.add(audit)
            count += 1

        db.commit()
        return count
    finally:
        if should_close:
            db.close()

if __name__ == '__main__':
    c = seed_database()
    print(f'Successfully seeded {c} exceptions.')
