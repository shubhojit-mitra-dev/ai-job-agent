# Deployment Specification: AI Career Platform

> **Status**: Approved Foundation (AWS-Native Target Architecture)  
> **Audience**: DevOps, Cloud Architects, Backend Engineers  
> **Target Region**: AWS `ap-south-1` (Mumbai)  
> **Revision**: 2.0 (Phase 01 Architecture Migration)

---

## 1. Cloud Architecture & Infrastructure Model

The platform leverages an **AWS Serverless & Managed Cloud Architecture** in `ap-south-1` (Mumbai) to achieve high availability, low latency for Indian candidates, and near-zero idle infrastructure cost.

```mermaid
flowchart TD
    GitHub["GitHub Actions CI/CD (AWS OIDC Auth)"] -->|Terraform Plan/Apply| AWSInfra["AWS Infrastructure (ap-south-1)"]
    GitHub -->|ZIP Deployment| Lambda["FastAPI Lambda Function"]
    GitHub -->|Run Alembic Migrations| Aurora[("Aurora PostgreSQL Serverless v2")]
    
    User["Candidate Browser (Next.js)"] -->|Cognito Auth| Cognito["Amazon Cognito User Pools"]
    User -->|HTTPS + Bearer JWT| APIGW["API Gateway HTTP API"]
    APIGW -->|JWT Authorizer Validation| APIGW
    APIGW -->|ASGI Proxy| Lambda
    Lambda -->|NullPool / port 5432| Aurora
    Lambda -->|ANN Vector Queries| S3Vectors[("Amazon S3 Vectors")]
    Lambda -->|Presigned URLs| S3Docs[("Private Amazon S3")]
    Lambda -->|Enqueue Tasks| SQS["Amazon SQS Queue"]
    EventBridge["EventBridge Scheduler (Asia/Kolkata)"] -->|Daily 06:00 IST| SQS
    SQS -->|Batch Trigger| WorkerLambda["Worker Lambda (Async)"]
    WorkerLambda -->|Embed & Store| S3Vectors
    WorkerLambda -->|Dead-Letter| DLQ["SQS DLQ"]
```

---

## 2. Component Specifications

