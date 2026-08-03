# Security Policy

## Supported versions

GEO-INFER is a continuously developed monorepo. Security fixes are evaluated
against the current `main` branch and the dependency lockfile in the checkout.
There are no version-specific support promises in this repository; consumers
should update to the current default branch before reporting or assessing a
fix.

## Reporting a vulnerability

Please do not open a public GitHub issue for a security vulnerability. Use
[GitHub Private Vulnerability Reporting](https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing/privately-reporting-a-security-vulnerability)
for this repository and include:

- A concise description of the vulnerability.
- Reproduction steps or a minimal proof of concept.
- Potential impact and affected modules or commands.
- Relevant environment and dependency information (without secrets).
- A suggested fix, if available.

The maintainers will acknowledge reports and provide status updates as the
investigation permits. Response and remediation time depends on severity,
reproducibility, and maintainer availability; this policy does not promise a
fixed response-time SLA.

## Security practices for contributors and users

1. Keep dependencies reproducible with `uv sync` and review lockfile changes.
2. Use environment variables or a secret manager for sensitive configuration;
   never commit credentials or tokens.
3. Validate untrusted input, paths, coordinate values, and output locations.
4. Follow least privilege when deploying integrations or services.
5. Treat detailed location data as potentially sensitive and apply appropriate
   anonymization, access controls, and jurisdictional requirements.

The GEO-INFER-SEC module contains security-related utilities, but its current
exports and coverage should be checked in
[GEO-INFER-SEC/README.md](./GEO-INFER-SEC/README.md) before relying on a
specific capability.
