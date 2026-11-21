# ADR-015: Amazon S3 Vectors for Scalable Candidate and Job Vector Similarity Search

- **Status**: Accepted
- **Date**: 2026-11-21
- **Authors**: Technical Lead, Architecture Engineer

---

## 1. Context
The AI Career Platform requires semantic vector search to match candidate profiles (skills, project summaries, aspirational goals) with job opportunity descriptions.

In Phase 00, `pgvector` inside PostgreSQL was initially considered. However, under our AWS-native architecture:
1. Storing and indexing large vector spaces (HNSW/IVFFlat indexes) directly inside relational database memory consumes significant Aurora Capacity Units (ACUs), inflating compute costs.
2. Amazon S3 Vectors provides scalable, cost-efficient vector storage and nearest-neighbor search decoupled from relational compute.
3. We must establish a clear separation of concerns between **embedding generation** and **vector storage & indexing**.
4. We must define vector indexing organization, tenant isolation, metadata filtering, lifecycle management, hybrid retrieval flows with Aurora PostgreSQL, and local development abstractions.

---

## 2. Decision

Adopt **Amazon S3 Vectors** as the authoritative vector storage and similarity retrieval engine for the platform:

### 2.1. Separation of Responsibilities
A strict architectural boundary is established:
- **Embedding Generation**: Performed exclusively by foundation embedding models (e.g. Amazon Titan Text Embeddings V2 via Amazon Bedrock, or configured open-source embedding providers).
- **Vector Storage & Indexing**: Performed by Amazon S3 Vectors. S3 Vectors stores the generated dense vector arrays, maintains vector indexes, and executes approximate nearest neighbor (ANN) cosine/Euclidean similarity queries.
- **Explicit Invariant**: S3 Vectors is **not** an embedding generation model. S3 Vectors accepts pre-computed embedding vectors and metadata payloads.

```mermaid
flowchart LR
    Text["Candidate Resume / Job Posting"] --> EmbedModel["Embedding Generator (Titan Text Embeddings V2)"]
    EmbedModel -->|Dense Vector (e.g. 1024-dim)| VectorStore["Amazon S3 Vectors Index"]
    VectorStore -->|Vector Similarity Query| TopMatches["Top-K Matching IDs + Similarity Scores"]
    TopMatches --> RelationalDB[("Aurora PostgreSQL (Relational Filters + Dealbreakers)")]
```

### 2.2. Vector Bucket and Index Organization
Vectors are partitioned into distinct indexes to prevent cross-domain pollution and ensure strict access boundaries:
1. **`job-vectors-index`**:
   - Contains embeddings of active, normalized job opportunity descriptions.
   - Metadata attributes: `job_id` (UUID), `experience_min`, `experience_max`, `work_mode` (remote/hybrid/onsite), `city`, `salary_floor_inr`, `is_active` (boolean).
2. **`candidate-vectors-index`**:
   - Contains candidate profile embeddings generated from structured resume summaries and confirmed competencies.
   - Metadata attributes: `candidate_id` (UUID), `updated_at`.
   - Strictly partitioned: candidate vectors are isolated and tagged with `candidate_id` to guarantee tenant isolation.

### 2.3. Metadata Filtering and Tenant Isolation
- **Tenant Isolation**: When querying or mutating candidate vectors, the application must pass an explicit filter matching the authenticated candidate ID (`metadata.candidate_id == current_user.id`).
- **Pre-Filtering vs Post-Filtering**:
  - S3 Vectors metadata filtering is applied to exclude hard dealbreakers where supported (e.g. `is_active == true`).
  - High-cardinality relational constraints (such as complex dealbreaker lists, CTC threshold comparisons, and dynamic company blocklists) are evaluated downstream in Aurora PostgreSQL to maximize index caching efficiency.

### 2.4. Vector Lifecycle: Upserts, Deletions, and Re-Indexing
- **Upsert on Profile / Job Ingestion**:
  - When a candidate uploads an updated resume or edits their profile, an async SQS worker triggers embedding generation and upserts the vector to S3 Vectors under the key `candidate_{user_id}`.
  - When new job postings are ingested, normalized embeddings are upserted under `job_{job_id}`.
- **Deletion on Account Deletion or Job Expiration**:
  - When a job is closed or flagged expired, its vector is deleted or marked inactive (`is_active = false`).
  - When a candidate exercises the Right to be Forgotten, their vector is deleted permanently from S3 Vectors.
- **Model Re-Indexing Strategy**:
  - If the embedding model changes (e.g. switching dimensions or upgrading versions), a batch re-indexing job is dispatched via SQS to recompute vectors from stored normalized text without requiring candidate re-uploads.

### 2.5. Hybrid Retrieval Integration with Aurora PostgreSQL
Retrieval operates via a two-stage **Hybrid Retrieval Pipeline**:
1. **Stage 1 (Semantic Retrieval via S3 Vectors)**:
   - The candidate profile embedding is queried against `job-vectors-index` requesting the top-`K` (e.g. top 100) nearest neighbors based on cosine similarity.
   - Returns a lightweight list: `[{job_id: "...", similarity: 0.87}, ...]`.
