# GEO-INFER open work ledger

> Last reviewed: 2026-08-03 (GeoLibre integration pass)
> Scope: the 44-module workspace rooted at this repository.

This is the canonical open-only ledger. Completed historical work is represented
by code, tests, validators, and receipts; it is deliberately not relisted as
unfinished work here.

## Completed (2026-07-31)

- **VIZ-01**: Deterministic visualization receipts — shared
  `write_visualization_receipt()` helper in SPACE with 8 unit tests. ACT
  orchestrator, Cascadia reporting engine, and Del Norte dashboard all produce
  `.manifest.json` sidecars with input hashes, H3 version metadata, artifact
  checks, and accessibility checks.
- **SIM-01**: MesaModelBridge wraps `mesa.Model` through the SimulationEngine
  interface (20 tests). Mesa is an optional dependency (HAS_MESA flag, graceful
  import path). Supports initialize/step/run/cancel/export_results/save_checkpoint.
- **DOMAIN-01**: 57 behavior-based acceptance tests across COG (16), SEC (36),
  OPS (8), and ENERGY (5) — covering documented feature scopes that previously
  lacked focused probes.
- **SPACE-01**: Hard-coded CWD-relative `config/target_areas.geojson` path in
  `UnifiedH3Backend._get_geometries` routed through a configurable
  `geojson_path` constructor parameter. 3 focused tests added
  (`test_unified_backend_geojson_seam.py`).

## Completed (2026-08-03 — GeoLibre integration)

- **GEOLIBRE-01**: `.geolibre.json` project writer in
  `geo_infer_space.core.geolibre_projects` — deterministic, schema-versioned
  (v0.1.0) emission with GeoJSON/tile layer builders and styled H3 grid export.
  13 unit tests (`test_geolibre_projects.py`); runnable example
  `GEO-INFER-EXAMPLES/examples/getting_started/geolibre_export/` verified to emit
  a valid project. No JavaScript added to the repo.
- **GEOLIBRE-02**: H3 resolution policy in `geo_infer_space.core.h3_policy` —
  `suggest_h3_resolution`, `check_cell_budget` (hard 200k cap), and
  `suggest_resolution_with_budget`. 13 unit tests (`test_h3_policy.py`).
- **GEOLIBRE-03**: Processing algorithm registry in
  `geo_infer_space.core.algorithm_registry` — GeoLibre-style
  `ProcessingAlgorithm`/`AlgorithmRegistry` with reference algorithms. 12 unit
  tests (`test_algorithm_registry.py`).
- **GEOLIBRE-04**: Optional WhiteboxTools bridge in
  `geo_infer_space.core.whitebox_bridge` — graceful `HAS_WHITEBOX` probe and
  `flow_accumulation` terrain helper. 5 unit tests (`test_whitebox_bridge.py`).
- **GEOLIBRE-05**: DuckDB-Spatial readers in `geo_infer_data.utils.duckdb_spatial`
  — GeoParquet/FlatGeobuf/Shapefile with transparent GeoPandas/Fiona fallback.
  5 unit tests (`test_duckdb_spatial.py`).
- **GEOLIBRE-06**: LLM proxy policy in `geo_infer_agent.core.llm_proxy` —
  model allowlist, size caps, output-token cap, and per-client rate limiting.
  12 unit tests (`test_llm_proxy.py`).

## Open items

