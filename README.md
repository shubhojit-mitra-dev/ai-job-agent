# AI Career Platform

[![Python: 3.12](https://img.shields.io/badge/Python-3.12-blue?logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Frontend-Next.js_16-black?logo=next.js)](https://nextjs.org/)
[![AWS: ap-south-1](https://img.shields.io/badge/AWS-ap--south--1-orange?logo=amazon-aws)](https://aws.amazon.com/)
[![Database: Aurora PostgreSQL Serverless v2](https://img.shields.io/badge/Database-Aurora_PostgreSQL_v2-336791?logo=postgresql)](https://aws.amazon.com/rds/aurora/)
[![Auth: Amazon Cognito](https://img.shields.io/badge/Auth-Amazon_Cognito-FF9900?logo=amazon-aws)](https://aws.amazon.com/cognito/)

An India-first, open-source, AI-powered career discovery platform engineered to help Indian students, fresh graduates, and professionals discover, evaluate, and track relevant career opportunities.

---

## 1. What We Are Building & Why

Navigating modern job boards in India is challenging: candidates face keyword-stuffed postings, ghost listings, opaque algorithmic filtering, and lack of transparent feedback.

The **AI Career Platform** provides an open-source, candidate-first alternative inspired by modern agentic career assistants:
- **Transparent Matching**: Deterministic, explainable compatibility scoring based on skills, domain depth, experience, and explicit candidate dealbreakers.
- **Candidate Memory & Discovery**: AI-assisted career goal intake with persistent, user-editable preferences.
- **Tailored Application Prep**: Ethical resume tailoring guidance highlighting existing experience without fabricating credentials.
- **Daily Opportunity Digests**: Automated, curated job notifications delivered directly with verified application URLs.
- **Dual AI Inference Tier**: Foundation models via Amazon Bedrock (with account quota resilience) and candidate Bring Your Own Key (BYOK) privacy (NVIDIA NIM, Cloudflare Workers AI, OpenRouter, Gemini).

---

## 2. Technology Stack & Target Architecture

| Tier | Technology | Description |
| :--- | :--- | :--- |
| **Frontend** | [Next.js 16](https://nextjs.org/) (App Router), TypeScript, Tailwind CSS | Responsive, accessible candidate-facing web application |
| **Backend** | [FastAPI](https://fastapi.tiangolo.com/) (Python 3.12), [Pydantic v2](https://docs.pydantic.dev/) | High-performance async REST API and agent orchestration services |
| **Authentication** | [Amazon Cognito User Pools](https://aws.amazon.com/cognito/) | Candidate registration, verification, and RS256 JWT issuance ([ADR-013](./docs/adr/ADR-013-cognito-authentication.md)) |
| **Relational Database** | [Amazon Aurora PostgreSQL Serverless v2](https://aws.amazon.com/rds/aurora/) | Auto-scaling relational candidate data, jobs, and rubrics in `ap-south-1` ([ADR-014](./docs/adr/ADR-014-aurora-postgresql-serverless-v2.md)) |
| **Vector Storage** | [Amazon S3 Vectors](https://aws.amazon.com/s3/) | Scalable vector indexing and ANN similarity search decoupled from DB compute ([ADR-015](./docs/adr/ADR-015-s3-vectors-for-vector-storage.md)) |
| **Document Storage** | Private [Amazon S3](https://aws.amazon.com/s3/) | Secure resume storage with Block Public Access and pre-signed URLs ([ADR-012](./docs/adr/ADR-012-resume-file-storage-and-secure-access.md)) |
| **ORM & Migrations**| [SQLAlchemy 2.0](https://www.sqlalchemy.org/) (Async) + [Alembic](https://alembic.sqlalchemy.org/) | Async queries via `asyncpg` with structured schema versioning ([ADR-004](./docs/adr/ADR-004-sqlalchemy-2-and-alembic.md)) |
| **Agent Framework** | [LangGraph](https://langchain-ai.github.io/langgraph/) | Directed-graph workflow orchestration for multi-step career agents |
| **AI Inference** | [Amazon Bedrock](https://aws.amazon.com/bedrock/) + Candidate BYOK | Amazon Titan foundation models (pending quota resolution) and candidate BYOK ([ADR-016](./docs/adr/ADR-016-bedrock-foundation-model-integration.md)) |
| **Embeddings** | [Amazon Titan Text Embeddings V2](https://aws.amazon.com/bedrock/) | Multilingual embeddings decoupled from Lambda package size ([ADR-011](./docs/adr/ADR-011-local-embedding-strategy-and-deployment-constraints.md)) |
| **Deployment** | AWS Lambda via [Mangum](https://mangum.fastapiexpert.com/) + API Gateway HTTP API | Serverless, cost-conscious backend in `ap-south-1` (Mumbai) ([ADR-002](./docs/adr/ADR-002-fastapi-aws-lambda-mangum-zip.md)) |
| **Async Tasks** | Amazon SQS + EventBridge Scheduler | Decoupled background task workers and recurring morning digests ([ADR-005](./docs/adr/ADR-005-sqs-background-processing.md), [ADR-006](./docs/adr/ADR-006-eventbridge-scheduler.md)) |
| **IaC & CI/CD** | Terraform + GitHub Actions (AWS OIDC) | Reproducible infrastructure without static cloud credentials ([ADR-007](./docs/adr/ADR-007-terraform-infrastructure-as-code.md), [ADR-008](./docs/adr/ADR-008-github-actions-with-aws-oidc.md)) |

---

## 3. Current Project Status

> **Current Phase**: Phase 01 — Candidate Core & Resume Ingestion  
> **Active Task**: AWS-Native Architecture Migration (Documentation & ADR Update)  
> **Last Merged Milestone**: Milestone 1 — Project Foundation (PR #6 Merged)

### Current Implementation State:
- [x] Monorepo layout initialized
- [x] FastAPI base application (`apps/api/app/main.py`) with working `/health` endpoint
- [x] Next.js 16 App Router frontend scaffolded (`apps/web`)
- [x] Python dependencies pinned via `uv` (`apps/api/pyproject.toml`, `apps/api/uv.lock`)
- [x] Engineering governance and architecture documentation established
- [x] Database connectivity, async session lifecycle, and Alembic migrations (`apps/api/alembic/`)
- [x] Automated test suites (`apps/api/tests/` with 31+ passing unit/integration tests)
- [x] JWT verification middleware and security fixtures (`apps/api/app/core/security.py`)
- [x] Local Docker Compose environment (`infra/docker/docker-compose.yml`)
- [x] CI/CD quality gates with GitHub Actions (`.github/workflows/ci.yml`)
- [x] AWS-native target architecture codified in ADR-001 through ADR-016
- [ ] Candidate profile domain models & schemas *(Phase 01, Subphase 01)*
- [ ] S3 resume pre-signed upload & parsing pipeline *(Phase 01, Subphase 02)*

---

## 4. Repository Structure

```text
ai-job-agent/
├── apps/
│   ├── api/                 # FastAPI backend (Python 3.12, uv)
│   │   ├── alembic/         # Database migrations (existing)
│   │   ├── app/             # Application source tree
│   │   │   ├── api/v1/      # REST API route handlers (existing)
│   │   │   ├── core/        # Core configuration, security, telemetry (existing)
│   │   │   ├── db/          # Database engine, session lifecycle, base models (existing)
│   │   │   ├── modules/     # Domain business logic (existing auth module, planned modules)
│   │   │   ├── schemas/     # Domain Pydantic request/response schemas (existing)
│   │   │   └── main.py      # FastAPI application entrypoint & /health route (existing)
│   │   ├── tests/           # Automated test suite (unit and integration tests) (existing)
│   │   ├── pyproject.toml   # Dependencies managed by uv (existing)
│   │   └── uv.lock          # Cryptographic dependency lockfile (existing)
│   └── web/                 # Next.js frontend application (App Router, Tailwind) (existing)
│       ├── src/app/         # Next.js App Router pages and layouts (existing)
│       ├── public/          # Static assets (existing)
│       └── AGENTS.md        # Next.js-specific framework agent guidance (existing)
├── docs/                    # Authoritative engineering documentation (existing)
│   ├── adr/                 # Architectural Decision Records (ADR-001 ... ADR-016) (existing)
│   ├── phases/              # High-level phase roadmaps (existing)
│   ├── subphases/           # Detailed subphase specifications (existing)
│   ├── progress/            # PROGRESS.md development tracker (existing)
│   └── walkthroughs/        # Post-subphase audit walkthroughs (existing)
├── infra/                   # Infrastructure definitions (existing)
│   ├── docker/              # Local Docker Compose setup (existing)
│   └── terraform/           # Terraform AWS infrastructure (planned)
├── packages/                # Shared monorepo packages (planned)
│   └── shared-schemas/      # Shared cross-boundary schema packages (planned)
├── .env.example             # Local environment variables template (existing)
├── .gitignore               # Monorepo ignore rules (existing)
├── AGENTS.md                # Authoritative instructions for AI coding agents (existing)
├── CLAUDE.md                # Minimal redirect to AGENTS.md (existing)
└── README.md                # Project overview and setup guide (existing)
```

---

## 5. Local Development Quickstart (100% Free & Offline)

The application can be run and tested completely offline without paid AWS credentials:

### Prerequisites
- **Node.js**: v20+ with npm
- **Python**: 3.12+
- **Docker & Docker Compose**
- **uv**: Fast Python package manager ([Astral uv](https://docs.astral.sh/uv/))

### 1. Clone & Setup Environment
```bash
git clone https://github.com/shubhojit-mitra-dev/ai-job-agent.git
cd ai-job-agent
cp .env.example .env
```

### 2. Start Local Database & Run Migrations
```bash
# Start local PostgreSQL container
docker compose up -d postgres

# Run database migrations
cd apps/api
uv sync
uv run alembic upgrade head
```

### 3. Backend (FastAPI)
```bash
cd apps/api
uv run uvicorn app.main:app --reload --port 8000
```
- API Health Check: [http://localhost:8000/health](http://localhost:8000/health)
- OpenAPI Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)

### 4. Frontend (Next.js)
```bash
cd apps/web
npm ci
npm run dev
```
- Web Application: [http://localhost:3000](http://localhost:3000)

---

## 6. Engineering Documentation & Governance

For complete architectural details, consult the authoritative documentation:
- [AGENTS.md](./AGENTS.md) — Coding agent rules, branching, and Definition of Done
- [docs/PRODUCT_SPEC.md](./docs/PRODUCT_SPEC.md) — Product vision, requirements, and user personas
- [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md) — AWS serverless architecture, Aurora PostgreSQL, S3 Vectors, and LangGraph
- [docs/DEVELOPMENT_GUIDE.md](./docs/DEVELOPMENT_GUIDE.md) — Development workflow, testing, and contribution standards
- [docs/TESTING_STRATEGY.md](./docs/TESTING_STRATEGY.md) — TDD protocols and deterministic mock testing
- [docs/SECURITY.md](./docs/SECURITY.md) — Amazon Cognito, BYOK encryption, S3 pre-signed security, and prompt injection defense
- [docs/DEPLOYMENT.md](./docs/DEPLOYMENT.md) — AWS Lambda, Mangum, Terraform, and GitHub Actions OIDC
- [docs/COST_AND_OPERATIONS.md](./docs/COST_AND_OPERATIONS.md) — Cloud cost management and \$200 budget guardrails
- [docs/progress/PROGRESS.md](./docs/progress/PROGRESS.md) — Live project development status
- [docs/adr/](./docs/adr/) — Architectural Decision Records (ADR-001 through ADR-016)
