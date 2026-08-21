# Tasks: Real-Time Exception Resolution Workbench

**Input**: Design documents from `specs/001-exception-resolution-workbench/`
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/openapi.json`, `quickstart.md`

## Format: `[ID] [P?] [Story?] Description with file path`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., [US1], [US2], [US3]...)
- All tasks include exact, concrete file paths.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, environment setup, and dependency management.

- [ ] T001 Initialize project structure, dependency manifest `requirements.txt`, and runtime entrypoint in `run.py`
- [ ] T002 [P] Implement environment configuration management and validation in `app/core/config.py`
- [ ] T003 [P] Implement SQLite database engine with WAL mode and session factory in `app/core/database.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core data models, schemas, repositories, and seed data required across all user stories.

**⚠️ CRITICAL**: No user story phase can proceed until this foundation is complete.

- [ ] T004 [P] Create SQLAlchemy Base class, metadata mixins, and UUID/ID generators in `app/models/base.py`
- [ ] T005 [P] Create relational ORM models (`Transaction`, `Exception`, `Resolution`, `AuditEvent`) in `app/models/transaction.py`, `app/models/exception.py`, `app/models/resolution.py`, and `app/models/audit.py`
- [ ] T006 [P] Create Pydantic schemas for data validation and API I/O in `app/schemas/transaction.py`, `app/schemas/exception.py`, `app/schemas/resolution.py`, `app/schemas/ai.py`, and `app/schemas/audit.py`
- [ ] T007 [P] Create database repositories for data access and queries in `app/repositories/transaction_repository.py`, `app/repositories/exception_repository.py`, and `app/repositories/audit_repository.py`
- [ ] T008 Create 12 representative mock enterprise exceptions (covering High/Med/Low confidence and missing evidence edge cases) in `data/mock_exceptions.json` and seed loader in `app/seed/seed_data.py`
- [ ] T009 Implement FastAPI application factory, CORS middleware, static file serving, and router mounting in `app/main.py`

**Checkpoint**: Foundation ready — database schema, seed data, and application bootstrap are fully operational.

---

## Phase 3: User Story 1 - Triage and Inspect Flagged Exceptions (Priority: P1) 🎯 MVP

**Goal**: Operations reviewer can view the real-time exception queue, filter by status/severity/type, and inspect structured evidence for any selected discrepancy.

**Independent Test**: Seed database with mock exceptions, start server, query GET `/api/exceptions` and GET `/api/exceptions/{id}`, and verify dashboard renders queue items with accurate discrepancy values and evidence fields.

### Tests for User Story 1
- [ ] T010 [P] [US1] Unit tests for deterministic exception detection engine in `tests/test_exception_engine.py`

### Implementation for User Story 1
- [ ] T011 [US1] Implement deterministic exception detection & variance calculation engine (`AMOUNT_MISMATCH`, `QUANTITY_MISMATCH`, `PAYMENT_OVERDUE`) in `app/services/exception_engine.py`
- [ ] T012 [US1] Implement exception list and detail API endpoints with status/severity/type filtering in `app/api/routes_exceptions.py`
- [ ] T013 [P] [US1] Build dashboard HTML layout, header metric counters, and split-screen queue containers in `frontend/templates/index.html`
- [ ] T014 [P] [US1] Implement enterprise operations stylesheet, severity badges, and dark/light contrast cards in `frontend/static/css/styles.css`
- [ ] T015 [US1] Implement reactive client logic for fetching exception queue, dynamic filtering, and detail drawer rendering in `frontend/static/js/app.js`

**Checkpoint**: User Story 1 complete — reviewer can triage exceptions and inspect evidence.

---

## Phase 4: User Story 2 - Request AI Root-Cause Explanation (Priority: P1)

**Goal**: Reviewer can ask the AI Employee to explain why an item was flagged, with explanation strictly grounded in verified evidence fields.

