# ADR-013: Amazon Cognito User Pools for Candidate Authentication

- **Status**: Accepted
- **Date**: 2026-11-21
- **Authors**: Technical Lead, Architecture Engineer

---

## 1. Context
The AI Career Platform requires secure candidate registration, authentication, password recovery, session management, and tenant isolation in AWS `ap-south-1` (Mumbai). Following the architectural decision to migrate from Supabase to an AWS-native foundation, we must establish an authoritative authentication and token verification architecture that integrates cleanly with AWS API Gateway, FastAPI running on AWS Lambda via Mangum, and Next.js 16.

We must define exact cryptographic verification protocols, delineate perimeter authorizer versus application middleware responsibilities, map external authentication identifiers to stable internal candidate identities, and enforce strict tenant isolation across all application services.

---

## 2. Decision

Adopt **Amazon Cognito User Pools** in AWS `ap-south-1` as the authoritative identity and authentication service for candidates:

### 2.1. Registration, Authentication, and Session Lifecycle
1. **User Registration & Verification**: Candidates register using email and password. Amazon Cognito handles email verification via one-time codes (OTP) and enforces strong password policies without custom backend authentication code.
2. **Authentication & Token Issuance**: Candidates authenticate directly against Cognito (or via hosted UI / frontend AWS Amplify / SDK client). Upon successful authentication, Cognito issues three JSON Web Tokens (JWTs):
   - **ID Token**: Contains user identity claims (`sub`, `email`, `email_verified`, `cognito:username`).
   - **Access Token**: Contains authorization claims (`sub`, `client_id`, `token_use=access`, `scope`).
   - **Refresh Token**: Used to obtain new access and ID tokens without prompting the candidate for credentials.
3. **Logout & Revocation**: Logout revokes refresh tokens via Cognito's `GlobalSignOut` or `RevokeToken` API, invalidating ongoing sessions across devices.

### 2.2. JWT Verification and Cryptographic Protocol
- **Asymmetric Signature Verification**: Cognito signs tokens using RSA (RS256) public key cryptography.
- **Authoritative JWKS Endpoint**: Public keys are retrieved from the well-known JWKS endpoint:
  `https://cognito-idp.ap-south-1.amazonaws.com/{userPoolId}/.well-known/jwks.json`
- **Verification Rules**:
  - `alg` must strictly match `RS256`.
  - `iss` must strictly equal `https://cognito-idp.ap-south-1.amazonaws.com/{userPoolId}`.
  - `aud` (for ID tokens) or `client_id` (for access tokens) must strictly match the configured Cognito App Client ID.
  - `token_use` must match the expected token type (`access` for API authorization).
  - `exp` must be in the future (tokens are rejected after expiration).
  - `sub` must be present and conform to a valid UUID format.

### 2.3. Architectural Separation of Responsibilities

```mermaid
flowchart LR
    Client["Next.js Web Client"] -->|HTTPS + Bearer JWT| APIGW["API Gateway HTTP API"]
    APIGW -->|JWT Authorizer (Perimeter Check)| APIGW
    APIGW -->|Proxy Request + Claims| Lambda["FastAPI Lambda"]
    Lambda --> AuthMiddleware["FastAPI Auth Middleware"]
    AuthMiddleware -->|Validate Claims & Map sub| CurrentUser["CurrentUser (user_id)"]
    CurrentUser --> AppService["Application Service Layer"]
    AppService -->|Tenant Filter (WHERE user_id = :uid)| Aurora[("Aurora PostgreSQL")]
```

1. **Perimeter Defense (API Gateway HTTP API JWT Authorizer)**:
   - Configured with the Cognito User Pool issuer and App Client ID.
   - Rejects unauthenticated, expired, or malformed requests at the AWS cloud perimeter (edge) with HTTP 401 Unauthorized before invoking Lambda.
   - Protects backend Lambda functions from denial-of-wallet invocation spikes.
2. **Application Defense in Depth (FastAPI Middleware)**:
   - The FastAPI backend does not blindly trust perimeter claims; in local development, direct testing, and defense-in-depth configurations, the backend independently verifies the Bearer token signature against Cognito's JWKS.
   - Extracts the authenticated `sub` (Cognito UUID) and maps it to the candidate's internal profile context.
3. **Stable Internal Candidate Identity**:
   - The Cognito `sub` UUID serves as the immutable foreign key identifier linking authentication records to relational candidate profiles (`candidates.cognito_sub = :sub`).
   - Relational tables maintain an internal primary key `user_id` (UUID) to isolate the application domain from future identity provider migrations.

