# GEO-INFER-ANT

Comprehensive swarm intelligence and complex adaptive systems modeling using Active Inference principles for emergent collective behavior in geospatial contexts.

## Contents

- `config/`
- `docs/`
- `examples/`
- `src/`
- `tests/`
- `run_tests.py`
- `setup.py`
- `.cursorrules`
- `IMPLEMENTATION_STATUS.md`
- `SKILL.md`
- `pyproject.toml`
- `requirements.txt`

## Public Interface

- `setup.py:get_version` (function)
- `setup.py:get_long_description` (function)

## Module Metadata

- Module: `GEO-INFER-ANT`
- Package: `geo_infer_ant`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-ANT`
- Tests: `uv run python GEO-INFER-TEST/run_unified_tests.py --module ANT`

## Dependencies

- `asyncio-mqtt>=0.11.0`
- `geopandas>=0.10.0`
- `h3>=4.0.0`
- `jsonschema>=4.0.0`
- `matplotlib>=3.5.0`
- `networkx>=2.8`
- `numpy>=1.21.0`
- `pyyaml>=6.0`
- `scikit-learn>=1.1.0`
- `scipy>=1.7.0`

## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module ANT
```

## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
