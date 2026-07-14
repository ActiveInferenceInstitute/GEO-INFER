# GEO-INFER-EXAMPLES

Comprehensive collection of working examples and tutorials demonstrating cross-module integration patterns and real-world applications.

## Contents

- `assessment_results/`
- `config/`
- `docs/`
- `examples/`
- `logs/`
- `scripts/`
- `src/`
- `tests/`
- `run_orchestrator.py`
- `setup.py`
- `.cursorrules`
- `.gitignore`
- `SKILL.md`
- `pyproject.toml`
- `requirements.txt`

## Public Interface

- `setup.py:read_readme` (function)
- `setup.py:read_version` (function)

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
- `requests>=2.28.0`
- `rich>=12.0.0`
- `typer>=0.7.0`


## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module EXAMPLES
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
