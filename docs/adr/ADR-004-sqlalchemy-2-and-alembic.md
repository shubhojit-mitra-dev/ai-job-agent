# ADR-004: SQLAlchemy 2.0 and Alembic

- **Status**: Accepted
- **Date**: 2026-11-20
- **Authors**: Technical Lead, Architecture Engineer

---

## 1. Context
We need a modern, type-safe Object Relational Mapper (ORM) and a deterministic schema migration management system for the Python FastAPI backend interacting with Supabase PostgreSQL.

## 2. Decision
Use **SQLAlchemy 2.0** with the `asyncpg` async driver as the application ORM, and **Alembic** for schema migrations:
1. All database queries use modern SQLAlchemy 2.0 typed `select()` constructs with async sessions.
2. Serverless Lambda execution uses `poolclass=NullPool` to avoid retaining idle connections across invocations.
3. Alembic is the authoritative schema migration tool. Migrations are executed in CI/CD deployment pipelines or developer CLI connecting directly to port 5432 with administrative credentials, completely outside Lambda cold starts.

## 3. Alternatives Considered
- **SQLModel**: Wrapper around SQLAlchemy and Pydantic. Rejected because raw SQLAlchemy 2.0 provides greater clarity, direct asyncpg support, and native Alembic integration.
- **Tortoise ORM / Peewee**: Smaller ecosystems and less comprehensive migration tooling.

## 4. Consequences
- **Positive**: Strict type safety, battle-tested migration versioning, async query execution, clean separation of DDL and runtime queries.
- **Negative**: Requires careful configuration when pairing `asyncpg` with transaction-mode connection poolers (`statement_cache_size=0`).

## 5. Risks
- Running Alembic during Lambda cold starts causes timeout issues and concurrent migration races. Mitigated by strictly forbidding in-lambda migration runs.

## 6. References
- SQLAlchemy 2.0 Documentation: https://docs.sqlalchemy.org/en/20/
- Supabase with SQLAlchemy troubleshooting: https://supabase.com/kb/troubleshooting/using-sqlalchemy-with-supabase-FUqebT

