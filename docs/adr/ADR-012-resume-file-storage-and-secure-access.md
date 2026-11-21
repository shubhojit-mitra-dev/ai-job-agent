# ADR-012: Resume File Storage and Secure Access

- **Status**: Accepted
- **Date**: 2026-11-20 (Accepted 2026-11-21)
- **Authors**: Technical Lead, Architecture Engineer

---

## 1. Context
Candidates upload personal resumes in PDF and DOCX formats. These documents contain sensitive Personal Identifiable Information (PII) including full names, contact emails, phone numbers, academic backgrounds, and employment histories.

Resumes must be stored securely, protected against unauthorized access, and made accessible to parsing workers and candidate owners without exposing public URLs or leaking PII.

Following our evaluation in Phase 00, we must formally select the authoritative storage provider and establish comprehensive security, lifecycle, and access control protocols.

---

## 2. Decision

Adopt **Private Amazon S3** in AWS `ap-south-1` (Mumbai) as the authoritative document and resume object store for the platform:

### 2.1. S3 Bucket Security Configuration
1. **Block Public Access (BPA)**: All four S3 Block Public Access settings are enabled unconditionally:
   - `BlockPublicAcls = true`
   - `IgnorePublicAcls = true`
   - `BlockPublicPolicy = true`
   - `RestrictPublicBuckets = true`
2. **Server-Side Encryption at Rest**:
   - Enforce server-side encryption with AWS Key Management Service (SSE-KMS) or Amazon S3 managed keys (SSE-S3).
   - All upload requests missing encryption headers or attempting unencrypted transfers are denied via bucket policy.
3. **Transport Security**:
   - Enforce TLS 1.2+ in transit via bucket policy (`aws:SecureTransport = true`).
4. **Least-Privilege IAM Execution Roles**:
   - FastAPI Lambda execution role is granted only `s3:PutObject`, `s3:GetObject`, and `s3:DeleteObject` restricted to the candidate partition (`arn:aws:s3:::career-platform-resumes-${env}/candidates/*`).
   - SQS Worker Lambda is granted read-only access (`s3:GetObject`) to process parsing tasks.

### 2.2. Object Key Organization and Candidate Partitioning
Objects are partitioned strictly by candidate ID:
```text
s3://career-platform-resumes-${env}/candidates/{user_id}/resumes/{resume_id}.pdf
```
- `{user_id}`: The internal candidate UUID matching the authenticated candidate profile.
- `{resume_id}`: A cryptographically random UUID identifying the specific resume upload.

### 2.3. Pre-Signed Access Controls
- **Zero Public Access**: The S3 bucket has zero public read permissions.
- **Short-Lived Pre-Signed Uploads**:
  - The client requests an upload authorization via `POST /api/v1/resumes/upload-url`.
  - The FastAPI backend validates the candidate's authentication token, confirms user identity, and generates a pre-signed S3 PUT URL with:
    - Expiration time strictly capped at **15 minutes** (900 seconds).
    - `Content-Length` conditions enforcing a **maximum size of 5 MB**.
    - Allowed `Content-Type` headers restricted to `application/pdf` and `application/vnd.openxmlformats-officedocument.wordprocessingml.document`.
- **Short-Lived Pre-Signed Downloads**:
  - Pre-signed GET URLs for viewing/downloading resumes are generated with a **15-minute expiration** only after validating that `current_user.id == target_user_id`.

### 2.4. Document Validation & Malware Scanning
- **File Size**: Strictly capped at 5 MB at API Gateway and pre-signed policy levels.
- **Magic Byte Validation**: Before dispatching a resume to the extraction pipeline, the worker inspects file magic bytes (e.g. `%PDF-` for PDFs, PK zip headers for DOCX) to prevent file extension spoofing.
- **Malware & Executable Protection**: Executable macros and embedded scripts in documents are rejected. In production, an asynchronous S3 Event trigger can invoke a scanning Lambda before parsing.

### 2.5. Lifecycle Rules, Retention, and Right to be Forgotten
1. **Incomplete Multipart Uploads**: S3 lifecycle rule aborts and removes incomplete multipart uploads after **7 days** to prevent hidden storage costs.
2. **Archived / Replaced Resumes**: When a candidate uploads a new primary resume, previous versions are transitioned to S3 Standard-Infrequent Access (IA) or flagged for deletion after 30 days.
3. **Account Deletion (Right to be Forgotten)**: When a candidate deletes their account, an automated S3 batch delete job permanently deletes all objects under `candidates/{user_id}/*`.
4. **Privacy in Logs**: S3 access logs and application logs must strictly redact object keys containing direct candidate identifiers and never log presigned URL query parameters.

---

## 3. Alternatives Considered

- **Supabase Storage**:
  - *Evaluation*: Used during initial Phase 00 exploration.
  - *Reason for Rejection*: Hosted outside our primary AWS `ap-south-1` region, introducing external data egress costs and latency when fetched by Lambda workers. Free tier is limited to 1 GB. Superseded by Amazon S3 to consolidate all storage, compute, and IAM under AWS `ap-south-1`.
- **Direct Database Storage (PostgreSQL BLOB / BYTEA)**:
  - *Reason for Rejection*: Storing binary PDF files inside Aurora PostgreSQL drastically bloats database size, exhausts buffer cache, degrades query performance, and complicates backups.

---

## 4. Consequences

### Positive
- High durability (99.999999999% - 11 9s) and native availability in `ap-south-1`.
- Co-located with FastAPI Lambda and SQS Worker Lambda: zero cross-cloud latency and zero intra-region data transfer fees.
- Offloads file transfer bandwidth from Lambda compute; candidates upload directly to S3 via pre-signed URLs.
- Fully automated lifecycle rules and encryption management via Terraform.

### Negative
- Requires implementing pre-signed URL generation via `aioboto3` / `boto3` in FastAPI.
- Local development requires a local S3 mock (e.g. Moto or LocalStack, or an abstract storage protocol with local disk fallback).

---

## 5. Security Implications
- S3 Block Public Access guarantees resumes cannot be exposed to the public internet by accidental ACL or bucket policy changes.
- Pre-signed URLs expire after 15 minutes, limiting exposure if a URL is intercepted.
- Candidate partitioning prevents cross-tenant access.

---

## 6. Cost Implications
- **Storage**: Amazon S3 Standard in `ap-south-1` costs **\$0.023 per GB-month**.
  - 1,000 resumes (average 1 MB each) = 1 GB = **~\$0.02/month**.
- **Requests**: PUT/POST requests cost \$0.005 per 1,000 requests; GET requests cost \$0.0004 per 1,000 requests.
- Monthly resume storage expense for early-stage candidate volume is **< \$0.10/month**, easily accommodated within our \$200 budget.

---

## 7. Risks and Mitigations
- **Risk**: Orphaned resume files if candidate aborts upload after receiving pre-signed URL.
  - *Mitigation*: The backend only links a resume to a candidate profile when the client confirms successful upload via a callback endpoint (`POST /api/v1/resumes/{id}/confirm`). A periodic S3 lifecycle or sweeper job purges unconfirmed files older than 24 hours.

---

## 8. References
- [Amazon S3 Security Best Practices](https://docs.aws.amazon.com/AmazonS3/latest/userguide/security-best-practices.html)
- [Working with Pre-Signed URLs](https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-presigned-url.html)
- [docs/SECURITY.md](../SECURITY.md)
