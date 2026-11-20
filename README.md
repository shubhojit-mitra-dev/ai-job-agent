# AI Career Platform

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
| **Agent Framework** | [LangGraph](https://langchain-ai.github.io/langgraph/) *(Planned)* | Directed-graph workflow orchestration for multi-step career agents |
| **Deployment** | AWS Lambda via [Mangum](https://mangum.fastapiexpert.com/) + API Gateway HTTP API *(Planned)* | Serverless, cost-conscious backend running in `ap-south-1` (Mumbai) |
| **Async Jobs** | Amazon SQS + EventBridge Scheduler *(Planned)* | Decoupled background task workers and recurring morning digests |
| **IaC & CI/CD** | Terraform + GitHub Actions (OIDC) *(Planned)* | Reproducible infrastructure without static cloud credentials |

---

## 3. Current Project Status

> **Current Milestone**: Milestone 1 — Project Foundation  
> **Active Subphase**: `phase-00/subphase-01-agentic-governance` (Engineering Governance & Architecture Documentation)

### Current Implementation State:
- [x] Monorepo layout initialized
- [x] FastAPI base application (`apps/api/app/main.py`) with working `/health` endpoint
- [x] Next.js 16 App Router frontend scaffolded (`apps/web`)
- [x] Python dependencies pinned via `uv` (`apps/api/pyproject.toml`, `apps/api/uv.lock`)
- [x] Engineering governance and architecture documentation established
- [ ] Database connectivity, pooling, and Alembic migrations *(Planned for Subphase 02)*
- [ ] Supabase Auth middleware and security fixtures *(Planned for Subphase 03)*
- [ ] Local Docker Compose environment *(Planned for Subphase 04)*
- [ ] CI/CD quality gates *(Planned for Subphase 05)*

---

## 4. Repository Structure

```text
ai-job-agent/
├── apps/
│   ├── api/                 # FastAPI backend (Python 3.12, uv)
│   │   ├── app/             # Application source (main.py scaffolded; modules planned)
│   │   ├── tests/           # Automated test suites (scaffolded)
│   │   ├── pyproject.toml   # Dependencies managed by uv
│   │   └── uv.lock          # Cryptographic dependency lockfile
│   └── web/                 # Next.js frontend application (App Router, Tailwind)
├── docs/                    # Authoritative engineering documentation
│   ├── adr/                 # Architectural Decision Records (ADR-001 ... ADR-012)
│   ├── phases/              # High-level phase roadmaps
│   ├── subphases/           # Detailed subphase specifications
│   ├── progress/            # PROGRESS.md development tracker
│   └── walkthroughs/        # Post-subphase audit walkthroughs
├── infra/                   # Infrastructure definitions (scaffolded / planned)
│   ├── docker/              # Local Docker Compose setup (Planned)
│   ├── supabase/            # Supabase schema definitions (Planned)
│   └── terraform/           # Terraform AWS infrastructure (Planned)
├── packages/
│   └── shared-schemas/      # Shared cross-boundary schema packages (Planned)
├── .env.example             # Local environment variables template
├── .gitignore               # Monorepo ignore rules
├── AGENTS.md                # Authoritative instructions for AI coding agents
├── CLAUDE.md                # Minimal redirect to AGENTS.md
└── README.md                # Project overview and setup guide
```

---

## 5. Local Development Quickstart

### Prerequisites
- **Node.js**: v20+ with npm
- **Python**: 3.12+
- **uv**: Fast Python package manager ([Astral uv](https://docs.astral.sh/uv/))

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
npm ci
npm run dev
```
- Web Application: [http://localhost:3000](http://localhost:3000)

---

## 6. Engineering Documentation & Governance

For complete architectural details, consult the authoritative documentation:
- [AGENTS.md](./AGENTS.md) — Coding agent rules, branching, and Definition of Done
- [docs/PRODUCT_SPEC.md](./docs/PRODUCT_SPEC.md) — Product vision, requirements, and user personas
- [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md) — Modular monolith, AWS serverless, and database pooling architecture
- [docs/DEVELOPMENT_GUIDE.md](./docs/DEVELOPMENT_GUIDE.md) — Development workflow, testing, and contribution standards
- [docs/TESTING_STRATEGY.md](./docs/TESTING_STRATEGY.md) — TDD protocols and deterministic mock testing
- [docs/SECURITY.md](./docs/SECURITY.md) — Supabase Auth, BYOK encryption, and prompt injection defense
- [docs/DEPLOYMENT.md](./docs/DEPLOYMENT.md) — AWS Lambda, Mangum, and Terraform deployment
- [docs/COST_AND_OPERATIONS.md](./docs/COST_AND_OPERATIONS.md) — Cloud cost management and operational boundaries
- [docs/progress/PROGRESS.md](./docs/progress/PROGRESS.md) — Live project development status