**Independent Test**: Click "Explain" on an open exception (`INV-1023`), verify AI cites exact invoice vs. PO amounts and variance, and check that an `AI_EXPLANATION_GENERATED` audit event is emitted.

### Tests for User Story 2
- [ ] T016 [P] [US2] Unit tests for dual-provider LLM client and failover behavior in `tests/test_ai_service.py`

### Implementation for User Story 2
- [ ] T017 [P] [US2] Define structured system prompts and hallucination-preventing JSON schemas in `app/llm/prompts.py`
- [ ] T018 [US2] Implement resilient dual-provider LLM client (Groq `llama-3.3-70b-versatile` -> NVIDIA NIM `nvidia/nemotron-3.5-lightning-30b-a3b` -> deterministic offline fallback) in `app/llm/provider.py`
- [ ] T019 [US2] Implement AI root-cause explanation service grounded in structured evidence in `app/services/ai_service.py`
- [ ] T020 [US2] Implement POST `/api/exceptions/{id}/explain` API endpoint in `app/api/routes_resolution.py`
- [ ] T021 [US2] Implement frontend AI Explanation panel with evidence citation tags and loading skeletons in `frontend/static/js/app.js`

**Checkpoint**: User Story 2 complete — reviewer receives grounded AI root-cause explanations.

---

## Phase 5: User Story 3 - AI Suggested Resolution with Confidence Scoring (Priority: P1)

**Goal**: Reviewer receives a resolution recommendation constrained to allowed business action enums, accompanied by a composite confidence score.

**Independent Test**: Request resolution suggestion on exceptions, verify action belongs to allowed enum, confidence score is between 0.0 and 1.0, and score breakdown matches formula.

### Tests for User Story 3
- [ ] T022 [P] [US3] Unit tests for composite confidence calculations and scoring weights in `tests/test_confidence.py`

### Implementation for User Story 3
- [ ] T023 [US3] Implement composite confidence calculation engine (30% evidence, 30% rule, 20% classification, 20% AI) in `app/services/confidence_engine.py`
- [ ] T024 [US3] Implement AI resolution recommendation generator with constrained action enums in `app/services/ai_service.py`
- [ ] T025 [US3] Implement POST `/api/exceptions/{id}/suggest` API endpoint in `app/api/routes_resolution.py`
- [ ] T026 [US3] Implement recommendation card, confidence gauge meter, and breakdown badges in `frontend/static/js/app.js`

**Checkpoint**: User Story 3 complete — AI recommendations with confidence metrics displayed.

---

## Phase 6: User Story 4 - Policy-Driven Autonomous Resolution (Priority: P1)

**Goal**: High-confidence exceptions (>= 0.90) with passing safety gates auto-resolve automatically; uncertain or incomplete cases are blocked and routed.

**Independent Test**: Run auto-resolve on `INV-1023` (94% -> auto-resolved), `PAY-2041` (78% -> blocked/pending human), and `PO-8872` (missing evidence -> blocked/escalated).

### Tests for User Story 4
- [ ] T027 [P] [US4] Unit tests for safety gates and auto-resolution policy rules in `tests/test_resolution.py`

### Implementation for User Story 4
- [ ] T028 [US4] Implement deterministic safety gates (evidence completeness, valid exception type, non-null mandatory fields) in `app/services/confidence_engine.py`
- [ ] T029 [US4] Implement resolution state machine, status transitions, and duplicate resolution guard in `app/services/resolution_service.py`
- [ ] T030 [US4] Implement POST `/api/exceptions/{id}/resolve` endpoint in `app/api/routes_resolution.py`
- [ ] T031 [US4] Implement frontend Auto-Resolve action button, policy status banner, and live queue status updates in `frontend/static/js/app.js`

**Checkpoint**: User Story 4 complete — autonomous resolution and safety gates enforced.

---

## Phase 7: User Story 5 - Human Review, Approval, Rejection, and Escalation (Priority: P2)

