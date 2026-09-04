# GEO-INFER Open Task & Backlog Ledger

> Last reviewed: 2026-09-04
> Scope: Multi-package repository (`GEO-INFER`) across workspace packages and 44 domain modules.
> Centralization Rule: All planned, open, or deferred engineering work across all modules is tracked exclusively in this ledger. Module source code and tests must never carry local task markers (`TODO`, `FIXME`, `XXX`, `HACK`).

---

## Open work and acceptance criteria

Completed implementation and deferred verification are tracked separately below.
Module names identify the responsible area, not an assigned person. Acquisition
items require an explicit area, source and resource budget before running them;
this ledger does not authorize full-region downloads or a package release.

| ID | Area / status | Bounded next step | Acceptance evidence / dependencies |
| --- | --- | --- | --- |
| **SPACE-01** | SPACE / deferred hardware verification | On supported physical hardware, run numeric distance and grouped-reduction parity for each backend claimed as supported (CuPy, Torch, JAX), including empty inputs, float64 precision, chunk boundaries and allocation failure. Keep H3 topology labeled as host CPU. | Record device/driver/library versions, actual backend diagnostics, CPU-reference tolerances, peak memory and separate cold/warm timings. Publish speed claims only for measured workloads; do not infer support from CPU fallback. Requires hardware. [Guide](GEO-INFER-SPACE/docs/GPU_ACCELERATION.md). |
| **DOCS-01** | INTRA / deferred browser verification | With a connected Interceptor browser, exercise the 44-preview index and representative module pages: online Leaflet map, tile/CDN failure, offline SVG fallback, narrow viewport, keyboard navigation and accessible labels. | Save browser/viewport versions, screenshots and observed interaction results; link/map controls and fallback remain usable, no relevant console errors, and asset receipts still match all 44 bundles. Extend checks to any page-specific failures. |
| **TEST-02** | TEST / deferred Windows verification | Run source and installed-wheel import-probe regressions on Windows, including early zero exits and timed-out imports that spawn a child. | Both validators reject incomplete receipts and nonfinite deadlines; parent and child terminate and cannot perform the delayed write. Record interpreter/OS versions and JUnit results. Fix and rerun if `taskkill /T /F` behaves differently. |
| **CI-01** | Repository / recurring hosted verification | Observe the exact pushed SHA on hosted Python 3.11/3.12 Linux CI; exercise clean wheel verification through the existing nonpublishing workflow when needed. | Required jobs pass for that SHA, with logs/artifacts retained by CI. Local macOS/Linux ARM64 results do not substitute for hosted x86 results. Fix attributable failures before considering this item complete; creating a version tag or external package publication requires a separate release decision. |
| **PLACE-02** | PLACE / future regional acquisition | Select one explicit US Cascadia area/HUC envelope, USGS layer, page/feature/byte/time caps and storage destination; acquire with the delivered resumable loader. Scale beyond that envelope only under a new bounded acquisition plan. | Retain source URL/query, retrieval time, CRS, object-ID snapshot, page/final checksums, completeness/empty/failure status and resume evidence. Preserve native IDs, multipart/parallel reaches and topology before filtering. Report coverage gaps; the 34-reach pilot establishes no whole-watershed coverage. [Guide](GEO-INFER-PLACE/src/geo_infer_place/hydrography/GUIDE.md). |
| **PLACE-V14** | PLACE / regional layer acquisition open | Obtain separately sourced `cascadia_bioregion_boundary.geojson`, `cascadia_major_watersheds.geojson`, `cascadia_subduction_zone.geojson` and `cascadia_volcanoes.geojson`. Document boundary interpretation, geographic extent, selection rules and redistribution terms for each. | Validate WGS84, required geometry types, stable feature identifiers, provenance and checksums; run actual-data renderer/integration checks. Keep missing-layer behavior explicit until data exists. Do not restore the former 12-volcano or earthquake-probability claims without evidence. |
| **PERF-01** | TEST / optional import-latency investigation | Reproduce native ART/pandas import latency in a clean macOS environment with installation and import times separated; compare default and hardlink installs under controlled cache/load conditions. | Retain native stacks, dependency/OS versions and repeated cold/warm timings. Investigate the observed 120-second timeouts without weakening OS validation or relabeling the successful 600-second correctness bound as a performance fix. No current import-speed guarantee. |
| **CODE-01** | Repository / optional code intelligence | Build a GEO-INFER-specific GitNexus index when the service is available and inspect affected symbol flows against the published change. | Record indexed repository identity and commit SHA; review unexpected callers/flows. Until then, retain direct source/caller inspection as the documented fallback, with reduced code-intelligence confidence. |

## Delivered capabilities

