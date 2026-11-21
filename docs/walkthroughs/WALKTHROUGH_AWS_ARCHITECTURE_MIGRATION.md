# Walkthrough: AWS-Native Target Architecture Migration (Documentation & ADRs)

> **Subphase**: AWS-Native Architecture Migration Documentation & ADR Update  
> **Target Branch**: `phase-01/aws-architecture-migration`  
> **Status**: Completed, Prepared for Review  
> **Deliverable Type**: Documentation Only (Zero Runtime Code / Infrastructure Changes)  
> **Date**: 2026-11-21

---

## 1. Executive Summary & Objective

Following the human Technical Lead's architectural approval to migrate the AI Career Platform away from Supabase toward an **AWS-Native Architecture** co-located in `ap-south-1` (Mumbai), this documentation update establishes comprehensive, authoritative governance and architectural specifications across the entire repository.

This deliverable codifies the complete AWS-native target stack across all core technical documents, updates existing ADRs, introduces 4 new comprehensive ADRs (ADR-013 through ADR-016), updates the product specification and engineering guidelines, and updates the progress tracker.

### Strict Scope Boundary Confirmation
- **Zero Application Runtime Code Changes**: No application runtime logic in `apps/api/` or `apps/web/` was modified.
- **Zero Dependency Removals**: Existing libraries and lockfiles (`uv.lock`, `package-lock.json`) remain intact.
- **Zero Database Migration Changes**: Existing Alembic migrations remain untouched.
- **Zero Cloud Resource Provisioning**: No Terraform apply was executed; no live AWS cloud resources were created.
- **Existing Tests Remain 100% Passing**: The existing Phase 00 test suite (31 unit/integration tests) continues to pass cleanly.

---

## 2. Approved AWS-Native Target Architecture

The target architecture consolidates the platform on AWS serverless and managed cloud services in `ap-south-1`:

| Component | Technology | Architectural Specification |
| :--- | :--- | :--- |
| **Frontend** | Next.js 16 (App Router), TypeScript, Tailwind CSS | Responsive candidate web UI with Amazon Cognito client |
| **Backend** | FastAPI (Python 3.12), Pydantic v2, SQLAlchemy 2.0 | Async modular monolith running on AWS Lambda via Mangum |
| **API Perimeter** | AWS API Gateway HTTP API (v2) | Managed edge routing, TLS termination, and Cognito JWT Authorizer |
| **Authentication** | Amazon Cognito User Pools | Candidate auth, OTP email verification, and RS256 JWTs ([ADR-013](../adr/ADR-013-cognito-authentication.md)) |
| **Relational Database** | Amazon Aurora PostgreSQL Serverless v2 | Auto-scaling PostgreSQL 16 compute (0.5–2.0 ACU) in `ap-south-1` ([ADR-014](../adr/ADR-014-aurora-postgresql-serverless-v2.md)) |
| **Vector Storage** | Amazon S3 Vectors | Scalable vector indexing and ANN similarity search decoupled from DB compute ([ADR-015](../adr/ADR-015-s3-vectors-for-vector-storage.md)) |
| **Document Storage** | Private Amazon S3 | Resume PDF storage with Block Public Access and 15-min pre-signed URLs ([ADR-012](../adr/ADR-012-resume-file-storage-and-secure-access.md)) |
| **Asynchronous Tasks** | Amazon SQS + DLQ + Worker Lambda | Background task processing (batch size 1–10, 6x visibility timeout) ([ADR-005](../adr/ADR-005-sqs-background-processing.md)) |
| **Scheduled Workloads**| Amazon EventBridge Scheduler | Daily morning digest triggers configured in `Asia/Kolkata` timezone ([ADR-006](../adr/ADR-006-eventbridge-scheduler.md)) |
| **AI Orchestration** | LangGraph | Stateful directed graphs for career discovery and resume tailoring |
| **Foundation Models** | Amazon Bedrock (Titan Models) + Candidate BYOK | Amazon Titan models (pending quota case resolution) and candidate BYOK ([ADR-016](../adr/ADR-016-bedrock-foundation-model-integration.md)) |
| **Embeddings** | Amazon Titan Text Embeddings V2 | Multilingual embeddings decoupled from Lambda package size ([ADR-011](../adr/ADR-011-local-embedding-strategy-and-deployment-constraints.md)) |
| **IaC & CI/CD** | Terraform + GitHub Actions (AWS OIDC) | Codified infrastructure with S3-native state locking and role-based CI ([ADR-007](../adr/ADR-007-terraform-infrastructure-as-code.md), [ADR-008](../adr/ADR-008-github-actions-with-aws-oidc.md)) |

