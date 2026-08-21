# Implementation Plan: Real-Time Exception Resolution Workbench

**Branch**: `001-exception-resolution-workbench` | **Date**: 2026-08-21 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/001-exception-resolution-workbench/spec.md`

## Summary

Build a lightweight, enterprise-grade Exception Resolution Workbench as a modular monolith (FastAPI backend + SQLite + Jinja2/Tailwind/JS frontend). The system enables human reviewers to triage flagged transaction discrepancies (`AMOUNT_MISMATCH`, `QUANTITY_MISMATCH`, `PAYMENT_OVERDUE`), inspect deterministic structured evidence, request AI root-cause explanations and constrained resolution recommendations via a resilient dual-provider LLM orchestration layer (Groq + NVIDIA NIM + deterministic offline fallback), enforce deterministic safety gates & composite confidence calculations, execute autonomous resolutions or human approvals, and maintain an immutable chronological audit trail.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**:
- Web & API: `fastapi >= 0.110.0`, `uvicorn >= 0.29.0`, `pydantic >= 2.6.0`, `jinja2 >= 3.1.3`, `python-dotenv >= 1.0.1`
- Persistence: `sqlalchemy >= 2.0.28`, SQLite with WAL mode
- LLM & HTTP Client: `httpx >= 0.27.0`, `openai >= 1.14.0` (for Groq and NVIDIA NIM OpenAI-compatible endpoints)
- Testing: `pytest >= 8.1.0`, `pytest-asyncio >= 0.23.0`

**Storage**: SQLite database (`sqlite:///./app.db`) managed via SQLAlchemy 2.0 ORM with WAL mode enabled for concurrent read/write isolation.

**Testing**: `pytest` test suite with TestClient integration, unit tests for deterministic detection engines, confidence math, safety gates, resolution state machine, and API endpoints.

**Target Platform**: Cross-platform web application (Windows, Linux, macOS).

**Project Type**: Modular Monolith Web Application with integrated REST API and responsive HTML5/Tailwind operations dashboard.

**Performance Goals**:
- Exception queue queries & filter updates: < 50ms
- AI Explanation & Resolution Recommendation: < 800ms via Groq primary (with 5s timeout failover to NVIDIA NIM)
- Deterministic policy check & autonomous resolution: < 20ms
- 100% deterministic availability when external LLMs are unreachable

**Constraints**:
- Zero external infrastructure dependencies (no Kafka, Redis, Celery, Docker/K8s, or React build step)
- Strict secret hygiene: `.env` excluded from Git via `.gitignore`
- Clean repository structure adhering to the Supervity Constitution

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Check | Status | Rationale |
|---|---|---|---|
| **I. Atomic Commits & Granular Version Control** | Every module/task committed atomically with Conventional Commits | **PASS** | Development planned in discrete testable slices with dedicated commit milestones |
| **II. Agentic AI Artifact Isolation** | `.agents/`, logs, and IDE caches strictly in `.gitignore` | **PASS** | `.gitignore` in root excludes all `.agents/`, `.gemini/`, `.env`, and temporary files |
| **III. Comprehensive Documentation** | Architecture, data model, API contracts, and guides fully documented | **PASS** | Specs, research, data-model, OpenAPI contract, and quickstart generated |
| **IV. Test-First & Quality Gates** | TDD test suite covers engines, confidence, resolution, and APIs | **PASS** | Automated test suite with unit, policy, and API integration tests |
| **V. Modular Architecture & Clean Code** | High cohesion, low coupling, separation of concerns | **PASS** | Clean modular monolith with distinct repository, service, and API layers |

## Project Structure

### Documentation (this feature)

```text
specs/001-exception-resolution-workbench/
├── spec.md              # Feature specification
├── plan.md              # This implementation plan
├── research.md          # Phase 0 research & architectural decisions
├── data-model.md        # Phase 1 data schema & lifecycle state machine
├── contracts/           # Phase 1 API contracts
│   └── openapi.json     # OpenAPI 3.1 contract specification
├── quickstart.md        # Phase 1 runnable quickstart & validation guide
├── checklists/
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Phase 2 tasks (/speckit-tasks output)
```

