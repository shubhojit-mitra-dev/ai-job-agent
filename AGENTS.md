# AGENTS.md — Authoritative Engineering Governance & Agent System Instructions

> **Notice for all AI Coding Agents**:  
> This file is the single, non-negotiable source of truth for engineering governance, architectural constraints, development standards, and coding workflows in this repository.  
> You must read, understand, and strictly adhere to all instructions herein before initiating any work.

---

## 1. Project Identity and Purpose

- **Project Description**: AI Career Platform — an India-first, open-source, candidate-centric career discovery platform designed for Indian students, fresh graduates, and professionals.
- **Core Mission**: Empower job seekers with transparent candidate-job matching, AI-assisted career goal discovery, tailored resume suggestions without fabrication, persistent preferences, and personalized daily digests.
- **Architecture Paradigm**: Modular Monolith on an AWS-Native Serverless / Managed Cloud foundation (FastAPI on AWS Lambda via Mangum, Next.js on frontend, Amazon Aurora PostgreSQL Serverless v2, Amazon S3 Vectors, Amazon Cognito User Pools, Amazon Bedrock / BYOK).
- **Governance**: You operate under a human Technical Lead. The human is the final authority for architectural decisions, scope approvals, and merging PRs. You must work methodically, inspect existing code before acting, avoid unnecessary abstractions, and never implement work outside the authorized subphase scope.

---

## 2. Mandatory Documentation Reading Order

Before proposing or executing changes, agents must consult project documentation in the following sequence:

1. [AGENTS.md](./AGENTS.md) (This file — governance, conventions, definition of done)
2. [docs/progress/PROGRESS.md](./docs/progress/PROGRESS.md) (Current phase, subphase status, active branches, known issues)
3. [docs/phases/PHASE_00_PROJECT_FOUNDATION.md](./docs/phases/PHASE_00_PROJECT_FOUNDATION.md) (Completed foundation milestones)
4. Specific subphase specification in `docs/subphases/` for your active task
5. [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md) (System architecture, data flows, integration constraints)
6. [docs/PRODUCT_SPEC.md](./docs/PRODUCT_SPEC.md) (Functional requirements, user personas, boundaries)
7. [docs/adr/](./docs/adr/) (Architectural Decision Records ADR-001 ... ADR-016)
8. [docs/DEVELOPMENT_GUIDE.md](./docs/DEVELOPMENT_GUIDE.md), [docs/TESTING_STRATEGY.md](./docs/TESTING_STRATEGY.md), [docs/SECURITY.md](./docs/SECURITY.md), and [docs/COST_AND_OPERATIONS.md](./docs/COST_AND_OPERATIONS.md)

---

## 3. Monorepo Structure

```text
ai-job-agent/
├── apps/
│   ├── api/                 # FastAPI backend (Python 3.12, uv, Mangum adapter)
│   │   ├── app/             # Application source tree
│   │   │   ├── api/v1/      # REST API route handlers (existing)
│   │   │   ├── core/        # Core configuration, security, telemetry (existing)
│   │   │   ├── db/          # Database engine, session lifecycle, base models (existing)
│   │   │   ├── modules/     # Domain business logic (existing auth module, planned modules)
│   │   │   ├── schemas/     # Domain Pydantic request/response schemas (existing)
│   │   │   └── main.py      # FastAPI application entrypoint & /health route (existing)
│   │   ├── tests/           # Automated test suite (unit and integration tests) (existing)
│   │   ├── pyproject.toml   # Python package definitions and dependency pins (existing)
│   │   └── uv.lock          # Cryptographic dependency lockfile (existing)
│   └── web/                 # Next.js frontend (TypeScript, Tailwind CSS, App Router) (existing)
│       ├── src/app/         # Next.js App Router pages and layouts (existing)
│       ├── public/          # Static assets (existing)
│       └── AGENTS.md        # Next.js-specific framework agent guidance (existing)
├── docs/                    # Authoritative engineering, architecture, and phase documentation (existing)
│   ├── adr/                 # Architectural Decision Records (ADR-001 ... ADR-016) (existing)
│   ├── phases/              # High-level phase roadmaps (existing)
│   ├── subphases/           # Detailed per-subphase implementation plans (existing)
│   ├── progress/            # PROGRESS.md tracking file (existing)
│   └── walkthroughs/        # Post-subphase audit walkthroughs (existing)
├── infra/                   # Infrastructure definitions (existing)
│   ├── docker/              # Local Docker Compose test container definitions (existing)
│   └── terraform/           # AWS Infrastructure as Code (planned)
├── packages/                # Shared monorepo packages (planned)
│   └── shared-schemas/      # Shared cross-boundary schema definitions (planned)
├── .env.example             # Documented template for local environment variables (existing)
├── .gitignore               # Strict ignore rules for environments, builds, and artifacts (existing)
├── CLAUDE.md                # Direct pointer to AGENTS.md (existing)
└── README.md                # Human-friendly repository overview and setup guide (existing)
```

---

## 4. Approved Architectural Constraints

All code must comply with approved Architectural Decision Records ([docs/adr/](./docs/adr/)):

