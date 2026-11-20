NOTE: this file is only for Humans, if you are an AI agent then you are strictly forbidden from reading this.

# TASK: Establish the Project's Engineering Governance, Architecture Documentation and AI-Agent Development System

You are acting as the **Senior Documentation and Architecture Engineer** for an AI-powered career discovery platform.

Your task is to establish a professional, self-documenting, AI-agent-friendly development environment inside the existing GitHub repository.

You are working under a human technical lead. The human is the final decision-maker for architectural changes, scope changes and implementation approvals.

You are expected to work like a disciplined junior engineer: inspect first, understand the existing project, document decisions accurately, avoid unnecessary complexity, and never implement anything outside the authorised scope.

---

# 1. FIRST: UNDERSTAND THE EXISTING REPOSITORY

Repository:

https://github.com/shubhojit-mitra-dev/ai-job-agent

Default branch: `master`

Before doing anything:

1. Read the complete repository structure.
2. Inspect existing source files, configuration files, lockfiles and frontend files.
3. Inspect the current Git status and recent commit history.
4. Read any existing AGENTS.md instructions, including the Next.js-specific instructions.
5. Identify what is already implemented and what is only scaffolded.
6. Do not assume that a directory or dependency exists merely because it was mentioned in an earlier conversation.
7. Do not overwrite existing working files unnecessarily.

Current known repository structure:

- `apps/api`: FastAPI backend, Python 3.12, managed with uv.
- `apps/web`: Next.js, TypeScript, Tailwind CSS.
- Root `.env.example`, `.gitignore` and README.
- Python dependencies and `uv.lock` already exist.
- Next.js generated instructions exist at `apps/web/AGENTS.md`.

The repository is the single source of truth.

If the actual repository differs from this description, trust the repository and report the discrepancy.

---

# 2. PRODUCT CONTEXT — UNDERSTAND WHAT WE ARE BUILDING

We are building an India-first, open-source, AI-powered career discovery platform.

The platform is designed primarily for Indian students, fresh graduates and professionals looking for suitable job opportunities.

The product should allow users to:

1. Register and authenticate.
2. Upload their resume.
3. Extract structured candidate information from their resume.
4. Have an AI-assisted conversation to understand their career goals.
5. Maintain persistent, editable candidate preferences and memory.
6. Discover jobs from multiple permitted job sources.
7. Search jobs using keyword and semantic retrieval.
8. Filter opportunities using explicit dealbreakers.
9. Rank jobs based on candidate-job compatibility.
10. Display transparent match scores and explanations.
11. Compare job opportunities.
12. Save jobs and track application status.
13. Tailor resumes for selected opportunities without fabricating experience.
14. Receive personalised daily email digests containing direct application links.
15. Interact with a conversational career assistant that can use controlled tools.

The product should implement a substantial candidate-facing career-agent experience inspired by publicly documented capabilities of Elip AI.

We are NOT attempting to reproduce proprietary internal implementations or copy their private data, models or source code.

Our objective is to independently engineer a useful open-source alternative using our own architecture.

## Core product principles

- Free to use, with no mandatory subscription.
- Bring Your Own Key (BYOK) for LLM inference.
- Local/open-source embeddings wherever technically practical.
- Transparent recommendations.
- User control over preferences and stored information.
- No fabricated job listings or application URLs.
- No fabricated resume qualifications.
- No automatic application submission in the initial release.
- Real users and measurable product quality matter more than feature count.

Do not expand into recruiter-side functionality in the initial product scope.

The project name is intentionally undecided. Use a neutral internal description such as "AI Career Platform" throughout documentation.

---

# 3. APPROVED TECHNOLOGY AND ARCHITECTURE DECISIONS

These decisions have been made by the human technical lead.

Do not silently replace them.

## Application

Frontend:
- Next.js
- TypeScript
- Tailwind CSS

Backend:
- Python 3.12
- FastAPI
- Pydantic
- uv for dependency management

Database:
- Supabase PostgreSQL
- pgvector
- SQLAlchemy 2.0
- Alembic

