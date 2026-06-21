# GEO-INFER-COMMS/src/geo_infer_comms/integrations

Integrations workspace within `GEO-INFER-COMMS`.

## Contents

- `__init__.py`
- `email_providers.py`

## Public Interface

- `email_providers.py:EmailProvider` (class)
- `email_providers.py:SendGridProvider` (class)
- `email_providers.py:SESProvider` (class)
- `email_providers.py:MailgunProvider` (class)
- `email_providers.py:EmailProviderFactory` (class)

## Module Metadata

- Module: `GEO-INFER-COMMS`
- Package: `geo_infer_comms`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-COMMS`
- Tests: `uv run python GEO-INFER-TEST/run_unified_tests.py --module COMMS`

## Dependencies

- `fastapi>=0.68.0`
- `pydantic>=1.8.0`

## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module COMMS
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
