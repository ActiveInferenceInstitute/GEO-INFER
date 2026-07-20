# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| Main / unreleased | ✅ Yes — security fixes are evaluated against the current workspace |
| 0.2.x | ✅ Yes — latest published beta line |
| 0.1.x and earlier | ❌ No — upgrade before reporting a version-specific issue |

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability, please report it responsibly.

### How to Report

1. **Do NOT** open a public GitHub issue for security vulnerabilities
2. Use [GitHub Private Vulnerability Reporting](https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing/privately-reporting-a-security-vulnerability) or email the Active Inference Institute security team
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Affected GEO-INFER modules
   - Suggested fix (if any)

### Response Timeline

- **Initial Response**: Within 48 hours
- **Status Update**: Within 7 days
- **Fix Timeline**: Depends on severity
  - Critical: 24-72 hours
  - High: 1-2 weeks
  - Medium: 1 month
  - Low: Next release

### Security Best Practices

When using GEO-INFER:

1. **Keep dependencies reproducible** - use `uv sync` and review lockfile changes
2. **Use environment variables** for sensitive configuration
3. **Validate inputs** when processing external data
4. **Follow least privilege** when deploying services

## Known Security Considerations

### GEO-INFER-SEC Module

The GEO-INFER-SEC module provides security utilities:

- Authentication and authorization
- Data encryption
- Audit logging
- Access control

See [GEO-INFER-SEC/README.md](./GEO-INFER-SEC/README.md) for details.

### Geospatial Data Privacy

When working with geospatial data:

- Be aware of privacy implications of location data
- Anonymize sensitive location information
- Follow [GDPR](https://gdpr.eu/) and local regulations
- Use differential privacy techniques when appropriate

---

*Last Updated: 2026-07-15*
