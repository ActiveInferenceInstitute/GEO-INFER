# Realms API update summary (historical)

> **Historical artifact.** This document records an earlier exploratory API
> integration and test run. The external endpoints and result counts below are
> not maintained GEO-INFER contracts and have not been verified as current.
> Treat this file as historical context only; use the repository's current
> source, tests, and documentation for supported behavior.

## Scope

The original work explored schema validation, nullable fields, response
serialization, output organization, and endpoint testing for a proposed
realms integration. The implementation files referenced by that work remain
under this directory for historical reference, but this repository does not
currently expose a maintained realms service through GEO-INFER-INTRA.

## Current verification

For current GEO-INFER verification, run the repository's documentation and
module checks from the repository root:

```bash
uv run python GEO-INFER-TEST/validate_documentation.py --strict
uv run python GEO-INFER-TEST/run_unified_tests.py --module INTRA
```

Do not infer current endpoint availability, response counts, timing, or
success rates from the historical report.
