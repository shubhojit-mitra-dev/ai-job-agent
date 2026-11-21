# Engineering Progress Tracker: AI Career Platform

> **Status**: Live Running Record  
> **Last Updated**: 2026-11-21  
> **Current Milestone**: Phase 01 — AWS-Native Architecture Migration (Documentation & ADRs)  
> **Current Phase**: `PHASE_01` (Candidate Core & Architecture Migration)  
> **Active Branch**: `phase-01/aws-architecture-migration`  
> **Target PR**: Dedicated Architecture Migration PR into `master`

---

## 1. Project Phase Overview

| Phase ID | Phase Name | Status | Subphases / Scope |
| :--- | :--- | :--- | :--- |
| **PHASE_00** | **Project Foundation** | **Completed** | Subphases 01–05 Consolidated & Merged via PR #6 |
| **PHASE_01** | **Candidate Core & Architecture Migration** | **Active** | AWS Architecture Migration & Subphases 01–04 |
| **PHASE_02** | Job Ingestion & Hybrid Retrieval Engine | Planned | Subphases 01–04 (S3 Vectors + Aurora) |
| **PHASE_03** | Explainable Compatibility Matching & Ranking | Planned | Subphases 01–04 (Deterministic Rubric) |
| **PHASE_04** | LangGraph Career Discovery Agent & BYOK | Planned | Subphases 01–04 (Bedrock Titan + BYOK) |
| **PHASE_05** | Daily Digest & SQS Async Workloads | Planned | Subphases 01–04 (EventBridge + SQS) |
| **PHASE_06** | Next.js Candidate Web Application | Planned | Subphases 01–05 (Cognito + UI) |
| **PHASE_07** | AWS Serverless Production Deployment | Planned | Subphases 01–04 (Terraform IaC) |

---

## 2. Phase 00 Completion & Merged Milestones

Phase 00 Project Foundation is complete and fully merged into `master`:

| Subphase ID | Subphase Name | Branch | Status | PR Reference |
| :--- | :--- | :--- | :--- | :--- |
| **01** | Engineering Governance & Architecture Documentation | `phase-00/subphase-01-agentic-governance` | **Merged** | [PR #1](https://github.com/shubhojit-mitra-dev/ai-job-agent/pull/1) |
| **02** | Database Connectivity & Alembic Scaffolding | `milestone-01/agent-a-database` | **Merged** | [PR #3](https://github.com/shubhojit-mitra-dev/ai-job-agent/pull/3) |
| **03** | Auth Verification & Security Middleware | `milestone-01/agent-b-supabase-auth` | **Merged** | [PR #4](https://github.com/shubhojit-mitra-dev/ai-job-agent/pull/4) |
| **04** | Local Development Environment (Docker Compose) | `milestone-01/agent-c-docker-compose` | **Merged** | [PR #2](https://github.com/shubhojit-mitra-dev/ai-job-agent/pull/2) |
| **05** | CI/CD Quality Gates & Automated Workflows | `milestone-01/agent-e-qa-ci` | **Merged** | [PR #5](https://github.com/shubhojit-mitra-dev/ai-job-agent/pull/5) |
| **Consolidated** | **Milestone 1 — Complete Foundation Hardening** | `milestone-01/foundation` | **Merged** | [PR #6](https://github.com/shubhojit-mitra-dev/ai-job-agent/pull/6) |

---

## 3. Active Branches & Pull Requests

- **Default Branch**: `master` (Protected, clean; HEAD includes PR #6 merge)
- **Active Feature Branch**: `phase-01/aws-architecture-migration`
- **Current Target PR**: `docs(architecture): migrate platform architecture to AWS-native stack`
- **Merged PRs**:
  - [PR #1: Governance & Documentation](https://github.com/shubhojit-mitra-dev/ai-job-agent/pull/1)
  - [PR #2: Docker Compose & Local Environment](https://github.com/shubhojit-mitra-dev/ai-job-agent/pull/2)
  - [PR #3: Async Database, Base & Alembic pgvector](https://github.com/shubhojit-mitra-dev/ai-job-agent/pull/3)
  - [PR #4: Auth Verification & Protected Route](https://github.com/shubhojit-mitra-dev/ai-job-agent/pull/4)
  - [PR #5: CI Quality Gates & Shared Fixtures](https://github.com/shubhojit-mitra-dev/ai-job-agent/pull/5)
  - [PR #6: Milestone 1 Foundation Hardening](https://github.com/shubhojit-mitra-dev/ai-job-agent/pull/6)

---

## 4. Architectural Decision Records (ADRs) Status

| ADR ID | Title | Status | Description / Replacement |
| :--- | :--- | :--- | :--- |
| **ADR-001** | Modular Monolith Architecture | Accepted | Core application structuring principles |
| **ADR-002** | FastAPI on AWS Lambda via Mangum & ZIP | Accepted | Serverless backend execution in `ap-south-1` |
| **ADR-003** | Supabase Auth and PostgreSQL | **Superseded** | Superseded by ADR-013, ADR-014, and ADR-015 |
| **ADR-004** | SQLAlchemy 2.0 and Alembic | Accepted | Async relational ORM and migration versioning |
| **ADR-005** | SQS-Based Background Processing | Accepted | Decoupled asynchronous worker queue + DLQ |
| **ADR-006** | EventBridge Scheduler for Scheduled Workloads | Accepted | Cron triggers with explicit `Asia/Kolkata` timezone |
| **ADR-007** | Terraform for Infrastructure as Code | Accepted | Codified infrastructure with S3-native state locking |
| **ADR-008** | GitHub Actions with AWS OIDC | Accepted | Keyless, role-based cloud deployment authentication |
| **ADR-009** | BYOK Provider Abstraction for LLM Inference | Accepted | Candidate-supplied keys with AES-256-GCM encryption |
| **ADR-010** | Hybrid Job Retrieval & Deterministic Ranking | Accepted | Vector similarity + relational dealbreakers + scoring |
| **ADR-011** | Embedding Strategy & S3 Vectors Integration | Accepted | Amazon Titan Text Embeddings V2 + multilingual benchmark |
| **ADR-012** | Resume File Storage and Secure Access | Accepted | Private Amazon S3 with Block Public Access & pre-signed URLs |
| **ADR-013** | Amazon Cognito User Pools for Authentication | Accepted | Candidate auth, JWT authorizer, and tenant isolation |
| **ADR-014** | Aurora PostgreSQL Serverless v2 & Connectivity | Accepted | Relational DB; evaluated Data API vs asyncpg vs RDS Proxy |
| **ADR-015** | Amazon S3 Vectors for Vector Storage | Accepted | Scalable vector search decoupled from relational compute |
| **ADR-016** | Bedrock Foundation Model Integration & Resilience | Accepted | Titan models, account quota fallback, Anthropic excluded |

---

## 5. Known Issues & External Blockers

- **Amazon Bedrock Account Quota / Throttling Blocker**:
  - *Status*: External blocker under active resolution with AWS Support (official case open).
  - *Application Impact*: **Non-blocking for development**. In accordance with [ADR-016](../adr/ADR-016-bedrock-foundation-model-integration.md), the backend is decoupled via `ENABLE_BEDROCK=false`, allowing 100% of local development, LangGraph agent workflows, and CI test pipelines to execute using deterministic mocks (`FakeLLMClient`) and candidate BYOK integrations.

---

## 6. Next Authorized Task

Upon review and merge of `phase-01/aws-architecture-migration` into `master`:
- **Next Milestone / Subphase**: `PHASE_01` Subphase 01 — Candidate Profile Domain Models, Pydantic Schemas, and SQLAlchemy Migration.