### 2.4. Authentication vs. Tenant Authorization
- **Non-Equivalence Mandate**: Authentication proves *identity* (who the caller is); it does **not** authorize *data access* (what the caller can see or mutate).
- Every candidate-scoped SQL query executed by the application must explicitly enforce tenant ownership:
  ```sql
  SELECT * FROM candidate_resumes WHERE user_id = :current_user_id;
  ```
- No user-supplied ID in URL query parameters, route paths, or request bodies can override the authenticated `current_user.id`.

### 2.5. Account Deletion and Right to be Forgotten
- When a candidate deletes their account:
  1. Relational records across Aurora PostgreSQL (profiles, resumes, preferences, dealbreakers) are deleted or marked purged.
  2. Stored resumes in Amazon S3 and vectors in Amazon S3 Vectors are permanently deleted.
  3. The Cognito user account is deleted via `AdminDeleteUser`.
  4. Active sessions are invalidated immediately.

---

## 3. Alternatives Considered

- **Supabase Auth (Supabase GoTrue)**:
  - *Evaluation*: Used during initial Phase 00 scaffolding. Provides excellent developer ergonomics and consolidated PostgreSQL integration.
  - *Reason for Rejection*: Superseded by this ADR to establish an AWS-native architecture co-located in `ap-south-1`, eliminating external third-party cloud dependencies, cross-cloud latency, and separate billing boundaries.
- **Custom Self-Hosted Auth (FastAPI + OAuth2PasswordBearer + PostgreSQL)**:
  - *Evaluation*: Complete control over password hashing, tables, and token issuance.
  - *Reason for Rejection*: Substantially increases security liability (credential storage, password reset flows, MFA, brute-force throttling, cryptographic key rotation). Violates the mandate to avoid custom authentication primitives.
- **Auth0 by Okta**:
  - *Evaluation*: Rich feature set and integrations.
  - *Reason for Rejection*: Commercial third-party SaaS with steep cost ramps beyond the free tier; hosted outside our direct AWS IAM and Terraform governance.

---

## 4. Consequences

### Positive
- Fully managed by AWS in `ap-south-1` with 99.9% availability SLA.
- Native integration with AWS API Gateway HTTP API JWT authorizers for perimeter token verification.
- Generous free tier: **50,000 monthly active users (MAUs)** always free for Cognito User Pools.
- Offloads credential hashing, verification emails, password resets, and brute-force defenses from application code.
- Fully codifiable via Terraform (`aws_cognito_user_pool`, `aws_cognito_user_pool_client`).

### Negative
- Local development without internet access requires a fake JWT verification fixture and mock authentication flow.
- Token claims customization requires Pre-Token Generation Lambda triggers if custom claims are needed.
- Developer experience is slightly more verbose than Supabase Auth SDK.

---

## 5. Security Implications
- **Brute-Force Protection**: Cognito provides built-in risk-based adaptive authentication, account lockout, and rate limiting.
- **No Stored Passwords**: Application databases never touch, hash, or store candidate passwords.
- **Token Tampering Defense**: Tokens are verified with asymmetric RS256 cryptography against Cognito's authoritative JWKS; symmetric algorithms (`HS256`, `none`) are rejected unconditionally.
- **Tenant Isolation**: Cognito `sub` is strictly verified before injecting `CurrentUser` into domain services.

---

## 6. Cost Implications
- **Free Allowance**: Amazon Cognito User Pools includes **50,000 MAUs** free under the AWS Free Tier.
- **Cost Beyond Free Tier**: \$0.0055 per MAU above 50,000. For our anticipated early-stage volume and $200 AWS credit budget, Cognito incurs **\$0.00** monthly baseline cost.

---

## 7. Risks and Mitigations
- **Risk**: Local development dependencies on live Cognito endpoints.
  - *Mitigation*: The backend auth module abstracts token verification behind a pluggable interface. Local development uses a deterministic fake JWT issuer (`APP_ENV=development` with test keys) or Dockerized mock without requiring live AWS connectivity.
- **Risk**: User identity desynchronization between Cognito and Aurora PostgreSQL.
  - *Mitigation*: Candidate profile creation is idempotent; if a candidate exists in Cognito but lacks an Aurora profile (e.g. after registration interruption), the first authenticated API call provisions the candidate profile record cleanly.

---

## 8. References
- [Amazon Cognito Developer Guide](https://docs.aws.amazon.com/cognito/latest/developerguide/what-is-amazon-cognito.html)
- [Amazon Cognito Pricing](https://aws.amazon.com/cognito/pricing/)
- [Controlling Access to HTTP APIs with JWT Authorizers](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-jwt-authorizer.html)
- [docs/SECURITY.md](../SECURITY.md)

