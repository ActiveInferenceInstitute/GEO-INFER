# H3 v4.5 migration guide

GEO-INFER-SPACE supports the `h3-py` range `>=4.5.0,<5`; the workspace lock
currently resolves `4.5.0`. The migration is complete for runtime surfaces.

## Required calls

- `latlng_to_cell` converts latitude/longitude to a cell.
- `cell_to_latlng` returns a cell center.
- `cell_to_boundary` returns native `(latitude, longitude)` vertices.
- `grid_disk` and `grid_ring` replace older neighborhood spellings.
- `cell_to_parent`, `cell_to_children`, `compact_cells`, and
  `uncompact_cells` provide hierarchy operations.
- `geo_to_cells` consumes GeoJSON `[longitude, latitude]` geometry.

Do not pass removed boundary-format keywords. Convert explicitly at the
GeoJSON or visualization boundary and close polygon rings.

```bash
uv run python GEO-INFER-TEST/validate_h3_active_inference_contract.py
uv run pytest GEO-INFER-SPACE/tests/unit/test_h3_operations_runtime.py -q --no-cov
```
