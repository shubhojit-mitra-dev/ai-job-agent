# AGENTS.md — Authoritative Engineering Governance & Agent System Instructions

> **Notice for all AI Coding Agents**:  
> This file is the single, non-negotiable source of truth for engineering governance, architectural constraints, development standards, and coding workflows in this repository.  
> You must read, understand, and strictly adhere to all instructions herein before initiating any work.

---

## 1. Project Identity and Purpose

- **Project Description**: AI Career Platform — an India-first, open-source, candidate-centric career discovery platform designed for Indian students, fresh graduates, and professionals.
- **Core Mission**: Empower job seekers with transparent candidate-job matching, AI-assisted career goal discovery, tailored resume suggestions without fabrication, persistent preferences, and personalized daily digests.
- **Architecture Paradigm**: Modular Monolith on a Serverless / Managed Cloud foundation (FastAPI on AWS Lambda via Mangum, Next.js on frontend, Supabase PostgreSQL with `pgvector`).
- **Governance**: You operate under a human Technical Lead. The human is the final authority for architectural decisions, scope approvals, and merging PRs. You must work methodically, inspect existing code before acting, avoid unnecessary abstractions, and never implement work outside the authorized subphase scope.

---

## 2. Mandatory Documentation Reading Order

Before proposing or executing changes, agents must consult project documentation in the following sequence:

1. [AGENTS.md](file:///home/blackknight05/Desktop/ai-job-agent/AGENTS.md) (This file — governance, conventions, definition of done)
2. [docs/progress/PROGRESS.md](file:///home/blackknight05/Desktop/ai-job-agent/docs/progress/PROGRESS.md) (Current phase, subphase status, active branches, known issues)
3. [docs/phases/PHASE_00_PROJECT_FOUNDATION.md](file:///home/blackknight05/Desktop/ai-job-agent/docs/phases/PHASE_00_PROJECT_FOUNDATION.md) (Current phase milestones)
4. Specific subphase specification in `docs/subphases/` for your active task
5. [docs/ARCHITECTURE.md](file:///home/blackknight05/Desktop/ai-job-agent/docs/ARCHITECTURE.md) (System architecture, data flows, integration constraints)
6. [docs/PRODUCT_SPEC.md](file:///home/blackknight05/Desktop/ai-job-agent/docs/PRODUCT_SPEC.md) (Functional requirements, user personas, boundaries)
7. [docs/adr/](file:///home/blackknight05/Desktop/ai-job-agent/docs/adr/) (Architectural Decision Records relevant to your domain)
8. [docs/DEVELOPMENT_GUIDE.md](file:///home/blackknight05/Desktop/ai-job-agent/docs/DEVELOPMENT_GUIDE.md), [docs/TESTING_STRATEGY.md](file:///home/blackknight05/Desktop/ai-job-agent/docs/TESTING_STRATEGY.md), and [docs/SECURITY.md](file:///home/blackknight05/Desktop/ai-job-agent/docs/SECURITY.md)

---

## 3. Monorepo Structure

```text
ai-job-agent/
├── apps/
│   ├── api/                 # FastAPI backend (Python 3.12, uv, Mangum adapter)
│   │   ├── app/
│   │   │   ├── api/v1/      # REST API route handlers
│   │   │   ├── core/        # Core configuration, security, telemetry
│   │   │   ├── db/          # Database engine, session lifecycle, base models
│   │   │   ├── modules/     # Domain business logic (candidate, jobs, matching, agent)
│   │   │   ├── schemas/     # Domain Pydantic request/response schemas
│   │   │   └── main.py      # FastAPI application entrypoint & ASGI lifespan
│   │   ├── tests/           # Unit, integration, and contract test suites
│   │   ├── pyproject.toml   # Python package definitions and dependency pins
│   │   └── uv.lock          # Cryptographic dependency lockfile
│   └── web/                 # Next.js frontend (TypeScript, Tailwind CSS, App Router)
│       ├── src/app/         # Next.js App Router pages and layouts
│       ├── public/          # Static assets
│       └── AGENTS.md        # Next.js-specific framework agent guidance (preserved)
├── docs/                    # Authoritative engineering, architecture, and phase documentation
│   ├── adr/                 # Architectural Decision Records (ADR-001 ... ADR-012)
│   ├── phases/              # High-level phase roadmaps
│   ├── subphases/           # Detailed per-subphase implementation plans
│   ├── progress/            # PROGRESS.md tracking file
│   └── walkthroughs/        # Post-subphase audit walkthroughs
├── infra/
│   ├── docker/              # Local Docker Compose & test container definitions
│   ├── supabase/            # Supabase schema definitions and local config
│   └── terraform/           # AWS Infrastructure as Code (planned)
├── packages/
│   └── shared-schemas/      # Shared cross-boundary schema definitions
├── .env.example             # Documented template for local environment variables
├── .gitignore               # Strict ignore rules for environments, builds, and artifacts
├── CLAUDE.md                # Direct pointer to AGENTS.md
└── README.md                # Human-friendly repository overview and setup guide
```

---

## 4. Approved Architectural Constraints

All code must comply with approved Architectural Decision Records ([docs/adr/](file:///home/blackknight05/Desktop/ai-job-agent/docs/adr/)):

1. **Modular Monolith**: Clean domain boundaries within `apps/api/app/modules/`. No arbitrary microservices, separate RPC daemons, or unnecessary message brokers.
2. **FastAPI on AWS Lambda**: Serverless backend packaging via ZIP deployed to AWS Lambda in `ap-south-1` (Mumbai) fronted by AWS API Gateway HTTP API and Mangum ASGI adapter.
3. **Database Engine & Pooling**:
   - Supabase PostgreSQL with `pgvector` for vector similarity.
   - SQLAlchemy 2.0 with `asyncpg` for application runtime.
   - For serverless AWS Lambda execution: use `NullPool` to prevent connection leaks across ephemeral instances, connect to Supabase Transaction Pooler (port 6543), and enforce `statement_cache_size=0` on `asyncpg` connect args because transaction poolers disallow prepared statement caching.
   - Alembic runs exclusively outside Lambda cold starts (CI/CD pipeline or migration runner) connecting directly to port 5432 (Session mode) with administrative credentials.
4. **Authentication & Authorization**:
   - Supabase Auth issues JWT access tokens.
   - FastAPI verifies JWT signatures and claims on protected routes; SQLAlchemy queries strictly enforce user tenancy (`WHERE user_id = current_user.id`).
5. **Asynchronous Background Processing**:
   - Heavy background tasks (resume parsing, batch job scraping, email digest generation) are dispatched to AWS SQS queues.
   - Dedicated worker Lambdas process SQS events idempotently with Dead-Letter Queues (DLQ).
   - EventBridge Scheduler manages cron-like recurring triggers (e.g. daily morning digests).
6. **AI & Agent Architecture**:
   - LangGraph orchestrates multi-step career agent workflows via stateful directed graphs.
   - Bring Your Own Key (BYOK) architecture for LLM providers (NVIDIA NIM, Cloudflare Workers AI, OpenRouter, Gemini).
   - Candidate API keys are encrypted at rest using AES-GCM envelope encryption before persistence.
   - Local/open-source Sentence Transformers embeddings are evaluated under strict Lambda bundle size limits (250MB uncompressed limit).
7. **Prohibited Infrastructure**:
   - Do NOT introduce EC2 instances, Kubernetes/EKS, NAT Gateways without explicit approval, ElastiCache/Redis clusters, RDS instances, or always-on servers.

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
2. **LLM Workflow Testing**:
   - Never call live, paid external LLM APIs inside automated test suites.
   - Use deterministic mock fixtures, synthetic test resumes/job postings, and fake provider interfaces.
3. **Database Testing**:
   - Test queries against ephemeral local PostgreSQL containers or transactional rollback fixtures.
4. **Test Integrity**:
   - Never weaken, disable, or delete a failing test to make a pipeline pass. Investigate and fix the true root cause.

---

## 7. Security & Privacy Mandates

- **Sensitive Data Handling**: Candidate resumes contain Personal Identifiable Information (PII). Resumes must be stored in secure, private object storage (e.g., Supabase Storage / S3) with restricted pre-signed URL access.
- **BYOK Key Protection**: User LLM keys must be encrypted at rest using authenticated symmetric encryption (AES-256-GCM). Never log or display plaintext API keys.
- **Prompt Injection Defense**: Untrusted text from user resumes or external job postings must be sanitized and strictly encapsulated in prompts with clear boundary delimiters.
- **SSRF Prevention**: All external job scraping and links must validate protocol (`https` only), restrict destinations to trusted hosts, and prevent loopback/internal IP requests.

---

## 8. Git, Branching, and PR Governance

- **Default Branch**: `master`.
- **Branch Protection**: Never commit or push directly to `master`. Never force-push (`git push -f`) without explicit authorization.
- **Subphase Branch Naming**:
  ```text
  phase-XX/subphase-YY-short-description
  ```
  *Example*: `phase-00/subphase-01-agentic-governance`
- **Commit Standards**: Conventional Commits format:
  ```text
  feat(module): add job search filter
  fix(auth): correct token expiry validation
  docs(adr): add ADR-012 for resume storage
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

