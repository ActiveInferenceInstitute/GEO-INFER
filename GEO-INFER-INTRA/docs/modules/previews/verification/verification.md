# DOCS-01 Preview Verification Receipt

Generated: 2026-09-08T10:26:55.682Z · Row: DOCS-01 · Schema: geo-infer-docs01-verification/v1

**Environment**: Chromium (headless, Puppeteer) against `http://127.0.0.1:8791`
(python3 http.server over `GEO-INFER-INTRA/docs/modules`). Online dependencies:
Leaflet 1.9.4 from unpkg, tiles from tile.openstreetmap.org.

**Raster note**: `captureScreenshot` is unavailable in the hidden shared headless
browser (CDP capture times out even on about:blank), so the recorded browser/viewport
versions are `printToPDF` captures under `page_versions/`.

## Checks

| Check | Status | Evidence |
| --- | --- | --- |
| all_45_pages_load_no_unexpected_console_errors | PASS | pages: 45; http_200: 45; console_errors_total: 0; unexpected: 0 |
| map_renders_online_representative | PASS | representative: ["ACT","SPACE","WATER"]; leaflet_online: true; map_visible: true; zoom_controls: true; tile_source: "https://tile.openstreetmap.org/" |
| cdn_failure_static_fallback_usable | PASS | method: "CDP Fetch.enable failRequest on unpkg.com and openstreetmap.org, cold-cache incognito context"; cold_cache: {"leaflet_loaded":false,"map_display":"none","static_svg_renderable":true,"h3_polygons_on_act":7,"page_errors":0}; warm_cache_blocked: {"leaflet_loaded":true,"map_visible":true,"note":"graceful - assets served from cache"}; keyboard_toggle_offline: true |
| narrow_viewport_usable | PASS | viewport: "375x667"; no_horizontal_overflow: true; summary_visible: true; svg_visible: true; captured: "act_cold_narrow.pdf" |
| keyboard_navigation_operable | PASS | target: "#static-preview summary"; enter_toggles: true; online toggles: {"openBefore":true,"openAfterEnter":false,"openRestored":true,"toggled":true}; cold_cache_offline: {"openAfterEnter":false,"openRestored":true,"note":"Enter toggled the details closed then restored it while offline (cold cache)"} |
| accessible_labels_present | PASS | map_aria_label: "Interactive H3 geometry"; svg_role_img: true; svg_title_and_desc: true; details_summary: "Static preview (available offline)"; h1_title: true; across_all_45: true |
| asset_receipts_match_45_bundles | PASS | method: "sha256+bytes recomputed from disk against manifests (receipt never trusted)"; artifacts: 180; mismatches: 0 |
| representative_page_versions_saved | PASS | format: "PDF (printToPDF at viewport size)"; note: "raster captureScreenshot is unavailable in the hidden headless browser (CDP captureScreenshot times out even on about:blank); page.pdf works and is the recorded browser/viewport version"; files: ["act_online.pdf","act_cdn_blocked.pdf","act_cold_cache_cdn_blocked.pdf","act_cold_narrow.pdf","geo-infer-space_online.pdf","geo-infer-water_online.pdf"] |
| verification_receipt_present | PASS | receipt: "previews/verification/verification.json"; doc: "previews/verification/verification.md" |

## Key observations

- All 45 pages: HTTP 200, Leaflet online, map rendered, static SVG present, zero console errors.
- Cold-cache CDN failure (unpkg.com + openstreetmap.org blocked at the CDP Fetch layer, incognito context):
  `typeof L === "undefined"`, map container `display:none`, and the always-present
  `details#static-preview` SVG is the usable surface (7 H3 polygons on ACT); zero page errors.
- Keyboard: Enter on the summary toggles the static preview online and offline.
- Narrow viewport 375×667: no horizontal overflow; summary and SVG stay visible.
- Asset receipts: sha256+bytes recomputed from disk against all 45 manifests — 180/180 artifacts match.
- Warm-cache blocked reload still rendered the map from cache (graceful degradation).