| ID | Scope | Open work | Behavior-based acceptance probe |
| --- | --- | --- | --- |
| TEST-01 | All modules | Finish the release-quality performance and coverage gates and record their exact output. Coverage run times out at 902s in this environment on 44 modules — the run is **still open** and must not be silently converted to a passing claim. | The release receipt records exact commands, exit codes, test counts, coverage, performance results, and optional backend availability with no skipped or xfailed tests. |
| DOMAIN-02 | SPM/METAGOV/TRANSPORT/EMERGENCY/CIV/REQ/ORG/NORMS | **DONE (2026-07-31):** 85 behavior-based acceptance tests added in `test_acceptance_<mod>.py` for all 8 modules; all verified passing (SPM 30, METAGOV 22, TRANSPORT 21, EMERGENCY 34, CIV 23, REQ 16, ORG 21, NORMS 27). | Each module adds a focused acceptance test file and a current status receipt. |
| DOMAIN-03 | SPACE/MATH/NORMS/ECON/ACT security hardening (2026-07-31) | **DONE:** (a) eval sandbox in SPACE raster: `__builtins__={}` blocks RCE; (b) MATH symbolic eval: `_reject_unsafe_numpy_access` AST guard blocks np file/pickle members; (c) NORMS: two `except Exception: pass` probes now log warnings; (d) ECON: `requests.get` now has `timeout=30`. ART + ACT cross-process determinism covered under REPRO-01 below. | Security repros: `__import__('os')` in SPACE raises NameError; `np.loadtxt` in MATH raises ValueError; ECON request has explicit timeout. |
| REPRO-01 | ART/SPM/BAYES/ACT deterministic seeding (Mahakala V2/V3/F3/F5) | **DONE (ART + SPM + BAYES + ACT PyMC):** ART `random.seed(hash(place_name))` → md5-derived seed (cross-process deterministic, verified 3 procs). SPM `fit_bayesian_glm` + BAYES `PyMCInterface.sample` + ACT `create_pymc_model` now thread `random_seed` into `pm.sample`. **DONE (SPM global-RNG, 2026-08-03):** SPM global-state `np.random.*` calls migrated to a seed-threaded pattern — `generate_coordinates`, `generate_synthetic_data`, `create_spatial_basis_functions`, `compute_power_analysis`, `ModelValidator`, `spatial_basis_functions`, and the empirical-Bayes/hierarchical paths accept `random_seed` and use `default_rng` when provided, preserving the legacy global path by default (8 repro tests in `test_helpers_reproducibility.py`, full SPM suite 353 green). **DONE (BAYES global-RNG, 2026-08-03):** BAYES `ModelComparison.compare_models`/LOO/WAIC/DIC, `sample_spatial_data`, multilevel/hierarchical/GP `posterior_predictive`, and `PyMCInterface.predict` accept `random_seed` and use `default_rng` when provided (5 repro tests in `test_reproducibility.py`, full BAYES suite 182 green). **OPEN:** ~54 bare `np.random.*` sites in RISK catastrophe models remain (largest slice); COG uses are ephemeral timestamped ID generators (low value to migrate). | `PlaceArt.from_place_name('Berlin')` yields identical coords across separate processes; `pm.sample(...)` returns identical traces given `random_seed`; `generate_coordinates('random', random_seed=7)` and `ModelComparison.compare_models(..., random_seed=7)` replay identically. |
| AUTH-01 | SEC token authentication (Mahakala SEC-03, CRITICAL) | **DONE (2026-07-31):** Token auth was 100% broken — sign/validate used different fresh random keys, and the payload's ISO-`.` corrupted the split. Fixed: stable `SecurityConfig.token_secret`/`GEO_INFER_TOKEN_SECRET` key + separate urlsafe-base64 payload/signature joined on `.`. Verified round-trip + tamper-reject. | `SecurityUtils().validate_token(generate_secure_token('alice'))` returns `'alice'`; a tampered token returns `None`. |
| SEC-02b | DATA storage glob/pickle (Mahakala SEC-11/SEC-02) | **DONE (glob):** `_find_data_file` now rejects `*?[]/\\\\` in `data_id`. **DONE (pickle, 2026-08-03):** storage (`core/storage.py`) and caching (`utils/caching.py`) module docstrings now document the pickle-load trust boundary — only deserialise pickles written by the repository's own layers, and require an independent integrity check for any untrusted payload. | `_find_data_file('*')` raises ValueError; untrusted `data_id` cannot widen the glob; storage/caching docs state 'load only trusted pickles'. |
| STATS-02 | BAYES 'PSIS-LOO' overclaim (Mahakala Wave 2/4) | **DONE (2026-07-31):** `_loo_comparison` now implements true PSIS-LOO (Vehtari et al. 2017) via `arviz.stats.stats.psislw` with the exact arviz `loo` formulas — verified to match `az.loo` on a synthetic InferenceData to 1e-6 (elpd, p_loo, se, pareto-k). Output gains `method` and `pareto_k_max` keys; naive log-mean-exp remains only as an arviz-unavailable fallback labelled `naive-loo`. 4 contract tests added (`test_psis_loo_contract.py`). | `_loo_comparison` matches `az.loo` exactly on a well-behaved matrix; `method == 'psis-loo'`; `pareto_k_max` finite. |
| STATS-04 | RISK `calculate_aal` divides total loss by event count, not exposure years (risk_metrics.py:45-49) | **DONE (2026-07-31):** Added `exposure_years` parameter — AAL = total loss / exposure years when provided; legacy event-count semantics retained with an explicit logger warning. Zero/negative exposure_years rejected. 4 regression tests (`test_aal_exposure_years.py`). | `calculate_aal(df, exposure_years=2.0)` returns total/2; legacy path warns and documents the over-estimation. |

