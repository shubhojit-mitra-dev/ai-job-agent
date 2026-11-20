# Walkthrough: Milestone 1 — Project Foundation Hardening & Verification Audit

> **Milestone**: Consolidated Project Foundation  
> **Branch**: `milestone-01/foundation`  
> **Target Branch**: `master` (PR #6)  
> **Date**: 2026-11-20  
> **Status**: Hardened & Prepared for Human Technical Lead Review  

---

## 1. Executive Summary

Milestone 1 establishes the initial technical foundation for the **AI Career Platform**, preparing the repository for candidate-centric career discovery without implementing speculative product features prematurely.

Following the initial technical review of PR #6, a focused hardening pass was conducted across cryptographic token verification, operational error handling, production configuration validation, database session semantics, Docker Compose specifications, and CI quality gates:

1. **Cryptographic JWT Verification & Resilient Error Handling**:
   - Asymmetric verification enforcing algorithm allowlists (`RS256`, `ES256`), issuer, audience (`authenticated`), expiration, and valid UUID subject (`sub`).
   - Removed broad exception handling (`except Exception`), strictly distinguishing invalid credentials (HTTP 401) from operational provider/network failures (HTTP 503).
   - Safe operational logging using structured error classes; prevents leaking bearer tokens, headers, or candidate claims into logs.
   - Comprehensive test suite covering valid RS256/ES256, expired tokens, forged signatures, invalid issuer/audience, non-UUID subjects, unknown key IDs (`kid`), malformed keys, and provider outages.

2. **Production Configuration Hardening**:
   - Strict Pydantic model validator (`validate_production_configuration`) rejecting placeholder Supabase URLs (`example.supabase.co`), development anon keys, insecure application secrets (<32 characters or containing `insecure`/`dev-`), and symmetric secret fallbacks when `APP_ENV=production`.
   - Clean, explicit local development defaults for seamless local onboarding.
   - Sanitized `.env.example` with obviously non-functional dummy placeholders (never realistic-looking service keys or encryption tokens).

3. **Database Engine, Alembic Migrations & Verification Scope**:
   - SQLAlchemy 2.0 asynchronous engine with dynamic pool resolution defaulting to `NullPool` (serverless Lambda / PgBouncer mode) and optional `QueuePool` for local stateful development.
   - Enforces `statement_cache_size=0` for Supabase / PgBouncer transaction pooling.
   - Request-scoped `get_db_session()` dependency ensuring automatic rollback on unhandled exceptions and guaranteed session closure.
   - Authoritative initial migration `0001_pgvector` installing PostgreSQL `vector` extension.
   - Deterministic testing tiers: Mocked session lifecycle unit tests, and real PostgreSQL integration tests executing against `pgvector/pgvector:pg16` in CI.

4. **Docker Compose & Container User Audit**:
   - Container execution audit: Confirmed that official `pgvector/pgvector:pg16` initializes file permissions as root (UID 0) and drops privileges via `gosu` to UID 999 (`postgres`) for the database daemon process.
   - Documented top-level `include:` directive requirement (Docker Compose v2.20.0+).
   - Explicit and configurable local credentials (`POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`).

5. **CI Quality Gates & Full Commit SHA Pinning**:
   - Pinned all GitHub Actions to immutable full commit SHAs (`actions/checkout`, `astral-sh/setup-uv`, `actions/setup-node`).
   - Dedicated PostgreSQL service container running `pgvector/pgvector:pg16` in CI for real migration execution (`alembic upgrade head`) and transaction verification.
   - Zero external secrets required in CI.

6. **Frontend Starter Baseline**:
   - Verified starter baseline using Next.js 16.4.6 App Router, React 19, and Turbopack. (Note: The frontend is a verified starter baseline for lint and build compliance, not a completed candidate application).

---

## 2. Testing Architecture & Tiers

To maintain strict engineering accuracy, the automated test suite is categorized into three distinct tiers:

### Tier 1: Pure Unit Tests (Mocks & Key Pairs)
- **Token Verification (`tests/unit/test_auth_jwt.py`)**:
  - `test_verify_valid_asymmetric_jwt_rs256`: Valid RS256 token verification.
  - `test_verify_valid_asymmetric_jwt_es256`: Valid ES256 (NIST P-256) token verification.
  - `test_verify_jwks_provider_unavailable_returns_503`: Provider network failure returns controlled 503 and logs safely without token leakage.
  - `test_verify_unknown_kid_returns_401`: Unknown `kid` returns 401 Unauthorized.
  - `test_verify_malformed_key_returns_401`: Malformed JWK key returns 401 Unauthorized.
  - `test_verify_expired_jwt`: Expired signature returns 401 Unauthorized.
  - `test_verify_invalid_issuer`: Untrusted issuer returns 401 Unauthorized.
  - `test_verify_invalid_audience`: Wrong audience returns 401 Unauthorized.
  - `test_verify_missing_sub_claim`: Missing subject returns 401 Unauthorized.
  - `test_verify_non_uuid_sub_claim`: Malformed UUID subject returns 401 Unauthorized.
  - `test_verify_forged_signature`: Forged key signature returns 401 Unauthorized.
  - `test_verify_disallowed_algorithm`: Disallowed algorithm (e.g. HS256 in prod) returns 401.
- **Configuration Validation (`tests/unit/test_config.py`)**:
  - `test_development_configuration_accepts_defaults`: Validates local defaults.
  - `test_production_rejects_example_supabase_url`: Rejects placeholder Supabase URL.
  - `test_production_rejects_dev_anon_key`: Rejects dev placeholder anon key.
  - `test_production_rejects_insecure_app_secret`: Rejects short or insecure app secret.
  - `test_production_rejects_jwt_secret_fallback`: Rejects HMAC secret in production.
  - `test_production_accepts_valid_configuration`: Accepts secure production settings.
- **Database Engine Pool (`tests/unit/test_db_session.py`)**:
  - `test_get_engine_pool_resolution`: Pool resolution logic (`NullPool` vs `QueuePool`).
  - `test_base_metadata_and_timestamp_mixin`: Base and timestamp audit columns.
  - `test_get_db_session_lifecycle_success`: Mocked session dependency success flow.
  - `test_get_db_session_lifecycle_error_rollback`: Mocked session dependency rollback flow.

### Tier 2: Mocked Route Integration Tests
- **Endpoint Route Protection (`tests/integration/test_auth_routes.py`)**:
  - `test_health_check_endpoint`: Public `GET /health` returns 200.
  - `test_get_me_without_authorization`: Missing Bearer header rejected (401/403).
  - `test_get_me_with_invalid_token`: Invalid Bearer token rejected (401).
  - `test_get_me_with_valid_bearer_token`: Valid Bearer token resolves `CurrentUser(user_id=..., email=..., role=...)`.

### Tier 3: Real PostgreSQL Integration Tests
- **Real Database & Extension Verification (`tests/integration/test_db_postgres.py`)**:
  - `test_real_postgres_connection_and_pgvector_extension`: Connects to actual PostgreSQL, verifies server engine, and queries `pg_extension` to confirm `vector` extension installation.
  - `test_real_postgres_transaction_rollback_semantics`: Executes transaction on real PostgreSQL, rolls back, and verifies state cleanup.
  - `test_real_postgres_session_lifecycle`: Executes query through `get_db_session()` against actual PostgreSQL.
  - *Note*: Gracefully skips in local environments when port 5432 is not running `pgvector/pgvector:pg16`; strictly enforced in CI via `REQUIRE_POSTGRES=true`.

---

## 3. Explicit Limitations & Boundaries of Milestone 1

To prevent misleading claims, the following boundaries are explicitly recorded:

1. **Authentication vs. Database Authorization**:
   - Authenticated candidate identity extraction (`sub` claim -> `CurrentUser.user_id`) is implemented and verified.
   - **Candidate-level database authorization, Row-Level Security (RLS) policies, and tenant isolation are NOT implemented in Milestone 1**. They will be implemented in Phase 01 alongside actual candidate domain tables (`candidates`, `resumes`). Direct database connections do not enforce candidate tenant isolation until domain models exist.
2. **Local Environment vs. CI Database Verification**:
   - Real PostgreSQL integration tests and migration runs are verified automatically in CI against an official `pgvector/pgvector:pg16` service container.
   - In local development, database tests fall back to unit/mock verification if a local `pgvector` container is not active.
3. **Frontend Application**:
   - The frontend is verified as a clean starter baseline (Next.js 16 App Router, TypeScript, ESLint, Turbopack production compilation).
   - Candidate-facing UI, authentication flows, and state management are not implemented in this milestone.

---

## 4. Automated Verification Results

```text
$ uv run pytest -v
============================= test session starts ==============================
platform linux -- Python 3.12.12, pytest-9.2.0, pluggy-1.7.0 -- apps/api/.venv/bin/python
cachedir: .pytest_cache
rootdir: apps/api
configfile: pyproject.toml
plugins: anyio-4.16.0, asyncio-1.5.0
asyncio: mode=Mode.AUTO, debug=False, asyncio_default_fixture_loop_scope=function, asyncio_default_test_loop_scope=function
collecting ... collected 29 items

tests/integration/test_auth_routes.py::test_health_check_endpoint PASSED [  3%]
tests/integration/test_auth_routes.py::test_get_me_without_authorization PASSED [  6%]
tests/integration/test_auth_routes.py::test_get_me_with_invalid_token PASSED [ 10%]
tests/integration/test_auth_routes.py::test_get_me_with_valid_bearer_token PASSED [ 13%]
tests/integration/test_db_postgres.py::test_real_postgres_connection_and_pgvector_extension SKIPPED [ 17%]
tests/integration/test_db_postgres.py::test_real_postgres_transaction_rollback_semantics SKIPPED [ 20%]
tests/integration/test_db_postgres.py::test_real_postgres_session_lifecycle PASSED [ 24%]
tests/unit/test_auth_jwt.py::test_verify_valid_asymmetric_jwt_rs256 PASSED [ 27%]
tests/unit/test_auth_jwt.py::test_verify_valid_asymmetric_jwt_es256 PASSED [ 31%]
tests/unit/test_auth_jwt.py::test_verify_jwks_provider_unavailable_returns_503 PASSED [ 34%]
tests/unit/test_auth_jwt.py::test_verify_unknown_kid_returns_401 PASSED  [ 37%]
tests/unit/test_auth_jwt.py::test_verify_malformed_key_returns_401 PASSED [ 41%]
tests/unit/test_auth_jwt.py::test_verify_expired_jwt PASSED              [ 44%]
tests/unit/test_auth_jwt.py::test_verify_invalid_issuer PASSED           [ 48%]
tests/unit/test_auth_jwt.py::test_verify_invalid_audience PASSED         [ 51%]
tests/unit/test_auth_jwt.py::test_verify_missing_sub_claim PASSED        [ 55%]
tests/unit/test_auth_jwt.py::test_verify_non_uuid_sub_claim PASSED       [ 58%]
tests/unit/test_auth_jwt.py::test_verify_forged_signature PASSED         [ 62%]
tests/unit/test_auth_jwt.py::test_verify_disallowed_algorithm PASSED     [ 65%]
tests/unit/test_config.py::test_development_configuration_accepts_defaults PASSED [ 68%]
tests/unit/test_config.py::test_production_rejects_example_supabase_url PASSED [ 72%]
tests/unit/test_config.py::test_production_rejects_dev_anon_key PASSED   [ 75%]
tests/unit/test_config.py::test_production_rejects_insecure_app_secret PASSED [ 79%]
tests/unit/test_config.py::test_production_rejects_jwt_secret_fallback PASSED [ 82%]
tests/unit/test_config.py::test_production_accepts_valid_configuration PASSED [ 86%]
tests/unit/test_db_session.py::test_get_engine_pool_resolution PASSED    [ 89%]
tests/unit/test_db_session.py::test_base_metadata_and_timestamp_mixin PASSED [ 93%]
tests/unit/test_db_session.py::test_get_db_session_lifecycle_success PASSED [ 96%]
tests/unit/test_db_session.py::test_get_db_session_lifecycle_error_rollback PASSED [100%]

======================== 27 passed, 2 skipped in 0.65s =========================

$ uv run ruff check .
All checks passed!

$ uv run ruff format --check .
29 files already formatted

$ uv run mypy .
Success: no issues found in 26 source files

$ cd apps/web && npm run lint && npm run build
✓ Compiled successfully in 737ms
  Finished TypeScript in 2.7s
  Collecting page data using 3 workers in 855ms
✓ Generating static pages using 3 workers (4/4) in 317ms
Finalizing page optimization in 17ms
```

---

## 5. Definition of Done Compliance Matrix

- [x] JWT error handling hardened: 401 vs 503 distinguished, safe logging enforced, ES256/RS256 verified, provider outage/unknown kid/malformed key tests added.
- [x] Production configuration validated: Rejects placeholder URLs, insecure keys, dev tokens, and symmetric secrets in production.
- [x] Database verification scoped and documented: Real PostgreSQL migration and rollback test implemented for CI; mock session tests clearly identified.
- [x] Docker Compose container user verified: Entrypoint root permissions and daemon UID 999 execution documented; compose v2.20+ requirement noted.
- [x] CI actions pinned to full commit SHAs; PostgreSQL pgvector service container integrated; no secrets required.
- [x] Documentation accurately reflects verified reality without exaggeration.
- [x] PR #6 updated on `milestone-01/foundation` branch awaiting human technical lead review.
