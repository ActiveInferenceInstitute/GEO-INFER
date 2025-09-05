### H3 v4 Migration Guide (SPACE)

This guide summarizes the migration from H3 v3 to v4 within the SPACE module.

#### Key API Changes

- geo_to_h3 → latlng_to_cell
- h3_to_geo → cell_to_latlng
- h3_to_geo_boundary → cell_to_boundary
- k_ring / hex_ring / hex_range → grid_disk / grid_ring / grid_disks_unsafe
- h3_distance → grid_distance
- compact / uncompact → compact_cells / uncompact_cells
- polyfill → polygon_to_cells

Refer to the official migration notes for full details.

#### Migration Tools

Run the automated migration and verification:
```bash
gis-fix-h3-v4
gis-verify-h3-v4
```

#### Notes

- Ensure h3>=4 is installed.
- Review any remaining warnings produced by the verifier for manual fixes.