## Scoped improvements (review findings, 2026-07-31)

### Major (next release blocking)

1. **SEC-01 — Unsafe YAML/deserialization**: `tarfile.extractall()` Tar Slip **FIXED** (safe-extract guards + 5 tests, commit 0952926b); `eval()` sandbox **FIXED** (SPACE `__builtins__={}`, MATH AST guard). YAML audit found **all** loads already `safe_load` — no change. **OPEN:** pickle model/cache loads (AG/AI/DATA/GIT/OPS) have no trust-boundary guard — document "only load trusted pickles."
2. **TEST-01 coverage receipt** (still open — coverage run times out at 902s).
3. **DOMAIN-02 acceptance tests** (DONE — 85 tests).
4. **STATS-01 — RFT cluster p-values mathematically invalid** (`cluster_p = E[K>u]/cluster_size`, rft.py:339-342): **DONE (2026-07-31)** — replaced with the valid RFT family-wise correction: FWE P(u) = expected number of excursions of the smooth field above u, via the textbook top-dimensional EC density `R·(4 ln2)^(D/2)·u^(D-1)·e^(-u²/2)/(2π)^((D+1)/2)` (also fixes a double smoothness-division that under-counted excursions). Both `cluster`/`peak` methods now return valid FWE p-values; the cluster block is no longer unconditional. Null-simulation FWER control added (`test_rft_fwe_contract.py`): FPR ≈7% at nominal 5%. **Documented limitation:** first-order RFT approximation (mildly anti-conservative); full Worsley cluster-extent correction remains future work.
5. **STATS-02 — 'PSIS-LOO' is not LOO**: **DONE** — true PSIS-LOO implemented via arviz `psislw`, verified 1e-6 against `az.loo` (commit pending). Naive path retained only as arviz-unavailable fallback.
6. **STATS-03 — AI train/test leakage**: `FeatureEngineer.fit_transform` fits the scaler on the full dataset (feature_engineering.py:177-179) with split happening after. **OPEN — document fit-on-train-only contract or move split before fit_transform.**
7. **STATS-04 — RISK `calculate_aal` divides total loss by event count, not exposure years** (risk_metrics.py:45-49). **DONE** — `exposure_years` parameter + legacy-warning; 4 tests.
8. **STATS-05 — tests assert shapes not statistical validity**: **DONE for LOO + RFT** — LOO has exact arviz-reference equivalence; RFT has known-null FWER control (FPR ≈7% at 5%) and BH-adjusted q-value match vs statsmodels. Remaining: no RFT cluster-extent test (blocked on full Worsley extent correction).

### Medium

