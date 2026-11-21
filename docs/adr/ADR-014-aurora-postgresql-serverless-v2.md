# ADR-014: Amazon Aurora PostgreSQL Serverless v2 and Lambda Connectivity Strategy

- **Status**: Accepted
- **Date**: 2026-11-21
- **Authors**: Technical Lead, Architecture Engineer

---

## 1. Context
The AI Career Platform requires a highly reliable, cost-effective relational database in AWS `ap-south-1` (Mumbai) for candidate profiles, parsed resumes, job opportunities, match records, and application state.

Following the decision to migrate from Supabase to an AWS-native architecture, we must establish our database platform and resolve the connectivity architecture between serverless AWS Lambda execution environments and PostgreSQL.

Critically, we must:
1. Retain **SQLAlchemy 2.0 (Async)** and **Alembic** schema migrations without rewriting domain models.
2. Evaluate and document three distinct Lambda-to-PostgreSQL connectivity options:
   - **RDS Data API over HTTPS**.
   - **Conventional PostgreSQL connections using `asyncpg`**.
   - **RDS Proxy with Lambda VPC connectivity**.
3. Evaluate cost, connection pooling, NAT Gateway requirements, Aurora auto-pause capabilities, and operational complexity against our strict \$200 three-month AWS credit budget.

---

## 2. Decision

### 2.1. Adopt Amazon Aurora PostgreSQL Serverless v2
Adopt **Amazon Aurora PostgreSQL Serverless v2** (PostgreSQL 16 compatible) in `ap-south-1` as the primary relational database.
- Scales dynamically in fractional Aurora Capacity Units (ACUs) from 0.5 ACU up to configured thresholds based on real-time CPU and memory demand.
- Supports auto-pause (scale-to-zero) in supported Aurora Serverless v2 configurations when completely idle, minimizing baseline cloud expenditure during non-usage windows.

### 2.2. Rigorous Evaluation of Lambda Connectivity Options

We conducted an exhaustive technical and economic evaluation across the three candidate connectivity architectures:

| Evaluation Dimension | Option 1: RDS Data API over HTTPS | Option 2: Direct TCP (`asyncpg` + `NullPool`) | Option 3: RDS Proxy + VPC |
| :--- | :--- | :--- | :--- |
| **SQLAlchemy 2.0 Compatibility** | **Poor / Non-Standard**: Requires specialized dialect (`sqlalchemy-aurora-data-api`). Lacks standard asyncpg connection pooling, prepared statements, and async streaming cursors. | **Excellent (Native)**: Standard `postgresql+asyncpg://` driver fully supported by SQLAlchemy 2.0 async engine and Alembic. | **Excellent**: Standard PostgreSQL connection string supported with `asyncpg` or `psycopg`. |
| **Lambda Networking** | **No VPC Required**: Lambda runs outside VPC; communicates via HTTPS AWS API endpoint. | **VPC Required**: Lambda must be inside VPC private subnets to route to Aurora private endpoint. | **VPC Required**: Lambda and RDS Proxy both reside inside the VPC. |
| **NAT Gateway / Egress Cost** | **Zero NAT Gateway Cost**: No NAT Gateway required for Lambda. Calls AWS APIs over public/regional HTTPS endpoints. | **High Cost Penalty**: If Lambda needs internet egress (BYOK LLMs, external job scraping), requires AWS NAT Gateway (~**\$32/mo** in `ap-south-1` + data charges) OR VPC Endpoints for all AWS services (~**\$7.20/mo** per endpoint). | **High Cost Penalty**: Identical to Option 2: requires NAT Gateway or multiple VPC Endpoints for any internet-bound Lambda. |
| **Connection Pooling** | **Stateless**: Connections are managed internally by the AWS Data API service. Lambda never opens TCP sockets to PostgreSQL. | **Application Controlled**: Lambda uses `NullPool` to open and close connections on demand. Concurrency must be capped to prevent connection exhaustion. | **Managed Pooler**: RDS Proxy maintains warm connection pool to Aurora; handles Lambda connection surges. |
| **Auto-Pause (Scale-to-Zero)** | **Fully Compatible**: Stateless HTTPS requests allow Aurora to scale to 0.5 or 0 ACUs when idle. | **Partially Compatible**: Idle Lambdas release connections via `NullPool`, allowing scaling down; however, background pings or lingering sockets can prevent sleep. | **Incompatible with Scale-to-Zero**: RDS Proxy maintains persistent warm connections to Aurora, preventing Aurora from auto-pausing to 0 ACUs. |
| **Alembic Migration Execution** | **Complex / Friction**: Running DDL migrations over Data API requires specialized migration scripts or a separate direct connection runner. | **Clean / Native**: Alembic connects natively via standard PostgreSQL connection string (`postgresql://`) in CI/CD. | **Clean / Native**: Alembic connects directly or via RDS Proxy. |
| **Fixed Monthly Cost** | **\$0.00 fixed**: Billed per request / ACU time only. | **~\$32/mo** for NAT Gateway if external egress needed; or \$0 if VPC Endpoints or separate egress architecture used. | **~\$15–\$25/mo** for RDS Proxy + **~\$32/mo** for NAT Gateway = **~\$47–\$57/mo** fixed baseline. |

### 2.3. Architectural Conclusion & Recommendation

