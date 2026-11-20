# ADR-005: SQS-Based Background Processing

- **Status**: Accepted
- **Date**: 2026-11-20
- **Authors**: Technical Lead, Architecture Engineer

---

## 1. Context
Asynchronous workloads—including resume parsing, embedding calculations, job ingestion, and email digest generation—must not block synchronous HTTP requests on the FastAPI API Gateway. We must choose a message queue mechanism that fits the serverless architecture.

## 2. Decision
Adopt **Amazon SQS** as the asynchronous message broker, coupled with a dedicated **Worker Lambda**:
1. Synchronous API endpoints enqueue task events to SQS.
2. A separate Worker Lambda consumes SQS event batches (1–10 messages) with an invocation visibility timeout of 60 seconds.
3. Fault tolerance is guaranteed using an SQS Dead-Letter Queue (DLQ) with `maxReceiveCount=3`.
4. All worker task handlers are written to be strictly idempotent.

## 3. Alternatives Considered
- **Celery with Redis**: Requires an always-on Redis cluster ($15–$30/mo) and running worker processes. Incompatible with cost-effective serverless architecture.
- **In-process FastAPI BackgroundTasks**: Runs within the API request context; if Lambda terminates or times out, unfinished background tasks are lost.

## 4. Consequences
- **Positive**: 1,000,000 monthly requests included in AWS free tier; fully serverless; zero idle costs; built-in retry and dead-letter queue semantics.
- **Negative**: SQS batch payload size limited to 256 KB (large payloads must pass object storage pointers, not raw file content).

## 5. Risks
- Message duplication. Mitigated by writing idempotent database writes using unique idempotency keys.

## 6. References
- AWS Lambda with SQS: https://docs.aws.amazon.com/lambda/latest/dg/with-sqs.html
- SQS Event Source Configuration: https://docs.aws.amazon.com/lambda/latest/dg/services-sqs-configure.html

