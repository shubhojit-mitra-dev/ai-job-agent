# ADR-008: GitHub Actions with AWS OIDC

- **Status**: Accepted
- **Date**: 2026-11-20
- **Authors**: Technical Lead, Architecture Engineer

---

## 1. Context
Automated CI/CD pipelines in GitHub Actions require authorization to execute Terraform plans/applies and deploy Lambda ZIP archives to AWS `ap-south-1`. Traditional setups store static `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` in GitHub repository secrets, which poses a serious security risk of credential leakage.

## 2. Decision
Adopt **GitHub Actions OpenID Connect (OIDC)** authentication with AWS IAM:
1. An AWS IAM Identity Provider is configured for GitHub's OIDC endpoint (`token.actions.githubusercontent.com`).
2. An IAM role with least-privilege trust policy is created, restricting assumption strictly to repository `shubhojit-mitra-dev/ai-job-agent` on branch `master`.
3. Workflows request short-lived (15–60 min) temporary STS security tokens using `aws-actions/configure-aws-credentials@v4`.
4. Absolutely zero permanent AWS access keys are stored in GitHub Secrets.

## 3. Alternatives Considered
- **Permanent IAM User Keys**: Storing long-lived access keys in GitHub Secrets. Rejected due to security risk and lack of automatic rotation.

## 4. Consequences
- **Positive**: No credential expiration or rotation overhead, granular role trust policies scoped to specific repos and branches, full AWS CloudTrail auditability.
- **Negative**: Requires initial setup of IAM OIDC provider in AWS account.

## 5. Risks
- Misconfigured trust policy permitting unauthorized branches. Mitigated by strictly scoping the `sub` claim to `repo:shubhojit-mitra-dev/ai-job-agent:ref:refs/heads/master`.

## 6. References
- GitHub Actions OIDC with AWS: https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-aws