**Goal**: Reviewer can review medium-confidence items, input decision rationale, and approve, reject, or escalate exceptions.

**Independent Test**: Submit human review with approval on `PAY-2041`, verify status becomes `RESOLVED`, and check `HUMAN_APPROVED` logged with reviewer reason.

### Tests for User Story 5
- [ ] T032 [P] [US5] Integration tests for human review decisions (`APPROVE`, `REJECT`, `ESCALATE`) in `tests/test_resolution.py`

### Implementation for User Story 5
- [ ] T033 [US5] Implement reviewer decision handlers and state transition logic in `app/services/resolution_service.py`
- [ ] T034 [US5] Implement POST `/api/exceptions/{id}/review` endpoint in `app/api/routes_resolution.py`
- [ ] T035 [US5] Implement human review modal with decision buttons (Approve / Reject / Escalate) and rationale input in `frontend/templates/index.html` and `frontend/static/js/app.js`

**Checkpoint**: User Story 5 complete — human-in-command operational review loop fully active.

---

## Phase 8: User Story 6 - Complete Historical Audit Trail (Priority: P2)

**Goal**: Compliance officers can inspect an immutable, chronological audit trail for every exception.

**Independent Test**: Query GET `/api/exceptions/{id}/audit` across an exception lifecycle and verify all events contain timestamps, actor attribution, and metadata.

### Tests for User Story 6
- [ ] T036 [P] [US6] Integration tests for audit event persistence and retrieval in `tests/test_api.py`

### Implementation for User Story 6
- [ ] T037 [US6] Implement audit logging service for recording lifecycle events in `app/services/audit_service.py`
- [ ] T038 [US6] Implement GET `/api/exceptions/{id}/audit` endpoint in `app/api/routes_audit.py`
- [ ] T039 [US6] Implement frontend chronological audit trail timeline component with actor badges in `frontend/static/js/app.js`

**Checkpoint**: User Story 6 complete — comprehensive audit trail visible and verifiable.

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Architecture documentation, quickstart validation, and system hardening.

- [ ] T040 [P] Create architecture documentation and component diagrams in `architecture/system.md`, `architecture/data-model.md`, `architecture/api.md`, and `architecture/README.md`
- [ ] T041 [P] Create project overview, setup guide, and golden demo scenarios in `README.md`
- [ ] T042 Execute full automated test suite (`pytest -v`) and validate golden demo scenarios against `specs/001-exception-resolution-workbench/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies
- **Setup (Phase 1)**: No dependencies — can start immediately.
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories.
- **User Story 1 (Phase 3)**: Depends on Phase 2 — Provides MVP exception queue.
- **User Story 2 (Phase 4)**: Depends on Phase 2 & US1 — Adds AI explanation.
- **User Story 3 (Phase 5)**: Depends on Phase 2 & US2 — Adds AI recommendations.
- **User Story 4 (Phase 6)**: Depends on Phase 2, US1 & US3 — Adds auto-resolution.
- **User Story 5 (Phase 7)**: Depends on Phase 2 & US4 — Adds human review loop.
- **User Story 6 (Phase 8)**: Depends on Phase 2 — Tracks all events across stories.
- **Polish (Phase 9)**: Depends on all user stories being complete.

---

## Implementation Strategy

### MVP Milestone (Phases 1, 2, 3)
1. Complete Setup (T001 - T003)
2. Complete Foundation (T004 - T009)
3. Complete User Story 1 (T010 - T015)
4. **Validate**: Reviewers can triage exceptions and view evidence.

### Complete Functional Delivery (Phases 4 - 8)
5. Add AI Explanations (US2: T016 - T021)
6. Add Suggestions & Confidence (US3: T022 - T026)
7. Add Policy & Autonomous Resolution (US4: T027 - T031)
8. Add Human Review & Escalation (US5: T032 - T035)
9. Add Audit Trail (US6: T036 - T039)
10. Final Polish & Golden Demo Verification (T040 - T042)
