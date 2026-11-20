# Phase 00, Subphase 01: Engineering Governance, Architecture Documentation & Agent System

> **Subphase Identifier**: `PHASE_00_SUBPHASE_01`  
> **Subphase Name**: Engineering Governance, Architecture Documentation & AI-Agent Development System  
> **Git Branch**: `phase-00/subphase-01-agentic-governance`  
> **Status**: Active (Implementation & Validation)  
> **Target Delivery**: Documentation Only (Zero Application Logic Changes)

---

## 1. Subphase Objective

Establish a self-documenting, disciplined, and AI-agent-friendly engineering governance system inside the existing GitHub repository (`shubhojit-mitra-dev/ai-job-agent`). 

This subphase codifies all approved architectural decisions, product specifications, coding standards, testing strategies, security mandates, and phase roadmaps into authoritative repository documentation so that future human engineers and AI coding agents can work with complete clarity, autonomy, and zero architectural drift.

---

## 2. Authorized Scope

### In Scope
1. **Root Governance Files**:
   - `AGENTS.md`: Authoritative instructions for all coding agents.
   - `CLAUDE.md`: Direct pointer redirecting Claude agents to `AGENTS.md`.
   - `README.md`: Professional project overview matching current repo state and approved target architecture.
2. **Core Technical Documentation (`docs/`)**:
   - `docs/PRODUCT_SPEC.md`: Product vision, target personas, functional requirements, and strict MVP boundaries.
   - `docs/ARCHITECTURE.md`: Modular monolith design, AWS serverless model, Supabase connection pooling rules, LangGraph architecture.
   - `docs/DEVELOPMENT_GUIDE.md`: Monorepo setup, `uv` workflows, formatting, linting, and branch conventions.
   - `docs/TESTING_STRATEGY.md`: TDD pyramid, deterministic mock fixtures, testing LLM agents without live APIs.
   - `docs/SECURITY.md`: Supabase Auth verification, BYOK key encryption, prompt injection defense, and pre-signed storage.
   - `docs/DEPLOYMENT.md`: AWS Lambda + Mangum, API Gateway HTTP API, SQS workers, Terraform IaC, GitHub Actions OIDC.
   - `docs/COST_AND_OPERATIONS.md`: Cost management, avoiding idle servers, CloudWatch retention, and budget guardrails.
3. **Architectural Decision Records (`docs/adr/`)**:
   - ADR-001 through ADR-012 with strictly accurate statuses (`Accepted` vs `Proposed`).
4. **Phase & Tracking Management**:
   - `docs/phases/PHASE_00_PROJECT_FOUNDATION.md`: High-level roadmap covering Phase 00 subphases.
   - `docs/subphases/PHASE_00_SUBPHASE_01_AGENTIC_GOVERNANCE.md`: Detailed plan for the active subphase only.
   - `docs/progress/PROGRESS.md`: Initialized live development tracking board.
   - `docs/walkthroughs/WALKTHROUGH_PHASE_00_SUBPHASE_01.md`: Post-completion audit walkthrough.

### Explicitly Excluded (Strict Scope Boundaries)
- No database engine configuration, connection code, or models.
- No Supabase database mutations or schema executions.
- No AWS resource provisioning, Terraform execution, or cloud credential setups.
- No Lambda handlers, Mangum imports, or SQS worker implementations.
- No modifications to existing application source code (`apps/api/app/main.py`, `apps/web/`).
- No modifications to lockfiles (`uv.lock`, `package-lock.json`).

---

## 3. Detailed Acceptance Criteria

1. **Governance & Guidelines**:
   - `AGENTS.md` exists at root, detailing mandatory documentation reading order, monorepo layout, approved architecture constraints, coding/testing standards, security mandates, and PR workflows.
   - `CLAUDE.md` redirects cleanly to `AGENTS.md`.
   - `README.md` reflects true current status (scaffolded) without claiming non-existent features are implemented.
2. **Technical Specifications**:
   - `docs/ARCHITECTURE.md` accurately details Supabase Transaction Pooler (port 6543) requirements (`statement_cache_size=0`, `NullPool`) and separates Alembic migration execution (port 5432).
   - `docs/TESTING_STRATEGY.md` establishes TDD rules and explicitly forbids live external LLM calls in CI/CD.
   - `docs/SECURITY.md` addresses candidate resume PII protection, BYOK AES-GCM encryption, and prompt injection defense.
3. **Architectural Decision Records**:
   - All 12 initial ADRs exist in `docs/adr/` using the standard ADR template.
   - ADR-011 is properly marked `Proposed` with trade-offs regarding the 250 MB Lambda ZIP packaging limit.
   - ADR-001 through ADR-010 and ADR-012 are marked `Accepted`.
4. **Phase & Subphase Discipline**:
   - Phase 00 plan outlines 5 subphases.
   - Only Subphase 01 has a detailed subphase document. Future subphases remain plan-level items.
5. **Quality & Validation**:
   - All Markdown cross-links resolve to existing files.
   - All Mermaid diagrams compile without syntax errors.
   - Working tree clean with zero uncommitted application file changes.

---

## 4. Verification Method

- Run documentation link checker and verify all referenced files exist.
- Run `git status` and `git diff` to confirm zero changes to existing application code.
- Run `apps/api` test client to ensure `/health` endpoint remains completely functional.
