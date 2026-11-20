# Cost & Operations Specification: AI Career Platform

> **Status**: Approved Foundation  
> **Audience**: Technical Lead, DevOps Engineers, FinOps  
> **Revision**: 1.0 (Phase 00)

---

## 1. Cost Management Principles & Strategy

The platform is designed to operate on a highly efficient, cost-conscious footprint. While AWS credits may be available, the architecture strictly minimizes baseline recurring operational expenses.

### Core Architectural Rules for Cost Containment:
1. **No Always-On Virtual Machines**: Strictly no EC2 instances or long-running worker VMs.
2. **No Managed Cache Clusters**: Strictly no Amazon ElastiCache (Redis/Memcached) clusters ($15–$30+/month minimum). In-memory caching uses application lifecycle memory; cross-instance data uses Supabase PostgreSQL.
3. **No NAT Gateways**: AWS NAT Gateways incur a flat cost of ~$32/month per gateway plus data transfer fees. Lambda functions that require internet access (e.g. BYOK LLM requests) must remain outside a private VPC unless VPC endpoints or IPv6 egress are configured.
4. **No Provisioned Concurrency**: Lambda functions use on-demand concurrency. Provisioned concurrency introduces fixed hourly costs.
5. **No AWS Managed Relational Database (RDS)**: Database infrastructure is consolidated onto Supabase.

---

## 2. Infrastructure Services Cost Matrix

| Service | Pricing Dimension | Free Tier / Included Allowance | Strategy to Prevent Overages |
| :--- | :--- | :--- | :--- |
| **AWS Lambda** | Requests & Compute (GB-seconds) | 1,000,000 requests/mo & 3.2M sec compute | 256–512 MB memory allocation; short timeouts (10s API, 60s worker); memory profiling |
| **API Gateway (HTTP API)** | API Requests | 1,000,000 requests/mo (first 12 mos) | High-volume read caching on client; lightweight payloads |
| **Amazon SQS** | API requests (messages) | 1,000,000 requests/mo permanent free tier | Batch message sending (`SendMessageBatch`); long-polling (WaitTimeSeconds=20) |
| **EventBridge Scheduler** | Scheduled invocations | 14,000,000 invocations/mo free tier | Minimal schedules (daily crons only) |
| **Amazon CloudWatch** | Ingestion & Storage | 5 GB ingestion & 5 GB archive free | Log retention set strictly to **7 days** in dev/test, **14 days** in production |
| **Supabase PostgreSQL** | Compute & Storage | 500 MB database & 1 GB storage (Free Tier) | Strict retention for expired job listings; connection pooling via Transaction Pooler |
| **LLM Inference** | Token usage | Managed by candidate via BYOK | Zero platform token liability; users provide personal provider keys |

---

## 3. Operational Guardrails & Alarms

### 3.1. AWS Budget & Cost Alarms
- **Billing Alarms**: Configured in CloudWatch using AWS Budgets:
  - Alert 1: Projected monthly cost exceeds \$10 (Warning).
  - Alert 2: Actual spend reaches \$25 (High Priority Notification).
- **Concurrency Caps**:
  - API Lambda reserved concurrency capped at 20 instances during initial release to guard against denial-of-wallet attacks.
  - SQS Worker Lambda concurrency capped at 5 instances.

### 3.2. CloudWatch Log Retention Enforcement
By default, CloudWatch log groups retain logs indefinitely, creating compounding storage costs.
- Terraform strictly configures `retention_in_days = 7` across all Lambda log groups.

### 3.3. Supabase Free Tier Monitoring
- Supabase pauses free-tier projects after 7 days of inactivity.
- Regular development and automated health probes keep active projects awake during active development cycles.
- Monitor database storage utilization to stay well beneath the 500 MB quota by pruning raw scraped HTML and storing only normalized job summaries.

