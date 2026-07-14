# GEO-INFER-AGENT

Intelligent autonomous agents for geospatial decision-making, perception, and action with Active Inference, BDI, and reinforcement learning architectures.

## Contents

- `.pytest_cache/`
- `config/`
- `docs/`
- `examples/`
- `src/`
- `tests/`
- `tools/`
- `setup.py`
- `.cursorrules`
- `SKILL.md`
- `pyproject.toml`
- `requirements.txt`

## Public Interface

- No public Python symbols are defined directly in this directory.

## Module Metadata

- Module: `GEO-INFER-AGENT`
- Package: `geo_infer_agent`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-AGENT`
- Tests: `uv run python GEO-INFER-TEST/run_unified_tests.py --module AGENT`

## Dependencies

- `numpy>=1.23.5`
- `torch>=2.0.0`
- `pyyaml>=6.0`
- `tqdm>=4.65.0`
- `requests>=2.28.2`
- `colorlog>=6.7.0`
- `pytest>=7.3.1`
- `pytest-cov>=4.1.0`
- `mypy>=1.3.0`
- `black>=23.3.0`
- `isort>=5.12.0`
- `matplotlib>=3.7.1`


## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module AGENT
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
