# Security Guidance

Security behavior is owned by the relevant module and repository policy. This
documentation hub does not claim a hosted authentication, database, SIEM, or
deployment service.

## Required practices

- Read the root [security policy](../../../SECURITY.md) before reporting a
  vulnerability.
- Do not commit secrets, tokens, private data, or generated credentials.
- Validate external inputs at module boundaries.
- Keep geospatial data privacy and re-identification risk in scope.
- Use least privilege for API, storage, and deployment credentials.
- Keep dependencies reproducible through `uv.lock` and review dependency
  changes.
- Do not expose a local API beyond its intended network boundary without
  configuring authentication, CORS, logging, and rate limits in the owning
  module.

## Security validation

```bash
uv run python GEO-INFER-TEST/validate_repo_contracts.py --strict-source-language
uv run python GEO-INFER-TEST/run_unified_tests.py --module SEC
uv run python GEO-INFER-TEST/run_unified_tests.py --module API
```

For vulnerability reports, use private GitHub reporting or the contact path in
the root policy rather than a public issue.
