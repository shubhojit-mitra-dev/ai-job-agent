# Architecture Specification: AI Career Platform

> **Status**: Approved Foundation  
> **Audience**: Technical Lead, Software Engineers, AI Coding Agents  
> **Target Region**: AWS `ap-south-1` (Mumbai)  
> **Revision**: 1.1 (Phase 00)

---

## 1. Architectural Paradigm: Modular Monolith

The **AI Career Platform** is designed as a **Modular Monolith** running on a Serverless Cloud Infrastructure.

### Rationale
- Distributed microservices introduce operational friction, network latency, distributed transactions, and high idle infrastructure costs that are unjustified for this stage of the platform.
- A well-architected modular monolith enforces strict domain boundaries inside `apps/api/app/modules/` through well-defined internal interfaces and schemas.
- Monorepo structure allows frontend, backend, shared schemas, and infrastructure code to evolve in lockstep while remaining decoupled.

```mermaid
flowchart TD
    Client["Next.js Web Client (Vercel / CloudFront)"]
    Gateway["AWS API Gateway HTTP API (ap-south-1)"]
    Lambda["FastAPI Backend (AWS Lambda + Mangum)"]
    SQS["Amazon SQS (Task Queue + DLQ)"]
    WorkerLambda["Worker Lambda (Async Processing)"]
    EventBridge["Amazon EventBridge Scheduler (Asia/Kolkata)"]
    SupabaseDB[("Supabase PostgreSQL + pgvector")]
    Storage[("Object Storage: S3 vs Supabase Storage (ADR-012)")]
    LLMProviders["BYOK LLM Providers (NIM, CF AI, OpenRouter, Gemini)"]

    Client -->|HTTPS / JWT| Gateway
    Gateway -->|ASGI Payload| Lambda
    Lambda -->|SQL / pgvector| SupabaseDB
    Lambda -->|Pre-signed URLs| Storage
    Lambda -->|Dispatch Job| SQS
    Lambda -->|LLM Inference (BYOK)| LLMProviders
    EventBridge -->|Daily 06:00 IST Cron| SQS
    SQS -->|Batch Events| WorkerLambda
    WorkerLambda -->|Update Status / Data| SupabaseDB
    WorkerLambda -->|Send Email| Client
```

---

## 2. Component Boundaries & Responsibilities

### 2.1. Frontend (`apps/web`)
- **Technology**: Next.js 16 (App Router), TypeScript, Tailwind CSS.
- **Role**: Candidate-facing UI, authentication session handling (Supabase Auth Client), resume upload workflow, conversational career assistant chat interface, job comparison view, and preference settings.
- **Boundary**: Never interacts directly with raw database credentials or internal background workers. Interacts exclusively with the FastAPI backend via REST endpoints carrying Supabase JWT access tokens.

### 2.2. Backend (`apps/api`)
- **Technology**: Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2.0 (Async), LangGraph, Mangum.
- **Role**: REST API routing, JWT token verification, domain business logic, prompt assembly, deterministic scoring engine, vector similarity retrieval, and async job dispatch.
- **Module Structure**:
  ```text
  apps/api/app/
  ├── api/v1/         # Versioned HTTP routing controllers
  ├── core/           # Settings, logging, security, encryption, telemetry
  ├── db/             # SQLAlchemy engine, session generator, base models
  ├── modules/
  │   ├── auth/       # User identity verification and tenant isolation
  │   ├── candidate/  # Profile, resume parsing, candidate memory
  │   ├── jobs/       # Ingestion, normalization, search, filtering
  │   ├── matching/   # Compatibility scoring and comparison engine
  │   ├── agent/      # LangGraph workflows and BYOK LLM integration
  │   └── digest/     # Daily email digest formulation and dispatch
  ├── schemas/        # Cross-module Pydantic schemas
  └── main.py         # Application instantiation and ASGI lifespan
  ```

---

## 3. Database Architecture, Connection Pooling & Tenant Isolation

The primary data store is **Supabase PostgreSQL** augmented with the **`pgvector`** extension for vector similarity calculations.

```mermaid
sequenceDiagram
    autonumber
    participant Lambda as AWS Lambda Instance
    participant Pooler as Supabase Transaction Pooler (Port 6543)
    participant Postgres as PostgreSQL Database (Supabase)

    Note over Lambda,Postgres: Serverless Request Execution with NullPool
    Lambda->>Pooler: Connect via asyncpg (statement_cache_size=0)
    Pooler->>Postgres: Acquire transaction-level physical connection
    Lambda->>Postgres: Execute scoped query (WHERE user_id = :uid)
    Lambda->>Pooler: Close session / release connection
    Note over Lambda: Lambda goes idle or terminates
```