---

## 3. Key Architectural Decisions Codified

### 3.1. Amazon Cognito User Pools ([ADR-013](../adr/ADR-013-cognito-authentication.md))
- **Role**: Replaces Supabase Auth for candidate registration, OTP verification, login, password resets, and session management.
- **Verification Protocol**: Asymmetric RS256 token verification against Cognito's authoritative JWKS:
  `https://cognito-idp.ap-south-1.amazonaws.com/{userPoolId}/.well-known/jwks.json`.
- **Perimeter vs Application Responsibilities**:
  - *API Gateway HTTP API JWT Authorizer*: Rejects invalid/expired tokens at the cloud perimeter edge, preventing unauthenticated invocations from consuming Lambda execution time.
  - *FastAPI Authentication Middleware*: Validates token claims independently (defense in depth), extracts the candidate UUID (`sub`), and injects an authenticated `CurrentUser` dependency.
- **Authentication != Authorization**: Explicitly enforces that authentication proves *identity*, while application SQL queries enforce *authorization* (`WHERE user_id = current_user.id`).
- **Identity Mapping**: Relational candidate profile records use an internal primary key `user_id` mapped to `cognito_sub` to protect the domain from future auth migrations.

### 3.2. Amazon Aurora PostgreSQL Serverless v2 ([ADR-014](../adr/ADR-014-aurora-postgresql-serverless-v2.md))
- **Preservation of ORM & Migrations**: Retains 100% of existing SQLAlchemy 2.0 async models and Alembic migrations.
- **Rigorous Evaluation of Lambda Connectivity**:
  1. *RDS Data API over HTTPS*: Evaluated thoroughly. Concluded that Data API is **not** a drop-in replacement for `asyncpg`. It executes SQL via HTTP POST, requires non-standard dialects (`sqlalchemy-aurora-data-api`), lacks async streaming cursors, and introduces DDL migration friction.
  2. *Direct TCP via `asyncpg`*: Provides native SQLAlchemy 2.0 and Alembic compatibility. Requires Lambda in VPC private subnets; requires careful egress architecture (VPC Endpoints or out-of-VPC workers) to eliminate the ~\$32/month NAT Gateway cost. Uses `poolclass=NullPool` and concurrency limits.
  3. *RDS Proxy + VPC*: **Rejected for initial phase** due to fixed monthly charges (~**\$15–\$25/month**) and persistent connections that prevent Aurora Serverless v2 from auto-pausing to 0 ACUs.
- **Recommendation**: Local development continues using containerized PostgreSQL with `asyncpg`. Production runtime connects via `asyncpg` with `NullPool` and concurrency caps. Specific production network boundary is recorded as an active evaluation for Phase 07 Terraform deployment.

### 3.3. Amazon S3 Vectors for Vector Storage ([ADR-015](../adr/ADR-015-s3-vectors-for-vector-storage.md))
- **Separation of Concerns**: Strictly separates **embedding generation** (Amazon Bedrock Titan V2 / external providers) from **vector storage & indexing** (Amazon S3 Vectors). S3 Vectors is explicitly **not** an embedding generation model.
- **Index Organization**: Partitioned indexes for `job-vectors-index` and `candidate-vectors-index`.
- **Tenant Isolation**: Candidate vectors are isolated by candidate ID metadata tagging and partitioned namespace.
- **Two-Stage Hybrid Retrieval Pipeline**:
  - *Stage 1*: S3 Vectors retrieves top-100 nearest neighbor job IDs via cosine similarity.
  - *Stage 2*: Aurora PostgreSQL filters matching jobs by hard relational constraints (dealbreakers, CTC floor, experience, locations) and evaluates the deterministic match rubric.
