# Cost & Operations Specification: AI Career Platform

> **Status**: Approved Foundation  
> **Audience**: Technical Lead, DevOps Engineers, FinOps  
> **Revision**: 1.1 (Phase 00)

---

## 1. Cost Management Principles & Strategy

The platform is designed to operate on a highly efficient, serverless footprint. While cloud credits or introductory allowances may be available, the architecture strictly minimizes baseline recurring operational expenses.

### Key Cost Realities
- **No Guaranteed Zero-Cost Hosting**: Hosting is never guaranteed to be ₹0 or \$0. Actual operating expenses depend on candidate traffic, invocation volumes, account eligibility (12-month introductory tier vs. always-free allowances), and third-party provider quotas.
- **Cost Minimization Mandate**: The architecture avoids fixed, idle charges by provisioning serverless, on-demand resources and enforcing strict operational limits.

### Architectural Rules for Cost Containment:
1. **No Always-On Virtual Machines**: Strictly no EC2 instances or long-running worker VMs.
2. **No Managed Cache Clusters**: Strictly no Amazon ElastiCache (Redis/Memcached) clusters. In-memory caching uses application lifecycle memory; persistent data uses Supabase PostgreSQL.
3. **No NAT Gateways**: AWS NAT Gateways incur a fixed monthly charge (~$32/month per gateway in `ap-south-1`) plus data processing fees. Lambda functions that require internet egress (e.g. BYOK LLM requests) must remain outside a private VPC unless required by regulatory constraints.
4. **No Provisioned Concurrency**: Lambda functions use on-demand concurrency. Provisioned concurrency introduces fixed hourly charges.
5. **No AWS Managed Relational Database (RDS)**: Relational database services are consolidated onto Supabase.

---

## 2. Infrastructure Services Cost & Allowance Matrix

*(Allowances referenced below reflect official provider documentation as of November 2026. Account eligibility and terms may vary.)*

| Service | Pricing Dimension | Reference Allowance & Documentation | Architectural Strategy to Prevent Overages |
| :--- | :--- | :--- | :--- |
| **AWS Lambda** | Requests & Compute (GB-seconds) | [AWS Lambda Pricing](https://aws.amazon.com/lambda/pricing/) includes **1M free requests** and **400,000 GB-seconds** of compute time monthly. | Size functions appropriately (256 MB = 1,600,000s compute; 512 MB = 800,000s compute); enforce conservative timeouts (10s API, 30s worker). |
| **API Gateway (HTTP API)** | API Requests | [API Gateway Pricing](https://aws.amazon.com/api-gateway/pricing/): 1M requests/mo free under initial 12-month tier; billed per million requests thereafter (~$1.00/million). | Lightweight payloads; HTTP API v2 (up to 70% cheaper than REST API v1); client-side query caching. |
| **Amazon SQS** | API requests (messages) | [Amazon SQS Pricing](https://aws.amazon.com/sqs/pricing/) includes **1M requests/mo** free under the always-free tier. | Long polling (`WaitTimeSeconds = 20`); batch message processing to minimize API call counts. |
| **EventBridge Scheduler** | Invocations | [EventBridge Pricing](https://aws.amazon.com/eventbridge/pricing/) includes **14M invocations/mo** free tier. | Lean schedule set (single daily digest cron at 06:00 AM IST). |
| **Amazon CloudWatch Logs** | Ingestion & Archive Storage | [CloudWatch Pricing](https://aws.amazon.com/cloudwatch/pricing/) includes 5 GB log ingestion and 5 GB storage free. | **Consistent 7-Day Retention Policy**: All Lambda log groups enforce `retention_in_days = 7` to prevent unbounded log accumulation. |
| **Supabase PostgreSQL** | Compute & Storage | [Supabase Pricing](https://supabase.com/pricing/): Free plan provides up to 500 MB database storage and 1 GB file storage. | Strict data retention for stale job postings; connection pooling via Transaction Pooler to avoid hitting connection limits. |
| **LLM Inference** | Token generation | Handled via candidate BYOK | Zero platform token liability; users supply personal provider keys (NIM, Cloudflare, OpenRouter, Gemini). |

---

## 3. Operational Guardrails & Alarms

### 3.1. AWS Budget & Cost Alarms
- **Billing Alarms**: Configured in CloudWatch using AWS Budgets:
  - Alert 1: Projected monthly spend exceeds \$10 (Warning).
  - Alert 2: Actual spend reaches \$25 (High Priority Notification).
- **Concurrency Caps**:
  - API Lambda reserved concurrency capped at 20 instances during initial release to guard against denial-of-wallet attacks.
  - SQS Worker Lambda concurrency capped at 5 instances to protect Supabase connection pool limits.

### 3.2. Consistent CloudWatch Log Retention Policy
By default, CloudWatch log groups retain log streams indefinitely, creating compounding storage costs.
- **Universal Policy**: Terraform strictly configures `retention_in_days = 7` across **all** Lambda log groups in both non-production and production environments.

### 3.3. Supabase Free Tier Monitoring
- Supabase pauses free-tier projects after 7 days of inactivity.
- Regular development and automated health probes keep active projects awake during development cycles.
- Monitor database storage utilization to stay well beneath the 500 MB quota by pruning raw scraped HTML and storing only normalized job summaries.
