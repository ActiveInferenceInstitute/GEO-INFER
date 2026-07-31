# GEO-INFER open work ledger

> Last reviewed: 2026-07-31 (second pass)
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

## Open items

| ID | Scope | Open work | Behavior-based acceptance probe |
| --- | --- | --- | --- |
| TEST-01 | All modules | Finish the release-quality performance and coverage gates and record their exact output. Coverage run times out at 902s in this environment on 44 modules — the run is **still open** and must not be silently converted to a passing claim. | The release receipt records exact commands, exit codes, test counts, coverage, performance results, and optional backend availability with no skipped or xfailed tests. |
| DOMAIN-02 | SPM/METAGOV/TRANSPORT/EMERGENCY/CIV/REQ/ORG/NORMS | Extend the DOMAIN-01 pattern (acceptance tests for claims documented in SKILL.md/AGENTS.md) to remaining modules. Each module needs `test_acceptance_<mod>.py` with real-API, no-mock, behavior-based tests. | Each module adds a focused acceptance test file and a current status receipt. |
| DOMAIN-03 | SPACE (config), SEC (pickle/tar), ACT (integration test), OPS (tarfile) | Security hardening: replace `yaml.load` with `yaml.safe_load`, add safe-extract for tar files, audit `eval`/`exec` uses. | Targeted fix per finding; verified by running the specific module test suite. |

## Scoped improvements (review findings, 2026-07-31)

### Major (next release blocking)

1. **SEC-01 — Unsafe YAML/deserialization**:
   `yaml.load(payload, Loader=yaml.FullLoader)` found in src; `tarfile.extractall()` without path sanitization (Tar Slip); pickle detection. Fix all `yaml.load`, `tarfile.extract*`, and audit `eval()`/`exec()` calls.
2. **TEST-01 coverage receipt** (already above).
3. **DOMAIN-02 acceptance tests** (already above).

### Medium

1. **ACT unit suite timeout**: `run_unified_tests.py --module ACT` times out at 300s+ for the per-module limit. Mark the heaviest tests `@pytest.mark.slow` or raise the per-module timeout to 600s.
2. **ART unit suite timeout**: same timeout issue.
3. **HEALTH slow tests in unit category**: `TestPerformance::test_large_dataset_performance` in `test_disease_surveillance.py` runs a performance test during the unit sweep — add `@pytest.mark.slow`.
4. **Integration test test_h3_spatial_model_creation at r=4**: fixed to r=8 but additionally the function works correctly; the pytest quirk around config-inherited `-W error` needs investigation.
5. **ACT integration test_h3_spatial_model_creation** — resolution fixed, but the pytest environment interaction remains open.
6. **`eval()` in symbolic_math.py**: expression evaluation uses `eval()` — should be constrained or isolated.

### Minor

1. **`np.random.seed(42)`** and `np.random.default_rng(seed=42)` usage across SPM, BAYES, RISK, COG — 90+ bare `np.random.seed` calls without deterministic import-order guarantees.
2. **`PyMC.sample()` missing `random_seed`** in GEO-INFER-BAYES/src/geo_infer_bayes/core/pymc_interface.py:194 — sampler runs non-deterministically.
3. **`config/outputs/` CWD-relative path references** in DATA connectors, IOT ingestion, and SPACE — route through config parameter or `Path` injection.
4. **SRAI `except: pass` pattern** in h3_adapter.py:84-85 (`except Exception:`) is legitimate (fallback to native H3) but the pattern is fragile; add a single-line log.
5. **Cross-process hash non-determinism** — Python's `hash()` differs across interpreter restarts; if used in any cache-key or join path, it corrupts cross-run reproducibility.

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