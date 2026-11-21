# Cost & Operations Specification: AI Career Platform

> **Status**: Approved Foundation (AWS-Native Target Architecture)  
> **Audience**: Technical Lead, DevOps Engineers, FinOps  
> **Target Region**: AWS `ap-south-1` (Mumbai)  
> **Budget Constraint**: ~$200 AWS credits valid for roughly 3 months  
> **Revision**: 2.0 (Phase 01 Architecture Migration)

---

## 1. Cost Management Principles & Strategy

The platform operates on a lean, serverless footprint in AWS `ap-south-1`. We have approximately **\$200 in AWS credits valid for roughly three months**. The architecture must prioritize strict cost containment to avoid depleting credits prematurely.

### Non-Negotiable Cost Guardrails:
1. **No Always-On Virtual Machines**: Strictly no Amazon EC2 instances, ECS services, or long-running worker VMs.
2. **No Managed Cache Clusters**: Strictly no Amazon ElastiCache (Redis/Memcached) clusters. In-memory caching uses application lifecycle memory; persistent data uses Aurora PostgreSQL.
3. **No RDS Proxy**: Managed RDS Proxy incurs fixed hourly charges (~**\$15–\$25/month**) and keeps warm connections open, preventing Aurora Serverless v2 from scaling down to 0 ACUs. Rejected in favor of `NullPool` with concurrency limits.
4. **NAT Gateway Avoidance**: An AWS NAT Gateway costs ~**\$32/month** in `ap-south-1` plus data processing fees, consuming over 45% of our monthly budget. Lambda functions must avoid NAT Gateways unless explicitly authorized by the Technical Lead. Use VPC Endpoints for S3 (free Gateway endpoint) and evaluate PrivateLink or split-worker architectures.
5. **No Provisioned Concurrency**: Lambda functions use on-demand concurrency. Provisioned concurrency introduces fixed hourly charges.
6. **No OpenSearch Serverless**: OpenSearch Serverless enforces minimums of 2–4 OCUs even when idle (~**\$175–\$350/month**), which would consume our entire credit allocation in under a month. Vector search is handled by Amazon S3 Vectors.
7. **Consistent 7-Day CloudWatch Retention**: CloudWatch logs must enforce `retention_in_days = 7` across **all** Lambda log groups to prevent unbounded log storage accumulation.

---

## 2. Infrastructure Services Cost & Allowance Matrix

*(Allowances and rates referenced below reflect official AWS documentation for `ap-south-1` as of November 2026. Account eligibility and terms may vary.)*

| Service | Pricing Dimension | Reference Allowance & Documentation | Architectural Strategy to Prevent Overages |
| :--- | :--- | :--- | :--- |
| **AWS Lambda** | Requests & Compute (GB-seconds) | [AWS Lambda Pricing](https://aws.amazon.com/lambda/pricing/): **1M free requests** and **400,000 GB-seconds** compute monthly. | Size functions appropriately (256 MB = 1,600,000s compute; 512 MB = 800,000s compute); enforce conservative timeouts (10s API, 30s worker). |
| **API Gateway (HTTP API)** | API Requests | [API Gateway Pricing](https://aws.amazon.com/api-gateway/pricing/): 1M requests/mo free under initial 12-month tier; ~$1.00/million thereafter. | Lightweight payloads; HTTP API v2 (up to 70% cheaper than REST API v1); client-side query caching. |
| **Amazon Cognito User Pools** | Monthly Active Users (MAUs) | [Amazon Cognito Pricing](https://aws.amazon.com/cognito/pricing/): **50,000 MAUs always free**. | Generous free tier completely covers early-stage candidate traffic (\$0 baseline). |
| **Amazon Aurora PostgreSQL Serverless v2** | ACU-hours & Storage | [Aurora Pricing](https://aws.amazon.com/rds/aurora/pricing/): ~\$0.12 per ACU-hour in `ap-south-1`; storage \$0.10/GB-month. | Configure min capacity at 0.5 ACU and max at 2.0 ACU. Enable auto-pause (scale-to-zero) during idle periods. Zero idle persistent connection poolers. |
| **Amazon S3 Vectors** | Vector Storage & Queries | [Amazon S3 Pricing](https://aws.amazon.com/s3/pricing/): Pay-per-query and storage. | Decoupled from relational database compute; avoids ACU memory inflation. |
| **Private Amazon S3** | Object Storage (GB) & Requests | [Amazon S3 Pricing](https://aws.amazon.com/s3/pricing/): \$0.023/GB-month in `ap-south-1`; 5 GB free for 12 months. | 5 MB upload limit; automated 7-day abort for incomplete multipart uploads; lifecycle rules for archived resumes. |
| **Amazon SQS** | API requests (messages) | [Amazon SQS Pricing](https://aws.amazon.com/sqs/pricing/): **1M requests/mo always free**. | Long polling (`WaitTimeSeconds = 20`); batch message processing (batch size 1–10). |
| **EventBridge Scheduler** | Invocations | [EventBridge Pricing](https://aws.amazon.com/eventbridge/pricing/): **14M invocations/mo free**. | Lean schedule set (single daily digest cron at 06:00 AM IST). |
| **Amazon CloudWatch Logs** | Ingestion & Storage | [CloudWatch Pricing](https://aws.amazon.com/cloudwatch/pricing/): 5 GB ingestion and 5 GB storage free. | **Universal 7-Day Retention**: All Lambda log groups enforce `retention_in_days = 7`. |
| **Amazon Bedrock (Titan Models)** | Tokens generated/processed | [Bedrock Pricing](https://aws.amazon.com/bedrock/pricing/): Pay-per-token. | Feature flag (`ENABLE_BEDROCK=false`) during pending quota; deterministic mocks in tests; candidate BYOK tier for high-volume inference. |
| **Candidate BYOK Inference** | Third-party tokens | User-supplied API keys | Zero platform token liability; users connect personal keys (NIM, Cloudflare, OpenRouter, Gemini). |

---

## 3. Operational Guardrails & Alarms

### 3.1. AWS Budget & Cost Alarms
- **Billing Alarms**: Configured in CloudWatch using AWS Budgets:
  - Alert 1: Projected monthly spend exceeds **\$10** (Warning notification).
  - Alert 2: Actual spend reaches **\$25** (High-priority engineering alert).
  - Alert 3: Cumulative 3-month spend approaches **\$150** (Critical review to safeguard remaining credits).
- **Concurrency Caps**:
  - API Lambda reserved concurrency capped at **20 instances** during initial release to guard against denial-of-wallet invocation spikes.
  - SQS Worker Lambda concurrency capped at **5 instances** to protect Aurora PostgreSQL connection limits.

### 3.2. Universal CloudWatch Log Retention Policy
By default, CloudWatch log groups retain log streams indefinitely, creating compounding storage costs.
- **Universal Policy**: Terraform strictly configures `retention_in_days = 7` across **all** Lambda log groups in both non-production and production environments.

### 3.3. Aurora Serverless v2 Scaling Guardrails
- **Min/Max ACUs**: Set minimum ACU to `0.5` and maximum ACU to `2.0` in non-production.
- **Auto-Pause (Scale-to-Zero)**: Ensure idle connections are not kept alive by application servers or unmanaged pingers, allowing Aurora to pause during inactive windows.

### 3.4. Bedrock Usage Controls & Quota Protection
- While the AWS Support quota case is pending, Bedrock invocations are disabled via `ENABLE_BEDROCK=false`.
- When enabled, Bedrock calls enforce strict `max_tokens` bounds (512–1024 tokens) and timeout limits (15 seconds).
