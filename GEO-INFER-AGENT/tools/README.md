# GEO-INFER-AGENT/tools

Tools workspace within `GEO-INFER-AGENT`.

## Contents

- `visualize_structure.py`

## Public Interface

- `visualize_structure.py:should_exclude` (function)
- `visualize_structure.py:collect_structure` (function)
- `visualize_structure.py:generate_tree_markdown` (function)
- `visualize_structure.py:generate_mermaid_flowchart` (function)
- `visualize_structure.py:generate_class_diagram` (function)
- `visualize_structure.py:main` (function)

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
- `requests>=2.28.2`
- `fastapi>=0.104.0`
- `pydantic>=2.5.0`
- `pandas>=1.3.0`
- `uvicorn>=0.24.0`
- `psutil>=5.9.0`
- `pytest>=7.3.1`
- `pytest-cov>=4.1.0`
- `pytest-asyncio>=0.20.0`


## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module AGENT
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