### 2.1. FastAPI on AWS Lambda via Mangum
- **Adapter**: [Mangum](https://mangum.fastapiexpert.com/) translates AWS API Gateway v2 HTTP API payload events into ASGI HTTP requests and converts ASGI responses back into API Gateway payload format.
- **Entrypoint**:
  ```python
  from fastapi import FastAPI
  from mangum import Mangum
  from app.main import app

  handler = Mangum(app)
  ```
- **Runtime**: Python 3.12 (standard AWS Lambda managed runtime).
- **Packaging**: Standard uncompressed ZIP deployment package (< 250 MB). Managed via `uv export` to generate frozen wheel dependencies packaged cleanly into the deployment archive.

### 2.2. AWS API Gateway HTTP API & Cognito JWT Authorizer
- **Protocol**: HTTP API (v2) provides cost-effective latency (up to 70% cheaper than REST API v1).
- **Perimeter Security**: Native Cognito JWT Authorizer validates Bearer tokens at the edge using the Cognito User Pool issuer URL (`https://cognito-idp.ap-south-1.amazonaws.com/{userPoolId}`), preventing unauthenticated requests from invoking Lambda.
- **Features**: Automatic TLS 1.2+ termination, native CORS handling, and proxy routing to Lambda.

### 2.3. Amazon Aurora PostgreSQL Serverless v2
- **Engine**: PostgreSQL 16 compatible.
- **Scaling**: Scaled dynamically between 0.5 ACU and 2.0 ACUs in non-production, with auto-pause (scale-to-zero) enabled during prolonged idle periods.
- **Connection Strategy**: Lambda connects via standard `asyncpg` with `poolclass=NullPool` and `statement_cache_size=0`. Concurrency is capped (maximum 20 API instances, 5 workers) to prevent database connection spikes.

### 2.4. Amazon S3 Vectors & Document Storage
- **S3 Vectors**: Houses partitioned vector indexes (`job-vectors-index`, `candidate-vectors-index`) for semantic matching.
- **Private S3**: Stores candidate resume documents with Block Public Access, SSE-KMS encryption, candidate-scoped keys (`candidates/{user_id}/resumes/{resume_id}.pdf`), and 15-minute pre-signed URLs.

### 2.5. Asynchronous Tasks with Amazon SQS
- **Queues**:
  - `career-platform-tasks` for background workloads (resume extraction, embeddings, vector indexing).
  - `career-platform-tasks-dlq` with `maxReceiveCount=3` for poison message handling.
- **Visibility Timeout Configuration**:
  - In accordance with AWS Lambda and SQS best practices ([AWS Lambda with SQS Documentation](https://docs.aws.amazon.com/lambda/latest/dg/with-sqs.html)), the queue's visibility timeout must be configured to **at least 6 times the timeout of the consumer Lambda function**, with the batching window (`MaximumBatchingWindowInSeconds`) and retry behavior factored in.
  - *Example*: For a Worker Lambda configured with a 30-second execution timeout and a 10-second batch window, the visibility timeout is set to at least 190–200 seconds to prevent concurrent duplicate message deliveries.
- **Worker**: A dedicated lightweight Lambda function triggered by SQS batches (batch size 1–10).

### 2.6. Scheduled Workloads with Amazon EventBridge Scheduler
- **Recurring Jobs**: Scheduled triggers configured with explicit timezone **`Asia/Kolkata`**.
- **Example Schedule**: Daily candidate morning digest formulated at **06:00 AM IST** (`cron(0 6 * * ? *)`).
- **Target**: EventBridge triggers SQS directly using native IAM role permissions, completely avoiding custom scheduling servers.

---

## 3. Infrastructure as Code (Terraform)

All AWS infrastructure is codified using **Terraform** within `infra/terraform/`:
- **Remote State Storage**: Remote encrypted Amazon S3 bucket in `ap-south-1`.
- **Native S3 State Locking**: Uses S3-native state locking via Terraform's S3 backend lockfile capability (`use_lockfile = true`, supported in Terraform 1.10+ / OpenTofu 1.7+ using S3 conditional writes). A separate DynamoDB table is avoided to eliminate unnecessary resources.
- **Modules**:
  - `modules/cognito`: User Pool, App Client, password policies, verification templates.
  - `modules/aurora`: Aurora Serverless v2 cluster, subnet groups, security groups.
  - `modules/s3`: Private resume storage bucket with Block Public Access and lifecycle rules.
  - `modules/s3_vectors`: Vector index bucket and partitioned index configuration.
  - `modules/api_gateway`: HTTP API, stages, CORS, Cognito JWT Authorizer, and Lambda integration.
  - `modules/lambda`: Function execution roles, log retention (7 days), memory/timeout settings.
  - `modules/sqs`: Main queues, DLQs, visibility timeouts, and redrive policies.
  - `modules/scheduler`: EventBridge schedules with timezone `Asia/Kolkata`.
  - `modules/iam`: Least-privilege IAM execution roles for Lambda and GitHub Actions OIDC.

---

## 4. CI/CD & Secure GitHub Actions OIDC

To prevent credential leakage:
- **No Long-Lived AWS Keys**: We do **not** store `AWS_ACCESS_KEY_ID` or `AWS_SECRET_ACCESS_KEY` in GitHub Secrets.
- **OpenID Connect (OIDC)**: GitHub Actions assumes an ephemeral AWS IAM Role using short-lived JWT tokens:
  ```yaml
  permissions:
    id-token: write
    contents: read
  steps:
    - name: Configure AWS Credentials via OIDC
      uses: aws-actions/configure-aws-credentials@v4
      with:
        role-to-assume: arn:aws:iam::ACCOUNT_ID:role/GitHubActionsDeploymentRole
        aws-region: ap-south-1
  ```

---

## 5. Deployment Procedures & Rollbacks

1. **Pull Request Validation**:
   - `uv run ruff check .`
   - `uv run mypy .`
   - `uv run pytest`
   - `terraform fmt -check` and `terraform validate`
2. **Main Branch Deployment**:
   - Merges to `master` trigger automatic packaging and deployment via GitHub Actions OIDC.
   - Run Alembic migration job against Aurora PostgreSQL direct connection.
   - Deploy backend Lambda ZIP package.
   - Run post-deployment smoke test (`GET /health`).
3. **Rollback Strategy**:
   - Lambda versions and aliases allow instantaneous rollback to previous stable versions (`aws lambda update-alias --function-name ... --function-version PREVIOUS_STABLE`).
