# GEO-INFER-EXAMPLES/examples/iot_radiation_monitoring/scripts

Scripts workspace within `GEO-INFER-EXAMPLES`.

## Contents

- `logs/`
- `output/`
- `enhanced_visualization.py`
- `run_example.py`

## Public Interface

- `enhanced_visualization.py:InteractiveRadiationDashboard` (class)
- `enhanced_visualization.py:create_geojson_with_features` (function)
- `enhanced_visualization.py:generate_time_series_plot_html` (function)
- `enhanced_visualization.py:main` (function)
- `run_example.py:EnhancedLogger` (class)
- `run_example.py:QualityController` (class)
- `run_example.py:load_config` (function)
- `run_example.py:generate_sample_sensor_data` (function)
- `run_example.py:perform_spatial_indexing` (function)
- `run_example.py:perform_bayesian_inference` (function)
- `run_example.py:detect_anomalies` (function)
- `run_example.py:save_results` (function)
- `run_example.py:run_tests` (function)
- `run_example.py:main` (function)

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
