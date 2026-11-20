# ADR-007: Terraform for Infrastructure as Code

- **Status**: Accepted
- **Date**: 2026-11-20
- **Authors**: Technical Lead, Architecture Engineer

---

## 1. Context
We need a declarative, repeatable, and version-controlled method to manage all AWS cloud resources (API Gateway, Lambda, SQS, IAM, EventBridge). Manual AWS console provisioning causes configuration drift and unrepeatable deployments.

## 2. Decision
Use **Terraform** as the authoritative Infrastructure as Code (IaC) tool:
1. All infrastructure code resides under `infra/terraform/`.
2. State is stored remotely in an encrypted Amazon S3 bucket with Amazon DynamoDB state locking.
3. Modular design: separate modules for `api_gateway`, `lambda`, `sqs`, `scheduler`, and `iam`.
4. Formatting and syntax checks are enforced via `terraform fmt -check` and `terraform validate` in CI/CD.

## 3. Alternatives Considered
- **AWS CDK**: Introduces Node.js synthesis and CloudFormation compilation layers. Terraform provides simpler HCL syntax and direct state management.
- **Serverless Framework / SAM**: Specialized for Lambda, but less robust when managing broader AWS infrastructure (IAM OIDC roles, S3 remote state, complex SQS policies).

## 4. Consequences
- **Positive**: Reproducible environments, explicit plan reviews in PRs, automated CI/CD deployment, state locking.
- **Negative**: Requires initial manual bootstrap of the S3 state bucket and DynamoDB lock table.

## 5. Risks
- State file corruption or concurrent writes. Mitigated by DynamoDB state locking.

## 6. References
- Terraform S3 Backend Documentation: https://developer.hashicorp.com/terraform/language/backend/s3
