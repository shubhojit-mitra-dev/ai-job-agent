# ADR-010: Hybrid Job Retrieval and Deterministic Recommendation Ranking

- **Status**: Accepted
- **Date**: 2026-11-20
- **Authors**: Technical Lead, Architecture Engineer

---

## 1. Context
Job discovery algorithms often suffer from two failure modes:
1. Pure keyword matching misses semantically equivalent skills (e.g. "FastAPI" vs "Python Web Frameworks").
2. Pure vector retrieval returns jobs that feel topical but violate hard dealbreakers (e.g. matching a senior 8-year role to a fresher, or recommending a 6-day in-office role when remote was required).
Furthermore, candidates distrust opaque recommendation scores.

## 2. Decision
Adopt a **Two-Stage Hybrid Retrieval & Deterministic Ranking Engine**:
1. **Stage 1: Hybrid Retrieval**:
   - `pgvector` calculates vector cosine similarity between candidate profile embeddings and job embeddings.
   - Relational SQL filters eliminate expired postings and apply strict non-negotiable candidate dealbreakers (e.g. location, maximum experience required, minimum salary).
2. **Stage 2: Deterministic Scoring Rubric (0–100%)**:
   - Primary Skills Overlap: 40%
   - Domain Relevance: 25%
   - Experience Alignment: 20%
   - Location / Work Mode Fit: 15%
3. **Transparent Explanations**:
   - For every recommended job, the system outputs explicit matched competencies, missing skills, and transparent reasoning for the computed score.

## 3. Alternatives Considered
- **Pure LLM-based Scoring**: Asking an LLM to evaluate every job. Rejected due to high latency, token cost, non-deterministic ratings, and risk of hallucinations.
- **Pure Vector Distance**: Using cosine distance directly as the score. Rejected because it cannot enforce binary dealbreakers and lacks explainability.

## 4. Consequences
- **Positive**: Sub-second search performance, transparent and verifiable scoring, hard dealbreakers are strictly honored.
- **Negative**: Requires careful indexing in PostgreSQL (`pgvector` HNSW/IVFFlat indexes alongside btree indexes on structured fields).

## 5. Risks
- Complex SQL queries degrading database performance. Mitigated by indexing and limiting initial candidate match pool to top 50 candidates before ranking.

## 6. References
- pgvector documentation: https://github.com/pgvector/pgvector
- [docs/PRODUCT_SPEC.md](file:///home/blackknight05/Desktop/ai-job-agent/docs/PRODUCT_SPEC.md)

