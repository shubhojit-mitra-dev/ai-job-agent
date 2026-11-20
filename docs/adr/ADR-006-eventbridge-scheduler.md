# ADR-006: EventBridge Scheduler for Scheduled Workloads

- **Status**: Accepted
- **Date**: 2026-11-20
- **Authors**: Technical Lead, Architecture Engineer

---

## 1. Context
The platform requires periodic cron-like scheduling:
- Daily morning candidate career digest generation at 06:00 AM India Standard Time (IST).
- Periodic job scraping and freshness validation.
We need a reliable, cost-effective scheduling mechanism that does not require a constantly running cron daemon and handles timezones accurately without manual UTC conversions.

## 2. Decision
Use **Amazon EventBridge Scheduler** to trigger scheduled workloads:
1. EventBridge Scheduler schedules are defined via Terraform using the explicit timezone **`Asia/Kolkata`** (`schedule_expression_timezone = "Asia/Kolkata"` with `cron(0 6 * * ? *)`).
2. The schedule target is configured to send a message directly to the SQS tasks queue using IAM permissions, bypassing any intermediary invoking Lambda.
3. The SQS Worker Lambda consumes the message and executes the batch digest or ingestion workflow.

## 3. Alternatives Considered
- **Self-hosted Celery Beat / Linux cron**: Requires permanent server compute. Rejected due to cost.
- **EventBridge Rules (Classic)**: EventBridge Scheduler is the newer, more flexible service offering native timezone support (`Asia/Kolkata`), retries, and direct SQS targets.

## 4. Consequences
- **Positive**: 14 million invocations/month free tier; high reliability; native timezone support without daylight saving/UTC confusion; no compute servers to manage.
- **Negative**: Debugging scheduled triggers requires CloudWatch metric and SQS queue inspection.

## 5. Risks
- Batch jobs triggering simultaneously could overwhelm Supabase database connection limits. Mitigated by throttling worker Lambda concurrency to 5 instances.

## 6. References
- Amazon EventBridge Scheduler User Guide: https://docs.aws.amazon.com/scheduler/latest/UserGuide/what-is-scheduler.html
