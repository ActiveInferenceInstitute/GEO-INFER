# GEO-INFER-NORMS/examples/output

Output workspace within `GEO-INFER-NORMS`.

## Contents

- `historical_zoning_changes.png`
- `zoning_adjacency_network.png`
- `zoning_analysis_results.json`
- `zoning_change_visualization.png`
- `zoning_compatibility_matrix.png`
- `zoning_distribution_by_category.png`
- `zoning_districts.png`
- `zoning_districts_highlight.png`

## Public Interface

- No public Python symbols are defined directly in this directory.

## Module Metadata

- Module: `GEO-INFER-NORMS`
- Package: `geo_infer_norms`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-NORMS`
- Tests: `uv run python GEO-INFER-TEST/run_unified_tests.py --module NORMS`

## Dependencies

- `geopandas>=0.10.0`
- `matplotlib>=3.4.0`
- `networkx>=2.6.0`
- `numpy>=1.20.0`
- `pandas>=1.3.0`
- `shapely>=1.8.0`


## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module NORMS
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
