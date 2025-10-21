# Security Policy

This repository implements a recommendation pipeline that processes
behavioural data. Although no personally identifiable information (PII)
is used, security best practices are followed throughout the code base.

## OWASP & Secure Coding

The pipeline adheres to the OWASP Top Ten awareness principles by
validating all external inputs, avoiding injection risks and minimising
attack surface. Specifically:

- **Input validation.** URLs, counts and dates provided via
  configuration are validated before use. The Pydantic settings class
  enforces types and patterns for each field.
- **Secrets management.** No secrets or credentials are committed to
  version control. All configuration is supplied via environment
  variables【599210147542025†L10-L43】. If additional secrets (e.g. S3
  access keys) are required they should be stored in a secure secret
  manager or GitHub Actions secrets and loaded at runtime.
- **Dependency pinning.** All dependencies are pinned to specific
  versions in `pyproject.toml`. This mitigates supply chain risks
  associated with ambiguous version ranges.
- **Least privilege.** The Dockerfile creates a non‑root user and
  executes the application under this account【209730043449387†L1541-L1554】. The
  container is built from a minimal base image and only necessary
  packages are installed.
- **Logging redaction.** Structured logs omit sensitive data and focus
  on high‑level metrics and correlation identifiers.

## Reporting Vulnerabilities

If you discover a security vulnerability in this project please
responsibly disclose it by opening a GitHub issue or contacting the
maintainer at [info@condata.io](mailto:info@condata.io). Do not submit
vulnerabilities through public pull requests.