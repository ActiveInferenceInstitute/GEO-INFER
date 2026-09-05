# Lower Smith River expanded selection

USGS NHDPlus HR NetworkNHDFlowline layer 3, retrieved 2026-09-05 UTC. Selection:
HUC8 `18010101` intersecting WGS84 `[-124.22,41.88,-124.16,41.96]`. Budgets:
2000 features, 16 MiB, 100 features/page, 180 seconds total request processing
with 45-second inactivity timeout. The selection returned 59 whole reaches in
one page, 209523 bytes in the final GeoJSON. This is an envelope excerpt, not
whole-watershed coverage. Native fields, IDs and complete intersecting geometry
are retained; nothing was invented or clipped into inferred outlets.

`manifest.json` contains the ID snapshot, source query, CRS and page/final
checksums. Repeating the identical acquisition reused the page and reproduced
identical GeoJSON hashes. `verification.json` records that check and full
topology: 59 edges, 61 nodes, two components, no cycles or known stream-order
decreases; three stream orders are unknown. Two boundary outlets are not
asserted to be basin outlets.

Source: [USGS service](https://hydro.nationalmap.gov/arcgis/rest/services/NHDPlus_HR/MapServer/3).
USGS-authored data are public domain; retain source attribution and the source
metadata when redistributing. The loader guide in the parent hydrography package
contains the executable acquisition API and source consistency limitations.