### Source Code (repository root)

```text
app/
├── main.py                          # FastAPI app entry point & route mounting
├── api/
│   ├── routes_exceptions.py         # Exception queue & detail endpoints
│   ├── routes_resolution.py         # AI explain, suggest, resolve, and review endpoints
│   └── routes_audit.py              # Audit trail query endpoints
├── models/
│   ├── base.py                      # SQLAlchemy Base & common mixins
│   ├── transaction.py               # Transaction ORM model
│   ├── exception.py                 # Exception ORM model
│   ├── resolution.py                # Resolution ORM model
│   └── audit.py                     # AuditEvent ORM model
├── schemas/
│   ├── transaction.py               # Pydantic schemas for transactions
│   ├── exception.py                 # Pydantic schemas for exceptions
│   ├── resolution.py                # Pydantic schemas for resolutions & review
│   ├── ai.py                        # Pydantic schemas for LLM prompts & structured responses
│   └── audit.py                     # Pydantic schemas for audit logs
├── services/
│   ├── exception_engine.py          # Deterministic detection & variance math
│   ├── ai_service.py                # AI employee explanation & recommendation orchestration
│   ├── confidence_engine.py         # Safety gates & composite confidence calculations
│   ├── resolution_service.py        # State machine transitions & resolution execution
│   └── audit_service.py             # Event recording & retrieval service
├── repositories/
│   ├── transaction_repository.py    # Transaction database access
│   ├── exception_repository.py      # Exception database access & filters
│   └── audit_repository.py          # Audit log persistence
├── llm/
│   ├── provider.py                  # Dual-provider client (Groq -> NVIDIA -> Offline fallback)
│   └── prompts.py                   # System prompts & structured JSON prompt templates
├── core/
│   ├── config.py                    # Settings via pydantic-settings / python-dotenv
│   └── database.py                  # Database engine, session maker, WAL init
└── seed/
    └── seed_data.py                 # 12 representative mock exceptions & transactions

frontend/
├── templates/
│   └── index.html                   # Dashboard shell & Jinja2 template
└── static/
    ├── css/
    │   └── styles.css               # Custom utility styles & theme enhancements
    └── js/
        └── app.js                   # Reactive client logic, filters, AI actions, modal/drawer

data/
└── mock_exceptions.json             # Raw mock dataset with High/Med/Low edge cases

tests/
├── test_exception_engine.py         # Deterministic detection & severity tests
├── test_confidence.py               # Composite confidence math & safety gate tests
├── test_resolution.py               # State machine, auto-resolve, and human review tests
└── test_api.py                      # FastAPI endpoint integration tests

architecture/
├── README.md                        # Architecture overview
├── system.md                        # Component interaction diagram
├── data-model.md                    # Data dictionary
└── api.md                           # REST endpoint documentation

.env.example                         # Template for environment configuration
requirements.txt                     # Pinned project dependencies
README.md                            # Project overview & quickstart
run.py                               # Application runner script
```

**Structure Decision**: Modular Monolith with clear separation across `api`, `services`, `repositories`, `models`, `llm`, and `frontend`. This delivers zero-config local startup, clear testability, and a clear path for potential future service extraction without microservice complexity.

## Complexity Tracking

| Component / Pattern | Why Needed | Simpler Alternative Rejected Because |
|---|---|---|
| **Repository Pattern** | Decouples ORM data access from business engines | Direct SQL/ORM calls inside routes make unit testing engines difficult |
| **Dual LLM Provider Client** | Guarantees zero downtime across API outages & rate limits | Single provider fails completely when quota or service outage occurs |
| **Separate Confidence Engine** | Enforces deterministic policy separate from AI text generation | Letting LLM decide its own confidence creates hallucination & safety risks |

