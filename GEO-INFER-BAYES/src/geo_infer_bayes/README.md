# GEO-INFER-BAYES/src/geo_infer_bayes

Geo Infer Bayes workspace within `GEO-INFER-BAYES`.

## Contents

- `api/`
- `core/`
- `models/`
- `utils/`
- `__init__.py`
- `civic_intel.py`
- `crescent-city-geo-intel.json`

## Public Interface

- `__init__.py:SpatialCovariance` (class)
- `__init__.py:GaussianProcess` (class)
- `civic_intel.py:CrescentCityIntel` (class)
- `civic_intel.py:HazardPriorEntry` (class)
- `civic_intel.py:HazardCategoricalPrior` (class)
- `civic_intel.py:load_crescent_city_contract` (function)
- `civic_intel.py:load_crescent_city_intel` (function)
- `civic_intel.py:build_hazard_prior_table` (function)
- `civic_intel.py:build_hazard_categorical_prior` (function)

## Module Metadata

- Module: `GEO-INFER-BAYES`
- Package: `geo_infer_bayes`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-BAYES`
- Tests: `uv run python GEO-INFER-TEST/run_unified_tests.py --module BAYES`

## Dependencies

- `arviz>=0.12.0`
- `matplotlib>=3.5.0`
- `numpy>=1.20.0,<2.0`
- `pandas>=1.3.0`
- `scipy>=1.7.0`
- `tqdm>=4.60.0`
- `xarray>=2022.3.0`


## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module BAYES
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