### 3.1. Connection Management for Serverless AWS Lambda
Serverless execution models (AWS Lambda) spin up and tear down instances concurrently in response to incoming traffic. Standard persistent connection pools (`QueuePool`) will exhaust database connection limits.

To ensure stability and cost control:
1. **Supabase Transaction Pooler**: The application connects to Supabase via the shared PgBouncer / Supavisor pooler on **Port 6543** in **Transaction Pooling Mode**.
2. **SQLAlchemy Engine Configuration**:
   - `poolclass=NullPool`: The backend does not maintain an in-memory client connection pool across invocations. Connections are opened on demand and closed immediately after the request finishes.
   - `connect_args={"statement_cache_size": 0}`: In transaction pooling mode, prepared statements are not supported across varying physical backend sessions. Setting `statement_cache_size=0` on `asyncpg` prevents fatal "prepared statement does not exist" errors.
3. **Database Migration Isolation**:
   - Alembic runs **strictly outside** runtime Lambda execution (invoked via local CLI or CI/CD deployment jobs).
   - Alembic connects to **Port 5432 (Session Mode / Direct)** with dedicated administrative credentials because DDL operations and migrations require session-level locks and prepared statements.

### 3.2. Authentication vs. Database Tenant Isolation
It is a critical architectural requirement that **Supabase Auth does NOT automatically secure direct SQLAlchemy database connections**:
1. **API Authentication Layer**: The client passes a Supabase JWT in the `Authorization: Bearer <token>` header. The FastAPI backend authenticates the caller by validating the JWT signature using Supabase's JWKS, checking claims (`iss`, `aud`, `exp`), and extracting the candidate user ID (`sub`).
2. **Database Connection Layer**: SQLAlchemy connects to PostgreSQL using fixed database credentials (connection string). PostgreSQL authenticates the backend process as a database role, not the individual candidate.
3. **Application-Level Isolation**: Every candidate-scoped SQL query must explicitly filter by the authenticated user ID (`WHERE user_id = current_user.id`).
4. **Defense in Depth**: Relying solely on application-level filtering is necessary but not sufficient for true defense in depth. We evaluate:
   - Setting session-level transaction parameters (e.g. `SET LOCAL app.current_user_id = :uid`) on each checkout so PostgreSQL Row-Level Security (RLS) policies can enforce tenant boundaries.
   - Using a dedicated application database role granted least-privilege table permissions (SELECT, INSERT, UPDATE, DELETE on application tables only) rather than the administrative `postgres` superuser role.

---

## 4. Agent Orchestration Architecture (LangGraph)

Agentic workflows (career intake, resume critique, search plan formulation) are implemented using **LangGraph** directed graphs.

```mermaid
stateDiagram-v2
    [*] --> IntakeMessage
    IntakeMessage --> ClassifyIntent: User Input
    ClassifyIntent --> CareerDiscoveryAgent: Goal / Preference Exploration
    ClassifyIntent --> JobSearchAgent: Job Inquiry / Search Request
    ClassifyIntent --> ResumeAdvisorAgent: Resume Tailoring Request
    
    CareerDiscoveryAgent --> UpdateCandidateMemory: Structured Preference Extracted
    UpdateCandidateMemory --> FormulateResponse
    
    JobSearchAgent --> RetrieveJobs: Semantic + Dealbreaker Filter
    RetrieveJobs --> RankMatches: Deterministic Rubric
    RankMatches --> FormulateResponse
    
    ResumeAdvisorAgent --> ExtractBulletPoints: Analyze Target Role
    ExtractBulletPoints --> CheckFabricationGuardrails: Verify Candidate Facts
    CheckFabricationGuardrails --> FormulateResponse
    
    FormulateResponse --> [*]
```

### 4.1. Core Agent Nodes
1. **Intake & Intent Classifier**: Categorizes the candidate's conversational turn (updating goals, searching jobs, asking for advice).
2. **Career Discovery Agent**: Conducts structured dialog to uncover candidate aspirations, desired CTC, preferred work modes, and explicit dealbreakers. Updates candidate memory tables.
3. **Job Search & Retrieval Node**: Constructs vector queries for `pgvector` alongside SQL filters for hard dealbreakers.
4. **Recommendation & Match Scorer**: Runs a deterministic rubric to generate transparent match scores and explanations.
5. **Resume Tailoring Advisor**: Reviews existing candidate resume bullets against target job requirements, suggesting rephrasings while strictly verifying against candidate-confirmed experience.

