# GEO-INFER-EXAMPLES/examples/module_orchestrators

Module Orchestrators workspace within `GEO-INFER-EXAMPLES`.

## Contents

- `ACT/`
- `AG/`
- `AGENT/`
- `AI/`
- `ANT/`
- `API/`
- `APP/`
- `ART/`
- `BAYES/`
- `BIO/`
- `CIV/`
- `COG/`
- `COMMS/`
- `DATA/`
- `ECON/`
- `GIT/`
- `HEALTH/`
- `INTRA/`
- `IOT/`
- `LOG/`
- `MATH/`
- `NORMS/`
- `OPS/`
- `ORG/`
- `PEP/`
- `PLACE/`
- `REQ/`
- `RISK/`
- `SEC/`
- `SIM/`
- `SPACE/`
- `SPM/`
- `TEST/`
- `TIME/`
- `generate_orchestrators.py`
- `update_to_thin_orchestrators.py`

## Public Interface

- `generate_orchestrators.py:create_orchestrator_structure` (function)
- `generate_orchestrators.py:main` (function)
- `update_to_thin_orchestrators.py:create_thin_orchestrator_script` (function)
- `update_to_thin_orchestrators.py:main` (function)

## Module Metadata

- Module: `GEO-INFER-EXAMPLES`
- Package: `geo_infer_examples`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-EXAMPLES`
- Tests: `uv run python GEO-INFER-TEST/run_unified_tests.py --module EXAMPLES`

## Dependencies

- `jupyterlab>=3.4.0`
- `matplotlib>=3.5.0`
- `pandas>=1.4.0`
- `pyyaml>=6.0`
- `h3>=4.5.0,<5`
- `requests>=2.28.0`
- `rich>=12.0.0`
- `typer>=0.7.0`


## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module EXAMPLES
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
