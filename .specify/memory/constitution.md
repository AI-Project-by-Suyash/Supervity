<!--
Sync Impact Report:
- Version change: Unversioned draft → 1.0.0
- List of modified principles:
  - Principle I: Atomic Commits & Granular Version Control (New)
  - Principle II: Agentic AI Artifact Isolation & Strict .gitignore Policy (New)
  - Principle III: Comprehensive & Continuous Documentation (New)
  - Principle IV: Test-First & Automated Verification (New)
  - Principle V: Modular Architecture & Clean Code (New)
- Added sections:
  - Repository Hygiene & Exclusion Constraints
  - Development Workflow & Quality Gates
  - Governance
- Removed sections: None
- Follow-up TODOs: None
-->

# Supervity Constitution

## Core Principles

### I. Atomic Commits & Granular Version Control
Every change MUST be captured in small, logical, and atomic commits. Commit history MUST remain clean, intentional, and documented using Conventional Commits standard (e.g., `feat:`, `fix:`, `docs:`, `test:`, `refactor:`). Rebasing or clean branch merges SHOULD be used to maintain a linear and inspectable Git timeline. Committing monolithic or opaque blocks of changes is strictly prohibited.

### II. Agentic AI Artifact Isolation & Strict .gitignore Policy
Agentic AI coding assistants, scratchpads, prompt traces, session transcripts, execution logs, internal agent configs, and tool metadata (including `.agents/`, agent cache dirs, `.gemini/`, `.claude/`, `.cursor/`, `.cline/`, `.roo/`, and machine-local agent state) MUST NEVER be committed or pushed to the upstream repository. All agentic runtime files MUST be isolated in `.gitignore`. The repository must strictly contain only production codebase assets, test suites, build configs, and official project documentation.

### III. Comprehensive & Continuous Documentation
Documentation is a first-class deliverable. Every feature, library, public API, configuration parameter, and architecture decision MUST be documented with clear, accessible, and up-to-date specifications and guides. Code changes MUST be accompanied by corresponding updates to READMEs, docstrings, API contracts, and user/developer documentation before merge approval.

### IV. Test-First & Automated Verification (NON-NEGOTIABLE)
Quality is enforced through rigorous testing. Test cases (unit, integration, and contract tests) MUST be designed and implemented alongside or prior to production code. All tests MUST pass deterministically in local environments and automated pipelines. Untested logic, dead code paths, and unverified edge cases MUST NOT pass review.

### V. Modular Architecture & Clean Code
The codebase MUST follow separation of concerns, high cohesion, low coupling, and YAGNI (You Aren't Gonna Need It) principles. Code MUST be readable, self-explanatory, and adhere to idiomatic language conventions. Complexity MUST be justified and minimized.

## Repository Hygiene & Exclusion Constraints

- **Git Exclusion Mandate**: `.gitignore` MUST explicitly cover all temporary runtime directories, local environment variables (`.env*`), IDE/agent working states, build artifacts, and dependency caches.
- **Secret & Credential Protection**: API keys, credentials, tokens, and private identifiers MUST NEVER be committed to Git. All secrets MUST be managed via secure environment variables or vault integrations.
- **Dependency Management**: Dependencies MUST be explicitly pinned and locked with determinism. Unused dependencies MUST be pruned promptly.

## Development Workflow & Quality Gates

- **Specification Before Implementation**: Significant features and architectural modifications MUST begin with a specification and implementation plan (Spec Kit workflow).
- **Mandatory Review & Compliance**: All pull requests and code modifications MUST be reviewed against this Constitution to ensure commit cleanliness, test coverage, documentation completeness, and exclusion compliance.
- **Continuous Integration**: Code MUST pass linting, type checks, and test suites prior to merge.

## Governance

This Constitution is the foundational governing policy for the Supervity project and supersedes any conflicting informal conventions. All contributors and automated assistants MUST strictly comply with these principles.

- **Amendments**: Amendments to this Constitution require explicit documentation, rationale, and approval through a versioned review process.
- **Versioning Policy**: Semantic versioning (MAJOR.MINOR.PATCH) is strictly applied:
  - MAJOR: Removal or backward-incompatible redefinition of core governance principles.
  - MINOR: Addition of new principles, sections, or materially expanded guidelines.
  - PATCH: Clarifications, typographic corrections, and non-semantic refinements.
- **Compliance Review**: Regular audits MUST verify that repository commits, `.gitignore` entries, documentation, and test suites adhere to constitutional requirements.

**Version**: 1.0.0 | **Ratified**: 2026-08-21 | **Last Amended**: 2026-08-21
