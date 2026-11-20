# Product Specification: AI Career Platform

> **Status**: Approved Foundation  
> **Audience**: Engineering, Product Architecture, AI Coding Agents  
> **Revision**: 1.0 (Phase 00)

---

## 1. Product Vision & Executive Summary

The **AI Career Platform** is an India-first, open-source, candidate-centric career discovery platform designed specifically for Indian college students, fresh engineering/science/commerce graduates, and early-to-mid-career professionals.

In the Indian employment ecosystem, candidates face systemic frictions:
- Job boards flooded with duplicate, expired, or non-actionable listings.
- Unclear job prerequisites where "freshers" are asked for 2–3 years of niche experience.
- Opaque algorithmic screening with zero feedback on why candidates are rejected or matched.
- Inefficient search engines relying solely on strict keyword matching that misses adjacent competencies.

The AI Career Platform flips this paradigm by acting as a personal, autonomous career advocate. Inspired by modern agentic workflows (such as public capabilities demonstrated by Elip AI), the platform prioritizes transparency, candidate empowerment, persistent preferences, and verified application routes.

---

## 2. Core Product Principles

1. **Free & Open-Source**: Core functionality is freely accessible without paywalls, subscription tiers, or artificial limitations.
2. **Bring Your Own Key (BYOK)**: To maintain sustainable cloud operations and preserve user privacy, advanced LLM reasoning uses user-supplied API keys (NVIDIA NIM, Cloudflare Workers AI, OpenRouter, Google Gemini, etc.).
3. **Local & Open Embeddings**: Semantic retrieval and vector indexing leverage lightweight, open-source embedding models (e.g., Sentence Transformers) where practical.
4. **Transparent, Explainable Matching**: No black-box scores. Every compatibility rating is accompanied by a breakdown of matched skills, missing competencies, domain alignment, and explicit dealbreaker violations.
5. **No Hallucinated Information**: The platform never fabricates job postings, company details, direct application URLs, or candidate experience on tailored resumes.
6. **No Automated Application Spam**: In the initial release, the platform will **not** submit applications automatically on behalf of users. Candidates retain full agency and must apply via direct, verified employer links.
7. **Candidate-Side Only**: The initial scope strictly serves job seekers. Recruiter-side features (applicant tracking systems, employer candidate search) are explicitly out of scope.

---

## 3. Target User Personas

### Persona A: The Final-Year Student ("Arjun", 21)
- **Background**: Tier-2/Tier-3 engineering college in Pune, studying Computer Science.
- **Pain Points**: Limited on-campus placement opportunities; overwhelmed by conflicting off-campus job posts; unsure how coursework maps to industry roles.
- **Needs**: Semantic discovery that recognizes project experience, identifies skill gaps, and recommends high-probability entry-level roles.

### Persona B: The Early-Career Switcher ("Priya", 24)
- **Background**: QA Engineer in Bengaluru seeking to transition to Backend Engineering (Python/Go).
- **Pain Points**: Rejection from automated ATS filters because current title is "QA"; job descriptions demand 3+ years experience with technologies she learned through self-study and internal contributions.
- **Needs**: Tailored resume guidance that reframes transferable engineering accomplishments; dealbreaker filtering for remote/hybrid Bengaluru opportunities.

### Persona C: The Specialized Non-Tech / Tech-Adjacent Professional ("Rohan", 27)
- **Background**: Product Operations / Analytics specialist in Gurugram.
- **Pain Points**: Flooded with generic data entry or sales jobs; wants curated alerts for genuine product operations and business analytics roles.
- **Needs**: Daily digest of filtered, high-relevance jobs; persistent candidate memory that remembers preferred CTC thresholds and location constraints.

---

## 4. User Journey & Functional Requirements

```mermaid
flowchart LR
    A["1. Register & Supabase Auth"] --> B["2. Upload Resume (PDF)"]
    B --> C["3. Extract Structured Profile"]
    C --> D["4. Interactive Career Chat"]
    D --> E["5. Persistent Memory & Dealbreakers"]
    E --> F["6. Semantic Job Ingestion & Retrieval"]
    F --> G["7. Explainable Scoring & Comparison"]
    G --> H["8. Tailor Resume & Daily Email Digest"]
```

