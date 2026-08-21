# Phase 0: Technical Research & Architecture Decisions

**Feature**: Real-Time Exception Resolution Workbench
**Branch**: `001-exception-resolution-workbench`
**Date**: 2026-08-21

---

## 1. Architectural Style & Module Boundaries

### Decision: Modular Monolith
- **Chosen**: A single FastAPI application with strictly isolated internal modules (Exception Engine, AI Service, Confidence Engine, Resolution Service, Audit Service, Repository Layer).
- **Rationale**:
  - Eliminates distributed systems overhead (network hops, serialization latency, service discovery, distributed transactions) within a 24-hour delivery constraint.
  - Enforces clean domain boundaries with repository and service interfaces that can be extracted into independent microservices in the future if scale requires.
- **Alternatives Considered**:
  - *Microservices (Docker/K8s/Kafka)*: Rejected due to unnecessary operational complexity, network failure points, and deployment overhead for a single-node assessment.
  - *Serverless Functions*: Rejected due to cold starts and fragmented local state management.

---

## 2. LLM Provider Hierarchy & Zero-Downtime Fallback Strategy

### Decision: Dual-Provider Orchestration (Groq Primary + NVIDIA NIM Secondary + Deterministic Fallback)
- **Chosen**:
  - **Primary**: Groq (`llama-3.3-70b-versatile`) for ultra-low latency (< 800ms) structured JSON inference.
  - **Secondary**: NVIDIA NIM (`nvidia/nemotron-3.5-lightning-30b-a3b` via `https://integrate.api.nvidia.com/v1`) with reasoning parameters for failover on 429 (rate limits), 5xx, or network timeouts.
  - **Deterministic Offline Fallback**: If both external LLM APIs fail or network is unavailable, the system synthesizes structured rule-based explanations and recommendations directly from evidence records.
- **Rationale**:
  - Guarantees 100% application uptime and testability in any environment (including air-gapped CI/CD).
  - Protects against public API quota limits.
- **Alternatives Considered**:
  - *Single LLM Provider*: Rejected due to vulnerability to rate limits and API downtime.
  - *LangChain / LlamaIndex*: Rejected to avoid heavy dependencies and opaque abstraction layers; native HTTPX/OpenAI client provides transparent, robust control.

---

## 3. Deterministic Exception & Severity Engine

### Decision: Pure Deterministic Mathematics & Rule Policy
- **Chosen**: Exception detection and severity calculation are 100% deterministic Python rules:
  - `AMOUNT_MISMATCH`: variance = abs(actual - expected) / expected. Flagged if variance > 0.10. Severity: < 5% (LOW), 5%–15% (MEDIUM), > 15% (HIGH).
  - `QUANTITY_MISMATCH`: diff = abs(actual - expected). Flagged if diff > 0. Severity: < 5% (LOW), 5%–15% (MEDIUM), > 15% (HIGH).
  - `PAYMENT_OVERDUE`: days = reference_date - due_date. Flagged if days > 0. Severity: 0–7 days (LOW), 8–30 days (MEDIUM), > 30 days (HIGH).
- **Rationale**: Core FDE principle — deterministic systems establish ground truth facts and enforce policy; LLMs only interpret evidence and suggest actions.

---

## 4. Confidence & Safety Gate Architecture

### Decision: Two-Tier Evaluation (Safety Gates + Composite Score)
- **Safety Gates**:
  1. Evidence completeness check (all required transaction & reference fields non-null).
  2. Exception classification validity check.
  3. Action enum validation.
  If any safety gate fails -> Auto-resolution is permanently blocked -> Routes to `PENDING_HUMAN` or `ESCALATED`.
- **Composite Score Formula**:
  `resolution_confidence = (0.30 * evidence_score) + (0.30 * rule_certainty) + (0.20 * classification_score) + (0.20 * ai_score)`
- **Policy Engine Thresholds**:
  - >= 0.90 AND Safety Gates Pass -> `AUTO_RESOLVE`
  - 0.70 <= confidence < 0.90 -> `PENDING_HUMAN`
  - < 0.70 -> `ESCALATE`

---

## 5. Storage & Concurrency Strategy

### Decision: SQLite with WAL Mode & SQLAlchemy 2.0 ORM
- **Chosen**: SQLite in Write-Ahead Logging (`WAL`) mode with foreign key constraints enabled.
- **Rationale**:
  - Zero-configuration local deployment; instant start up.
  - WAL mode allows concurrent readers and non-blocking writes.
  - SQLAlchemy 2.0 models allow transparent migration to PostgreSQL if required in production.

---

## 6. Frontend Stack & UI/UX Design System

### Decision: Vanilla HTML5 / TailwindCSS / Vanilla JavaScript (No React / Node Build Step)
- **Chosen**: Single-page operations dashboard rendered with Jinja2 / static HTML, styled with modern Tailwind CSS via CDN, and dynamic state interactions powered by clean modular JavaScript.
- **Rationale**:
  - Zero frontend build tooling (no npm/node/webpack complexity).
  - Instant loading, responsive layout, enterprise-grade dark/light contrast cards, clear severity badges, and split-screen detail/evidence inspection.