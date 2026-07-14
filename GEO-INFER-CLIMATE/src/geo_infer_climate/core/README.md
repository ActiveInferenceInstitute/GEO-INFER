# GEO-INFER-CLIMATE/src/geo_infer_climate/core

Core workspace within `GEO-INFER-CLIMATE`.

## Contents

- `__init__.py`
- `classification.py`
- `climate_data.py`
- `climate_indices.py`
- `downscaling.py`
- `extreme_events.py`
- `impact_assessment.py`
- `precipitation_analysis.py`
- `projections.py`
- `temperature_trends.py`

## Public Interface

- `classification.py:ClimateClassifier` (class)
- `climate_data.py:ClimateDataProcessor` (class)
- `climate_indices.py:ClimateIndicesCalculator` (class)
- `downscaling.py:DownscalingMethods` (class)
- `extreme_events.py:ExtremeEventType` (class)
- `extreme_events.py:Severity` (class)
- `extreme_events.py:ExtremeEvent` (class)
- `extreme_events.py:ExtremeEventAnalyzer` (class)
- `impact_assessment.py:ClimateImpactAssessor` (class)
- `precipitation_analysis.py:PrecipitationAnalyzer` (class)
- `projections.py:ClimateProjections` (class)
- `temperature_trends.py:TemperatureTrendAnalyzer` (class)

## Module Metadata

- Module: `GEO-INFER-CLIMATE`
- Package: `geo_infer_climate`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-CLIMATE`
- Tests: `uv run python GEO-INFER-TEST/run_unified_tests.py --module CLIMATE`

## Dependencies

- `numpy>=1.20.0`
- `pandas>=1.3.0`
- `scipy>=1.7.0`
- `matplotlib>=3.4.0`
- `xarray>=0.19.0`
- `netcdf4>=1.5.8`
- `pyyaml>=6.0`
- `scikit-learn>=1.0.0`


## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module CLIMATE
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
