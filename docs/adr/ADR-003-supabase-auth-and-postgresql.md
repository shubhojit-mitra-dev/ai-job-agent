# ADR-003: Supabase Auth and PostgreSQL

- **Status**: Superseded
- **Date**: 2026-11-20 (Superseded on 2026-11-21)
- **Authors**: Technical Lead, Architecture Engineer

> **Superseded Note (2026-11-21)**:  
> This ADR is **superseded** by:
> - [ADR-013: Amazon Cognito User Pools for Candidate Authentication](./ADR-013-cognito-authentication.md)
> - [ADR-014: Amazon Aurora PostgreSQL Serverless v2 and Lambda Connectivity Strategy](./ADR-014-aurora-postgresql-serverless-v2.md)
> - [ADR-015: Amazon S3 Vectors for Scalable Candidate and Job Vector Similarity Search](./ADR-015-s3-vectors-for-vector-storage.md)
> 
> Following the technical lead's approval to migrate toward an AWS-native architecture co-located in `ap-south-1` (Mumbai), third-party Supabase services are replaced with Amazon Cognito User Pools, Amazon Aurora PostgreSQL Serverless v2, and Amazon S3 Vectors.  
> The original context, decision, and trade-offs are preserved below for historical auditability.

---

## 1. Context (Historical)
The platform requires secure candidate authentication, user management, and a robust relational database with vector similarity search capabilities (`pgvector`). We must evaluate whether to operate standalone AWS RDS PostgreSQL or leverage Supabase's managed PostgreSQL platform, and establish clear boundaries between API-layer authentication and database-level isolation.

## 2. Decision (Superseded)
Adopt **Supabase** for user authentication and managed PostgreSQL storage:
1. **Supabase Auth**: Manages candidate user registration, OAuth, and issues signed JWT access tokens.
2. **Supabase PostgreSQL**: Managed PostgreSQL 15/17 engine with the `pgvector` extension enabled for semantic embeddings.
3. **Connection Strategy**: Lambda runtime connects to Supabase via the shared Transaction Pooler on port 6543 (`statement_cache_size=0`), while Alembic migrations connect directly via session mode on port 5432.
4. **Tenant Isolation & Security Boundary**:
   - Supabase Auth validates caller identity at the API Gateway / FastAPI middleware level.
   - Supabase Auth does **not** automatically protect direct SQLAlchemy database connections. The application database role connects using application credentials.
   - Application queries must enforce user ownership (`WHERE user_id = current_user.id`).
   - Defense in depth is provided by using a dedicated least-privileged database role and evaluating transaction-scoped configuration parameters (`SET LOCAL app.current_user_id = :uid`) executed inside each transaction before tenant-protected queries to drive PostgreSQL Row-Level Security (RLS) policies without connection-level leakage across pooled transactions.

## 3. Alternatives Considered (Historical)
- **AWS RDS PostgreSQL**: AWS RDS requires minimum ~$15/month for the smallest `db.t4g.micro` instance with zero included free auth services. Rejected due to cost.
- **Custom Auth with Cognito**: AWS Cognito has higher complexity and less flexible developer ergonomics than Supabase Auth.

## 4. Consequences (Historical)
- **Positive**: Consolidated database and auth stack, native `pgvector` extension, built-in pooling infrastructure, generous free tier.
- **Negative**: Third-party dependency outside AWS; free tier instances pause after 7 days of inactivity; transaction pooler disallows prepared statements; direct database access requires explicit tenant isolation logic.

## 5. Risks (Historical)
- Prepared statement cache errors with `asyncpg`. Mitigated by setting `statement_cache_size=0` on SQLAlchemy engine connect args.
- Cross-tenant data leaks if application queries omit tenant filters. Mitigated by least-privileged database roles, mandatory user tenancy checks, and RLS defense in depth.

## 6. References
- [ADR-013: Amazon Cognito User Pools for Candidate Authentication](./ADR-013-cognito-authentication.md)
- [ADR-014: Amazon Aurora PostgreSQL Serverless v2 and Lambda Connectivity Strategy](./ADR-014-aurora-postgresql-serverless-v2.md)
- [ADR-015: Amazon S3 Vectors for Scalable Candidate and Job Vector Similarity Search](./ADR-015-s3-vectors-for-vector-storage.md)
- Supabase Connecting to Postgres: https://supabase.com/docs/guides/database/connecting-to-postgres
- Supabase Connection Pooling: https://supabase.com/docs/guides/database/connecting-to-postgres/pooling-and-limits
- [docs/SECURITY.md](../SECURITY.md)