Authentication:
- Supabase Auth
- Backend-side access-token verification
- Proper user ownership and tenant isolation

AI:
- LangGraph for graph-based agent orchestration
- Specialised agent nodes with explicit responsibilities
- BYOK provider abstraction
- NVIDIA NIM, Cloudflare Workers AI, OpenRouter, Gemini and other eligible providers may be evaluated.
- Sentence Transformers/local embeddings are the preferred initial direction, subject to deployment feasibility.

Architecture:
- Modular monolith.
- Monorepo.
- No unnecessary microservices.
- No unnecessary message brokers or distributed infrastructure.

Local development:
- Docker Compose.
- PostgreSQL/pgvector where required for local integration tests.
- Local execution should remain possible without AWS.

## AWS infrastructure

The approved deployment direction is:

- AWS Lambda for the FastAPI backend.
- AWS API Gateway HTTP API.
- Mangum as the ASGI-to-Lambda adapter.
- Python 3.12 Lambda runtime initially.
- ZIP deployment packages.
- Terraform for infrastructure as code.
- AWS region: `ap-south-1` (Mumbai).
- The human has AWS credits available, but ongoing costs must still be minimised.

Background processing:
- Amazon SQS.
- Lambda worker.
- Dead-letter queue.
- Idempotent task execution.
- EventBridge Scheduler for recurring jobs and scheduled ingestion.

Do not introduce:
- EC2 servers.
- NAT Gateways without a demonstrated requirement.
- RDS.
- ElastiCache.
- Provisioned Lambda concurrency.
- Kubernetes.
- Always-running worker servers.

The architecture must be cost-conscious, not artificially complex.

## CI/CD

- GitHub Actions.
- Automated testing and quality checks on pull requests.
- Terraform validation and formatting checks.
- AWS authentication through GitHub Actions OIDC.
- No permanent AWS access keys stored in GitHub secrets.
- Deployment from the approved main branch.
- Deployment smoke tests.
- Documented rollback procedures.

## Database connection considerations

Supabase PostgreSQL remains the database.

The architecture documentation must explicitly discuss:

- Supabase shared pooler.
- Transaction pooling for serverless workloads.
- SQLAlchemy async connection handling.
- asyncpg prepared-statement caching limitations in transaction mode.
- `statement_cache_size=0` where appropriate.
- `NullPool` versus bounded connection pooling.
- Lambda concurrency and Supabase connection limits.
- Separate migration and application database credentials.
- Safe Alembic execution outside Lambda cold starts.

Do not implement any database connection code in this task.

## Important deployment consideration

Local Sentence Transformers models must not automatically be bundled into the API Lambda.

Document the trade-offs around:
- ZIP package size.
- Cold starts.
- Memory requirements.
- Model download and caching.
- Background inference workloads.

This is an architectural investigation, not an instruction to build a separate embedding service now.

---

# 4. DOCUMENTATION AND AGENTIC DEVELOPMENT GOVERNANCE

Create a professional documentation structure.

The documentation must be useful to future coding agents that may have no knowledge of previous conversations.

Every important engineering decision must be discoverable from the repository.

## Required root files

### AGENTS.md

This is the authoritative instruction file for all coding agents.

It must contain:

- Project identity and purpose.
- Mandatory documentation-reading order.
- Repository structure.
- Approved architectural decisions.
- Coding standards.
- Testing standards.
- Security requirements.
- Git workflow.
- Branch naming conventions.
- Commit conventions.
- Pull request requirements.
- Documentation maintenance requirements.
- Architectural change approval requirements.
- Definition of Done.
- Rules for using skills.
- Instructions for investigating errors.
- Instructions for maintaining progress documentation.

Keep it practical and enforceable. Avoid generic motivational instructions.

### CLAUDE.md

This file must be a short redirect to the root `AGENTS.md`.

It must explicitly instruct Claude agents to read and follow `AGENTS.md` before doing any work.

Do not duplicate the entire instruction set.

### README.md

Create a professional project README explaining:

- What the product is.
- Why it exists.
- Main features.
- Technology stack.
- High-level architecture.
- Repository structure.
- Local development prerequisites.
- Setup instructions based on the actual repository.
- Links to detailed documentation.
- Current project status.

Do not claim features are implemented when they are only planned.

## Required docs directory

Create:

```text
docs/
├── PRODUCT_SPEC.md
├── ARCHITECTURE.md
├── DEVELOPMENT_GUIDE.md
├── TESTING_STRATEGY.md
├── SECURITY.md
├── DEPLOYMENT.md
├── COST_AND_OPERATIONS.md
│
├── phases/
│
├── subphases/
│
├── adr/
│
├── progress/
│   └── PROGRESS.md
│
└── walkthroughs/
```

Each document must have a clear purpose.

Avoid duplicating the same information across multiple files. Use links to authoritative documents instead.

### PRODUCT_SPEC.md

Document:

- Product vision.
- Target audience.
- Problems being solved.
- Product principles.
- Functional requirements.
- Non-functional requirements.
- Core user journeys.
- MVP scope.
- Explicitly excluded functionality.
- Future possibilities.

Separate MVP requirements from future features.

### ARCHITECTURE.md

Document:

- Modular monolith architecture.
- Application boundaries.
- Frontend/backend responsibilities.
- Authentication flow.
- Database interaction.
- Agent orchestration architecture.
- Job ingestion architecture.
- Retrieval and ranking architecture.
- Background processing architecture.
- Scheduled email architecture.
- AWS deployment architecture.
- High-level data flows.

Use Mermaid diagrams where they genuinely improve understanding.

Do not create overly complicated diagrams.

Include important architectural trade-offs.

### DEVELOPMENT_GUIDE.md

Explain:

- Repository structure.
- Local development workflow.
- Python dependency management with uv.
- Frontend dependency management.
- Environment configuration.
- Formatting and linting.
- Branch strategy.
- Commit conventions.
- PR workflow.
- Documentation update requirements.

Only document commands verified against the existing project or clearly mark future commands as planned.

### TESTING_STRATEGY.md

Define:

- Unit testing.
- Integration testing.
- API testing.
- Database testing.
- Agent workflow testing.
- Retrieval and ranking evaluation.
- Frontend testing.
- Infrastructure validation.
- End-to-end testing.

Define what should be mocked and what requires actual integration tests.

Explain how to test LLM workflows without making every test depend on a live paid API.

Use deterministic fixtures, fake providers and controlled test datasets.

### SECURITY.md

Cover:

- Authentication and authorisation.
- User data isolation.
- Resume security.
- API-key encryption.
- Secrets management.
- Prompt injection.
- Untrusted resume and job-description content.
- SSRF prevention.
- File upload validation.
- Rate limiting.
- Logging and sensitive data redaction.
- Dependency security.
- AWS IAM least privilege.
- Account and data deletion.

Pay particular attention to the fact that uploaded resumes contain sensitive personal information.

Do not assume that using Supabase Auth automatically secures direct SQLAlchemy database access.

Document how backend user ownership and database access controls must work together.

### DEPLOYMENT.md

Document the intended deployment model:

- AWS Lambda.
- API Gateway HTTP API.
- Mangum.
- ZIP packaging.
- SQS worker.
- EventBridge Scheduler.
- CloudWatch.
- Terraform.
- AWS OIDC.
- GitHub Actions.

Explain local versus cloud deployment.

Explain Terraform remote state and bootstrap requirements.

Use official documentation and clearly distinguish decisions from unresolved investigations.

### COST_AND_OPERATIONS.md

Document:

- AWS credit usage.
- AWS free allowances where applicable.
- Expected cost-generating services.
- Cost risks.
- Budget alerts.
- Lambda concurrency limits.
- CloudWatch retention.
- Supabase free-tier limitations.
- LLM provider quotas.
- Email provider limits.
- Free-tier dependency risks.

Never promise that the platform is guaranteed to cost ₹0.

---

# 5. ARCHITECTURAL DECISION RECORDS

Create an ADR directory.

Use a consistent ADR template:

