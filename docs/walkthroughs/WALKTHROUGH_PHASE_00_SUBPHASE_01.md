# Walkthrough: Phase 00, Subphase 01 — Engineering Governance & Architecture Documentation

> **Subphase**: `PHASE_00_SUBPHASE_01`  
> **Subphase Name**: Engineering Governance, Architecture Documentation and AI-Agent Development System  
> **Branch**: `phase-00/subphase-01-agentic-governance`  
> **Author**: Senior Documentation and Architecture Engineer  
> **Status**: Completed (Ready for Review)

---

## 1. What Was Accomplished

In this subphase, we established a complete, professional, and self-documenting engineering governance environment for the **AI Career Platform** monorepo (`ai-job-agent`).

Key accomplishments:
1. **Established Authoritative Governance**: Authored root `AGENTS.md` and pointer `CLAUDE.md`, codifying mandatory reading order, modular monolith constraints, coding/testing standards, security rules, and PR lifecycle requirements.
2. **Updated Project Documentation**: Rewrote `README.md` to accurately reflect the product vision, current scaffolded status, and quickstart instructions without claiming unimplemented capabilities.
3. **Drafted Core Technical Specifications**:
   - `PRODUCT_SPEC.md`: Product vision, target Indian user personas, functional requirements, and strict MVP boundaries.
   - `ARCHITECTURE.md`: Modular monolith design, AWS serverless model (Lambda + Mangum + API Gateway HTTP API), SQS async task workers, EventBridge scheduling, and Supabase connection pooling safeguards.
   - `DEVELOPMENT_GUIDE.md`: Monorepo conventions, `uv` workflows, formatting, typing, and branch standards.
   - `TESTING_STRATEGY.md`: TDD cadence, deterministic mock testing for LLM workflows without live paid API calls, and isolated database fixtures.
   - `SECURITY.md`: Supabase Auth token validation, candidate resume PII protection, BYOK AES-GCM envelope encryption, and prompt injection defense.
   - `DEPLOYMENT.md`: Infrastructure topology in AWS `ap-south-1` (Mumbai), Terraform IaC, and GitHub Actions OIDC (no static cloud keys).
   - `COST_AND_OPERATIONS.md`: Cost management policies (strictly no EC2, no NAT Gateways, no ElastiCache, no RDS), CloudWatch log retention rules, and budget alerts.
4. **Codified Architectural Decision Records**: Created ADR-001 through ADR-012 with strictly accurate statuses (`Accepted` vs `Proposed` for ADR-011).
5. **Formulated Phase & Subphase Management**:
   - Outlined 5 subphases for `PHASE_00` in `docs/phases/PHASE_00_PROJECT_FOUNDATION.md`.
   - Detailed only the active subphase in `docs/subphases/PHASE_00_SUBPHASE_01_AGENTIC_GOVERNANCE.md`.
6. **Initialized Progress & Tracking**: Initialized live tracking in `docs/progress/PROGRESS.md`.
7. **Strict Scope Discipline**: Zero modifications were made to existing application code (`apps/api/app/main.py`), and no database or cloud resources were touched.

---

## 2. File Changes Summary

