# Development Guide: AI Career Platform

> **Status**: Approved Foundation (AWS-Native Target Architecture)  
> **Audience**: Engineers, Contributors, AI Coding Agents  
> **Revision**: 2.0 (Phase 01 Architecture Migration)

---

## 1. Monorepo Organization & Tooling

This repository is organized as a lightweight monorepo containing frontend, backend, infrastructure definitions, and shared documentation.

```text
ai-job-agent/
├── apps/
│   ├── api/                 # FastAPI backend (Python 3.12, uv)
│   └── web/                 # Next.js frontend (Node.js 20+, npm)
├── docs/                    # Authoritative technical documentation
├── infra/                   # Infrastructure definitions (docker, terraform)
└── packages/
    └── shared-schemas/      # Shared cross-boundary contracts
```

### Primary Toolchains
- **Backend**: Managed exclusively with **`uv`** (Astral's ultra-fast Python package manager). Do not run `pip` directly.
- **Frontend**: Managed with **`npm`** and Next.js 16.
- **Git**: Branching conventions, atomic conventional commits, and pull requests required for all changes.

---

## 2. Local Environment Setup (100% Offline & Free)

### Critical Requirement: Zero Paid Cloud Services for Local Development
Our local development environment is designed to be **completely functional without AWS credentials or paid cloud services**:
- **Relational Database**: Local containerized PostgreSQL with `pgvector` runs via Docker Compose.
- **Authentication**: The backend includes local JWT fixtures and verification helpers to test authentication without a live Amazon Cognito User Pool.
- **Vector Search**: An in-memory vector store implementation (`FakeVectorStore`) executes semantic similarity matching using pure Python and NumPy, requiring zero AWS S3 Vectors configuration.
- **Document Storage**: Resume uploads are emulated locally via disk storage or pre-signed URL mocks without live Amazon S3 buckets.
- **AI Inference**: LangGraph agents run against `FakeLLMClient` returning deterministic responses without requiring live Amazon Bedrock or third-party LLM credits.

### 2.1. Prerequisites
- Python `3.12`
- Node.js `20.x` or later
- Docker & Docker Compose
- `uv` (Install: `curl -LsSf https://astral.sh/uv/install.sh | sh`)
- Git

### 2.2. Configuration Setup
Copy the environment template from the root directory:
```bash
cp .env.example .env
```
Key variables configured in `.env`:
- `APP_ENV`: `development` | `test` | `production`
- `APP_SECRET_KEY`: Used for local session/state encryption
- `DATABASE_URL`: Async connection string (`postgresql+asyncpg://postgres:postgres_local_dev_insecure@localhost:5432/career_platform`)
- `COGNITO_USER_POOL_ID`: Amazon Cognito User Pool ID (production/staging only)
- `COGNITO_CLIENT_ID`: Amazon Cognito App Client ID (production/staging only)
- `S3_RESUME_BUCKET_NAME`: Private resume S3 bucket name
- `ENABLE_BEDROCK`: Feature flag (`false` by default during local development)
- `LLM_ENCRYPTION_KEY`: 32-byte hexadecimal key for BYOK encryption at rest

### 2.3. Starting the Local Database
```bash
# Start local PostgreSQL container with pgvector
docker compose up -d postgres

# Verify database health
docker compose ps
```

---

## 3. Backend Development (`apps/api`)

### 3.1. Dependency Management with `uv`
All dependencies are pinned in `pyproject.toml` and locked in `uv.lock`.
```bash
cd apps/api

# Sync virtual environment to exact lockfile state
uv sync

# Add a production dependency
uv add <package-name>

# Add a development dependency
uv add --dev <package-name>
```

### 3.2. Running Database Migrations
```bash
cd apps/api

# Run migrations forward
uv run alembic upgrade head

# Rollback one migration
uv run alembic downgrade -1
```

### 3.3. Running the Development Server
```bash
cd apps/api
uv run uvicorn app.main:app --reload --port 8000
```
- Health Check: `curl http://localhost:8000/health`
- Interactive OpenAPI Docs: `http://localhost:8000/docs`

### 3.4. Formatting & Linting
We enforce strict style and lint standards with **Ruff**:
```bash
cd apps/api

# Check linting rules
uv run ruff check .

# Automatically fix fixable lint issues
uv run ruff check --fix .

# Verify formatting
uv run ruff format --check .

# Auto-format codebase
uv run ruff format .
```

### 3.5. Static Type Checking
Static types are validated with **Mypy**:
```bash
cd apps/api
uv run mypy .
```

---

## 4. Frontend Development (`apps/web`)

### 4.1. Dependency Management & Dev Server
```bash
cd apps/web

# Install dependencies reproducibly
npm ci

# Start local Next.js dev server
npm run dev
```
Web app runs on `http://localhost:3000`.

### 4.2. Linting & Formatting
```bash
cd apps/web
npm run lint
```
*Note*: Follow Next.js guidelines preserved in `apps/web/AGENTS.md`.

---

## 5. Git & Subphase Branching Workflow

We adhere strictly to subphase-isolated branches. Direct commits to `master` are prohibited.

### 5.1. Branch Naming Convention
```text
phase-XX/subphase-YY-short-description
```
*Examples*:
- `phase-00/subphase-01-agentic-governance`
- `phase-01/aws-architecture-migration`
- `phase-01/subphase-01-candidate-schema`

### 5.2. Atomic Conventional Commits
All commit messages must adhere to the Conventional Commits specification:
- `feat(scope)`: New user or agent capability
- `fix(scope)`: Bug fix
- `docs(scope)`: Documentation changes only
- `test(scope)`: Adding or correcting tests
- `refactor(scope)`: Code change that neither fixes a bug nor adds a feature
- `chore(scope)`: Routine maintenance or tooling updates

*Example*:
```bash
git commit -m "docs(architecture): migrate platform architecture to AWS-native stack"
```

### 5.3. Pull Request Requirements
1. The branch must branch off the latest `master`.
2. All linting, typing, and test checks must pass with zero errors.
3. The subphase walkthrough must be completed in `docs/walkthroughs/`.
4. `docs/progress/PROGRESS.md` must be updated.
