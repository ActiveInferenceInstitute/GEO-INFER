# GEO-INFER-PLACE/tests/unit

Unit workspace within `GEO-INFER-PLACE`.

## Contents

- `test_api_clients.py`
- `test_caching.py`
- `test_comprehensive_dashboard.py`
- `test_dashboard_advanced.py`
- `test_data_sources.py`
- `test_del_norte_analyzers.py`
- `test_h3_operations.py`
- `test_integration_wrappers.py`
- `test_module_bridge.py`
- `test_place_analyzer.py`
- `test_place_interface.py`
- `test_unified_backend.py`
- `test_visualization_engine.py`

## Public Interface

- No public Python symbols are defined directly in this directory.

## Module Metadata

- Module: `GEO-INFER-PLACE`
- Package: `geo_infer_place`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-PLACE`
- Tests: `uv run python -m pytest GEO-INFER-PLACE/tests/unit`

## Dependencies

- `geopandas>=0.10.0`
- `shapely>=1.8.0`
- `h3>=4.0.0`
- `numpy>=1.20.0`
- `pandas>=1.3.0`
- `pyyaml>=6.0`
- `folium>=0.14.0`
- `plotly>=5.0.0`
- `matplotlib>=3.5.0`
- `seaborn>=0.12.0`
- `branca>=0.6.0`
- `requests>=2.28.0`

## Validation

```bash
uv run python -m pytest GEO-INFER-PLACE/tests/unit
```

## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
