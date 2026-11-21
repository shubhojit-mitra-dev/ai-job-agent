# ADR-011: Embedding Generation Strategy, S3 Vectors Integration, and Deployment Constraints

- **Status**: Accepted
- **Date**: 2026-11-20 (Updated 2026-11-21)
- **Authors**: Technical Lead, Architecture Engineer

---

## 1. Context
We require high-dimensional semantic vector embeddings for job opportunities and candidate profile summaries to power semantic similarity matching. However, deploying standard Sentence Transformers / PyTorch models inside an AWS Lambda ZIP deployment package introduces severe constraints:
- AWS Lambda uncompressed ZIP deployment package size is strictly capped at **250 MB**.
- Standard PyTorch (`torch`), `scipy`, and `transformers` wheels easily exceed 400–800 MB, causing packaging failure.
- In-memory model loading during Lambda cold starts can add 3–8 seconds of latency and demand 1–2 GB of Lambda RAM ($).

With the migration to an AWS-native architecture and the adoption of **Amazon S3 Vectors** (ADR-015), we must define an embedding generation strategy that:
1. Separates embedding generation from vector storage.
2. Identifies our initial production embedding model candidate while preserving provider neutrality.
3. Provides a clean local development and automated testing experience without external API dependencies.
4. Addresses multilingual retrieval realities for Indian candidate and job markets.

---

## 2. Decision

### 2.1. Adopt Amazon Titan Text Embeddings V2 as Initial Candidate
Adopt **Amazon Titan Text Embeddings V2** (`amazon.titan-embed-text-v2:0`) via Amazon Bedrock as the primary candidate embedding model for production:
- Supports flexible output dimensions (1024, 512, or 256 dimensions; normalized embeddings).
- Native support for multilingual text across 100+ languages, well-suited for Indian hiring contexts.
- Completely eliminates embedding model weights and PyTorch dependencies from the Lambda ZIP package, keeping deployment packages < 50 MB.

### 2.2. Embedding Provider Abstraction (`EmbeddingProvider`)
To ensure the platform is never locked into a single provider, embedding generation is abstracted behind an asynchronous protocol:

```python
class EmbeddingProvider(Protocol):
    async def embed_text(self, text: str) -> list[float]: ...
    async def embed_batch(self, texts: list[str]) -> list[list[float]]: ...
```

- **Production Implementation**: `BedrockTitanEmbeddingProvider` invokes the Amazon Bedrock runtime API.
- **Alternative Open Provider**: An optional fallback client for inexpensive open endpoints (e.g. Cloudflare Workers AI `bge-small-en-v1.5` or FastEmbed in a dedicated container).
- **Local / CI Implementation (`FakeEmbeddingProvider`)**: Generates deterministic synthetic embedding vectors (e.g. hash-seeded floats) without making external network or paid API calls.

### 2.3. Delineation from Vector Storage (Amazon S3 Vectors)
- S3 Vectors (ADR-015) is strictly a vector index and similarity retrieval store; it does **not** compute embeddings.
- Embedding generation occurs prior to vector upsert:
  1. The resume parsing or job ingestion worker calls `EmbeddingProvider.embed_text(normalized_text)`.
  2. The resulting vector array is passed to `VectorStore.upsert_vector(index_name, id, vector, metadata)`.

### 2.4. Multilingual Retrieval Benchmark Requirement
The Indian hiring landscape involves job descriptions and search queries in English, Hinglish, and regional languages (Hindi, Marathi, Tamil, Telugu, Kannada, Bengali).
- In Phase 02, the team will establish a deterministic benchmark test suite measuring retrieval accuracy (Recall@K, MRR) across:
  - Technical English job listings.
  - Job titles transliterated into Latin script (e.g. "fresher bharti", "backend developer naukri").
  - Hybrid multilingual job requirements.
- The model choice will be validated or adjusted based on benchmark results before final production freeze.

---

## 3. Alternatives Considered

- **Direct PyTorch in API Lambda**: Rejected immediately due to the 250 MB package size limit and 3–8s cold start penalties.
- **FastEmbed / ONNX Runtime in SQS Worker Lambda**: Feasible (< 80 MB wheel), but Bedrock Titan Text Embeddings V2 offloads compute entirely and provides higher-dimensional multilingual support without CPU contention in Lambda.
- **Proprietary Paid Embedding APIs (e.g. OpenAI text-embedding-3)**: Violates our AWS-native consolidation and budget constraints.

---

## 4. Consequences

### Positive
- Backend Lambda ZIP package remains ultra-lightweight (< 50 MB), resulting in sub-second cold starts.
- Native multilingual support via Titan Text Embeddings V2.
- Local development and CI testing run 100% offline with zero cost via `FakeEmbeddingProvider`.

### Negative
- Production embedding generation requires Bedrock runtime access, subject to the current AWS Support quota resolution (ADR-016).
- Re-indexing required if embedding model dimensions or versions are changed in the future.

---

## 5. Security Implications
- Text sent for embedding generation must be scrubbed of candidate direct contact identifiers (phone numbers, personal emails) before transmission.
- Bedrock API calls use least-privilege IAM execution roles (`bedrock:InvokeModel`).

---

## 6. Cost Implications
- Titan Text Embeddings V2 is billed at **\$0.00002 per 1,000 input tokens** (extremely economical: \$0.02 per 1,000,000 tokens).
- For 10,000 candidate resumes (average 500 tokens each) and 50,000 job descriptions, total embedding generation cost is **< \$0.60**, well within our \$200 budget.

---

## 7. Risks and Mitigations
- **Risk**: Bedrock quota blocker delays live Titan embeddings.
  - *Mitigation*: Application code and tests use `FakeEmbeddingProvider`. Bedrock runtime is wired via dependency injection once account access is cleared.

---

## 8. References
- [Amazon Bedrock Titan Text Embeddings V2](https://docs.aws.amazon.com/bedrock/latest/userguide/titan-embedding-models.html)
- [ADR-015: Amazon S3 Vectors for Vector Storage](./ADR-015-s3-vectors-for-vector-storage.md)
- [ADR-016: Amazon Bedrock Foundation Model Integration](./ADR-016-bedrock-foundation-model-integration.md)