1. **ACT unit suite timeout**: **DONE** — 9 heaviest tests marked `@pytest.mark.slow` (removes ~380s). Operator runs `pytest -m "not slow"`.
2. **ART unit suite timeout**: **DONE** — 6 heaviest tests marked `@pytest.mark.slow` (place/style/generative/procedural + style-transfer); default suite now 52 tests / 16s.
3. **HEALTH slow tests in unit category**: **DONE** — `test_large_dataset_performance` marked `@pytest.mark.slow`.
4. **ACT integration test_h3_spatial_model_creation**: **DONE** — root cause was malformed 4-level GeoJSON boundary (native H3 v4 rejects); fixed boundary to valid 3-level Polygon + r=8.
5. **RISK cross-validation is a stub** (V6): `_calibrate_with_cross_validation` returns `calibrated_parameters: {}` — never fits a model (risk_engine.py:752-784). **OPEN — implement real fitting or rename the method to `cross_validate_loss`.**
6. **`Path(__file__)` directory walks break on `pip install`** (V7): OPS/SPACE/PLACE/HEALTH/INTRA resolve config via `Path(__file__).parent...`. **OPEN — use `importlib.resources` or explicit config paths.**

### Minor

1. **`np.random.seed(42)`/298 bare `np.random.*` global-state calls** across SPM, BAYES, RISK, COG — migrate to `np.random.default_rng()` per class. **OPEN — large mechanical refactor.**
2. **PyMC `random_seed`**: **DONE** — threaded through SPM `fit_bayesian_glm`, BAYES `PyMCInterface.sample`, ACT `create_pymc_model`.
3. **`config/outputs/` CWD-relative path references** in DATA connectors, IOT ingestion, and SPACE — route through config parameter or `Path` injection. SPACE geojson seam **DONE**; others **OPEN**.
4. **SRAI `except: pass` pattern** in h3_adapter.py:84-85 — legitimate fallback; keep.
5. **Cross-process hash non-determinism**: **DONE for ART** (`hash(place_name)` → md5-seeded, verified cross-process deterministic). AUDIT other `hash()` uses as cache/join keys — OPEN.
6. **ECON `requests.get` no timeout**: **DONE** — `timeout=30`.
7. **NORMS `except Exception: pass` probes**: **DONE** — both increase/decrease probes now log warnings.
8. **COMMS email providers swallow exceptions** (V11): SendGrid/SES `except ... return False` with no typed error. **OPEN — raise typed exception or return structured error.**
9. **FDR correction is threshold-only, not BH-adjusted p-values** (rft.py:392-408): **DONE** — proper Benjamini-Hochberg adjusted q-values (monotone, verified against `statsmodels`).
10. **PLACE `os.chdir()` in tests** (V13): **OPEN — use `monkeypatch.chdir()`.**

## Release gate commands

Run from the repository root with a task-specific cache if needed:

```bash
set -o pipefail
UV_CACHE_DIR=/tmp/geo-infer-uv-cache uv sync --locked --all-packages
UV_CACHE_DIR=/tmp/geo-infer-uv-cache uv run python GEO-INFER-TEST/rewrite_readme_agents.py --check
UV_CACHE_DIR=/tmp/geo-infer-uv-cache uv run python GEO-INFER-TEST/validate_repo_contracts.py --strict-source-language --skip-import-smoke
UV_CACHE_DIR=/tmp/geo-infer-uv-cache uv run python GEO-INFER-TEST/validate_test_contracts.py --strict
UV_CACHE_DIR=/tmp/geo-infer-uv-cache uv run python GEO-INFER-TEST/validate_documentation.py --strict
UV_CACHE_DIR=/tmp/geo-infer-uv-cache uv run python GEO-INFER-TEST/validate_skills.py --check-xrefs
UV_CACHE_DIR=/tmp/geo-infer-uv-cache uv run python GEO-INFER-TEST/validate_h3_active_inference_contract.py
UV_CACHE_DIR=/tmp/geo-infer-uv-cache uv run python GEO-INFER-TEST/run_unified_tests.py --category unit
UV_CACHE_DIR=/tmp/geo-infer-uv-cache uv run python GEO-INFER-TEST/run_unified_tests.py --category integration
UV_CACHE_DIR=/tmp/geo-infer-uv-cache uv run python GEO-INFER-TEST/run_unified_tests.py --category system
UV_CACHE_DIR=/tmp/geo-infer-uv-cache uv run python GEO-INFER-TEST/run_unified_tests.py --category performance
UV_CACHE_DIR=/tmp/geo-infer-uv-cache uv run python GEO-INFER-TEST/run_unified_tests.py --category coverage --timeout 900
git diff --check
```