- Number.
- Title.
- Status.
- Date.
- Context.
- Decision.
- Alternatives considered.
- Consequences.
- Risks.
- References.

Initially document these decisions:

ADR-001: Modular Monolith Architecture.

ADR-002: FastAPI Deployment on AWS Lambda Using Mangum and ZIP Packaging.

ADR-003: Supabase Auth and PostgreSQL.

ADR-004: SQLAlchemy 2.0 and Alembic.

ADR-005: SQS-Based Background Processing.

ADR-006: EventBridge Scheduler for Scheduled Workloads.

ADR-007: Terraform for Infrastructure as Code.

ADR-008: GitHub Actions with AWS OIDC.

ADR-009: BYOK Provider Abstraction for LLM Inference.

ADR-010: Hybrid Job Retrieval and Deterministic Recommendation Ranking.

ADR-011: Local Embedding Strategy and Its Deployment Constraints.

ADR-012: Resume File Storage and Secure Access.

Important:

Do not blindly mark every decision as Accepted.

Use:
- Accepted: Approved decision.
- Proposed: Requires further validation or human approval.
- Superseded: Replaced by a later decision.

If an architectural decision requires research, investigate it using official documentation before writing it.

Do not invent AWS capabilities, pricing or service limits.

---

# 6. PHASE AND SUBPHASE MANAGEMENT

Every development phase must contain between 3 and 10 subphases, depending on complexity.

Each phase must have a phase document explaining:

- Objective.
- Scope.
- Deliverables.
- Dependencies.
- Subphases.
- Acceptance criteria.
- Expected application behaviour after completion.
- Risks.

Each subphase must have its own separate Git branch.

Branch naming convention:

```text
phase-XX/subphase-YY-short-description
```

Example:

```text
phase-00/subphase-01-agentic-governance
```

Important documentation rule:

Create the complete phase-level plan, but create detailed documentation for only the current subphase.

Do not generate every future subphase document in advance.

Create each future subphase document only when we are ready to begin that subphase.

This prevents stale documentation.

## Initial phase

Create:

`docs/phases/PHASE_00_PROJECT_FOUNDATION.md`

It should describe the overall foundation phase and break it into logical subphases.

The current task is the first subphase:

`docs/subphases/PHASE_00_SUBPHASE_01_AGENTIC_GOVERNANCE.md`

This current subphase is limited to establishing the documentation and agentic development governance system.

Do not create detailed documents for future subphases yet.

---

# 7. TDD AND QUALITY REQUIREMENTS

We follow Test-Driven Development for application implementation.

For each implementation subphase:

1. Understand the acceptance criteria.
2. Design the expected behaviour.
3. Create tests first.
4. Review the test cases.
5. Implement the smallest solution.
6. Run tests.
7. Investigate failures.
8. Fix the actual root cause.
9. Refactor without changing required behaviour.
10. Run the full relevant test suite.

Never weaken or delete a legitimate failing test merely to make the pipeline pass.

If a test appears incorrect, explain why and obtain approval before changing it.

For documentation-only subphases, use documentation-specific validation instead of inventing application tests.

---

# 8. GIT AND PULL REQUEST WORKFLOW

The default branch is `master`.

Never implement directly on `master`.

For each subphase:

1. Create its dedicated branch from the latest `master`.
2. Read its phase and subphase documentation.
3. Complete only the authorised scope.
4. Keep commits atomic and logically coherent.
5. Use conventional commit messages.
6. Run required checks.
7. Update progress documentation.
8. Create a walkthrough document after completing the subphase.
9. Open a GitHub Pull Request.
10. Wait for human review and approval.
11. Merge only after approval.
12. Start the next subphase from the updated `master`.

Atomic commits should represent one coherent logical change.

Related files may belong in the same commit when they implement one coherent change. Do not create meaningless one-file commits simply to satisfy a numerical restriction.

Never:
- Force-push without explicit approval.
- Push directly to master.
- Merge your own PR without human approval.
- Silently discard user changes.
- Modify unrelated files.

If GitHub access or PR creation is unavailable, prepare the branch and report the exact remaining manual action.

