# ADR-003: Supabase Auth and PostgreSQL

- **Status**: Accepted
- **Date**: 2026-11-20
- **Authors**: Technical Lead, Architecture Engineer

---

## 1. Context
The platform requires secure candidate authentication, user management, and a robust relational database with vector similarity search capabilities (`pgvector`). We must evaluate whether to operate standalone AWS RDS PostgreSQL or leverage Supabase's managed PostgreSQL platform, and establish clear boundaries between API-layer authentication and database-level isolation.

## 2. Decision
Adopt **Supabase** for user authentication and managed PostgreSQL storage:
1. **Supabase Auth**: Manages candidate user registration, OAuth, and issues signed JWT access tokens.
2. **Supabase PostgreSQL**: Managed PostgreSQL 15/17 engine with the `pgvector` extension enabled for semantic embeddings.
3. **Connection Strategy**: Lambda runtime connects to Supabase via the shared Transaction Pooler on port 6543 (`statement_cache_size=0`), while Alembic migrations connect directly via session mode on port 5432.
4. **Tenant Isolation & Security Boundary**:
   - Supabase Auth validates caller identity at the API Gateway / FastAPI middleware level.
   - Supabase Auth does **not** automatically protect direct SQLAlchemy database connections. The application database role connects using application credentials.
   - Application queries must enforce user ownership (`WHERE user_id = current_user.id`).
   - Defense in depth is provided by using a dedicated least-privileged database role and evaluating session-scoped configuration parameters (`SET LOCAL app.current_user_id = :uid`) to drive PostgreSQL Row-Level Security (RLS) policies.

## 3. Alternatives Considered
- **AWS RDS PostgreSQL**: AWS RDS requires minimum ~$15/month for the smallest `db.t4g.micro` instance with zero included free auth services. Rejected due to cost.
- **Custom Auth with Cognito**: AWS Cognito has higher complexity and less flexible developer ergonomics than Supabase Auth.

## 4. Consequences
- **Positive**: Consolidated database and auth stack, native `pgvector` extension, built-in pooling infrastructure, generous free tier.
- **Negative**: Third-party dependency outside AWS; free tier instances pause after 7 days of inactivity; transaction pooler disallows prepared statements; direct database access requires explicit tenant isolation logic.

## 5. Risks
- Prepared statement cache errors with `asyncpg`. Mitigated by setting `statement_cache_size=0` on SQLAlchemy engine connect args.
- Cross-tenant data leaks if application queries omit tenant filters. Mitigated by least-privileged database roles, mandatory user tenancy checks, and RLS defense in depth.

## 6. References
- Supabase Connecting to Postgres: https://supabase.com/docs/guides/database/connecting-to-postgres
- Supabase Connection Pooling: https://supabase.com/docs/guides/database/connecting-to-postgres/pooling-and-limits
- [docs/SECURITY.md](../SECURITY.md)
