# AI Career Platform

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python: 3.12](https://img.shields.io/badge/Python-3.12-blue?logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Frontend-Next.js_16-black?logo=next.js)](https://nextjs.org/)
[![Database: Supabase PostgreSQL](https://img.shields.io/badge/Database-Supabase_PostgreSQL-3ECF8E?logo=supabase)](https://supabase.com/)

An India-first, open-source, AI-powered career discovery platform engineered to help Indian students, fresh graduates, and professionals discover, evaluate, and track relevant career opportunities.

---

## 1. What We Are Building & Why

Navigating modern job boards in India is challenging: candidates face keyword-stuffed postings, ghost listings, opaque algorithmic filtering, and lack of transparent feedback.

The **AI Career Platform** provides an open-source, candidate-first alternative inspired by modern agentic career assistants:
- **Transparent Matching**: Deterministic, explainable compatibility scoring based on skills, domain depth, experience, and explicit candidate dealbreakers.
- **Candidate Memory & Discovery**: AI-assisted career goal intake with persistent, user-editable preferences.
- **Tailored Application Prep**: Ethical resume tailoring guidance highlighting existing experience without fabricating credentials.
- **Daily Opportunity Digests**: Automated, curated job notifications delivered directly with verified application URLs.
- **Bring Your Own Key (BYOK)**: Privacy-preserving LLM inference allowing users to connect their own API keys (NVIDIA NIM, Cloudflare Workers AI, OpenRouter, Gemini).

---

## 2. Technology Stack & Target Architecture

| Tier | Technology | Description |
| :--- | :--- | :--- |
| **Frontend** | [Next.js](https://nextjs.org/) (App Router), TypeScript, Tailwind CSS | Responsive, accessible candidate-facing web application |
| **Backend** | [FastAPI](https://fastapi.tiangolo.com/) (Python 3.12), [Pydantic v2](https://docs.pydantic.dev/) | High-performance async REST API and agent orchestration services |
| **Database** | [Supabase](https://supabase.com/) PostgreSQL + [pgvector](https://github.com/pgvector/pgvector) | Relational candidate data, job postings, and vector embeddings |
| **ORM & Migrations**| [SQLAlchemy 2.0](https://www.sqlalchemy.org/) (Async) + [Alembic](https://alembic.sqlalchemy.org/) | Async database queries with structured schema versioning |
| **Agent Framework** | [LangGraph](https://langchain-ai.github.io/langgraph/) | Directed-graph workflow orchestration for multi-step career agents |
| **Deployment** | AWS Lambda via [Mangum](https://mangum.fastapiexpert.com/) + API Gateway HTTP API | Serverless, cost-conscious backend running in `ap-south-1` (Mumbai) |
| **Async Jobs** | Amazon SQS + EventBridge Scheduler | Decoupled background task workers and recurring morning digests |
| **IaC & CI/CD** | Terraform + GitHub Actions (OIDC) | Reproducible infrastructure without static cloud credentials |

---

## 3. Current Project Status

> **Current Milestone**: Milestone 1 — Project Foundation  
> **Active Subphase**: `phase-00/subphase-01-agentic-governance` (Engineering Governance & Architecture Documentation)

### Scaffolded State:
- [x] Monorepo structure (`apps/api`, `apps/web`, `infra/`, `packages/`, `docs/`)
- [x] FastAPI base application (`apps/api/app/main.py`) with working `/health` endpoint
- [x] Next.js 16 App Router application scaffolded (`apps/web`)
- [x] Python dependencies pinned via `uv`
- [ ] Database engine, pooling, and Alembic migrations (Planned for Subphase 02)
- [ ] Supabase Auth middleware (Planned for Subphase 03)
- [ ] Local Docker Compose environment (Planned for Subphase 04)

---

## 4. Repository Structure

```text
ai-job-agent/
├── apps/
│   ├── api/                 # FastAPI backend (Python 3.12, uv)
│   │   ├── app/             # Application source (api, core, db, modules, schemas)
│   │   ├── tests/           # Automated test suites
│   │   └── pyproject.toml   # Dependencies managed by uv
│   └── web/                 # Next.js frontend application
├── docs/                    # Authoritative engineering documentation
│   ├── adr/                 # Architectural Decision Records (ADR-001 ... ADR-012)
│   ├── phases/              # High-level phase roadmaps
│   ├── subphases/           # Detailed subphase specifications
│   ├── progress/            # PROGRESS.md development tracker
│   └── walkthroughs/        # Post-subphase audit walkthroughs
├── infra/                   # Infrastructure definitions (docker, supabase, terraform)
├── packages/                # Shared monorepo packages
├── .env.example             # Local environment variables template
├── AGENTS.md                # Authoritative instructions for AI coding agents
└── README.md                # Project documentation
```

---

## 5. Local Development Quickstart

### Prerequisites
- **Node.js**: v20+ with npm
- **Python**: 3.12+
- **uv**: Fast Python package manager ([Astral uv](https://docs.astral.sh/uv/))
- **Docker**: For upcoming local database services

### 1. Clone & Setup Environment
```bash
git clone https://github.com/shubhojit-mitra-dev/ai-job-agent.git
cd ai-job-agent
cp .env.example .env
```

### 2. Backend (FastAPI)
```bash
cd apps/api
uv sync
uv run uvicorn app.main:app --reload --port 8000
```
- API Health Check: [http://localhost:8000/health](http://localhost:8000/health)
- OpenAPI Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)

### 3. Frontend (Next.js)
```bash
cd apps/web
npm install
npm run dev
```
- Web Application: [http://localhost:3000](http://localhost:3000)

---

## 6. Engineering Documentation & Governance

For complete architectural details, consult the authoritative documentation:
- [AGENTS.md](file:///home/blackknight05/Desktop/ai-job-agent/AGENTS.md) — Coding agent rules, branching, and Definition of Done
- [docs/PRODUCT_SPEC.md](file:///home/blackknight05/Desktop/ai-job-agent/docs/PRODUCT_SPEC.md) — Product vision, requirements, and user personas
- [docs/ARCHITECTURE.md](file:///home/blackknight05/Desktop/ai-job-agent/docs/ARCHITECTURE.md) — Modular monolith, AWS serverless, and database pooling architecture
- [docs/DEVELOPMENT_GUIDE.md](file:///home/blackknight05/Desktop/ai-job-agent/docs/DEVELOPMENT_GUIDE.md) — Development workflow, testing, and contribution standards
- [docs/TESTING_STRATEGY.md](file:///home/blackknight05/Desktop/ai-job-agent/docs/TESTING_STRATEGY.md) — TDD protocols and deterministic mock testing
- [docs/SECURITY.md](file:///home/blackknight05/Desktop/ai-job-agent/docs/SECURITY.md) — Supabase Auth, BYOK encryption, and prompt injection defense
- [docs/DEPLOYMENT.md](file:///home/blackknight05/Desktop/ai-job-agent/docs/DEPLOYMENT.md) — AWS Lambda, Mangum, and Terraform deployment
- [docs/COST_AND_OPERATIONS.md](file:///home/blackknight05/Desktop/ai-job-agent/docs/COST_AND_OPERATIONS.md) — Cloud cost management and operational boundaries
- [docs/progress/PROGRESS.md](file:///home/blackknight05/Desktop/ai-job-agent/docs/progress/PROGRESS.md) — Live project development status

