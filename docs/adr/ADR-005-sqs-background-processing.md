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
2. A separate Worker Lambda consumes SQS event batches (1–10 messages).
3. **Visibility Timeout Formula**: The SQS queue visibility timeout must be configured to **at least six times the configured Lambda function timeout**, factoring in the batching window (`MaximumBatchingWindowInSeconds`) and retry behavior in accordance with official AWS architectural guidance.
4. Fault tolerance is guaranteed using an SQS Dead-Letter Queue (DLQ) with `maxReceiveCount=3`.
5. All worker task handlers are written to be strictly idempotent.

## 3. Alternatives Considered
- **Celery with Redis**: Requires an always-on Redis cluster and running worker processes. Incompatible with cost-effective serverless architecture.
- **In-process FastAPI BackgroundTasks**: Runs within the API request context; if Lambda terminates or times out, unfinished background tasks are lost.

## 4. Consequences
- **Positive**: 1,000,000 monthly requests included in AWS always-free tier; fully serverless; zero idle costs; built-in retry and dead-letter queue semantics.
- **Negative**: SQS batch payload size limited to 256 KB (large payloads must pass object storage pointers, not raw file content).

## 5. Risks
- Message duplication. Mitigated by idempotent database writes using unique idempotency keys and proper visibility timeout sizing.

## 6. References
- AWS Lambda with SQS Documentation: https://docs.aws.amazon.com/lambda/latest/dg/with-sqs.html
- SQS Event Source Configuration: https://docs.aws.amazon.com/lambda/latest/dg/services-sqs-configure.html
