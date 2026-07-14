# GEO-INFER-SPACE

H3 v4 spatial indexing and comprehensive geospatial analysis framework with advanced spatial methods and coordinate transformations.

## Contents

- `.pytest_cache/`
- `docs/`
- `examples/`
- `output/`
- `reports/`
- `scripts/`
- `src/`
- `test_output/`
- `tests/`
- `demo_all_methods.py`
- `verify_installation.py`
- `.cursorrules`
- `SKILL.md`
- `pyproject.toml`
- `requirements.txt`
- `uv.lock`

## Public Interface

- `demo_all_methods.py:success` (function)
- `demo_all_methods.py:info` (function)
- `demo_all_methods.py:section` (function)
- `verify_installation.py:verify_h3_backend` (function)
- `verify_installation.py:verify_srai_backend` (function)
- `verify_installation.py:verify_dispatcher` (function)

## Module Metadata

- Module: `GEO-INFER-SPACE`
- Package: `geo_infer_space`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-SPACE`
- Tests: `uv run python GEO-INFER-TEST/run_unified_tests.py --module SPACE`

## Dependencies

- `fastapi>=0.68.0`
- `fiona>=1.8.0`
- `geojson-pydantic>=0.4.0`
- `geopandas>=0.10.0`
- `h3>=4.5.0,<5`
- `networkx>=2.6.0`
- `numpy>=1.20.0,<2.0`
- `pandas>=1.3.0`
- `pydantic>=1.8.0`
- `pyproj>=3.3.0`
- `python-multipart>=0.0.5`
- `pyyaml>=6.0`


## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module SPACE
```


## Implemented Nested H3 Contracts

- `geo_infer_space.nested.NestedH3Grid` builds real `h3>=4.5.0,<5`
  hierarchies from seed cells or boundary vertices across ordered resolutions.
- Hierarchy outputs include deterministic `parent_child_map`,
  `child_parent_map`, `same_level_neighbors`, level summaries, validation
  diagnostics, and finite child-to-parent aggregation.
- Validation rejects invalid H3 cells, unordered resolutions, orphan children,
  wrong-resolution children, and parent/child mismatches.

```python
from geo_infer_space.nested import NestedH3Grid

grid = NestedH3Grid("sf_nested")
hierarchy = grid.build_h3_hierarchy_from_cells(
    ["89283082803ffff"],
    resolutions=[7, 8, 9],
)
assert hierarchy["validation"]["is_valid"]
assert hierarchy["validation"]["orphan_count"] == 0
```

Nested validation command:

```bash
uv run pytest GEO-INFER-SPACE/tests/unit/test_nested_h3_contract.py -q
uv run python GEO-INFER-TEST/validate_h3_active_inference_contract.py
```

## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
