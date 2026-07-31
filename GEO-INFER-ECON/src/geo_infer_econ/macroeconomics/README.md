# GEO-INFER-ECON/src/geo_infer_econ/macroeconomics

Macroeconomics workspace within `GEO-INFER-ECON`.

## Contents

- `__init__.py`
- `growth_models.py`

## Public Interface

- `__init__.py:AggregateGrowthModels` (class)
- `__init__.py:BusinessCycleModels` (class)
- `__init__.py:MonetaryPolicyModels` (class)
- `__init__.py:FiscalPolicyModels` (class)
- `__init__.py:TradeModels` (class)
- `growth_models.py:RegionProfile` (class)
- `growth_models.py:SolowGrowthModel` (class)
- `growth_models.py:SpatialGrowthModels` (class)
- `growth_models.py:EndogenousGrowthModels` (class)
- `growth_models.py:RegionalConvergenceAnalysis` (class)
- `growth_models.py:TechnologyDiffusionModels` (class)
- `growth_models.py:example_growth_analysis` (function)

## Module Metadata

- Module: `GEO-INFER-ECON`
- Package: `geo_infer_econ`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-ECON`
- Tests: `uv run python GEO-INFER-TEST/run_unified_tests.py --module ECON`

## Dependencies

- `numpy>=1.20.0`
- `pandas>=1.3.0`
- `scipy>=1.7.0`
- `geopandas>=0.12.0`
- `shapely>=2.0.0`
- `scikit-learn>=1.0.0`
- `matplotlib>=3.5.0`
- `seaborn>=0.12.0`
- `networkx>=2.8.0`
- `h3>=4.5.0,<5`
- `pyyaml>=6.0`
- `requests>=2.28.0`


## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module ECON
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