1. **Modular Monolith**: Clean domain boundaries within `apps/api/app/modules/`. No arbitrary microservices, separate RPC daemons, or unnecessary message brokers ([ADR-001](./docs/adr/ADR-001-modular-monolith-architecture.md)).
2. **FastAPI on AWS Lambda**: Serverless backend packaging via ZIP deployed to AWS Lambda in `ap-south-1` (Mumbai) fronted by AWS API Gateway HTTP API and Mangum ASGI adapter ([ADR-002](./docs/adr/ADR-002-fastapi-aws-lambda-mangum-zip.md)).
3. **Database Engine & Pooling**:
   - **Amazon Aurora PostgreSQL Serverless v2** (PostgreSQL 16 compatible) in `ap-south-1` ([ADR-014](./docs/adr/ADR-014-aurora-postgresql-serverless-v2.md)).
   - SQLAlchemy 2.0 with `asyncpg` for application runtime ([ADR-004](./docs/adr/ADR-004-sqlalchemy-2-and-alembic.md)).
   - For serverless AWS Lambda execution: use `NullPool` to prevent connection leaks across ephemeral instances, and set `statement_cache_size=0`.
   - Alembic runs exclusively outside Lambda cold starts (CI/CD pipeline or migration runner) connecting directly to port 5432 with administrative credentials.
   - Lambda connectivity follows the evaluation in [ADR-014](./docs/adr/ADR-014-aurora-postgresql-serverless-v2.md).
4. **Authentication, Authorization & Database Isolation**:
   - **Amazon Cognito User Pools** issues JWT access tokens upon candidate login ([ADR-013](./docs/adr/ADR-013-cognito-authentication.md)).
   - API Gateway HTTP API JWT Authorizer validates tokens at the perimeter edge.
   - FastAPI verifies JWT signatures (via Cognito JWKS), issuer, client ID/audience, and expiry on protected routes, extracting the authenticated candidate ID (`sub`).
   - SQLAlchemy connects to PostgreSQL using application credentials. Application SQL queries must enforce strict tenant isolation (`WHERE user_id = current_user.id`).
   - Note: Direct SQLAlchemy connections do **not** inherit authentication context automatically. Defense in depth is provided by least-privileged database roles and/or setting transaction-scoped context variables (`SET LOCAL app.current_user_id = :authenticated_user_id`) inside each transaction.
5. **Asynchronous Background Processing**:
   - Heavy background tasks (resume parsing, batch job scraping, email digest generation) are dispatched to Amazon SQS queues ([ADR-005](./docs/adr/ADR-005-sqs-background-processing.md)).
   - Dedicated worker Lambdas process SQS events idempotently with Dead-Letter Queues (DLQ).
   - SQS visibility timeout must be configured to at least six times the Lambda function timeout, accounting for batch windows and retry behavior.
   - EventBridge Scheduler manages cron-like recurring triggers configured explicitly with timezone `Asia/Kolkata` (e.g. daily morning digests at 06:00 AM IST) ([ADR-006](./docs/adr/ADR-006-eventbridge-scheduler.md)).
6. **Vector Search & Document Storage**:
   - **Amazon S3 Vectors** manages vector indexing and approximate nearest neighbor (ANN) similarity search for candidates and jobs ([ADR-015](./docs/adr/ADR-015-s3-vectors-for-vector-storage.md)).
   - **Private Amazon S3** in `ap-south-1` stores candidate resume documents with Block Public Access, SSE-KMS encryption, candidate-scoped keys, and short-lived (15-minute) pre-signed URLs ([ADR-012](./docs/adr/ADR-012-resume-file-storage-and-secure-access.md)).
7. **AI & Agent Architecture**:
   - LangGraph orchestrates multi-step career agent workflows via stateful directed graphs.
   - Foundation model inference leverages **Amazon Bedrock** (Amazon Titan models) with graceful fallback and resilience abstractions ([ADR-016](./docs/adr/ADR-016-bedrock-foundation-model-integration.md)). Note: Bedrock access is currently subject to an account-level quota blocker with an open AWS Support case; the application must decouple from Bedrock via `ENABLE_BEDROCK=false` and use fake providers or candidate BYOK.
   - **Anthropic models are explicitly excluded** from the planned inference stack.
   - **Bring Your Own Key (BYOK)** architecture allows candidates to connect personal keys (NVIDIA NIM, Cloudflare Workers AI, OpenRouter, Gemini), encrypted at rest via AES-256-GCM envelope encryption ([ADR-009](./docs/adr/ADR-009-byok-provider-abstraction.md)).
   - Candidate resumes and job descriptions are treated as untrusted input. Delimiters provide context separation but are not security boundaries. LLM outputs must never independently authorize privileged actions.
   - Embedding generation uses Amazon Titan Text Embeddings V2 as the initial candidate ([ADR-011](./docs/adr/ADR-011-local-embedding-strategy-and-deployment-constraints.md)), decoupled from S3 Vectors storage.
8. **Prohibited Infrastructure**:
   - Do NOT introduce EC2 instances, Kubernetes/EKS, NAT Gateways without explicit authorization, ElastiCache/Redis clusters, RDS Proxy (avoids fixed monthly cost), OpenSearch Serverless, or always-on servers ([docs/COST_AND_OPERATIONS.md](./docs/COST_AND_OPERATIONS.md)).

