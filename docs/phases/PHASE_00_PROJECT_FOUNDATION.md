# Phase 00: Project Foundation

> **Phase Identifier**: `PHASE_00`  
> **Phase Name**: Project Foundation  
> **Status**: Active (Subphase 01 in review)  
> **Target Subphases**: 5 Subphases

---

## 1. Phase Objective
Establish the complete architectural, governance, database, authentication, local development, and CI/CD foundation for the AI Career Platform. At the conclusion of Phase 00, the platform will have a verified, reproducible environment ready for domain feature implementation (candidate profile, job ingestion, matching, and LangGraph agents) without technical ambiguity.

---

## 2. Scope & Key Deliverables

- **In Scope**:
  - Full engineering governance documentation and AI coding agent guidelines (`AGENTS.md`).
  - Authoritative Architecture Specifications and Architectural Decision Records (ADRs).
  - PostgreSQL database connectivity via SQLAlchemy 2.0 async engine and `asyncpg` with Supabase transaction pooler safeguards.
  - Alembic database migration scaffolding connected via session mode.
  - Supabase Auth JWT verification middleware on protected FastAPI endpoints.
  - Local containerized development stack via Docker Compose (PostgreSQL with `pgvector`).
  - Automated CI/CD pipelines (GitHub Actions) for linting, typing, and testing.
- **Explicitly Excluded**:
  - Domain business logic, candidate resume parsing, job scraping, matching algorithms, or LangGraph agent graphs (deferred to Phase 01+).
  - AWS production resource creation (Terraform apply) or cloud deployments (deferred to deployment phases).

---

## 3. Subphase Breakdown

Phase 00 is broken into 5 logically sequenced subphases:

| Subphase ID | Subphase Name | Git Branch | Status | Scope Summary |
| :--- | :--- | :--- | :--- | :--- |
| **01** | **Agentic Governance & Architecture Documentation** | `phase-00/subphase-01-agentic-governance` | **In Review** | Root governance, product spec, architecture, ADRs, test strategy, security specs, and progress tracking. |
| **02** | **Database Connectivity & Alembic Scaffolding** | `phase-00/subphase-02-db-connectivity-alembic` | Pending | SQLAlchemy 2.0 async engine, `NullPool` config, session lifecycle, base model, and verified Alembic setup. |
| **03** | **Supabase Auth Middleware & Security** | `phase-00/subphase-03-auth-middleware` | Pending | Backend JWT signature verification, `CurrentUser` dependency, tenant isolation checks, and auth test fixtures. |
| **04** | **Local Development Environment** | `phase-00/subphase-04-local-docker-compose` | Pending | Docker Compose with PostgreSQL + `pgvector`, seed scripts, local verification commands. |
| **05** | **CI/CD Quality Gates & Automation** | `phase-00/subphase-05-cicd-quality-gates` | Pending | GitHub Actions for Ruff, Mypy, Pytest, Next.js lint/typecheck, and PR automated validation. |

*Note: In accordance with governance rules, detailed subphase specification documents are created just-in-time when each subphase is authorized to begin. Only Subphase 01 is detailed at this time.*

---

## 4. Dependencies & Prerequisites
- Python 3.12 and `uv` package manager.
- Node.js 20+ and npm.
- Git repository with `master` default branch.
- Supabase account with active access.

---

## 5. Acceptance Criteria & Phase Definition of Done

Phase 00 is complete when:
1. All 5 subphases have been completed on their dedicated branches, approved by the Technical Lead, and merged into `master`.
2. The FastAPI backend boots cleanly locally and can query a PostgreSQL database with `pgvector` enabled using async SQLAlchemy sessions.
3. Protected endpoints verify Supabase JWT access tokens and reject invalid/expired tokens with 401 Unauthorized.
4. Database migrations run cleanly forward and backward via Alembic.
5. Automated tests pass 100% in local and CI environments.
6. Progress tracking and subphase walkthroughs are fully documented in `docs/`.

---

## 6. Risks & Mitigation
- **Risk**: Connection pool exhaustion when transitioning to serverless AWS Lambda.
  - *Mitigation*: Architect engine with `NullPool` and `statement_cache_size=0` from day one in Subphase 02.
- **Risk**: Stale documentation across multi-step development.
  - *Mitigation*: Just-in-time subphase documentation rule; every subphase requires a walkthrough document before merge.

