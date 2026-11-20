# ADR-002: FastAPI Deployment on AWS Lambda Using Mangum and ZIP Packaging

- **Status**: Accepted
- **Date**: 2026-11-20
- **Authors**: Technical Lead, Architecture Engineer

---

## 1. Context
We need a hosting runtime for the Python 3.12 FastAPI backend. Objectives include: minimizing fixed idle operational costs, scaling dynamically under traffic surges, and maintaining rapid response times for Indian users in `ap-south-1` (Mumbai). Running an EC2 instance or ECS cluster incurs 24/7 compute billing regardless of traffic.

## 2. Decision
Deploy the FastAPI backend as a serverless function on **AWS Lambda** in region `ap-south-1` using the **Mangum** ASGI adapter, fronted by an **AWS API Gateway HTTP API (v2)**. Code and dependencies are packaged as standard uncompressed ZIP deployment packages (< 250 MB).

## 3. Alternatives Considered
- **Always-on Container (ECS Fargate / EC2)**: Rejected due to recurring baseline monthly costs (~$15–$40/month minimum) and management overhead.
- **AWS Lambda Container Images (OCI)**: Allows up to 10 GB images, but cold starts are generally slower and container registry management adds build complexity compared to native ZIP packaging.
- **Platform-as-a-Service (Render / Railway)**: Outside the authorized AWS infrastructure stack.

## 4. Consequences
- **Positive**: True zero-idle cost, automatic horizontal scaling, built-in cloud metrics, high availability within `ap-south-1`.
- **Negative**: Lambda cold starts (~500ms–1.2s for Python runtimes); deployment package size is strictly bounded to 250 MB uncompressed; requires stateless execution and serverless database pooling.

## 5. Risks
- Package size creep from heavy dependencies. Mitigated by strictly managing dependencies with `uv` and keeping heavy machine learning models off the primary API Lambda.

## 6. References
- AWS Lambda Python Developer Guide: https://docs.aws.amazon.com/lambda/latest/dg/lambda-python.html
- Mangum Documentation: https://mangum.fastapiexpert.com/
