# ADR-006: EventBridge Scheduler for Scheduled Workloads

- **Status**: Accepted
- **Date**: 2026-11-20
- **Authors**: Technical Lead, Architecture Engineer

---

## 1. Context
The platform requires periodic cron-like scheduling:
- Daily morning candidate career digest generation (e.g. 06:00 AM IST).
- Periodic job scraping and freshness validation.
We need a reliable, cost-effective scheduling mechanism that does not require a constantly running cron daemon.

## 2. Decision
Use **Amazon EventBridge Scheduler** to trigger scheduled workloads:
1. EventBridge Scheduler schedules are defined via Terraform (e.g., `cron(30 0 * * ? *)` UTC, which is 06:00 AM IST).
2. The schedule target is configured to send a message directly to the SQS tasks queue using IAM permissions, bypassing any intermediary invoking Lambda.
3. The SQS Worker Lambda consumes the message and executes the batch digest or ingestion workflow.

## 3. Alternatives Considered
- **Self-hosted Celery Beat / Linux cron**: Requires permanent server compute. Rejected due to cost.
- **EventBridge Rules (Classic)**: EventBridge Scheduler is the newer, more flexible service offering timezone support, retries, and direct SQS targets.

## 4. Consequences
- **Positive**: 14 million invocations/month free; high reliability; native timezone support; no compute servers to manage.
- **Negative**: Debugging scheduled triggers requires CloudWatch metric and SQS queue inspection.

## 5. Risks
- Batch jobs triggering simultaneously could overwhelm Supabase database connection limits. Mitigated by throttling worker Lambda concurrency to 5 instances.

## 6. References
- Amazon EventBridge Scheduler User Guide: https://docs.aws.amazon.com/scheduler/latest/UserGuide/what-is-scheduler.html
