# Development Guide: AI Career Platform

> **Status**: Approved Foundation  
> **Audience**: Engineers, Contributors, AI Coding Agents  
> **Revision**: 1.0 (Phase 00)

---

## 1. Monorepo Organization & Tooling

This repository is organized as a lightweight monorepo containing frontend, backend, infrastructure definitions, and shared documentation.

```text
ai-job-agent/
├── apps/
│   ├── api/                 # FastAPI backend (Python 3.12, uv)
│   └── web/                 # Next.js frontend (Node.js 20+, npm)
├── docs/                    # Authoritative technical documentation
├── infra/                   # Infrastructure definitions (docker, supabase, terraform)
└── packages/
    └── shared-schemas/      # Shared cross-boundary contracts
```

### Primary Toolchains
- **Backend**: Managed exclusively with **`uv`** (Astral's ultra-fast Python package manager). Do not run `pip` directly.
- **Frontend**: Managed with **`npm`** and Next.js 16.
- **Git**: Branching conventions, atomic conventional commits, and pull requests required for all changes.

---

## 2. Local Environment Setup

### 2.1. Prerequisites
- Python `3.12`
- Node.js `20.x` or later
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
- `SUPABASE_URL`: Supabase project URL
- `SUPABASE_ANON_KEY`: Public client key
- `SUPABASE_SERVICE_ROLE_KEY`: Admin service role key (backend only)
- `DATABASE_URL`: SQLAlchemy async connection string
- `LLM_ENCRYPTION_KEY`: 32-byte hexadecimal key for BYOK encryption at rest

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

### 3.2. Running the Development Server
```bash
cd apps/api
uv run uvicorn app.main:app --reload --port 8000
```
- Health Check: `curl http://localhost:8000/health`
- Interactive OpenAPI Docs: `http://localhost:8000/docs`

### 3.3. Formatting & Linting
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

### 3.4. Static Type Checking
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
- `phase-00/subphase-02-database-connectivity`

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
git commit -m "docs(governance): establish root AGENTS.md and engineering guidelines"
```

### 5.3. Pull Request Requirements
1. The branch must branch off the latest `master`.
2. All linting, typing, and test checks must pass with zero errors.
3. The subphase walkthrough must be completed in `docs/walkthroughs/`.
4. `docs/progress/PROGRESS.md` must be updated.
5. Create a GitHub Pull Request targeting `master` and request Technical Lead review.