### Root Files Created / Modified
- [AGENTS.md](file:///home/blackknight05/Desktop/ai-job-agent/AGENTS.md): Authoritative instructions for all coding agents.
- [CLAUDE.md](file:///home/blackknight05/Desktop/ai-job-agent/CLAUDE.md): Direct pointer to `AGENTS.md`.
- [README.md](file:///home/blackknight05/Desktop/ai-job-agent/README.md): Professional project README with architecture and setup details.

### Core Architecture & Governance Documentation Created
- [docs/PRODUCT_SPEC.md](file:///home/blackknight05/Desktop/ai-job-agent/docs/PRODUCT_SPEC.md)
- [docs/ARCHITECTURE.md](file:///home/blackknight05/Desktop/ai-job-agent/docs/ARCHITECTURE.md)
- [docs/DEVELOPMENT_GUIDE.md](file:///home/blackknight05/Desktop/ai-job-agent/docs/DEVELOPMENT_GUIDE.md)
- [docs/TESTING_STRATEGY.md](file:///home/blackknight05/Desktop/ai-job-agent/docs/TESTING_STRATEGY.md)
- [docs/SECURITY.md](file:///home/blackknight05/Desktop/ai-job-agent/docs/SECURITY.md)
- [docs/DEPLOYMENT.md](file:///home/blackknight05/Desktop/ai-job-agent/docs/DEPLOYMENT.md)
- [docs/COST_AND_OPERATIONS.md](file:///home/blackknight05/Desktop/ai-job-agent/docs/COST_AND_OPERATIONS.md)

### Architectural Decision Records Created (`docs/adr/`)
- [ADR-001: Modular Monolith Architecture](file:///home/blackknight05/Desktop/ai-job-agent/docs/adr/ADR-001-modular-monolith-architecture.md) (Accepted)
- [ADR-002: FastAPI Deployment on AWS Lambda Using Mangum and ZIP Packaging](file:///home/blackknight05/Desktop/ai-job-agent/docs/adr/ADR-002-fastapi-aws-lambda-mangum-zip.md) (Accepted)
- [ADR-003: Supabase Auth and PostgreSQL](file:///home/blackknight05/Desktop/ai-job-agent/docs/adr/ADR-003-supabase-auth-and-postgresql.md) (Accepted)
- [ADR-004: SQLAlchemy 2.0 and Alembic](file:///home/blackknight05/Desktop/ai-job-agent/docs/adr/ADR-004-sqlalchemy-2-and-alembic.md) (Accepted)
- [ADR-005: SQS-Based Background Processing](file:///home/blackknight05/Desktop/ai-job-agent/docs/adr/ADR-005-sqs-background-processing.md) (Accepted)
- [ADR-006: EventBridge Scheduler for Scheduled Workloads](file:///home/blackknight05/Desktop/ai-job-agent/docs/adr/ADR-006-eventbridge-scheduler.md) (Accepted)
- [ADR-007: Terraform for Infrastructure as Code](file:///home/blackknight05/Desktop/ai-job-agent/docs/adr/ADR-007-terraform-infrastructure-as-code.md) (Accepted)
- [ADR-008: GitHub Actions with AWS OIDC](file:///home/blackknight05/Desktop/ai-job-agent/docs/adr/ADR-008-github-actions-with-aws-oidc.md) (Accepted)
- [ADR-009: BYOK Provider Abstraction for LLM Inference](file:///home/blackknight05/Desktop/ai-job-agent/docs/adr/ADR-009-byok-provider-abstraction.md) (Accepted)
- [ADR-010: Hybrid Job Retrieval and Deterministic Recommendation Ranking](file:///home/blackknight05/Desktop/ai-job-agent/docs/adr/ADR-010-hybrid-job-retrieval-and-deterministic-ranking.md) (Accepted)
- [ADR-011: Local Embedding Strategy and Its Deployment Constraints](file:///home/blackknight05/Desktop/ai-job-agent/docs/adr/ADR-011-local-embedding-strategy-and-deployment-constraints.md) (Proposed)
- [ADR-012: Resume File Storage and Secure Access](file:///home/blackknight05/Desktop/ai-job-agent/docs/adr/ADR-012-resume-file-storage-and-secure-access.md) (Accepted)

### Phase & Progress Documentation Created
- [docs/phases/PHASE_00_PROJECT_FOUNDATION.md](file:///home/blackknight05/Desktop/ai-job-agent/docs/phases/PHASE_00_PROJECT_FOUNDATION.md)
- [docs/subphases/PHASE_00_SUBPHASE_01_AGENTIC_GOVERNANCE.md](file:///home/blackknight05/Desktop/ai-job-agent/docs/subphases/PHASE_00_SUBPHASE_01_AGENTIC_GOVERNANCE.md)
- [docs/progress/PROGRESS.md](file:///home/blackknight05/Desktop/ai-job-agent/docs/progress/PROGRESS.md)
- [docs/walkthroughs/WALKTHROUGH_PHASE_00_SUBPHASE_01.md](file:///home/blackknight05/Desktop/ai-job-agent/docs/walkthroughs/WALKTHROUGH_PHASE_00_SUBPHASE_01.md)

---

## 3. Important Implementation & Architectural Decisions

### 3.1. Supabase Transaction Pooler & Serverless SQLAlchemy
In [docs/ARCHITECTURE.md](file:///home/blackknight05/Desktop/ai-job-agent/docs/ARCHITECTURE.md) and [ADR-003](file:///home/blackknight05/Desktop/ai-job-agent/docs/adr/ADR-003-supabase-auth-and-postgresql.md), we established critical connection rules for AWS Lambda execution:
- **Port 6543 (Transaction Mode)**: The serverless application runtime connects to Supabase PgBouncer/Supavisor on port 6543 with `poolclass=NullPool`.
- **Prepared Statement Workaround**: `asyncpg` caches prepared statements by default. Because PgBouncer in transaction mode assigns arbitrary backend connections to each transaction, cached prepared statements cause fatal `"prepared statement does not exist"` errors. The engine must enforce `connect_args={"statement_cache_size": 0}`.
- **Direct Port 5432 for Alembic**: Alembic migrations require session locks and transaction-level DDL commands that are unsupported in transaction pooling mode. Alembic connects directly to port 5432 outside the Lambda runtime.

### 3.2. Local Embedding Strategy Constraints (ADR-011)
In [ADR-011](file:///home/blackknight05/Desktop/ai-job-agent/docs/adr/ADR-011-local-embedding-strategy-and-deployment-constraints.md), we documented the packaging constraints of AWS Lambda:
- Uncompressed ZIP archives cannot exceed **250 MB**.
- Standard PyTorch wheels exceed 400 MB.
- Therefore, we marked ADR-011 as **Proposed** and documented the trade-off investigation: using ONNX Runtime with FastEmbed CPU wheels (< 80 MB) running strictly inside the asynchronous SQS Worker Lambda, protecting the API Gateway Lambda from dependency bloat.

### 3.3. Deterministic Matching vs. LLM Scoring (ADR-010)
In [ADR-010](file:///home/blackknight05/Desktop/ai-job-agent/docs/adr/ADR-010-hybrid-job-retrieval-and-deterministic-ranking.md), we rejected using raw LLM calls for calculating recommendation match scores. Instead, we codified a deterministic 0–100% rubric (Skills 40%, Domain 25%, Experience 20%, Location 15%) combined with binary dealbreaker disqualifiers, utilizing the LLM solely to generate structured explanations of the score.

---

## 4. Document Interrelationships & Reading Order

The documentation suite forms a coherent hierarchy:

```mermaid
graph TD
    AGENTS["AGENTS.md<br/>(Authoritative Governance)"] --> PROGRESS["docs/progress/PROGRESS.md<br/>(Live Status & Next Tasks)"]
    AGENTS --> PHASES["docs/phases/PHASE_00_PROJECT_FOUNDATION.md<br/>(Phase Roadmap)"]
    PHASES --> SUBPHASES["docs/subphases/PHASE_00_SUBPHASE_01_AGENTIC_GOVERNANCE.md<br/>(Current Active Scope)"]
    AGENTS --> ARCH["docs/ARCHITECTURE.md<br/>(System & AWS Architecture)"]
    AGENTS --> SPEC["docs/PRODUCT_SPEC.md<br/>(Requirements & User Personas)"]
    ARCH --> ADRS["docs/adr/<br/>(ADR-001 through ADR-012)"]
    AGENTS --> DEV["docs/DEVELOPMENT_GUIDE.md<br/>(Workflows & Commands)"]
    AGENTS --> TEST["docs/TESTING_STRATEGY.md<br/>(TDD & Mocking)"]
    AGENTS --> SEC["docs/SECURITY.md<br/>(Auth, BYOK & PII Protection)"]
    AGENTS --> DEP["docs/DEPLOYMENT.md<br/>(Serverless & Terraform)"]
    AGENTS --> COST["docs/COST_AND_OPERATIONS.md<br/>(FinOps & Budget Guards)"]
```

---

## 5. Verification Performed & Validation Results

1. **File Cross-Link Verification**:
   - Verified that all relative and absolute Markdown file links point to existing files.
2. **Mermaid Diagram Validation**:
   - Verified that all Mermaid diagrams in `docs/PRODUCT_SPEC.md`, `docs/ARCHITECTURE.md`, `docs/TESTING_STRATEGY.md`, `docs/SECURITY.md`, `docs/DEPLOYMENT.md`, and this walkthrough use valid supported diagram syntax (`flowchart`, `sequenceDiagram`, `stateDiagram-v2`).
3. **Application Code Integrity**:
   - Ran `git status` to ensure zero existing application code was modified.
   - Tested FastAPI `/health` endpoint to ensure application continues to function cleanly:
     ```bash
     cd apps/api && uv run python -c "from app.main import app; from starlette.testclient import TestClient; client = TestClient(app); res = client.get('/health'); assert res.status_code == 200"
     ```
     Result: **Verified Clean (HTTP 200)**.
4. **Scope Adherence**:
   - Zero database engines, models, migrations, or AWS resources were implemented.
   - All work was strictly confined to documentation and governance.

---

## 6. Commit & Pull Request Readiness

- PR: [GitHub PR #1](https://github.com/shubhojit-mitra-dev/ai-job-agent/pull/1)
- Branch: `phase-00/subphase-01-agentic-governance`
- Atomic documentation commits prepared and pushed to origin.