1. **Do NOT Claim RDS Data API is a Drop-in `asyncpg` Driver**:
   - The RDS Data API executes SQL via HTTP POST requests (`rds-data:ExecuteStatement`). It is **not** wire-compatible with PostgreSQL TCP wire protocol and does **not** natively support `asyncpg`.
   - Adopting Data API would require non-standard dialects (`sqlalchemy-aurora-data-api`), introducing maintenance friction, limitations on bulk operations, and custom Alembic migration runners.
2. **Reject RDS Proxy for Initial Deployment**:
   - RDS Proxy incurs a fixed hourly charge per vCPU (~**\$0.015/vCPU-hr** = ~\$11–\$22/month minimum) and prevents Aurora Serverless v2 from scaling to 0 ACUs by keeping persistent pool connections open. This violates our strict cost-containment mandate on a \$200 budget.
3. **Recommended Cost-Conscious Architecture**:
   - **Local Development**: Continues using local containerized PostgreSQL (`pgvector/pgvector:pg16`) via Docker Compose with `asyncpg` and Alembic. Developers do **not** require AWS credentials or Aurora instances.
   - **Production Application Runtime**: Connect to Aurora PostgreSQL Serverless v2 using standard `asyncpg` with `NullPool` and explicit Lambda concurrency caps (maximum 20 API instances, 5 SQS workers) to prevent database connection spikes.
   - **NAT Gateway Avoidance**: To eliminate the \$32/month NAT Gateway cost while keeping Lambda in a VPC for database access:
     - Architecture Option A: Place the API Lambda inside the VPC and use **VPC Endpoints (PrivateLink)** only for essential AWS services (S3, SQS, Bedrock, Cognito), while offloading internet-bound BYOK LLM requests to an out-of-VPC worker or reverse proxy.
     - Architecture Option B: In non-production testing, evaluate whether Aurora public accessibility with strict IP allowlisting and SSL/TLS certificate verification can serve as an ephemeral cost-saving strategy, or whether the RDS Data API dialect matures sufficiently to support our SQLAlchemy async workloads cleanly.
   - **Unresolved Decision Recording**: The specific production network boundary (VPC Endpoints vs NAT Gateway vs Data API adapter) is recorded as an **Active Evaluation** for Phase 07 (Terraform Infrastructure), ensuring we do not prematurely lock into infrastructure before measuring actual Lambda traffic patterns.

---

## 3. Consequences

### Positive
- Retains 100% of existing SQLAlchemy 2.0 async models, schemas, and Alembic migrations.
- Aurora Serverless v2 scales dynamically between 0.5 and 2.0 ACUs during active testing, minimizing idle spend.
- Co-located in `ap-south-1` (Mumbai), providing sub-10ms network latency to Lambda compute.
- Avoids the fixed overhead of RDS Proxy (~$15–$25/mo).

### Negative
- Direct VPC connectivity requires careful network planning (subnets, route tables, security groups) in Terraform.
- Lambda in VPC requires resolving internet egress for BYOK LLMs without blowing the budget on NAT Gateways.

---

## 4. Security Implications
- **Encryption at Rest**: Aurora storage is encrypted using AWS KMS (`aws/rds` or customer-managed key).
- **Encryption in Transit**: SSL/TLS (`sslmode=require`) is enforced for all client connections.
- **Database Role Isolation**: The application runtime connects using a dedicated non-superuser role (`career_app_user`) with permissions restricted strictly to application tables. Alembic migrations execute using dedicated administrative credentials during deployment.
- **Tenant Isolation**: As established in [ADR-003](./ADR-003-supabase-auth-and-postgresql.md) and [docs/SECURITY.md](../SECURITY.md), all queries must enforce user ownership filters (`WHERE user_id = :uid`), augmented by transaction-scoped context (`SET LOCAL app.current_user_id = :uid`) inside each transaction.

---

## 5. Cost Implications
- **Aurora Serverless v2**: Billed at ~\$0.12 per ACU-hour in `ap-south-1`.
  - At 0.5 ACU baseline running 4 hours/day during active development: 0.5 * \$0.12 * 4 * 30 = **~\$7.20/month**.
  - Auto-pause during nights/weekends keeps relational database costs well within our \$200 credit budget.
- **Storage**: \$0.10 per GB-month. For early-stage testing (< 5 GB), relational storage costs under **\$0.50/month**.

---

## 6. Risks and Mitigations
- **Risk**: Connection exhaustion under high Lambda concurrency.
  - *Mitigation*: Configure `poolclass=NullPool` on SQLAlchemy engines; set Lambda reserved concurrency limits (20 API, 5 worker); use `statement_cache_size=0`.
- **Risk**: High NAT Gateway charges.
  - *Mitigation*: Strictly avoid provisioning AWS NAT Gateways without explicit authorization. Use S3 Gateway Endpoints (free) and evaluate PrivateLink or split-worker architectures.

---

## 7. References
- [Amazon Aurora Serverless v2 Documentation](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-serverless-v2.html)
- [Using the RDS Data API](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/data-api.html)
- [Managing Connections with Amazon RDS Proxy](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/rds-proxy.html)
- [Amazon Aurora Pricing](https://aws.amazon.com/rds/aurora/pricing/)
- [docs/SECURITY.md](../SECURITY.md)
