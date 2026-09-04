# Hydrography

The installed `geo_infer_place.hydrography` package owns USGS NHDPlus HR
acquisition, network topology, high-order views, and H3 surface-water analysis.
The former Cascadia location modules re-export these classes for compatibility.

## Acquire an explicit region

```bash
python -m geo_infer_place.hydrography --pilot --output ./smith-river-data
```

This bounded pilot selects intersecting whole reaches in the lower Smith River
HUC8 `18010101`, envelope `(-124.22, 41.90, -124.18, 41.94)`. It does **not**
represent the complete Smith River watershed. `--huc8 18010101` selects all
reachcodes in that watershed; `--bbox WEST SOUTH EAST NORTH` selects another
explicit envelope. Combining HUC8 and bbox intersects the selections.

US Cascadia acquisition uses `--bbox -124.8 40 -114.5 49`. Large selections may
exceed the default 10,000-feature or 128 MiB limits: partition them or explicitly
set `--max-features` and `--max-bytes` to approved resource budgets. The service
contains US hydrography; this does not provide Canadian Fraser basin coverage.
No full-region download runs by default.

The importer snapshots source object IDs, retrieves bounded pages, preserves all
native source fields, and writes `flowlines.geojson` only after checking every
requested ID. `manifest.json` records source URL, selection, UTC acquisition time,
CRS, object IDs, page checksums, final checksum and `complete`, `empty`, `failed`,
or `incomplete` status. Re-running the same selection reuses verified pages.
Different source/selection/page size requires a different output directory.
Use one writer per output directory. The per-request inactivity timeout is 45 seconds; `max_duration` defaults to
180 seconds and is checked at headers/body-read boundaries. An in-progress
blocking read can add up to the inactivity timeout. Slow body trickles cannot
reset that duration budget. No automatic retry obscures errors; rerun
to resume after connectivity recovers. Corrupted cache pages are rejected.

Membership is frozen at the object-ID snapshot; the live service can change
attributes between requests. Boundary crossings are not inferred basin outlets.
For offline authoritative bulk products and metadata, use the
[USGS distribution documentation](https://www.usgs.gov/national-hydrography/access-national-hydrography-products).
The data source is the official
[NetworkNHDFlowline layer](https://hydro.nationalmap.gov/arcgis/rest/services/NHDPlus_HR/MapServer/3).

## Analyze without checkout-relative imports

```python
from geo_infer_place.hydrography import CascadianSurfaceWaterDataSources

source = CascadianSurfaceWaterDataSources(dataset_path="smith-river-data/flowlines.geojson")
network = source.get_flowline_network(min_stream_order=4)
report = network.full_network_validation
high_order = source.load_pnw_high_order_flowlines(4)
```

`get_flowline_network` retains **all** supplied reaches for upstream/downstream
traversal; `selected_comids` records the high-order selection. Validation runs on
the full graph before the high-order view is generated. Reports expose cycles
and downstream stream-order decreases; review those diagnostics rather than
assuming all source topology is valid. Parallel channels retain distinct IDs.
USGS negative stream-order sentinels become nullable canonical orders while the
original source field is retained. Reports count unknown orders separately.
Native `nhdplusid`, `fromnode`, `tonode`, `streamorde` and `lengthkm` remain in the
loaded frame; canonical aliases are added. The legacy `comid` argument and alias
refer to the native NHDPlusID for HR data, not an NHDPlus V2 COMID.

Provide `flowlines=...` for an existing GeoDataFrame. Missing local datasets,
missing topology attributes, duplicate IDs and failed HTTP queries raise errors.
There is no implicit OSM or constructed-data substitution. `sample_flowlines()`
explicitly loads the bundled 34-reach USGS excerpt with checksum verification;
its provenance is available in `frame.attrs["provenance"]`. It is a test/example
resource, not the default regional dataset.

Inject a source with `GeoInferSurfaceWater(backend, data_source=source)`. The
network-flowline source does not query waterbodies; analysis reports
`water_body_area_sqkm=None` for that unknown measurement. Empty target grids do
not trigger a regional download. The H3 network index samples coordinates and
midpoints and apportions source lengths among sampled cells; it is an approximate
index, not an exact line-cell intersection measurement. `run_analysis` performs
actual geometry overlay for its requested cells.

## Migration and verification

Replace `src.data_modules.surface_water...` imports and `sys.path` edits with
`geo_infer_place.hydrography`. Default graph access now requires explicit input.
Keep topology data unfiltered; use a high-order view for display.

```bash
python -m pytest GEO-INFER-PLACE/tests/unit/test_cascadia_flowlines.py GEO-INFER-PLACE/tests/unit/test_hydrography_ingestion.py GEO-INFER-PLACE/tests/integration/test_cascadia_hydrography.py
```

These tests exercise real loopback HTTP failures/resumption, corruption,
resource limits, native ID preservation, explicit constructed topology,
parallel reaches, real H3 overlay and the bundled measured excerpt.


## Deployment compatibility controls

`GEO_INFER_CASCADIA_FLOWLINES_PATH` supplies a local dataset when neither
`dataset_path` nor `flowlines` is passed explicitly. Explicit arguments take
precedence. A nonempty `GEO_INFER_SURFACE_WATER_OFFLINE` enables local-only
access; `offline=True` also selects it explicitly. Offline requests read supplied
flowlines or the matching completed, checksummed ingestion cache. Missing or
incomplete local data raises an error and never initiates a network request.

`GeoInferSurfaceWater(..., allow_projection_fallback=True)` explicitly permits
writing unbuffered raw flowlines if their buffering projection fails. The
`projection_degraded` instance flag and output column report that condition;
the default raises the projection error. This retains the upstream degraded-output
capability while keeping strict processing as the normal behavior. Invalid
summary input still raises rather than being replaced by zero-valued measurements.