- **Local Development**: Abstracted behind a `VectorStore` protocol; local runs and tests use `FakeVectorStore` (pure Python/NumPy cosine similarity, 0ms latency, zero cloud dependencies).
- **Multilingual Benchmark Mandate**: In Phase 02, the team will benchmark retrieval accuracy for Indian-context job titles, transliterated queries ("fresher bharti"), and bilingual text.

### 3.4. Private Amazon S3 Resume Storage ([ADR-012](../adr/ADR-012-resume-file-storage-and-secure-access.md))
- Formally accepted Private Amazon S3 as the authoritative document store.
- **Security Invariants**: Block Public Access (all 4 settings), SSE-KMS / SSE-S3 encryption at rest, TLS 1.2+ transport security, and candidate-scoped keys:
  `candidates/{user_id}/resumes/{resume_id}.pdf`.
- **Pre-Signed URLs**: Short-lived (15-minute) pre-signed PUT and GET URLs generated only after verifying candidate ownership.
- **File Validation**: 5 MB upload size limit, MIME type restrictions (PDF, DOCX), magic byte verification (`%PDF-`), and executable macro rejection.
- **Retention & Deletion**: 7-day abort for incomplete multipart uploads; complete purge of `candidates/{user_id}/*` on account deletion.

### 3.5. Amazon Bedrock & Resilience Abstraction ([ADR-016](../adr/ADR-016-bedrock-foundation-model-integration.md))
- **Target Models**: Amazon Titan foundation models (e.g. `amazon.titan-text-express-v1`).
- **Anthropic Exclusion**: Anthropic models are explicitly excluded from the planned production stack due to cost and licensing boundaries.
- **Resilience & Decoupling**:
  - Bedrock access is currently subject to an account-level quota blocker with an open AWS Support case.
  - Bedrock availability is **not** a blocker for application development.
  - Feature flag: `ENABLE_BEDROCK: bool = False`. The application falls back gracefully to `FakeLLMClient` or candidate BYOK providers without crashing.
- **BYOK Preservation**: Full preservation of candidate Bring Your Own Key architecture (NVIDIA NIM, Cloudflare Workers AI, OpenRouter, Gemini), encrypted at rest via AES-256-GCM envelope encryption.

---

## 4. Architectural Decision Records (ADRs) Summary

| ADR ID | Title | Status | Impact / Changes |
| :--- | :--- | :--- | :--- |
| **ADR-001** | Modular Monolith Architecture | Accepted | Reconfirmed core monolith architecture |
| **ADR-002** | FastAPI on AWS Lambda via Mangum & ZIP | Accepted | Reconfirmed serverless backend execution |
| **ADR-003** | Supabase Auth and PostgreSQL | **Superseded** | Marked Superseded; links to ADR-013, ADR-014, and ADR-015 |
| **ADR-004** | SQLAlchemy 2.0 and Alembic | Accepted | Updated relational context to Aurora PostgreSQL Serverless v2 |
| **ADR-005** | SQS-Based Background Processing | Accepted | Reconfirmed async task queue + DLQ |
| **ADR-006** | EventBridge Scheduler for Scheduled Workloads | Accepted | Updated database connection limit wording |
| **ADR-007** | Terraform for Infrastructure as Code | Accepted | Reconfirmed S3-native state locking |
| **ADR-008** | GitHub Actions with AWS OIDC | Accepted | Reconfirmed keyless cloud deployment |
| **ADR-009** | BYOK Provider Abstraction for LLM Inference | Accepted | Updated encryption target from Supabase to Aurora / local DB |
| **ADR-010** | Hybrid Job Retrieval & Deterministic Ranking | Accepted | Updated vector retrieval reference to Amazon S3 Vectors (ADR-015) |
| **ADR-011** | Embedding Strategy & S3 Vectors Integration | **Accepted** | Updated to Amazon Titan Text Embeddings V2 + multilingual benchmark |
| **ADR-012** | Resume File Storage and Secure Access | **Accepted** | Accepted Private Amazon S3 with Block Public Access & pre-signed URLs |
| **ADR-013** | Amazon Cognito User Pools for Authentication | **Accepted (New)** | Detailed Cognito JWT authorizer, JWKS verification, tenant isolation |
| **ADR-014** | Aurora PostgreSQL Serverless v2 & Connectivity | **Accepted (New)** | Evaluated Data API vs direct asyncpg vs RDS Proxy; recorded trade-offs |
| **ADR-015** | Amazon S3 Vectors for Vector Storage | **Accepted (New)** | Decoupled vector storage, two-stage hybrid retrieval, local fake |
| **ADR-016** | Bedrock Foundation Model Integration & Resilience | **Accepted (New)** | Titan models, account quota fallback, Anthropic excluded, BYOK |

