# Engineering Progress Tracker: AI Career Platform

> **Status**: Live Running Record  
> **Last Updated**: 2026-11-20  
> **Current Milestone**: Milestone 1 — Project Foundation (Consolidated Complete, In Review)  
> **Current Phase**: `PHASE_00` (Project Foundation)  
> **Active Branch**: `milestone-01/foundation`  
> **Target PR**: Consolidated PR into `master` (Awaiting Human Review)

---

## 1. Project Phase Overview

| Phase ID | Phase Name | Status | Subphases |
| :--- | :--- | :--- | :--- |
| **PHASE_00** | **Project Foundation** | **In Review** | Subphases 01–05 Consolidated |
| **PHASE_01** | Candidate Core & Resume Ingestion | Planned | Subphases 01–04 |
| **PHASE_02** | Job Ingestion & Hybrid Retrieval Engine | Planned | Subphases 01–04 |
| **PHASE_03** | Explainable Compatibility Matching & Ranking | Planned | Subphases 01–04 |
| **PHASE_04** | LangGraph Career Discovery Agent & BYOK | Planned | Subphases 01–04 |
| **PHASE_05** | Daily Digest & SQS Async Workloads | Planned | Subphases 01–04 |
| **PHASE_06** | Next.js Candidate Web Application | Planned | Subphases 01–05 |
| **PHASE_07** | AWS Serverless Production Deployment | Planned | Subphases 01–04 |

---

## 2. Phase 00 Subphase Breakdown & Status

| Subphase ID | Subphase Name | Branch | Status | PR Reference |
| :--- | :--- | :--- | :--- | :--- |
| **01** | Engineering Governance & Architecture Documentation | `phase-00/subphase-01-agentic-governance` | **Merged** | [PR #1](https://github.com/shubhojit-mitra-dev/ai-job-agent/pull/1) |
| **02** | Database Connectivity & Alembic Scaffolding | `milestone-01/agent-a-database` | **Merged** | [PR #3](https://github.com/shubhojit-mitra-dev/ai-job-agent/pull/3) |
| **03** | Supabase Auth Verification & Security Middleware | `milestone-01/agent-b-supabase-auth` | **Merged** | [PR #4](https://github.com/shubhojit-mitra-dev/ai-job-agent/pull/4) |
| **04** | Local Development Environment (Docker Compose) | `milestone-01/agent-c-docker-compose` | **Merged** | [PR #2](https://github.com/shubhojit-mitra-dev/ai-job-agent/pull/2) |
| **05** | CI/CD Quality Gates & Automated Workflows | `milestone-01/agent-e-qa-ci` | **Merged** | [PR #5](https://github.com/shubhojit-mitra-dev/ai-job-agent/pull/5) |
| **Consolidated** | **Milestone 1 — Complete Foundation** | `milestone-01/foundation` | **In Review** | Final Consolidated PR into `master` |

---

## 3. Active Branches & Pull Requests

- **Default Branch**: `master` (Protected, clean)
- **Active Feature Branch**: `milestone-01/foundation`
- **Consolidated PR**: Milestone 1 Foundation into `master` (Awaiting Human Review)
- **Merged PRs**:
  - [PR #1: Governance & Documentation](https://github.com/shubhojit-mitra-dev/ai-job-agent/pull/1)
  - [PR #2: Docker Compose & Local Environment](https://github.com/shubhojit-mitra-dev/ai-job-agent/pull/2)
  - [PR #3: Async Database, Base & Alembic pgvector](https://github.com/shubhojit-mitra-dev/ai-job-agent/pull/3)
  - [PR #4: Supabase Asymmetric Auth & Protected Route](https://github.com/shubhojit-mitra-dev/ai-job-agent/pull/4)
  - [PR #5: CI Quality Gates & Shared Fixtures](https://github.com/shubhojit-mitra-dev/ai-job-agent/pull/5)

---

## 4. Architectural Decisions Pending Human Approval

- **ADR-011: Local Embedding Strategy and Its Deployment Constraints**:
  - *Status*: **Proposed**
  - *Context*: Standard Sentence Transformers / PyTorch models exceed the 250 MB AWS Lambda ZIP package limit and cause cold-start latency.
  - *Evaluation*: Proposes ONNX Runtime / FastEmbed CPU wheels in the SQS Worker Lambda or lightweight serverless inference endpoints. Awaiting technical lead review before implementation in Phase 01.

- **ADR-012: Resume File Storage and Secure Access**:
  - *Status*: **Proposed**
  - *Context*: Candidate resumes contain sensitive personal information (PII) requiring private object storage with pre-signed access controls.
  - *Evaluation*: Evaluates Supabase Storage versus Amazon S3 in `ap-south-1`. Awaiting technical lead review before selecting the authoritative provider in Phase 01.

---

## 5. Known Issues & Blockers

- *None*: The complete milestone passed 16 automated tests, strict mypy type checking across all 24 source files, ruff lint and format validation, Docker Compose schema validation, and Next.js 16 production static builds.

---

## 6. Next Authorized Task

Upon review and merge of `milestone-01/foundation` into `master`:
- **Next Milestone / Phase**: `PHASE_01` — Candidate Core & Resume Ingestion (Domain models, PII-safe parsing, storage abstraction).