### 4.1. Authentication & Candidate Profile
- **FR-01**: Candidate can securely authenticate using Supabase Auth (Email/Password or OAuth).
- **FR-02**: Candidate can upload their resume in PDF or DOCX format (up to 5MB).
- **FR-03**: Async parser extracts structured candidate data: contact details, education, technical skills, domain expertise, project highlights, and work history.
- **FR-04**: Candidate can view, edit, augment, or overwrite extracted information at any time.

### 4.2. Interactive Career Goal Discovery & Agent Memory
- **FR-05**: Interactive conversational interface to understand career aspirations, preferred tech stacks, work culture preferences, and long-term goals.
- **FR-06**: System extracts and maintains persistent, structured candidate preferences:
  - Desired job titles & seniority levels.
  - Target locations (e.g., Bengaluru, Hyderabad, Pune, NCR, Remote).
  - Minimum Compensation / CTC floor (in INR LPA).
  - Explicit Dealbreakers (e.g., "No unpaid internships", "No 6-day workweeks", "No bonded contracts").
- **FR-07**: Preferences remain completely editable and can be updated by the candidate whenever desired.

### 4.3. Job Ingestion, Semantic Retrieval & Filtering
- **FR-08**: Job ingestion pipeline indexes opportunities from permitted, legitimate job boards and company career portals.
- **FR-09**: Opportunities are parsed into structured entities: Title, Company, Location, Work Mode (Remote/Hybrid/Onsite), Experience Range, Salary/Stipend, Required Skills, and Direct Application Link.
- **FR-10**: Hybrid Retrieval Engine:
  - Vector similarity search via `pgvector` for semantic match.
  - Exact relational filtering for hard constraints (locations, experience band, salary threshold).
  - Negative filtering against candidate dealbreakers.

### 4.4. Explainable Matching & Opportunity Comparison
- **FR-11**: Compatibility Scoring (0–100%) computed via a deterministic evaluation rubric:
  - Primary skills overlap (40%).
  - Domain / context relevance (25%).
  - Experience / seniority alignment (20%).
  - Location and work mode fit (15%).
  - Hard dealbreakers act as strict binary disqualifiers.
- **FR-12**: Every matched job displays a human-readable explanation:
  - Why this is a fit.
  - Identified skill gaps or missing technologies.
  - Actionable advice for bridging gaps.
- **FR-13**: Job Comparison view allowing candidates to compare up to 3 roles side-by-side on match score, tech stack, location, and requirements.

### 4.5. Ethical Resume Tailoring
- **FR-14**: For a specific target job, generate suggested resume bullet improvements that emphasize relevant existing candidate experience.
- **FR-15**: Strict Ethical Guardrail: The agent must **never** invent fictitious companies, degrees, dates, or non-existent technical accomplishments.

### 4.6. Daily Digest & Notifications
- **FR-16**: Automated morning email digest featuring top-5 personalized opportunities with direct application links.
- **FR-17**: Candidates can pause, adjust frequency, or unsubscribe from digests.

---

## 5. Non-Functional Requirements (NFR)

- **Performance**: API responses for conversational queries under 2.5 seconds (p95); search retrieval under 300ms (p95).
- **Cost Minimization**: Backend runs serverless on AWS Lambda (`ap-south-1`) to minimize idle costs; no always-running virtual machines or managed cache clusters.
- **Availability**: 99.9% uptime for core API and web interface.
- **Security & Privacy**: Zero plaintext storage of BYOK LLM credentials; strict user data isolation; encrypted PDF storage with pre-signed access.
- **Accessibility**: Frontend conforms to WCAG 2.1 AA standards; responsive across mobile and desktop devices.

---

## 6. MVP Scope vs. Excluded Scope

### In Scope (MVP)
1. Supabase Auth with secure backend token validation.
2. PDF resume upload and structured profile extraction.
3. Conversational career goal intake with persistent candidate memory and dealbreakers.
4. Hybrid search (keyword + `pgvector`) over curated job listings.
5. Deterministic, explainable compatibility scoring.
6. Side-by-side job comparison.
7. Ethical resume bullet tailoring.
8. Daily email digest generation via EventBridge Scheduler and SQS.
9. BYOK integration for candidate-driven LLM interactions.

### Explicitly Excluded (Initial Release)
1. **Automated Application Submission**: Bot-submitting forms on external portals is disallowed.
2. **Recruiter Portal**: No employer accounts, posting management, or candidate resume databases.
3. **Paid Monetization**: No subscription gating, payment processing, or recruiter credits.
4. **Proprietary Scraper Reverse-Engineering**: All job data ingestion must respect robots.txt and official APIs.
