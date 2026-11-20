# ADR-001: Modular Monolith Architecture

- **Status**: Accepted
- **Date**: 2026-11-20
- **Authors**: Technical Lead, Architecture Engineer

---

## 1. Context
The platform requires a scalable, clean backend architecture to manage candidate profiles, career conversations, job discovery, ranking, and asynchronous digests. A key engineering question is whether to adopt a microservices topology or a monolithic codebase. Microservices introduce complex distributed transactions, deployment overhead, service meshes, and higher baseline cloud infrastructure costs.

## 2. Decision
We adopt a **Modular Monolith** architecture within a single monorepo (`apps/api`). Domain capabilities (Auth, Candidate, Jobs, Matching, Agent, Digest) are separated into strict internal packages under `apps/api/app/modules/`. Each module exposes well-typed public service interfaces and Pydantic schemas, forbidding cyclic cross-module imports.

## 3. Alternatives Considered
- **Microservices**: Independent services for Auth, Ingestion, Matching, and LLM Agents. Rejected due to operational complexity, network latency, and unnecessary cloud hosting overhead.
- **Unstructured Monolith**: Standard Django/Flask flat app without strict domain boundaries. Rejected due to risk of tight coupling and spaghetti code.

## 4. Consequences
- **Positive**: Single codebase, straightforward local debugging, unified database transactions, single deployment pipeline, zero network overhead between internal modules.
- **Negative**: Requires strict discipline to prevent domain boundary erosion; long-term growth may eventually require module extraction if scaling bottlenecks emerge.

## 5. Risks
- Modules could bypass public interfaces and query other domains' database tables directly. Enforced via static analysis and code review guidelines in `AGENTS.md`.

## 6. References
- Modular Monolith architectural patterns.
- [docs/ARCHITECTURE.md](file:///home/blackknight05/Desktop/ai-job-agent/docs/ARCHITECTURE.md)
