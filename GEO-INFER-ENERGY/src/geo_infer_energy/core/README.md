# GEO-INFER-ENERGY/src/geo_infer_energy/core

Core workspace within `GEO-INFER-ENERGY`.

## Contents

- `__init__.py`
- `carbon_footprint.py`
- `energy_demand.py`
- `energy_grid.py`
- `energy_infrastructure.py`
- `renewable_resources.py`
- `solar_analysis.py`
- `wind_analysis.py`

## Public Interface

- `carbon_footprint.py:CarbonFootprintAnalyzer` (class)
- `energy_demand.py:EnergyDemandForecaster` (class)
- `energy_grid.py:EnergyGridOptimizer` (class)
- `energy_infrastructure.py:EnergyInfrastructurePlanner` (class)
- `renewable_resources.py:RenewableType` (class)
- `renewable_resources.py:SuitabilityClass` (class)
- `renewable_resources.py:RenewableSite` (class)
- `renewable_resources.py:RenewableResourceAssessor` (class)
- `solar_analysis.py:SolarAnalyzer` (class)
- `wind_analysis.py:WindAnalyzer` (class)

## Module Metadata

- Module: `GEO-INFER-ENERGY`
- Package: `geo_infer_energy`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-ENERGY`
- Tests: `uv run python GEO-INFER-TEST/run_unified_tests.py --module ENERGY`

## Dependencies

- `numpy>=1.20.0`
- `pandas>=1.3.0`
- `scipy>=1.7.0`
- `matplotlib>=3.4.0`
- `xarray>=0.19.0`
- `pyyaml>=6.0`
- `scikit-learn>=1.0.0`

## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module ENERGY
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
