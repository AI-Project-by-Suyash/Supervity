# Supervity: Real-Time Exception Resolution Workbench

> **Enterprise AI Employee Workbench** for autonomous and human-in-the-loop exception triage, root-cause explanation, and policy-driven resolution.

---

## Highlights & Features

- **Deterministic Discrepancy Engine**: Zero-hallucination mathematical verification of invoice variances, quantity shortfalls, and payment due dates.
- **Dual-Tier Resilient AI Inference**: Sub-second Groq (`llama-3.3-70b-versatile`) with transparent failover to NVIDIA NIM (`nvidia/nemotron-3.5-lightning-30b-a3b`) and offline deterministic fallback.
- **Evidence-Grounded Explanations**: AI employee outputs are strictly grounded in structured transactional evidence fields.
- **Composite Confidence Scoring**: Multidimensional scoring formula weighting evidence completeness (30%), rule certainty (30%), classification confidence (20%), and AI confidence (20%).
- **Deterministic Safety Gates & Policy**: Enforces strict policy thresholds ($\ge 90\%$ Auto-Resolve, $70	ext{--}89\%$ Human Review, $<70\%$ Escalation) with mandatory non-null evidence validation.
- **Human-in-Command Governance**: Interactive reviewer decision modal requiring rationale logs for audit compliance.
- **Immutable Audit Trail**: Chronological event timeline recording every system, AI, and reviewer action.

---

## Quickstart Runbook

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env` and supply your API keys:
```env
GROQ_API_KEY=your_groq_api_key
NVIDIA_API_KEY=your_nvidia_api_key
```

### 3. Run the Application
```bash
python run.py
```
Open your browser at **`http://localhost:8000`** to access the interactive workbench dashboard.

### 4. Run Automated Test Suite
```bash
pytest -v
```

---

## Golden Demo Test Scenarios

1. **Scenario 1: High Confidence Autonomous Resolution**
   - Select `INV-1023` (Acme Industrial Supplies, 25% price variance, 100% evidence completeness).
   - Click **Explain** $ightarrow$ AI cites exact ₹62,500 vs ₹50,000 variance.
   - Click **Suggest Resolution** $ightarrow$ Recommends `REQUEST_VENDOR_CORRECTION` with **97% confidence** (`AUTO_RESOLVE`).
   - Click **Auto Resolve** $ightarrow$ Status changes to `RESOLVED` and audit trail records `AUTO_RESOLVED`.

2. **Scenario 2: Medium Confidence Human Review Gate**
   - Select `PAY-2041` (Nexus Cloud Services, 17 days past due, 88% evidence completeness).
   - Click **Suggest Resolution** $ightarrow$ 82% confidence (`HUMAN_REVIEW`).
   - Click **Auto Resolve** $ightarrow$ Blocked by policy; prompts human review.
   - Click **Human Review** $ightarrow$ Select `APPROVE`, enter verification notes, submit $ightarrow$ Status transitions to `RESOLVED` with `HUMAN_APPROVED` audit event.

3. **Scenario 3: Missing Evidence Safety Gate Escalation**
   - Select `PO-8872` (SteelCraft Fasteners, missing goods receipt delivery quantity).
   - Click **Suggest Resolution** $ightarrow$ Confidence below 70% with safety gate alert.
   - Click **Auto Resolve** $ightarrow$ Blocked and automatically routed to `ESCALATED`.

---

## Architecture & Design Docs
- [System Architecture](architecture/system.md)
- [Data Model & State Machine](architecture/data-model.md)
- [API Reference](architecture/api.md)