---

## 5. Repository-Wide Supabase Reference Audit

Every mention of Supabase across the repository was inspected and classified into one of three categories:

1. **Historical / Preserved in Superseded ADRs**:
   - `docs/adr/ADR-003-supabase-auth-and-postgresql.md`: Preserved with explicit `Superseded Note (2026-11-21)` and links to replacement ADRs.
   - `docs/walkthroughs/WALKTHROUGH_PHASE_00_SUBPHASE_01.md` & `WALKTHROUGH_MILESTONE_01_FOUNDATION.md`: Retained as accurate audit logs of Phase 00 execution.
2. **Intentionally Retained for Existing Foundation Runtime Code**:
   - `apps/api/app/core/security.py`: Retains existing JWT verification functions created during Milestone 1. These serve as working, tested foundations and will be refactored to Cognito endpoints during Phase 01 authentication implementation.
   - `apps/api/app/core/config.py`: Retains configuration attributes matching the current runtime test suite.
   - `apps/api/tests/`: Unit and integration test suites validating existing token and session logic.
3. **Migrated in Active Documentation**:
   - `AGENTS.md`: Completely migrated to Aurora, S3 Vectors, Cognito, Bedrock.
   - `README.md`: Badges, tech stack table, and architecture links updated to AWS native.
   - `docs/ARCHITECTURE.md`: Complete overhaul of system diagrams, component boundaries, and data flows.
   - `docs/SECURITY.md`: Cognito JWKS verification, S3 security, and least-privilege DB roles.
   - `docs/COST_AND_OPERATIONS.md`: \$200 credit budget, Aurora scaling, NAT Gateway avoidance.
   - `docs/DEPLOYMENT.md`: AWS Lambda, API Gateway, Terraform modules, and CI/CD.
   - `docs/DEVELOPMENT_GUIDE.md`: 100% free local development without AWS credentials.
   - `docs/TESTING_STRATEGY.md`: Test pyramid with mock fixtures and zero live cloud API calls.
   - `docs/PRODUCT_SPEC.md`: Functional requirements updated for Cognito, S3, and S3 Vectors.
   - `docs/progress/PROGRESS.md`: Updated to reflect Milestone 1 merged and active AWS migration.
   - `docs/phases/PHASE_00_PROJECT_FOUNDATION.md`: Updated to completed status.
   - `.env.example`: Updated to document future AWS-native environment variables.

---

## 6. Local Development & Verification Results

### 6.1. Quality Gates Execution
The entire backend test and verification suite was executed to ensure zero regressions in existing code:
```bash
cd apps/api
uv run ruff check .
uv run ruff format --check .
uv run mypy .
uv run pytest -v
```
**Results**:
- **Ruff Lint**: `All checks passed!`
- **Ruff Format**: `29 files already formatted.`
- **Mypy Static Type Analysis**: `Success: no issues found in 26 source files.`
- **Pytest**: `31 passed, 1 skipped` (100% test pass rate).

### 6.2. Frontend Quality Gates Execution
```bash
cd apps/web
npm run lint
npm run build
```
**Results**:
- **ESLint**: Passed with zero errors.
- **Next.js 16 Production Build**: Compiled successfully in Turbopack; static pages generated cleanly.

---

## 7. Next Authorized Task

With the AWS-native target architecture documentation and ADRs established and verified, the next authorized milestone is:
- **Phase 01: Candidate Core & Resume Ingestion**
  - **Subphase 01**: Candidate Profile Domain Models, Pydantic Schemas, and SQLAlchemy Migration.