Optional integrations such as SRAI, external data services, and GPU execution
must be reported separately with their prerequisite and observed result.

Note: `validate_repo_contracts.py` with `--strict-source-language` has been
observed to time out in this environment. The other gates (test contracts, H3
contracts, documentation, skills xrefs, and the unified test suites) pass
cleanly. The full-fleet coverage run consistently times out at 902s — this
**remains open** and must not be converted to a passing claim without a
clean run.

## Documentation deep-review pass (2026-08-02)

Findings from the 2026-08-02 docs-deep pass. Log: `REVIEW_LOG_2026-08-02.md`.

### Major

1. **DOCS-01 — Newline-collapsed markdown (148 files)** — a formatting
   corruption committed across the INTRA docs hub (117 files), EXAMPLES docs,
   MATH docs, SPACE docs, NORMS, OPS, PLACE, METAGOV, and INTRA templates:
   every newline stripped, so headings/lists/tables/fences render as one
   paragraph. Mechanical reflow restored block structure with content
   preserved byte-for-byte. ✓ COMPLETED (4b0b436e, 61991e33).
2. **DOCS-02 — Broken internal links (211 findings, 16 files)** — hub pages
   linked to sibling pages that were never created (`advanced/index.md` 32,
   `tutorials/index.md` 29, `h3_readme.md` 15, `geospatial/*/index.md` 36,
   `knowledge_base/*` 18, `workflows/index.md` 9, `user_guide/index.md` 7,
   `ontology/index.md` 7, `module_readme_template.md` 8,
   `architecture/overview.md` 4, `h3/ecosystem.md` 1). Retargeted to real
   pages or de-linked; no dead links remain in scanned docs. ✓ COMPLETED
   (045585e4, 681db68f).
3. **DOCS-03 — Fabricated external URLs (14 files)** — `geo-infer.org`,
   `forum.geo-infer.org`, `api.geo-infer.org`, `discord.gg/geo-infer`, and
   `github.com/ActiveInferenceInstitute/GEO-INFER` (wrong org). Replaced with the real
   remote (`github.com/ActiveInferenceInstitute/GEO-INFER`) or removed. ✓
   COMPLETED (4b0b436e).
4. **DOCS-04 — Stale documentation artifacts** — `DOCUMENTATION_IMPROVEMENTS.md`,
   `DOCUMENTATION_IMPROVEMENTS_SUMMARY.md`, `DOCUMENTATION_STANDARDS.md` were
   single-line, referenced pages that never existed, and prescribed conventions
   the repo does not use. Rewritten to current repo state. ✓ COMPLETED
   (045585e4).

### Medium

5. **DOCS-05 — Link-only hub pages rewritten with grounded pointers** —
   `tutorials/index.md`, `geospatial/analysis/index.md`,
   `geospatial/case_studies/index.md`, `geospatial/standards/index.md`,
   `knowledge_base/index.md`, `knowledge_base/best_practices/index.md`,
   `workflows/index.md`, `user_guide/index.md`, `ontology/index.md`,
   `geospatial/algorithms/index.md`. ✓ COMPLETED (045585e4).
6. **DOCS-06 — `module_readme_template.md` wrong relative paths** —
   `../GEO-INFER-INTRA/docs/*` and `../LICENSE` corrected. ✓ COMPLETED
   (045585e4).
