# GEO-INFER-EXAMPLES/src/geo_infer_examples/models

Models workspace within `GEO-INFER-EXAMPLES`.

## Contents

- `__init__.py`
- `integration_models.py`

## Public Interface

- `integration_models.py:ModuleType` (class)
- `integration_models.py:DataFormat` (class)
- `integration_models.py:IntegrationPattern` (class)
- `integration_models.py:ModuleSpec` (class)
- `integration_models.py:ModuleConnection` (class)
- `integration_models.py:WorkflowStep` (class)
- `integration_models.py:WorkflowDefinition` (class)
- `integration_models.py:ExecutionContext` (class)
- `integration_models.py:SpatialTemporalData` (class)
- `integration_models.py:AnalysisResult` (class)
- `integration_models.py:IntegrationResult` (class)
- `integration_models.py:HealthSurveillanceData` (class)
- `integration_models.py:AgriculturalData` (class)
- `integration_models.py:UrbanPlanningData` (class)
- `integration_models.py:ClimateData` (class)
- `integration_models.py:IntegrationPatterns` (class)
- `integration_models.py:DataFormatConverter` (class)
- `integration_models.py:load_workflow_from_file` (function)
- `integration_models.py:save_workflow_to_file` (function)

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
