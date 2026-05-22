# GEO-INFER-PLACE/locations/del_norte_county

Del Norte County workspace within `GEO-INFER-PLACE`.

## Contents

- `config/`
- `del_norte_dashboard/`
- `create_del_norte_dashboard.py`
- `run_analysis.py`
- `requirements.txt`
- `requirements_advanced.txt`
- `run_analysis.sh`

## Public Interface

- `create_del_norte_dashboard.py:main` (function)
- `run_analysis.py:load_location_config` (function)
- `run_analysis.py:cleanup_old_results` (function)
- `run_analysis.py:main` (function)

## Module Metadata

- Module: `GEO-INFER-PLACE`
- Package: `geo_infer_place`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-PLACE`
- Tests: `uv run python GEO-INFER-TEST/run_unified_tests.py --module PLACE`

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
uv run python GEO-INFER-TEST/run_unified_tests.py --module PLACE
```

## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
