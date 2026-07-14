# GEO-INFER-EXAMPLES/src/geo_infer_examples/core

Core workspace within `GEO-INFER-EXAMPLES`.

## Contents

- `module_orchestrator.py`

## Public Interface

- `module_orchestrator.py:ConfigManager` (class)
- `module_orchestrator.py:setup_logging` (function)
- `module_orchestrator.py:APIConnector` (class)
- `module_orchestrator.py:PerformanceMonitor` (class)
- `module_orchestrator.py:ExecutionStrategy` (class)
- `module_orchestrator.py:ModuleStatus` (class)
- `module_orchestrator.py:WorkflowExecution` (class)
- `module_orchestrator.py:ModuleOrchestrator` (class)

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
