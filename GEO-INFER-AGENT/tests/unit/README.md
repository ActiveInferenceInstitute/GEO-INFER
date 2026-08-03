# GEO-INFER-AGENT/tests/unit

Unit workspace within `GEO-INFER-AGENT`.

## Contents

- `models/`
- `test_agent_base.py`
- `test_agent_communication.py`
- `test_coordination.py`
- `test_data_collector.py`
- `test_hybrid.py`
- `test_llm_proxy.py`
- `test_messaging.py`
- `test_planning.py`
- `test_rule_based.py`
- `test_task_management.py`
- `test_telemetry.py`

## Public Interface

- No public Python symbols are defined directly in this directory.

## Module Metadata

- Module: `GEO-INFER-AGENT`
- Package: `geo_infer_agent`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-AGENT`
- Tests: `uv run python -m pytest GEO-INFER-AGENT/tests/unit`

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
uv run python -m pytest GEO-INFER-AGENT/tests/unit
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
