# GEO-INFER-METAGOV/src/geo_infer_metagov/utils

Utils workspace within `GEO-INFER-METAGOV`.

## Contents

- `__init__.py`
- `helpers.py`

## Public Interface

- `helpers.py:validate_spatial_scope` (function)
- `helpers.py:validate_stakeholder_groups` (function)
- `helpers.py:validate_decision_domains` (function)
- `helpers.py:calculate_collaboration_potential` (function)
- `helpers.py:calculate_power_concentration` (function)
- `helpers.py:extract_governance_metrics` (function)
- `helpers.py:generate_governance_report` (function)
- `helpers.py:format_governance_output` (function)
- `helpers.py:merge_governance_structures` (function)
- `helpers.py:validate_ostrom_principles` (function)
- `helpers.py:calculate_governance_health_score` (function)

## Module Metadata

- Module: `GEO-INFER-METAGOV`
- Package: `geo_infer_metagov`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-METAGOV`
- Tests: `uv run python GEO-INFER-TEST/run_unified_tests.py --module METAGOV`

## Dependencies

- `numpy>=1.20`
- `pyyaml>=6.0`
- `typing_extensions>=4.0`

## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module METAGOV
```

## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