| ID | Area | Completed scope and evidence |
| --- | --- | --- |
| **ARCH-01** | Packaging | All 44 domain wheels have metadata and source/resource inventory checks, clean isolated installation, origin/version/resource probes, bounded process cleanup and completion receipts. Locked Python 3.11/3.12 wheel checks passed on macOS and Linux ARM64; hosted verification is tracked in CI-01. |
| **TIME-01** | TIME | Real WebSocket/Kafka adapters, explicit replay, bounded event-time buffers, watermark/session/sliding windows, anomaly integration and commit-after-processing. Real local WebSocket and Kafka delivery/replay/resume checks passed. [Migration guide](GEO-INFER-TIME/docs/streaming_migration.md). |
| **PLACE-01** | PLACE | Installable resumable USGS loader and checksummed 34-reach lower Smith River pilot, with native IDs and full topology before filtering. Full-region and missing-layer acquisition are separate PLACE-02/PLACE-V14 work. |
| **SPACE-01 implementation** | SPACE | Lazy device selection, bounded numeric distance joins, float64 CPU references, stable grouping and honest H3 host-topology reporting. Physical-device verification remains SPACE-01 above. |
| **DOCS-01 implementation** | INTRA | All 44 deterministic HTML/SVG/PNG bundles show computed H3 geometry, illustrative-data labels, artifact checksums and offline fallback. Browser interaction remains DOCS-01 above. |

---

## ✅ Completed & Verified Work (Audit Log)

1. **REPRO-01 (Completed)**: Explicit seeds use isolated `np.random.Generator` instances across `GEO-INFER-RISK` (`rng.py`), `GEO-INFER-BAYES` (`rng.py`), `GEO-INFER-MATH` (`rng.py`), and `GEO-INFER-SPM` (`rng.py`); unseeded SPM helpers retain their documented behavior, including the legacy global stream where promised.
2. **PLACE-V14 renderer correction (Completed)**: The renderer requires explicit WGS84 data or reports partial/unavailable layers when requested. Constructed geometry tests and tracked county boundaries verify the pipeline; actual regional acquisition and scientific coverage remain the open PLACE-V14 item above.
3. **SUPPLY-01 (Completed)**: Cleaned all installation references to point to verified editable installs (`uv pip install -e ./GEO-INFER-<MODULE>`).
4. **H3 v4.5 Composition (Completed)**: Implemented end-to-end multi-module composition suite (`test_h3_space_time_bayes_risk_act_composition.py`) connecting H3 spatial grids to `TIME`, `BAYES`, `RISK`, and `ACT`.
5. **BAYES-01 (Completed)**: Added batched inducing-point `SparseSpatialGP` regression with collapsed variational ELBO optimization, finite posterior uncertainty, and a 10,001-observation no-dense-covariance regression test.
6. **RISK-01 (Completed)**: Added directed multi-hazard interaction matrices and engine-level compound exceedance calculation for ordered hazard chains including earthquake to fire-following to flood.
7. **SPM-01 (Completed)**: Added full Gaussian Euler-characteristic inference across all boundary resel dimensions, peak FWE thresholds, topological cluster-extent FWE p-values, closed-form unit contracts, and fixed-seed known-null Monte Carlo calibration for both peak and cluster inference.
8. **SEC-01 (Completed)**: Added authenticated GISP1 HMAC-SHA256 serialization envelopes across `DATA` (`utils/secure_serialization.py`, `caching`, `storage`), `GIT` (`utils/secure_serialization.py`, `advanced_cache`), and `OPS` (`core/secure_serialization.py`, `cache`), with SEC integration coverage (`tests/integration/test_serialization_security.py`); unsigned, truncated, cross-context, and tampered payloads never reach a deserializer.
9. **ACT-01 (Completed)**: Added continuous POMDP Active Inference via a Laplace/Kalman-Bucy filter (`models/continuous_pomdp.py`) bridging discrete categorical and continuous-state Gaussian-filter inference, with free-energy-scored action selection and a focused unit test.
10. **MATH-01 (Completed)**: Added vectorized SIMD ray-casting point-in-polygon (`geometry.points_in_polygon_vectorized`) replacing iterative loops in spatial clustering.
11. **DATA-01 (Completed)**: Added cloud-connector byte-range reading (`connectors/cloud.py` `read_byte_range`) for chunked remote GeoParquet / Cloud-Optimized GeoTIFF access.
12. **TEST-01 (Completed)**: Added the parametric load benchmark harness (`tests/unit/test_parametric_load_benchmarks.py`) to the unified test runner's performance surface.

The [September review ledger](GEO-INFER-TEST/docs/hardening_2026_09.md) records baseline, final checks, API migrations and verification limits.