### 4.2. BYOK (Bring Your Own Key) Provider Abstraction
To support user privacy and zero-marginal-cost operation:
- The system abstracts LLM inference behind a unified provider protocol (`LLMClient`).
- Supported providers: NVIDIA NIM, Cloudflare Workers AI, OpenRouter, Google Gemini.
- Candidate keys are encrypted at rest using AES-256-GCM envelope encryption and decrypted only in ephemeral execution memory.

### 4.3. Prompt Injection Defense & Authorization Boundaries
- Resumes and job descriptions are untrusted inputs. Delimiters (such as `<candidate_resume>`) provide context separation for parsing prompts, but do **not** constitute a formal security boundary.
- **Principle of Non-Autonomous Authorization**: LLM outputs must never independently authorize privileged state mutations or data exports.
- All agent tool invocations must adhere to strict, allowlisted schemas, and the backend must validate structured outputs and enforce tenant authorization checks independently of the model.

---

## 5. Local Embeddings & Packaging Constraints

The target architecture prefers local/open-source Sentence Transformers embeddings (e.g., `all-MiniLM-L6-v2` or `bge-small-en-v1.5`).

### AWS Lambda ZIP Package Constraints
- AWS Lambda uncompressed ZIP deployment package size limit is **250 MB**.
- PyTorch and transformers runtimes frequently exceed 300–500 MB.
- **Architectural Investigation (ADR-011)**:
  - *Option A*: Package a lightweight ONNX Runtime with quantized model weights (< 120 MB) inside the ZIP deployment.
  - *Option B*: Offload embedding generation to a dedicated worker or serverless inference endpoint (e.g., Cloudflare Workers AI / Fastembed in SQS worker).
  - *Resolution*: Investigated in [ADR-011](./adr/ADR-011-local-embedding-strategy-and-deployment-constraints.md). The primary API Lambda must **not** be bloated with standard PyTorch wheels.

---

## 6. Background Task & Scheduled Workloads

Heavy or periodic tasks must never block synchronous user HTTP requests.

```mermaid
flowchart LR
    Event["EventBridge Scheduler (Daily 06:00 IST)"] -->|Send Batch Message| SQS["AWS SQS Queue"]
    HTTP["FastAPI Upload Endpoint"] -->|Enqueue Parse Task| SQS
    SQS -->|Trigger (Batch Size: 1-10)| Worker["Worker Lambda"]
    Worker -->|Failed after retries| DLQ["Dead-Letter Queue (DLQ)"]
    Worker -->|Success| DB[("Supabase PostgreSQL")]
```

1. **Amazon SQS & Visibility Timeout Best Practice**:
   - Manages asynchronous queues for: resume parsing, embedding generation, and daily digest dispatch.
   - Configured with a Dead-Letter Queue (DLQ) with `maxReceiveCount=3` for fault tolerance.
   - **Visibility Timeout Relationship**: In accordance with official AWS documentation, the SQS queue visibility timeout must be configured to **at least 6 times the Lambda function timeout**, also taking into account the configured batch window (`MaximumBatchingWindowInSeconds`) and retry behavior. This prevents duplicate processing of in-flight messages while workers execute.
2. **Worker Lambda**:
   - Listens to SQS events, processes tasks idempotently, and records state back to PostgreSQL.
3. **EventBridge Scheduler**:
   - Manages recurring schedules configured with the explicit timezone **`Asia/Kolkata`**.
   - Example: Daily candidate email digest triggers at **06:00 AM IST** (`cron(0 6 * * ? *)` with `schedule_expression_timezone = "Asia/Kolkata"`).

---

## 7. AWS Serverless Deployment Architecture

- **AWS Region**: `ap-south-1` (Mumbai) to ensure low latency for Indian candidates.
- **API Gateway HTTP API**: Cost-effective managed gateway providing TLS termination, CORS configuration, and routing to Lambda.
- **Mangum Adapter**: Wraps the FastAPI ASGI application inside the standard AWS Lambda handler interface (`handler = Mangum(app)`).
- **Terraform**: Manages AWS API Gateway, Lambda functions, IAM roles, SQS queues, and EventBridge schedules using S3 remote state with S3-native state locking.
- **GitHub Actions (OIDC)**: Deploys infrastructure and code changes securely without permanent AWS access keys.