---

## 5. Coding & Implementation Standards

### Python (Backend)
- **Formatting & Linting**: Ruff enforces code style, formatting, and linting rules (`ruff check .`, `ruff format --check .`).
- **Type Safety**: Mypy enforces strict static typing on all models, signatures, and functions (`mypy .`).
- **Pydantic v2**: Strict validation models for all I/O schemas with explicit Field descriptions and validation bounds.
- **Dependency Management**: `uv` exclusively manages Python packages (`uv add`, `uv run`). Never invoke `pip install` or create unmanaged `.venv` directories.

### TypeScript / Next.js (Frontend)
- **Framework Conventions**: Next.js App Router with TypeScript and Tailwind CSS.
- **Rules Preservation**: Always preserve `apps/web/AGENTS.md` generated guidance regarding Next.js 16 breaking changes.
- **Component Design**: Modular, accessible, server-component-first where appropriate, strictly typed interfaces.

---

## 6. Testing Strategy & TDD Workflow

We adhere strictly to Test-Driven Development (TDD) for all application code:

1. **Test-First Cadence**:
   - Write failing unit/integration tests covering acceptance criteria.
   - Run tests to verify expected failure.
   - Implement the minimal clean solution.
   - Verify tests pass.
   - Refactor cleanly.
2. **LLM & AWS Workflow Testing**:
   - Never call live, paid external LLM or cloud APIs inside automated test suites.
   - Use deterministic mock fixtures (`FakeLLMClient`, `FakeVectorStore`, `FakeEmbeddingProvider`).
   - Test for malicious inputs, prompt injection attempts, and tool authorization guards.
3. **Database Testing**:
   - Test queries against ephemeral local PostgreSQL containers or transactional rollback fixtures.
4. **Test Integrity**:
   - Never weaken, disable, or delete a failing test to make a pipeline pass. Investigate and fix the true root cause.

---

## 7. Security & Privacy Mandates

- **Sensitive Data Handling**: Candidate resumes contain Personal Identifiable Information (PII). Resumes are stored in Private Amazon S3 with Block Public Access, candidate-scoped keys (`candidates/{user_id}/resumes/{resume_id}.pdf`), and short-lived pre-signed URLs.
- **BYOK Key Protection**: User LLM keys must be encrypted at rest using authenticated symmetric encryption (AES-256-GCM). Never log or display plaintext API keys.
- **Prompt Injection Defense**: Untrusted text from user resumes or external job postings must be encapsulated with boundary delimiters. LLMs must not possess autonomous authority to perform privileged state mutations without external authorization checks.
- **SSRF Prevention**: All external job scraping and links must validate protocol (`https` only), restrict destinations to trusted hosts, and prevent loopback/internal IP requests.

---

## 8. Git, Branching, and PR Governance

- **Default Branch**: `master`.
- **Branch Protection**: Never commit or push directly to `master`. Never force-push (`git push -f`) without explicit authorization.
- **Subphase Branch Naming**:
  ```text
  phase-XX/subphase-YY-short-description
  ```
  *Example*: `phase-01/subphase-01-candidate-schema`
- **Commit Standards**: Conventional Commits format:
  ```text
  feat(module): add job search filter
  fix(auth): correct token expiry validation
  docs(adr): add ADR-014 for Aurora PostgreSQL
  test(agent): add deterministic mock tests for goal parser
  ```
- **Pull Request Lifecycle**:
  1. Complete authorized subphase scope.
  2. Verify all linter, typecheck, and test commands pass locally.
  3. Generate a comprehensive walkthrough document in `docs/walkthroughs/`.
  4. Update `docs/progress/PROGRESS.md`.
  5. Push the dedicated subphase branch and create a GitHub Pull Request against `master`.
  6. Await human Technical Lead review and approval. Do not merge your own PR.

---

## 9. Definition of Done (DoD)

A subphase is considered complete **only** when all of the following conditions are met:

1. All specific acceptance criteria in the subphase specification are satisfied.
2. Automated tests (unit, integration, or contract) are implemented and 100% passing.
3. Code passes static typing (`mypy`), linting (`ruff`), and formatting checks.
4. No architectural constraints, security rules, or approved ADRs are violated.
5. `docs/progress/PROGRESS.md` is accurately updated reflecting completed work.
6. A detailed post-subphase walkthrough document is written in `docs/walkthroughs/`.
7. A GitHub Pull Request is opened with clear context and test evidence, awaiting human review.

---

## 10. Rules for Using Agent Skills & Investigating Errors

- **Skill Usage**: Global agent skills must be installed with `-g` outside the repository tree. Never commit skill directories or caches into the repository.
- **Error Investigation Protocol**:
  1. Read full error outputs, tracebacks, and exit codes.
  2. Pinpoint the exact file, line number, and function causing the failure.
  3. Determine the structural root cause rather than treating symptoms.
  4. Formulate the smallest correct fix with regression tests.
  5. Do not blind-retry commands or mask errors with loose exception catching.
