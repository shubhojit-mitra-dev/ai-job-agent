# ADR-011: Local Embedding Strategy and Its Deployment Constraints

- **Status**: Proposed
- **Date**: 2026-11-20
- **Authors**: Technical Lead, Architecture Engineer

---

## 1. Context
We intend to leverage open-source/local embeddings (e.g. Sentence Transformers `all-MiniLM-L6-v2`, 384 dimensions) for job postings and candidate profiles. However, deploying Sentence Transformers inside an AWS Lambda ZIP deployment package introduces severe constraints:
- AWS Lambda uncompressed ZIP deployment package size is strictly capped at **250 MB**.
- Standard PyTorch (`torch`), `scipy`, and `transformers` wheels easily exceed 400–800 MB, causing packaging failure.
- In-memory model loading during Lambda cold starts can add 3–8 seconds of latency and demand 1–2 GB of Lambda RAM ($).

## 2. Decision (Investigation Underway)
We propose to **strictly forbid bundling standard PyTorch/Sentence-Transformers wheels into the primary API Gateway Lambda**.

We are evaluating the following implementation paths:
1. **Option 1: ONNX Runtime + FastEmbed in Worker Lambda**:
   - Use `fastembed` with ONNX Runtime CPU wheels (< 80 MB) running exclusively inside the asynchronous SQS Worker Lambda.
   - Embeddings are computed strictly out-of-band during background resume parsing or job ingestion.
2. **Option 2: Cloudflare Workers AI / FastEmbed Serverless Endpoint**:
   - Offload embedding computation to a lightweight serverless endpoint running open models (e.g. `bge-small-en-v1.5`) via free daily inference credits.
3. **Option 3: Dedicated Containerized Worker (OCI)**:
   - Package a separate worker Lambda using an AWS Lambda Container Image (allowing up to 10 GB), triggered solely via SQS.

## 3. Alternatives Considered
- **Direct PyTorch in API Lambda**: Rejected immediately due to package size limits and unacceptable cold starts.
- **Proprietary Paid Embedding APIs (e.g. OpenAI text-embedding-3)**: Violates the core product principle of avoiding mandatory paid platform API liabilities.

## 4. Consequences
- **Positive**: Protects the API Lambda from bloat, keeps HTTP response latency fast, maintains cost controls.
- **Negative**: Requires asynchronous embedding formulation; requires validation of ONNX vs standard PyTorch output quality.

## 5. Risks
- Complexity in synchronizing vector indexing if embeddings are computed asynchronously. Mitigated by state status flags (`PENDING_EMBEDDING`, `ACTIVE`) on job and profile records.

## 6. References
- AWS Lambda Deployment Packages: https://docs.aws.amazon.com/lambda/latest/dg/python-package.html
- FastEmbed / ONNX Runtime documentation.

