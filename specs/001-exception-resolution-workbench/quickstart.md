# Quickstart & Validation Guide

**Feature**: Real-Time Exception Resolution Workbench
**Branch**: `001-exception-resolution-workbench`
**Date**: 2026-08-21

---

## 1. Prerequisites & Setup

### Environment
- Python 3.11+
- Virtual environment recommended

### Installation & Run Commands
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Verify or copy .env
cp .env.example .env

# 3. Start the application
python run.py
# Server runs at http://localhost:8000
```

---

## 2. Automated Test Suite Execution

Run automated unit, policy, engine, and API tests:
```bash
pytest -v
```

Expected output:
- `test_exception_engine.py`: Tests variance calculations, overdue dates, and evidence assembly.
- `test_confidence.py`: Tests composite confidence math (95% -> Auto, 80% -> Human, 50% -> Escalate) and safety gates.
- `test_resolution.py`: Tests state transitions, duplicate resolution rejections, and audit event emission.
- `test_api.py`: Tests all REST endpoints against OpenAPI contract.

---

## 3. Golden Demo Walkthrough Scenarios

Open your browser at `http://localhost:8000`.

### Scenario A — High Confidence Auto-Resolution
1. **Target**: `INV-1023` (Acme Supplies) — `AMOUNT_MISMATCH` (Expected ₹50,000, Actual ₹62,500, Variance 25% > Threshold 10%).
2. **Action 1**: Click `INV-1023` in the queue. Observe the structured evidence card.
3. **Action 2**: Click **"Explain"**. The AI Employee explains the exact variance referencing PO and Invoice figures.
4. **Action 3**: Click **"Suggest Resolution"**. AI returns `REQUEST_VENDOR_CORRECTION` with confidence $\ge 94\%$.
5. **Action 4**: Click **"Auto Resolve"**. The system executes resolution, updates status to `RESOLVED`, moves item out of active queue, and logs `AUTO_RESOLVED` event in audit trail.

### Scenario B — Medium Confidence Human Review Loop
1. **Target**: `PAY-2041` — `PAYMENT_OVERDUE` (17 days overdue).
2. **Action 1**: Click `PAY-2041`. Observe evidence.
3. **Action 2**: Click **"Suggest Resolution"**. AI returns `REQUEST_PAYMENT_REVIEW` with confidence $\approx 78\%$.
4. **Action 3**: Observe that Auto-Resolution is blocked because confidence $< 90\%$. The item transitions to `PENDING_HUMAN`.
5. **Action 4**: Reviewer enters verification note ("Terms verified with treasury") and clicks **"Approve"**. Status updates to `RESOLVED` with `HUMAN_APPROVED` logged.

### Scenario C — Incomplete Evidence Safety Gate & Escalation
1. **Target**: `PO-8872` — `QUANTITY_MISMATCH` (Actual quantity `null` / missing delivery receipt).
2. **Action 1**: Click `PO-8872`. Observe missing evidence alert.
3. **Action 2**: Click **"Suggest Resolution"**.
4. **Action 3**: Observe Safety Gate actively blocks auto-resolve due to incomplete evidence; resolution confidence falls below $70\%$.
5. **Action 4**: System flags `ESCALATED` for senior investigation and logs `AUTO_RESOLUTION_BLOCKED` + `ESCALATED` audit events.