7. **DOCS-07 — Stale anchors** — `geospatial/algorithms/index.md` anchors into
   `spatial_indexing.md`; `support/faq.md` anchor into `support/index.md`.
   ✓ COMPLETED (045585e4).

### Minor

8. **DOCS-08 — `architecture/overview.md` dead image and page links** — image
   reference removed (no such image exists in the repo), links retargeted.
   ✓ COMPLETED (045585e4).
9. **DOCS-09 — srai_full_reference.md provenance** — vendored 1.4 MB snapshot
   of upstream `kraina-ai/srai`; added a provenance header explaining its
   upstream-relative links. Full re-link of its ~45 internal links **DEFERRED**
   (would require verifying paths against the upstream repo; the file is a
   reference snapshot, not navigation).
10. **DOCS-10 — historical assessment artifacts** — `*assessment_results*`
    single-line dumps left untouched as historical records (not user-facing
    navigation). **DEFERRED** by policy; see README "Artifact and Output
    Hygiene".

8. **DOCS-08 updated (2026-08-02 second pass)** — beyond the image/link
   fix, `architecture/overview.md` was rewritten to describe the real
   repository architecture (module layers, validators, docs hub) instead of
   an aspirational service stack. ✓ COMPLETED (045585e4).
9. **DOCS-09 — srai_full_reference.md upstream re-link** — all 45 relative
   links rewritten to upstream `kraina-ai/srai` GitHub URLs by parsing the
   snapshot's embedded directory tree (237 entries). ✓ COMPLETED.
10. **DOCS-10 — assessment_results archival** — the 22 single-line historical
    dumps were reflowed for readability (content preserved) and remain
    clearly dated historical records. ✓ COMPLETED (reflow).
11. **DOCS-11 — Newline-collapsed code fences** — 117+ files had inline code
    fences (```` ```lang ... ``` ```` on one line) that never close under
    CommonMark; a fence-restoration pass split them onto their own lines and
    repaired dangling opens. The 24 residual files were subsequently repaired
    with a conservative state-machine pass; literal prose that mentions fence
    syntax remains intentionally inline. ✓ COMPLETED.
12. **DOCS-12 — Fabricated statistics and API claims** — MATH tutorial
    contained fabricated outputs (Moran's I 0.6892 vs measured 0.8078) and a
    fake readthedocs URL; rewritten with outputs verified by running the code.
    `docs/examples/*` how-to pages used non-existent APIs
    (`EnvironmentalMonitoringModel`, `SpatialAnalyzer`) with fabricated
    results ("95% accuracy"); all six pages gained an illustrative-guide
    banner and fabricated result metrics were removed. EXAMPLES historical
    analysis docs (9) gained dated-provenance banners. ✓ COMPLETED.
13. **DOCS-13 — Private local paths scrubbed** — removed personal machine
    paths from HANDOFF_2026-07-31.md, a `.cursorrules` plan artifact, 8
    committed ACT output reports, and a PLACE integration test (now
    env-var driven). ✓ COMPLETED.
14. **DOCS-14 — Stale environment claims** — Python 3.8/3.9/3.10 references in
    ANT/CIV/EDU/EMERGENCY/EXAMPLES docs and INTRA installation/environment/
    documentation-guide pages corrected to the 3.11+ workspace target;
    `user_guide/installation.md` and `geospatial/getting_started/index.md`
    rewritten (they described a non-existent PyPI package, CLI, and web app).
    ✓ COMPLETED.

### Open / deferred summary

- EXAMPLES assessment-era docs: preserved as historical records with
  provenance banners (policy question on full removal stays open).
- External URL audit: 561 unique URLs checked. Repository-owned and concrete
  dead links were repaired; upstream citations and sites that reject automated
  requests (403) remain as citations and are not treated as repository link
  failures.
- TEST-01, STATS-03, RISK cross-validation, `Path(__file__)` config walks,
  `np.random` refactor, COMMS exceptions, PLACE `os.chdir()`: unchanged code
  items from the 2026-07-31 pass — still open above.