# Engineering Progress Tracker: AI Career Platform

> **Status**: Live Running Record  
> **Last Updated**: 2026-11-20  
> **Current Milestone**: Milestone 1 — Project Foundation  
> **Current Phase**: `PHASE_00` (Project Foundation)  
> **Current Subphase**: `PHASE_00_SUBPHASE_01` (Engineering Governance & Architecture Documentation)

---

## 1. Project Phase Overview

| Phase ID | Phase Name | Status | Subphases |
| :--- | :--- | :--- | :--- |
| **PHASE_00** | **Project Foundation** | **Active** | Subphases 01–05 |
| **PHASE_01** | Candidate Core & Resume Ingestion | Planned | TBD |
| **PHASE_02** | Job Ingestion & Hybrid Retrieval Engine | Planned | TBD |
| **PHASE_03** | Explainable Compatibility Matching & Ranking | Planned | TBD |
| **PHASE_04** | LangGraph Career Discovery Agent & BYOK | Planned | TBD |
| **PHASE_05** | Daily Digest & SQS Async Workloads | Planned | TBD |
| **PHASE_06** | Next.js Candidate Web Application | Planned | TBD |
| **PHASE_07** | AWS Serverless Production Deployment | Planned | TBD |

---

## 2. Phase 00 Subphase Breakdown & Status

| Subphase ID | Subphase Name | Branch | Status | PR Reference |
| :--- | :--- | :--- | :--- | :--- |
| **01** | **Engineering Governance & Architecture Documentation** | `phase-00/subphase-01-agentic-governance` | **Completed (Awaiting Review)** | [PR #1](https://github.com/shubhojit-mitra-dev/ai-job-agent/pull/1) |
| **02** | Database Connectivity & Alembic Scaffolding | `phase-00/subphase-02-db-connectivity-alembic` | Pending | — |
| **03** | Supabase Auth Verification & Security Middleware | `phase-00/subphase-03-auth-middleware` | Pending | — |
| **04** | Local Development Environment (Docker Compose) | `phase-00/subphase-04-local-docker-compose` | Pending | — |
| **05** | CI/CD Quality Gates & Automated Workflows | `phase-00/subphase-05-cicd-quality-gates` | Pending | — |

---

## 3. Active Branches & Pull Requests

- **Active Branch**: `phase-00/subphase-01-agentic-governance`
- **Default Branch**: `master` (Protected, clean)
- **Merged PRs**: None (Initial foundation subphase)

---

## 4. Architectural Decisions Pending Human Approval

- **ADR-011: Local Embedding Strategy and Its Deployment Constraints**:
  - *Status*: **Proposed**
  - *Context*: Standard Sentence Transformers / PyTorch models exceed the 250 MB AWS Lambda ZIP package limit and cause cold-start latency.
  - *Evaluation*: Proposes ONNX Runtime / FastEmbed CPU wheels in the SQS Worker Lambda or lightweight serverless inference endpoints. Awaiting technical lead review before implementation.

---

## 5. Known Issues & Blockers

- *None*: The scaffolded FastAPI backend and Next.js frontend are intact; all documentation links, Mermaid diagrams, and governance contracts have been validated.

---

## 6. Next Authorized Task

Upon review and merge of `phase-00/subphase-01-agentic-governance`:
- **Next Task**: `PHASE_00_SUBPHASE_02` — Configuring PostgreSQL connectivity, SQLAlchemy 2.0 async engine (`NullPool`, `statement_cache_size=0`), and Alembic schema migrations scaffolding.
