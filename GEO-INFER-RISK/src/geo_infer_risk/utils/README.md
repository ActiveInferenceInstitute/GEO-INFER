# GEO-INFER-RISK/src/geo_infer_risk/utils

Utils workspace within `GEO-INFER-RISK`.

## Contents

- `config_loader.py`
- `risk_metrics.py`
- `validation.py`

## Public Interface

- `config_loader.py:ConfigurationLoader` (class)
- `config_loader.py:load_config` (function)
- `config_loader.py:load_config_with_defaults` (function)
- `config_loader.py:create_example_config` (function)
- `config_loader.py:get_default_config` (function)
- `config_loader.py:save_config` (function)
- `risk_metrics.py:calculate_aal` (function)
- `risk_metrics.py:calculate_ep_curve` (function)
- `risk_metrics.py:calculate_pml` (function)
- `risk_metrics.py:calculate_loss_by_return_period` (function)
- `risk_metrics.py:calculate_tail_value_at_risk` (function)
- `risk_metrics.py:calculate_annual_occurrence_exceedance_probability` (function)
- `risk_metrics.py:calculate_annual_aggregate_exceedance_probability` (function)
- `risk_metrics.py:calculate_loss_frequency_curve` (function)
- `risk_metrics.py:calculate_correlation_matrix` (function)
- `validation.py:ValidationResult` (class)
- `validation.py:ConfigurationValidator` (class)
- `validation.py:validate_config` (function)
- `validation.py:validate_data_file` (function)
- `validation.py:validate_csv_file` (function)

## Module Metadata

- Module: `GEO-INFER-RISK`
- Package: `geo_infer_risk`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-RISK`
- Tests: `uv run python GEO-INFER-TEST/run_unified_tests.py --module RISK`

## Dependencies

- `numpy>=1.20.0`
- `pandas>=1.3.0`
- `scipy>=1.7.0`


## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module RISK
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