2. **Stage 2 (Relational Filtering & Deterministic Scoring in Aurora)**:
   - The application queries Aurora PostgreSQL:
     ```sql
     SELECT * FROM jobs 
     WHERE id IN (:candidate_job_ids)
       AND experience_min <= :candidate_exp
       AND salary_inr >= :candidate_min_ctc
       AND work_mode = ANY(:allowed_modes)
       AND NOT (dealbreaker_flags && :candidate_dealbreakers);
     ```
   - Matches passing relational filters are evaluated by the deterministic compatibility scoring rubric (ADR-010).

### 2.6. Local Development and Testing Abstraction
To ensure developers can run and test the application without AWS credentials, S3 Vectors access, or network overhead:
- Define an abstract `VectorStore` protocol in `apps/api/app/modules/jobs/vector_store.py`:
  ```python
  class VectorStore(Protocol):
      async def upsert_vector(self, index_name: str, vector_id: str, vector: list[float], metadata: dict) -> None: ...
      async def query_similarity(self, index_name: str, vector: list[float], top_k: int, filters: dict | None = None) -> list[VectorMatch]: ...
      async def delete_vector(self, index_name: str, vector_id: str) -> None: ...
  ```
- In local development and automated CI/CD test suites, instantiate a `FakeVectorStore`:
  - Maintains an in-memory dictionary of vectors.
  - Computes exact cosine similarity via pure Python / NumPy.
  - Requires zero network calls, zero AWS permissions, and executes in < 5ms.

### 2.7. Embedding Candidate & Multilingual Benchmark Mandate
- **Initial Candidate**: **Amazon Titan Text Embeddings V2** (`amazon.titan-embed-text-v2:0`) via Amazon Bedrock (1024, 512, or 256 dimensions; normalized embeddings; multilingual support).
- **Multilingual Retrieval Benchmark Requirement**:
  - The Indian employment market features job postings and candidate queries mixing English and regional Indian languages/scripts (e.g. Hindi, Hinglish, Marathi, Tamil, Telugu).
  - Before finalizing production weights, Phase 02 must execute a benchmark suite evaluating retrieval accuracy for Indian-context job titles, localized tech descriptions, and bilingual queries.

---

## 3. Alternatives Considered

- **`pgvector` inside Aurora PostgreSQL**:
  - *Evaluation*: Used in Phase 00 local Docker Compose.
  - *Reason for Rejection*: In Aurora Serverless, keeping large HNSW graph indexes in memory inflates ACU scaling and memory pressure. Offloading vector indexing to S3 Vectors keeps Aurora lean and allows Aurora to scale down during idle periods.
- **Pinecone / Qdrant / Weaviate Cloud**:
  - *Evaluation*: Popular dedicated vector databases.
  - *Reason for Rejection*: Third-party SaaS services requiring separate vendor contracts, API keys, egress networking, and higher baseline monthly fees (\$20–\$70/mo). Violates our AWS-native consolidation and \$200 budget constraint.
- **OpenSearch Serverless (Vector Search)**:
  - *Evaluation*: AWS managed OpenSearch vector collection.
  - *Reason for Rejection*: OpenSearch Serverless enforces a minimum of 2–4 OpenSearch Compute Units (OCUs) even when idle, resulting in minimum monthly costs of **~\$175–\$350/month**, which would exhaust our entire \$200 credit budget in under 30 days.

---

## 4. Consequences

### Positive
- Fully decoupled from relational compute; Aurora does not need to scale ACUs solely for vector index memory.
- S3-based durability, high availability, and native AWS IAM access controls.
- Local development remains 100% offline via `FakeVectorStore`.

### Negative
- S3 Vectors requires a two-step hybrid retrieval architecture (query S3 Vectors, then join/filter in Aurora).
- Vector store client must be implemented cleanly behind our abstract protocol.

---

## 5. Security Implications
- **Encryption at Rest**: S3 Vectors uses AWS KMS encryption.
- **Least-Privilege IAM**: Lambda execution roles have granular permissions restricted strictly to the designated vector bucket and indexes (`s3vectors:QueryIndex`, `s3vectors:PutVectors`, `s3vectors:DeleteVectors`).
- **Tenant Isolation**: Candidate vectors are isolated by metadata and partitioned namespace.

---

## 6. Cost Implications
- S3 Vectors charges based on vectors stored and query invocations, with no idle cluster charges.
- Compared to OpenSearch Serverless (minimum \$175+/mo) or always-on Aurora memory (extra ACUs), S3 Vectors operates well within our \$200 credit budget for early-stage candidate volumes.

---

## 7. Risks and Mitigations
- **Risk**: Eventual consistency or latency between S3 Vectors upsert and Aurora profile record commits.
  - *Mitigation*: Vector indexing is dispatched asynchronously via SQS. The relational database remains the immediate source of truth for profile data; vector status is tracked via an `is_indexed` flag.

---

## 8. References
- [Amazon S3 Developer Guide](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html)
- [Amazon Bedrock Titan Text Embeddings V2](https://docs.aws.amazon.com/bedrock/latest/userguide/titan-embedding-models.html)
- [docs/ARCHITECTURE.md](../ARCHITECTURE.md)