---

# 9. WALKTHROUGH DOCUMENTATION

At the end of every completed subphase, create a walkthrough document.

Naming convention:

`docs/walkthroughs/WALKTHROUGH_PHASE_XX_SUBPHASE_YY.md`

The walkthrough should explain:

1. What was accomplished.
2. What changed.
3. Why each important change was necessary.
4. Files created, modified and deleted.
5. Important implementation decisions.
6. Relevant code excerpts for complex or non-obvious logic.
7. How the files relate to one another.
8. The recommended reading order for understanding the implementation.
9. Tests performed and results.
10. PR link and commit references.

Do not explain trivial syntax or every line of ordinary code.

Focus on architectural reasoning, abstractions, advanced Python concepts and important engineering patterns.

Keep the walkthrough detailed enough that the human technical lead can understand the implementation without needing to reverse-engineer the entire codebase.

---

# 10. PROGRESS TRACKING

Maintain:

`docs/progress/PROGRESS.md`

It is the running record of the project's development.

Include:

- Current phase.
- Current subphase.
- Overall milestone status.
- Completed subphases.
- Pending subphases.
- Merged PRs.
- Active branches.
- Known issues.
- Architectural decisions pending approval.
- Next authorised task.

Update it at the end of every subphase.

Never mark an incomplete task as completed.

The repository state and merged PRs take precedence over the progress document if there is a discrepancy.

---

# 11. ERROR INVESTIGATION RULES

When encountering an error:

1. Read the complete error output.
2. Identify the file and line.
3. Identify the responsible function/module.
4. Understand the underlying cause.
5. Reproduce the error where possible.
6. Identify the smallest correct fix.
7. Add a regression test where appropriate.
8. Re-run the relevant tests.

Do not blindly retry commands.

Do not introduce workarounds without understanding the failure.

Report unresolved errors transparently.

---

# 12. SKILL DISCOVERY AND USAGE

We want to use agent skills where they improve implementation quality.

Skills must be installed globally, not inside the repository.

First execute the following command exactly as requested:

```bash
npx skills use "https://github.com/vercel-labs/skills" --skill "find-skills"
```

Capture the complete output in a temporary file first if necessary.

Read the complete generated instructions.

Resolve relative paths from the supporting-files directory provided by the command.

Use the skill-discovery instructions to identify relevant skills.

Consider skills for:
- FastAPI and Python backend engineering.
- Next.js.
- AWS Lambda.
- Terraform.
- GitHub Actions.
- PostgreSQL.
- LangGraph and agent development.
- Security.
- Testing.

Do not install every available skill.

Install only skills that have a clear practical use.

Use:

```bash
npx skills add <owner/repo>
```

only when an appropriate skill is not already installed.

Verify the installed skill and read its instructions before using it.

Do not commit globally installed skills into the project repository.

---

# 13. OFFICIAL DOCUMENTATION AND RESEARCH

When documenting external technologies, prioritise official documentation.

Important references:

AWS Lambda Python:
https://docs.aws.amazon.com/lambda/latest/dg/lambda-python.html

AWS Lambda ZIP packages:
https://docs.aws.amazon.com/lambda/latest/dg/python-package.html

AWS Lambda and SQS:
https://docs.aws.amazon.com/lambda/latest/dg/with-sqs.html

SQS event source configuration:
https://docs.aws.amazon.com/lambda/latest/dg/services-sqs-configure.html

EventBridge Scheduler:
https://docs.aws.amazon.com/scheduler/latest/UserGuide/what-is-scheduler.html

Terraform S3 backend:
https://developer.hashicorp.com/terraform/language/backend/s3

GitHub Actions OIDC with AWS:
https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-aws

Supabase PostgreSQL connections:
https://supabase.com/docs/guides/database/connecting-to-postgres

Supabase connection pooling:
https://supabase.com/docs/guides/database/connecting-to-postgres/pooling-and-limits

Supabase with SQLAlchemy:
https://supabase.com/kb/troubleshooting/using-sqlalchemy-with-supabase-FUqebT

Mangum:
https://mangum.fastapiexpert.com/

Check current documentation rather than relying exclusively on model knowledge.

Document source links for important technical decisions.

If a feature, quota, pricing detail or service capability cannot be verified, explicitly mark it as unverified.

---

# 14. STRICT SCOPE OF THE CURRENT TASK

This task is ONLY for project documentation and agentic development governance.

You are authorised to:

- Inspect the repository.
- Research official technical documentation.
- Discover and install relevant global skills.
- Create root agent instruction files.
- Create the initial documentation structure.
- Write the product specification.
- Write the architecture documentation.
- Write initial ADRs.
- Create the Phase 00 plan.
- Create the first subphase document.
- Create the initial progress tracker.
- Create a professional README.
- Create a walkthrough after the documentation subphase is complete.
- Create a documentation-only branch and PR.

You are NOT authorised to:

- Implement PostgreSQL connectivity.
- Create SQLAlchemy database engines.
- Configure Alembic.
- Create database models.
- Create or modify Supabase database schemas.
- Change Supabase authentication settings.
- Use Supabase MCP to mutate infrastructure or database resources.
- Create AWS resources.
- Run Terraform apply.
- Create actual Terraform infrastructure code.
- Configure AWS credentials.
- Create Lambda handlers.
- Add Mangum.
- Create SQS workers.
- Create GitHub Actions deployment workflows.
- Modify application business logic.
- Add application dependencies.
- Build agents.
- Implement API endpoints beyond the existing scaffold.

Do not modify existing application code or lockfiles during this documentation task.

Do not create secrets or request that the human paste credentials into the repository.

If you identify a necessary architectural correction, document it as a proposed decision instead of implementing it.

---

# 15. DEFINITION OF DONE FOR THIS TASK

The task is complete only when:

1. The repository has a comprehensive root AGENTS.md.
2. CLAUDE.md correctly redirects to AGENTS.md.
3. README.md accurately describes the product and current state.
4. The required core documentation exists.
5. Architecture decisions are documented.
6. Initial ADRs exist with correct statuses.
7. Phase 00 has a clear plan containing 3–10 subphases.
8. Only the first subphase has detailed subphase documentation.
9. The progress tracker is initialised.
10. Documentation links and Mermaid diagrams have been validated.
11. The documentation is internally consistent.
12. Existing application code remains unchanged.
13. No database or AWS implementation has been started.
14. A walkthrough document has been created.
15. The documentation branch has been pushed and a PR opened, or any GitHub limitation has been reported.

---

# 16. EXECUTION APPROACH

Do not generate everything blindly in one pass.

Work in this order:

**Stage A — Repository audit**
- Inspect all existing files.
- Identify current state.
- Read existing agent instructions.
- Discover relevant skills.
- Research official documentation.

**Stage B — Documentation design**
- Establish the directory structure.
- Define the product specification.
- Define the architecture.
- Identify ADRs and their statuses.
- Define the phase plan.
- Define agent instructions.

**Stage C — Documentation implementation**
- Create the authorised documentation files.
- Keep documents consistent.
- Preserve existing application files.
- Avoid duplicate content.

**Stage D — Validation**
- Verify internal links.
- Validate Mermaid diagrams.
- Check consistency between ADRs and architecture.
- Check that all decisions are correctly labelled.
- Check that no implementation work has accidentally been introduced.

**Stage E — Git workflow**
- Update progress.
- Create walkthrough.
- Commit logically.
- Push the branch.
- Open the PR.
- Provide the human with a concise completion report.

Before starting, provide a brief audit summary and the intended documentation plan.

Then execute the authorised documentation task.

If a genuinely important architectural decision is missing or contradictory, stop and ask the human rather than inventing an answer.

Remember:

**We are building a serious software product, not a demo generated by an AI.**

Prefer simple, maintainable engineering over unnecessary abstractions.

The goal is to let future AI coding agents understand the project, work independently within clearly defined boundaries, and deliver small, tested, reviewable changes without repeatedly requiring the human to explain the entire system.

