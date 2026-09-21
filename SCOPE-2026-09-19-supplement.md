> Provenance (2026-09-20): the file below is the hp geo-infer coordinator's
> independent 88-item scoping spec (its own parallel read-only pass over the
> same tree), preserved verbatim after the acting coordinator restored the
> committed main spec. Evidence store for the addendum pointer in
> SCOPE-2026-09-19.md; items indexed GS19-NN; overlap mapping in the main
> spec's addendum section.

# SCOPE-2026-09-19 — GEO-INFER full-fleet scoping pass (14 lanes, 88 items)

> Produced 2026-09-20 by a read-only 14-lane scout swarm against
> `main @ 07a5fe3154e192ccb3986dbf17e041a4efc1539b` (v0.3.0 tip,
> `main == origin/main`). Spec-only: no implementation is authorized; items
> enter execution only on an explicit go. This pass sweeps the tree at
> v0.3.0 — three events after the 2026-09-11 full campaign (189/189), the
> 2026-09-15 docs pass, and the 2026-09-17 v0.3.0 release — so every item
> below is fresh evidence, not re-opened campaign work.

## Method

14 read-only scout lanes in one parallel batch: 5 package-level lenses
(ci-gates, packaging, docs-truth, test-estate, pipeline-perf-sec) + 9 module
batches covering all 45 modules. Lane contract: READ-ONLY, no
suites/formatters (probes prescribed, one <60s pytest allowed), `uv run
--no-sync` only, never grep `__pycache__`/`*.pyc`, 3–8 items per lane, tier
rubric = the ledger's own (Major = external/release-scale, Medium = self-serve
multi-session, Minor = bounded single-session), every item carries
Motivation/Evidence (file:line)/Bounded next step/Acceptance probe/Effort.
Raw lane yield 92 items → 88 after cross-lane dedupe (the api_schema.yaml
fabrication family was folded; see GS19-20).

## Ledger disposition

- **REL-01 — CORRECTED AND ESCALATED.** The row's residual ("go/no-go on the
  post-tag delta") is stale: **the v0.3.0 release itself failed.**
  `release.yml` run 35274969824 aborted at job `ci-gate` ("Wait for CI success
  on the tagged commit", exit 1); the `release` job was skipped (0s) — **zero
  wheel artifacts exist for v0.3.0**. Root cause verified by the ci-gates
  lane: tag-push `ci.yml` run 35274969748 FAILED at step "Enforce module
  coverage floors" (validate job 105383245674, 21:15:29→21:36:29Z) while the
  identical tree PASSED the same step on main (run 35268910816,
  20:14:55→20:34:13Z). Mechanism = GS19-01. Recovery path: re-run the failed
  validate job (attempt 2), then re-run release.yml's ci-gate so run
  35274969824 completes — an authorized `gh` action for the owner; the
  durable fix is GS19-01. Recommend updating the REL-01 row with these
  receipts when the next ledger edit lands.
- **v0.2.1 context:** released successfully (run 35053351237, 2026-09-16)
  after one failed attempt (35051345070) — the flake pattern has now bitten
  releases twice in three tags.
- **CODE-01:** unchanged (index staleness is the row's own cadence; counts
  confirmed at 67453/97164, not re-filed).
- **SPACE-01, PLACE-V14, PLACE-04, TEST-GNN-01, TEST-04:** verified still
  open on their recorded external blockers (hardware, licensed data, Windows
  runtime, I/O-cause investigation, advisor auth). PLACE fail-closed chain
  re-verified intact (regional_layers.py / _regional_download_worker.py /
  hydrography manifests vs docs/usgs_regional_layers.md).

## Premise corrections (facts that changed vs earlier passes)

- `validate_test_contracts.py:31` DOES cover root `tests/` — the "root tests/
  blind spot" is fixed; residual asymmetry is only the tests/README.md
  inventory rule (module tests only).
- `measure_module_coverage.py` COVERAGE_FILE isolation verified PRESENT and
  correct (per-module tempdir at :106-112) — playbook trap closed.
- The repo-wide static scan found the only banned pytest.skip sites in the
  tree are the 9 cascadia integration lines (GS19-06); all validator-visible
  markers are registered.

## Exclusions

- DOCS-03 banner-covered historical docs (EXAMPLES INTEGRATION_GUIDE.md,
  assessment_results/*.md, etc.) are deliberately excluded — bannered, not
  truth-passed.
- Local noise observed, untouched: tracked-and-modified `*.pyc` under
  GEO-INFER-PLACE (filed as GS19-27); `manuscript/config.yaml` uncommitted
  hunk captured and dispositioned (GS19-33 — keep).
- Not executed in-lane (probes prescribed): `uv lock --check`
  (GS19-04 acceptance), the rename pre-image probe inside GS19-03
  ([INFERENCE] flagged).

## Major — external resources or release-scale decisions

**GS19-01 · MAJOR · CI/RELEASE · v0.3.0 wheel release is broken: tag-push coverage-floor flake blocked all artifacts** (Lane: ci-gates)
- Motivation: v0.3.0 shipped with NO wheel artifacts. Every release tag push plays a ~20-minute 45-module flake lottery: the release commit bumps `__version__` in all 45 modules' `__init__.py`, so `check_coverage_floor._changed_modules` marks every module changed and re-measures the entire fleet under xdist with `filterwarnings=['error']`; a single flake/warning in ANY module yields pytest rc=1 → FAILED-SUITE → gate exit 1. `release.yml`'s ci-gate then fails closed on the first failed read.
- Evidence: `.github/workflows/ci.yml:148-165` (BASE_SHA resolution: on tag push `event.before` is the zero SHA → fallback to tag commit's parent); run 35274969748 tag validate job step 13 FAILED vs run 35268910816 main same step PASSED (same tree, ~1h apart, both ~20 min = full-fleet measurement); `GEO-INFER-TEST/check_coverage_floor.py:43-56` (pathspecs mark all 45 modules on version-bump commits), `:120-135` (rc=1 → FAILED-SUITE); `.github/workflows/release.yml:44-64` (ci-gate polls newest run per SHA, `--limit 1`).
- Bounded next step: (1) recover the release — re-run validate job 105383245674 attempt 2; when green, re-run release.yml ci-gate so run 35274969824 completes and uploads v0.3.0 wheels (owner-authorized `gh` action, not lane work); (2) durable fix — filter per-file hunks in `_changed_modules` so `__version__`-only src changes do not re-measure a module, and add one bounded retry of a FAILED-SUITE measurement before failing the gate.
- Acceptance probe: `gh run list --workflow ci.yml --commit 07a5fe3154e192ccb3986dbf17e041a4efc1539b --limit 5 && gh release view v0.3.0 --json assets --jq '.assets | length'` — post-fix: assets > 0.
- Effort: L

## Medium — self-serve, multi-session

**GS19-02 · MEDIUM · CI/DOCS · Generated signposts document weaker validator flags than CI — regen locks in the drift** (Lane: ci-gates)
- Motivation: Developers following AGENTS/README signposts run gates strictly weaker than CI (`validate_repo_contracts.py --strict-source-language` missing `--strict-import-smoke`; `validate_skills.py --check-xrefs` missing `--warnings-fatal`), so import-smoke and cross-reference failures that block CI pass silently locally. Root cause: the generator's embedded templates hardcode the weaker flags and `--check` actively reverts hand-fixes.
- Evidence: `ci.yml:104-111`; `AGENTS.md:37,40`; `CLAUDE.md:55`; `README.md:43-46`; `rewrite_readme_agents.py:852,917-920,1013-1016`; `test_ci_workflow_contracts.py:39-60` (pins markers, not documented flags).
- Bounded next step: update the embedded command blocks in rewrite_readme_agents.py to mirror ci.yml exactly; extend test_ci_workflow_contracts.py to assert generated signposts carry the CI strict flags.
- Acceptance probe: `uv run python GEO-INFER-TEST/rewrite_readme_agents.py && grep -n 'validate_skills.py --check-xrefs --warnings-fatal' AGENTS.md README.md GEO-INFER-TEST/AGENTS.md`
- Effort: S

**GS19-03 · MEDIUM · CI/LINT · Ruff gate surfaces have structural blind spots** (Lane: ci-gates)
- Motivation: All four ruff surfaces are real, but: format is enforced ONLY on the changed set (no repo-wide check; stale `[tool.black]` config at pyproject.toml:295-307 describes a formatter CI never runs); F401/F841/F811 cover only `GEO-INFER-*/tests` — root tests/, examples/, GEO-INFER-TEST top-level scripts, scripts/, manuscript/ get no dead-import policing; F823/E721/E722 missing from the tests surface; the diff-scoped gate can fail on rename pre-images ([INFERENCE — probe below]); `tests_lint_metric.py:33-35` duplicates the tests-lint contract as a second hard-coded copy.
- Evidence: `ci.yml:79-81,92-96,125-131`; `tests_lint_metric.py:33-35,51-57`; `pyproject.toml:295-307`.
- Bounded next step: add `--no-renames` to both git diff invocations; extend the tests surface to root `tests/` + add F823; add a periodic repo-wide `ruff format --check`; share the rule set between tests_lint_metric.py and ci.yml via one constant.
- Acceptance probe: the rename probe in the lane report (`git diff --name-only -z --diff-filter=ACMRTUXB` over a synthetic rename must not feed a nonexistent path to ruff).
- Effort: M

**GS19-04 · MEDIUM · PACKAGING · Stale standalone uv.locks inside workspace members shadow the canonical lock** (Lane: packaging)
- Motivation: GEO-INFER-ACT/uv.lock (0.2.0, 4167 lines, py≤3.13 markers) and GEO-INFER-SPACE/uv.lock (0.2.0, 3143 lines, 2023-era pins) resolve a 0.2.0 package universe for any uv command run inside those dirs, diverging from the root workspace lock (both 0.3.0 there).
- Evidence: `GEO-INFER-ACT/uv.lock:948-951`, `:1-7`; `GEO-INFER-SPACE/uv.lock:722-725`, `:8-16`; root `uv.lock:2479-2481,4924-4926`; `pyproject.toml:410-411` (workspace members glob) [tracked-ness: INFERENCE pending shell git].
- Bounded next step: delete both nested locks; confirm `uv lock --check` from the repo root still passes.
- Acceptance probe: `test ! -f GEO-INFER-ACT/uv.lock && test ! -f GEO-INFER-SPACE/uv.lock && uv lock --check && echo OK`
- Effort: S

**GS19-05 · MEDIUM · PACKAGING · Third-party dependency floors drift across module pyprojects** (Lane: packaging)
- Motivation: geopandas declared at five floors (0.9.0 BIO … 0.13.0 DATA/FOREST; BIO undercuts the root's own >=0.10.0), mypy at five values (fleet >=0.910 vs GIT/DATA/HEALTH/EDU outliers), black at three, SPACE caps numpy<2.0 invisibly governing the whole workspace. The fleet's real compatibility floor is the loosest declaration, stated nowhere.
- Evidence: `GEO-INFER-BIO/pyproject.toml:41`; root `pyproject.toml:32,131,133`; `GEO-INFER-{GIT:60,DATA:76,HEALTH:53,EDU:52-53}/pyproject.toml`; `GEO-INFER-SPACE/pyproject.toml:43`.
- Bounded next step: pick canonical floors (geopandas>=0.13.0; mypy/black aligned to the root quality extra; confirm numpy cap intent) and sweep all 45 pyprojects in one mechanical pass; re-lock.
- Acceptance probe: `grep -h '"geopandas[>=]' GEO-INFER-*/pyproject.toml | sort -u` — expect a single floor.
- Effort: M

**GS19-06 · MEDIUM · TEST · Cascadia integration test tree is tri-blind: 9 banned pytest.skip calls invisible to validator, runner, and root testpaths** (Lane: test-estate)
- Motivation: TESTING.md bans in-test skips repo-wide and CI enforces it — but the cascadia integration tree is outside every enforcement surface (validator glob, run_unified_tests EXTRA_TEST_PATHS, root testpaths). Nine pytest.skip calls will never fail anything and can never be converted; the deferral itself is tracked (PLACE-V14) but the contract-invisibility is not.
- Evidence: `GEO-INFER-PLACE/locations/cascadia/tests/integration/test_bioregion_pipeline.py:109,112,117,208,220,233,260,274,293`; `validate_test_contracts.py:31`; `run_unified_tests.py:40-47`; root `pyproject.toml:360-363`; `TESTING.md:37`.
- Bounded next step: extend validate_test_contracts.test_files() with the nested-tree glob (`GEO-INFER-*/locations/**/tests/**/*.py`); convert the 9 skip sites to explicit failures. Wiring the tree into EXTRA_TEST_PATHS stays gated on PLACE-V14.
- Acceptance probe: `uv run python GEO-INFER-TEST/validate_test_contracts.py --strict` — exits 1 listing the 9 lines before conversion, 0 after.
- Effort: M

**GS19-07 · MEDIUM · SECURITY · Unauthenticated pickle/joblib deserialization in AG/AI/LOG against the repo's own HMAC-envelope convention** (Lane: pipeline-perf-sec)
- Motivation: AG AgricultureModel.load + 4 joblib model subclasses, AI ModelTrainer.load_model (joblib + pickle fallback), LOG _load_gpickle deserialize unauthenticated files — arbitrary code execution on any tampered/swapped artifact. DATA/GIT/OPS already refuse loads until an HMAC-SHA256 GISP1 envelope verifies; adoption is mechanical but spans three modules.
- Evidence: `GEO-INFER-AG/src/geo_infer_ag/models/base.py:127-128`, `carbon_sequestration.py:688`, `crop_yield.py:462`, `soil_health.py:632`, `water_usage.py:736`; `GEO-INFER-AI/src/geo_infer_ai/core/training.py:643,651`; `GEO-INFER-LOG/src/geo_infer_log/core/routing.py:41-42`; mitigation contrast `GEO-INFER-DATA/src/geo_infer_data/core/storage.py:343-349`.
- Bounded next step: adopt the secure_serialization envelope in the three modules (sign on save, verify-before-deserialize on load, fail closed like GIT advanced_cache.py).
- Acceptance probe: tamper probe from the lane report (`AgricultureModel.load` on a corrupted payload must fail closed before any deserialization).
- Effort: M

**GS19-08 · MEDIUM · AGENT · docs/api_schema.yaml documents nine fabricated endpoint groups and omits four live routes** (Lane: mods-act-agent-ai-ant-api)
- Motivation: The 31.8KB API contract advertises /active-inference/*, /multi-agent/*, /spatial-reasoning/*, /learning/*, /communication/*, /agents/{agentId}/pause — none implemented; the real /action, /state, /message, DELETE /agents/{agent_id} routes are undocumented. Consumers fabricate clients against a fictional surface.
- Evidence: `GEO-INFER-AGENT/docs/api_schema.yaml:166,184,216,237,259,291,325,347,368,390,411,433,480`; `src/geo_infer_agent/api/agent_endpoints.py:81-201` (sole app; 7 real paths).
- Bounded next step: regenerate the paths section from `agent_endpoints.app.openapi()`, keep matching component schemas; ledger the disposition.
- Acceptance probe: normalized spec-paths vs live-routes diff is empty.
- Effort: S

**GS19-09 · MEDIUM · API · openapi_spec.yaml fabricates OGC-process/jobs endpoints and documents real paths without their /api/v1 prefix** (Lane: mods-act-agent-ai-ant-api)
- Motivation: /processes, /jobs, /data/upload, /search do not exist; the implemented polygon collection + /algorithms* registry are documented without the /api/v1 prefix app.py mounts them under, and /health/detailed + /algorithms are absent. Client generation from this spec 404s everywhere; the curl examples (correct paths) prove the spec alone is stale fiction.
- Evidence: `GEO-INFER-API/docs/openapi_spec.yaml:39,69,97,174,256,271,292,321,342,363,392`; `src/geo_infer_api/app.py:60-62`; `endpoints/algorithms_router.py:115,123,134`.
- Bounded next step: regenerate from `create_app().openapi()`; reconcile /health* at root, re-home real paths under /api/v1, add /algorithms, delete fabricated sections; spot-check geojson_api.md/algorithms_api.md in the same pass.
- Acceptance probe: spec paths == live routes (with prefix) after fix.
- Effort: S

**GS19-10 · MEDIUM · AGENT · API server ships wildcard-origin CORS with allow_credentials=True on a 0.0.0.0-bound default** (Lane: mods-act-agent-ai-ant-api)
- Motivation: The wildcard + credentialed combination lets any origin make credentialed requests against cookie/basic-auth'd deployments; start_api_server binds 0.0.0.0:8000 by default. GEO-INFER-API already hardened exactly this pattern (cors_allow_credentials) — copy it.
- Evidence: `GEO-INFER-AGENT/src/geo_infer_agent/api/agent_endpoints.py:71,72,226-228`; hardened precedent `GEO-INFER-API/src/geo_infer_api/app.py:22-34`; same-file drift: app metadata hardcodes version="0.1.0" (:65) while the package is 0.3.0.
- Bounded next step: port cors_allow_credentials; explicit allowed-origins setting; drive the FastAPI version from `geo_infer_agent.__version__`; add a TestClient preflight assertion.
- Acceptance probe: preflight with attacker origin must not yield (acao=='*' and acac=='true').
- Effort: S

**GS19-11 · MEDIUM · GIT · pyproject is the only module missing `package-dir = {"" = "src"}` — wheel build unproven** (Lane: mods-git-health-insurance-intra-iot)
- Motivation: src-layout + packages.find without the mapping can fail or emit an empty wheel; editable installs mask the defect, so the release artifact was likely never wheel-verified for GIT. Directly bears on REL-01.
- Evidence: `GEO-INFER-GIT/pyproject.toml:80-84`; sibling contrast `GEO-INFER-IOT/pyproject.toml:102-103` (+ HEALTH/INSURANCE/INTRA); repo-wide grep: package-dir present in every module except GIT.
- Bounded next step: add the mapping; build the wheel and inspect contents; extend validate_packaging to assert package-dir presence for src-layout modules.
- Acceptance probe: `uv build --package geo-infer-git` + wheel namelist check (lane report).
- Effort: S

**GS19-12 · MEDIUM · IOT · BayesianSpatialInference: untested inference path, unlogged exception swallow, hard-coded z-scores** (Lane: mods-git-health-insurance-intra-iot)
- Motivation: The module's headline capability has only construction/presence tests; the entire infer path is guarded by broad `except Exception` returning error dicts (outer catch doesn't log), and posterior confidence bounds use a two-value z-score hardcode (any CI ≠ 0.95 silently gets z=1.0).
- Evidence: `GEO-INFER-IOT/src/geo_infer_iot/core/inference.py:79-81,117,155-156,181`; `api/inference_api.py:97-98` (400 mapping good, no route test); `tests/unit/test_fixwave_regressions.py:39-49`.
- Bounded next step: behavioral tests for infer_spatial_distribution (success + each error path) and get_posterior_map z-scores (use scipy.stats.norm.ppf); add logger.error to the outer catch.
- Acceptance probe: new pytest set passes with success/failure assertions on the same entry point.
- Effort: M

**GS19-13 · MEDIUM · INSURANCE · External data integration is scaffold against fabricated endpoints, funnels all failures to silent None** (Lane: mods-git-health-insurance-intra-iot)
- Motivation: DataIntegrationManager retries `requests.get` against endpoints that do not exist (api.creditbureau.com etc.) with empty env-key auth and an UNDECLARED `requests` dependency; every failure — DNS, missing key, missing library, coding error — collapses to None, so underwriting callers cannot distinguish "no record" from "integration never worked".
- Evidence: `underwriting/utils/data_integration.py:82-106,233-238,170-172,532-533,557-558`; `pyproject.toml:36-39` (numpy/pandas only); `underwriting/__init__.py` docstring claims "Integration with external data sources and APIs".
- Bounded next step: make it loud — explicit endpoint/credential configuration with a configuration error when unset, or re-document as offline mock registry and stop network attempts by default; declare or document `requests`; tests assert no egress + chosen failure semantics.
- Acceptance probe: `get_data('credit_bureau', ...)` never returns bare None post-fix (loud config error or explicit mock marker).
- Effort: M

**GS19-14 · MEDIUM · HEALTH · analyze_with_active_inference substitutes plausible-looking defaults on failure with no failure flag — all seven paths untested** (Lane: mods-git-health-insurance-intra-iot)
- Motivation: Seven sequential broad catches replace failed stages with values indistinguishable from real output (failed risk assessment still yields score 0.5, risk_level "unknown"); for an epidemiology decision surface this masks outages. Zero tests exercise any of the paths.
- Evidence: `GEO-INFER-HEALTH/src/geo_infer_health/core/enhanced_disease_surveillance.py:298-307,319-330,335-338,353-356,370-374`; tests grep: zero failure-path coverage.
- Bounded next step: add `failed_stages` (and/or `degraded: bool`) to the returned dict set by each catch; tests monkeypatch each stage helper to raise and assert the flag propagates.
- Acceptance probe: forced-failure tests pass post-fix (lane report).
- Effort: M

**GS19-15 · MEDIUM · LOG · EnhancedLogger async processor has no stop/close; daemon thread silently drops queued entries** (Lane: mods-log-marine-math-metagov-norms)
- Motivation: async_logging defaults True; no stop/close/shutdown exists (flag set False only at init), the loop dies at interpreter exit killing queued entries, and log() enqueues unconditionally — exit-burst logs are silently lost. HAS_STRUCTLOG/HAS_PROMETHEUS probed and never used.
- Evidence: `GEO-INFER-LOG/src/geo_infer_log/__init__.py:233-239,296-299,303-310,371-375,32-33`.
- Bounded next step: add stop(timeout) (set flag, join with deadline, drain); retain thread handle; atexit safety net; delete or use the dead flags; lifecycle regression test.
- Acceptance probe: `EnhancedLogger('probe'); l.stop(timeout=2)` → queue empty, flag False.
- Effort: M

**GS19-16 · MEDIUM · NORMS · Compliance core paths swallow exceptions and fabricate "non-compliant" verdicts** (Lane: mods-log-marine-math-metagov-norms)
- Motivation: Two load-bearing evaluators conflate "evaluator crashed" with "violated": ComplianceTracker.evaluate_metric logs and sets is_compliant=False/level 0.0; check_norm_compliance returns (False, 0.0) for a raising condition callable — a buggy/hostile norm condition is indistinguishable from genuine non-compliance, with certainty 0.0 preventing even weighting.
- Evidence: `GEO-INFER-NORMS/src/geo_infer_norms/core/compliance_tracking.py:370-374`; `normative_inference.py:311-314` (contrast: probe paths at :515-547 log-and-continue deliberately).
- Bounded next step: introduce a distinct evaluation-error outcome (error entry / ('error', None) state), let the API layer map it to 5xx rather than folding into ValueError handling; regression tests prove a raising condition surfaces as an error state.
- Acceptance probe: lane probe — a condition that raises must NOT produce (False, 0.0).
- Effort: M

**GS19-17 · MEDIUM · PEP · API ships fabricated success endpoints for performance, learning, conflicts, and surveys** (Lane: mods-ops-org-pep-place-req)
- Motivation: Four route groups are echo stubs: POST returns fabricated "created" messages with zero persistence; GETs return hardcoded empty lists. README.md:3 and pyproject description advertise "performance tracking, and community engagement" — claims outrun implementation. Real domains (hr/crm/talent) all back onto core/data_store.py.
- Evidence: `GEO-INFER-PEP/src/geo_infer_pep/api/__init__.py:78-142`; `README.md:3`; `pyproject.toml:8`.
- Bounded next step: per domain — back the four groups with the shared pep_data_manager (Employee/Customer/Candidate pattern + pydantic models) OR remove the stubs and drop the claims until implemented.
- Acceptance probe: lane TestClient probe — POST then GET must return the created record.
- Effort: M

**GS19-18 · MEDIUM · PEP · PEPValidator and PEPOrchestrator have zero test coverage while tests/core and tests/models are empty doc-only scaffolds** (Lane: mods-ops-org-pep-place-req)
- Motivation: 43 KB of core code is exported and driven by live API routes yet untested; tests/core/ and tests/models/ exist as advertised test surfaces containing only READMEs — the tests/ tree advertises structure it does not have.
- Evidence: `GEO-INFER-PEP/tests/core/`, `tests/models/` (doc-only); `src/geo_infer_pep/core/__init__.py:5-7`; `api/__init__.py:49-75,157-205`; `tests/integration/test_pep_integration.py:137-138`.
- Bounded next step: add tests/unit/test_validator.py (validate_* pass/fail paths) and test_orchestrator.py (workflow create→get→execute against an isolated PEPDataManager); fold the empty scaffold dirs into a doc-structure fix.
- Acceptance probe: `uv run --no-sync python -m pytest GEO-INFER-PEP/tests/unit/test_validator.py GEO-INFER-PEP/tests/unit/test_orchestrator.py -q` green.
- Effort: M

**GS19-19 · MEDIUM · TEST · TEST's own docs/api_reference.md fabricates API — and the import-truth validator's scope structurally misses module docs** (Lane: mods-test-time-transport-water)
- Motivation: The page instructs `from geo_infer_test import TestResult` (renamed to TestOutcome; ImportError) and claims three console scripts (geo-test*) declared in no pyproject. validate_doc_imports.py — built to catch exactly this — hardcodes DOC_ROOT to GEO-INFER-INTRA/docs, leaving module docs trees ungoverned (same root cause behind the whole api_schema family).
- Evidence: `GEO-INFER-TEST/docs/api_reference.md:38-49,92-97`; `src/geo_infer_test/models/types.py:7-12`; `src/geo_infer_test/__init__.py:19,57`; `validate_doc_imports.py:29,174-175`.
- Bounded next step: truth-up api_reference.md (TestOutcome; delete/reimplement the scripts section); widen validate_doc_imports to `GEO-INFER-*/docs/**/*.md`; fix whatever the widened scan surfaces.
- Acceptance probe: documented imports resolve; widened validator runs green over module docs.
- Effort: M

## Minor — bounded single-session changes

**GS19-20 · MINOR · DOCS(api_schema family) · REST design specs presented as live APIs across 7 modules, missing the repo's own "design spec only" banner** (Lanes: mods-risk-sec-sim-space-spm, mods-app-art-bayes-bio-civ, mods-ops-org-pep-place-req — folded from 4 lane items)
- Motivation: RISK (2144-line v2 spec), SIM (1704), SPM, BAYES (1142), ART (1410), OPS (1267), REQ (619) ship full OpenAPI specs with production/staging server URLs and auth schemes for HTTP layers that do not exist (no api/ package, no fastapi/flask anywhere in those src trees; SPM's "API" is an in-process dict facade; OPS app serves only /health,/version,/metrics). GEO-INFER-APP and GEO-INFER-ORG already carry the honest banner — this family just never received it. SEC is the special case: it ships a real Flask blueprint whose 6 routes have ZERO overlap with its 19 documented path groups → regenerate from the blueprint instead.
- Evidence: `GEO-INFER-RISK/docs/api_schema.yaml:34-39`; `GEO-INFER-SIM/docs/api_schema.yaml:37-42,804-806`; `GEO-INFER-SPM/docs/api_schema.yaml:20-25`; `GEO-INFER-BAYES/docs/api_schema.yaml:1-25,177-285`; `GEO-INFER-ART/docs/api_schema.yaml:1-31`; `GEO-INFER-OPS/docs/api_schema.yaml:17-20`; `GEO-INFER-REQ/docs/api_schema.yaml:17-28` (fabricated contact email req-support@geo-infer.org); `GEO-INFER-SEC/docs/api_schema.yaml:27-30,58-574` vs `security_api.py:118-312`; honest precedents `GEO-INFER-APP/docs/api_schema.yaml:1-9`, `GEO-INFER-ORG/docs/api_schema.yaml:1-8`.
- Bounded next step: prepend the APP/ORG banner to RISK/SIM/SPM/BAYES/ART/OPS/REQ (strip or annotate live-server claims; fix REQ's contact email); regenerate SEC's schema from the blueprint routes.
- Acceptance probe: `grep -L "design spec" GEO-INFER-{RISK,SIM,SPM,BAYES,ART,OPS,REQ}/docs/api_schema.yaml` returns nothing; SEC documented-path set matches blueprint routes.
- Effort: M (one coordinated session)

**GS19-21 · MINOR · CI · Trigger coverage asymmetry: feature-branch PRs get gnn-interchange and import-probes but never the main CI** (Lane: ci-gates) — Evidence: `ci.yml:5-11`, `gnn-interchange.yml:6-15`, `import-probes.yml:4-7`. Next step: pick one policy (drop ci.yml's PR branches filter, or restrict the other two) and document the dispatch requirement. Probe: branch-filter grep alignment. Effort: S

**GS19-22 · MINOR · CI · release.yml: release job has no timeout-minutes and the workflow has no concurrency group** (Lane: ci-gates) — Evidence: `release.yml:35,66-68`. Next step: timeout-minutes ~60 on the release job; `concurrency: group: geo-infer-release-${{ github.ref }}` without cancel-in-progress. Probe: actionlint + grep. Effort: S

**GS19-23 · MINOR · CI · import-probes.yml hardcodes pytest==8.4.2 / build==1.3.0 outside uv.lock (lock: pytest 8.4.1)** (Lane: ci-gates) — Evidence: `import-probes.yml:36`; `uv.lock:9602-9603`; `GEO-INFER-TEST/docs/pin_review_2026-Q3.md:7`. Next step: pin to locked versions or derive from the lock at runtime; add the pins as a pin_review row. Probe: version equality grep. Effort: S

**GS19-24 · MINOR · CI/DOCS · Gitleaks full-history scan has no documented local replication path — secrets detected only after push** (Lane: ci-gates) — Evidence: `GEO-INFER-TEST/docs/secret_scan_policy.md:3-6`; `ci.yml:133-145` (linux-only tarball). Next step: local-replication section with the exact command + darwin/arm64 note; append to AGENTS/README Standard Commands via the generator. Probe: invocation line present in the policy doc. Effort: S

**GS19-25 · MINOR · PACKAGING · Legacy setup.py metadata drift (SIM 0.1.0/wrong URL/bogus OSI-CC classifier/scipy dep; PEP 0.1.0); 40/45 modules still carry setup.py** (Lane: packaging) — Evidence: `GEO-INFER-SIM/setup.py:8,14,21,29-32`; `GEO-INFER-PEP/setup.py:5`. Next step: delete SIM+PEP setup.py (pyproject canonical; decide scipy in SIM deps); optional follow-up: delete the remaining 38 stubs. Probe: `test ! -f GEO-INFER-SIM/setup.py && test ! -f GEO-INFER-PEP/setup.py`. Effort: S

**GS19-26 · MINOR · PACKAGING · Stale intra-workspace version floors: cross-module deps pinned >=0.1.0/0.2.0 while every member is 0.3.0** (Lane: packaging) — Evidence: `GEO-INFER-ACT/pyproject.toml:46,62,63,70`; `GEO-INFER-BIO/pyproject.toml:73-75`; `GEO-INFER-RISK/pyproject.toml:45`; `GEO-INFER-TRANSPORT/pyproject.toml:43`; modern precedent `GEO-INFER-INSURANCE/pyproject.toml:45-48,61-63`. Next step: normalize to the INSURANCE convention (no floors + [tool.uv.sources] workspace = true); re-lock. Probe: grep for non-0.3.0 geo-infer-* floors returns nothing. Effort: S

**GS19-27 · MINOR · PACKAGING · Tracked-and-modified *.pyc under GEO-INFER-PLACE (50+ on disk) keep git status dirty; ignore rules predate the tracking** (Lane: packaging) — Evidence: root `.gitignore:1-3` already ignores them; PLACE pycs appear as tracked-and-modified every session; ACT pycache holds pycs for deleted sources. Next step: enumerate `git ls-files | grep '\\.pyc$'`, `git rm -r --cached` batched, commit. Probe: `git ls-files | grep -c '\\.pyc$'` == 0. Effort: S

**GS19-28 · MINOR · PACKAGING · Metadata completeness sweep: ENERGY/WATER have no classifiers at all; 19 modules ship empty [project.scripts]; 8 lack [project.urls]; root "4 - Beta" vs fleet "3 - Alpha" is an unanswered policy** (Lane: packaging) — Evidence: ENERGY/WATER pyprojects (no classifiers block); empty scripts census AG,API,APP,BAYES,COG,COMMS,ECON,EXAMPLES,MATH,NORMS,OPS,ORG,PEP,PLACE,REQ,RISK,SIM,SPM,TIME; missing urls: CLIMATE,EDU,EMERGENCY,ENERGY,FOREST,MARINE,TRANSPORT,WATER; SPACE's intentional-emptiness comment is the precedent. Next step: add classifier blocks, delete or populate empty scripts sections, add the standard urls block; decide the Development Status policy. Probe: lane grep set. Effort: S

**GS19-29 · MINOR · PACKAGING · Root virtual-package residue: phantom geo_infer_framework references and a stale root egg-info artifact** (Lane: packaging) — Evidence: `pyproject.toml:261` (isort known_first_party for a nonexistent package); `geo_infer_framework.egg-info/` on disk (gitignored legacy artifact); uv treats root as virtual (`uv.lock:3628-3630`). Next step: delete the egg-info dir, fix/drop the isort entry, make virtual-root status explicit. Probe: no egg-info dir + no grep hit. Effort: S

**GS19-30 · MINOR · DOCS · CHANGELOG.md Version History table contradicts the release sections and shipped tags** (Lane: docs-truth) — Evidence: `CHANGELOG.md:860` (0.2.0 dated 2026-02-25 vs shipped 2026-09-11), `:856-862` (0.2.1 missing; rows out of order), `:92` + `:151` (two [0.2.0] headers under a declared Keep-a-Changelog format). Next step: merge the 09-10 section under the canonical 09-11 section; rewrite the table to 4 ordered rows. Probe: one [0.2.0] header; rows read 0.1.0/0.2.0/0.2.1/0.3.0. Effort: S

**GS19-31 · MINOR · DOCS · CHANGELOG [0.3.0] omits shipped commits from the v0.2.1..v0.3.0 window** (Lane: docs-truth) — Evidence: SEC test-hardening commits fff0fb59/b73de0a7/bdf5fb51 and TEST import-smoke kill-margin widening fc5dd1ac plus the manuscript figure-polish series are absent from `CHANGELOG.md:8-41` (reflog-corroborated). Next step: add "### Tests" and "### Changed" lines with SHAs. Probe: grep returns the new lines. Effort: S

**GS19-32 · MINOR · DOCS · CLAUDE.md pytest-marker list incomplete vs root pyproject strict-markers config** (Lane: docs-truth) — Evidence: `CLAUDE.md:59` lists 8 markers; `pyproject.toml:368-383` declares 14 (--strict-markers makes the gap an error for agents). Next step: enumerate all 14 or point at the pyproject block. Probe: marker-set equality. Effort: S

**GS19-33 · MINOR · DOCS · manuscript/config.yaml uncommitted hunk: captured and dispositioned — KEEP** (Lane: docs-truth) — Evidence: `git diff` this pass: the ONLY hunk is the generator-owned `date` field, 2026-09-17T11:57:23-07:00 → 13:07:20-07:00 — exactly the v0.3.0 release-commit instant (reflog .git/logs/HEAD:193); all statically checkable consistency claims verified (version, geometry margin, FIGURE_HEIGHT_FRACTION lock-step, bibliography policy). Next step: none (commit it as-is with the next docs change, or `git checkout -- ` if a pristine tree is wanted; do NOT hand-edit). Probe: `git diff -- manuscript/config.yaml` shows only the date hunk. Effort: S

**GS19-34 · MINOR · TEST · Module-local pytest configs (INSURANCE, cascadia) silently bypass the root strict test policy on direct invocation** (Lane: test-estate) — Evidence: `GEO-INFER-INSURANCE/pyproject.toml:78-82`; `GEO-INFER-PLACE/locations/cascadia/pyproject.toml:72-75`; root policy `pyproject.toml:353-363` + `conftest.py:50-54,109-111` (confcutdir semantics drop the root conftest). Next step: delete both local [tool.pytest.ini_options] sections; re-run both suites under the root config. Probe: pytest --co inside INSURANCE shows rootdir = repo root. Effort: S

**GS19-35 · MINOR · TEST · API version surface drifted out of the released fleet: Settings.app_version stuck at 0.2.0, cemented by its own test** (Lane: test-estate) — Evidence: `GEO-INFER-API/src/geo_infer_api/core/config.py:43`; `tests/unit/test_config.py:10` asserts the stale literal; fleet gate `test_runtime_metadata.py:37-45` doesn't cover app_version. Next step: derive from importlib.metadata.version("geo-infer-api") (static fallback); fix the test to compare against the distribution version. Probe: pytest passes at any release. Effort: S

**GS19-36 · MINOR · TEST · TEST module conftest keeps a divergent second marker registry driven by filename substrings; the validator cannot see conftest-applied markers** (Lane: test-estate) — Evidence: `GEO-INFER-TEST/tests/conftest.py:769-770,778-792` (temporal/ml undeclared anywhere; test_time→temporal substring heuristic); `validate_test_contracts.py:104-105` (conftest exemption). Next step: delete dead substring branches; register or remove temporal/ml; optionally AST-scan conftests for applied markers. Probe: targeted unit test on the hook. Effort: S

**GS19-37 · MINOR · TEST · PLACE unit cache test burns 3 seconds of real wall-clock sleep for a 2-second TTL** (Lane: test-estate) — Evidence: `GEO-INFER-PLACE/tests/unit/test_caching.py:43,20` (~6% of the 52.3s suite); SEC's frozen-datetime pattern at `test_physical_security.py:146-155` is the estate idiom. Next step: replace the sleep with a clock seam (monkeypatched frozen time source); keep the expired-entry-reads-None contract. Probe: no test in the file exceeds ~0.1s. Effort: S

**GS19-38 · MINOR · TEST · The slow/fast marker taxonomy is inert in the unified runner; ACT's 535-test unit lane (267s) is the fleet cost hotspot** (Lane: test-estate) — Evidence: `run_unified_tests.py:300-310,385-397` (no -m anywhere); `pyproject.toml:369` advertises deselection; `.geo-infer-test-results/ACT_unit_results.xml:1` (535 tests/267.1s). Next step: category lanes apply `-m "not slow"` (+ a slow complement lane); annotate ACT's heaviest classes; assert the slow lane runs on a scheduled surface. Probe: ACT unit-lane duration drops measurably. Effort: M

**GS19-39 · MINOR · TEST · Packaged-config regression family hand-copied across ~7 modules with already-divergent idioms** (Lane: test-estate) — Evidence: SPACE vs GIT copies (`test_config_loader_packaged_config.py` in both; GIT adds literal inventory counts that break on list changes); family by filename in HEALTH/INTRA/PLACE/RISK; shared plugin seam already exists (`conftest.py:12`). Next step: extract a parametrized packaged-config helper into geo_infer_test.testing; migrate the seven files; keep genuinely module-specific asserts local. Probe: helper unit test + migrated suites green. Effort: M

**GS19-40 · MINOR · SECURITY · No-timeout requests.get on external downloads in PLACE cascadia acquisition (4 call-sites) can hang the county pipeline indefinitely** (Lane: pipeline-perf-sec) — Evidence: `locations/cascadia/src/core/download_empirical_data.py:71`, `data_modules/improvements/data_sources.py:68,96`, `data_modules/mortgage_debt/geo_infer_mortgage_debt.py:69`; sibling convention timeout=30..300 (`current_use/data_sources.py:257`). Next step: explicit timeout tuples matching siblings, or route through the deadline-capped session helper `_regional_download_worker.py:65-68` already implements. Probe: socket-hang unit test completes via TimeoutExpired. Effort: S

**GS19-41 · MINOR · SECURITY · AGENT torch.load without explicit weights_only is code-exec-unsafe across the declared torch>=2.0.0 range** (Lane: pipeline-perf-sec) — Evidence: `src/geo_infer_agent/core/active_inference.py:664`; torch>=2.0.0 declared, lock resolves 2.8.0 (safe default) — declared-range envs get the unsafe default. Next step: `torch.load(filepath, weights_only=True)`. Probe: roundtrip test passes with the flag. Effort: S

**GS19-42 · MINOR · SECURITY/ROBUSTNESS · SPACE GPU grid_distance kernel swallows every exception per cell pair, conflating backend errors with the documented incomparable sentinel** (Lane: pipeline-perf-sec) — Evidence: `src/geo_infer_space/backends/gpu/gpu_acceleration.py:436-441` (`except Exception: pass`) vs docstring :432-435 reserving -1 for documented cases. Next step: narrow the catch to h3.CellIndexError/ValueError/KeyError; let unexpected exceptions propagate or log-and-raise. Probe: AttributeError from a broken backend propagates instead of silent -1. Effort: S

**GS19-43 · MINOR · SECURITY · DATA backend config silently falls back to hardcoded Postgres/MinIO dev credentials when env vars are unset** (Lane: pipeline-perf-sec) — Evidence: `core/storage.py:813-824` ("password"/"minioadmin" defaults), docstring :801-811 admits dev intent but nothing enforces the boundary; hosts configurable so localhost assumption is not structural. Next step: warn loudly or fail closed when env unset AND host not loopback (or require explicit opt-in). Probe: env-unset probe emits the warning/failure. Effort: S

**GS19-44 · MINOR · ROBUSTNESS · OPS docker build/push subprocess.run without timeout or output capture can block the deployment pipeline indefinitely** (Lane: pipeline-perf-sec) — Evidence: `src/geo_infer_ops/core/deployment.py:78-79,100-101`. Next step: config-driven timeouts (build 1800s, push 900s) + TimeoutExpired handler returning False. Probe: patched-hang test returns False. Effort: S

**GS19-45 · MINOR · ROBUSTNESS · COMMS global communication-system singleton uses unlocked check-then-set; concurrent first access can leak a fully-constructed system** (Lane: pipeline-perf-sec) — Evidence: `src/geo_infer_comms/__init__.py:336-344,350-360`. Next step: module-level threading.Lock (double-checked init) for both accessors. Probe: 4-thread first-call race yields one instance id. Effort: S

**GS19-46 · MINOR · AI · Package docstrings advertise capabilities with zero implementation (model repository, pre-trained models, CNN/object detection/segmentation)** (Lane: mods-act-agent-ai-ant-api) — Evidence: `src/geo_infer_ai/__init__.py:12`; `models/cv/image_classifier.py:4-5` vs `_initialize_model` :47-70 (RandomForest/MLP only). Next step: truth-up the two docstrings; pre-trained assets would be a new scope row, not a docstring promise. Probe: grep prints CLEAN. Effort: S

**GS19-47 · MINOR · AI · SKILL.md frontmatter declares required prerequisites (geo-infer-act, geo-infer-bayes) that contradict pyproject and the skill's own text** (Lane: mods-act-agent-ai-ant-api) — Evidence: `GEO-INFER-AI/SKILL.md:6,7` vs `pyproject.toml:37-42` vs SKILL.md:103 ("Standalone"). Next step: demote to recommended or delete. Probe: lane frontmatter-vs-pyproject script exits 0. Effort: S

**GS19-48 · MINOR · ACT · Ships a REST client (api.Client) and endpoint map for a /models service that no module implements** (Lane: mods-act-agent-ai-ant-api) — Evidence: `src/geo_infer_act/api/client.py:10-38`, `endpoints.py:10-14`; zero FastAPI/APIRouter in the module; framework exposes no /models either; tests exercise mocks only. Next step: (a) re-scope docstrings to name the external deployment, or (b) remove the dead surface; prefer (a) per no-orphaned-interface. Probe: documented-scope grep + test_api.py green. Effort: S

**GS19-49 · MINOR · BIO · Container spec contradicts the package contract: python:3.9 base vs requires-python >=3.11, plus both services launch the namespace-shadowed src.* module path** (Lane: mods-app-art-bayes-bio-civ) — Evidence: `Dockerfile:2,8-10,14,29,36`; `docker-compose.yml:32` (bare uvicorn not on image PATH). Next step: base image 3.11/3.12-slim; installed-distribution module paths (no src.* shadow); align compose to `uv run uvicorn`; drop build-essential if unneeded; docker smoke /health + /graphql. Probe: lane docker probe. Effort: S

**GS19-50 · MINOR · BIO · requirements.txt claims to be a "mirror of [project.dependencies]" but drifts on shapely (1.8.0 vs 2.0.0)** (Lane: mods-app-art-bayes-bio-civ) — Evidence: `requirements.txt:1,12` vs `pyproject.toml:49`. Next step: regenerate verbatim from pyproject. Probe: both lines read shapely>=2.0.0. Effort: S

**GS19-51 · MINOR · ART · 8 of 10 "public interface" validators have zero callers anywhere and zero tests** (Lane: mods-app-art-bayes-bio-civ) — Evidence: `src/geo_infer_art/utils/README.md:13-23` vs repo-wide grep (only validate_file_path/validate_geospatial_data imported, at geo_art.py:30); no test imports the module. Next step: delete the 7 leaf validators (+ validate_coordinates losing its only caller) or wire them into the core paths they were written for; correct utils/README.md. Probe: grep shows only validators.py-internal matches; unit suite green. Effort: S

**GS19-52 · MINOR · BAYES · geo_observations exports omitted from __all__ while sibling civic_intel names are listed** (Lane: mods-app-art-bayes-bio-civ) — Evidence: `src/geo_infer_bayes/__init__.py:32-35,37-49`. Next step: add both names to __all__. Probe: subset assert passes. Effort: S

**GS19-53 · MINOR · BAYES · TFPInterface docstrings document a TFP delegation path that cannot exist — tensorflow_probability is hard-wired to None with no import code path** (Lane: mods-app-art-bayes-bio-civ) — Evidence: `src/geo_infer_bayes/api/tfp_interface.py:4-5,19-21,39-40`; the test suite already calls the NumPy backend "permanent" (`tests/unit/test_api_interfaces.py:76-77`). Next step: rewrite module/class docstrings to the permanent-backend truth; delete or honestly-annotate the dead flags. Probe: 'delegates to TFP' grep returns nothing; suite green. Effort: S

**GS19-54 · MINOR · APP · _save_agents swallows every persistence failure with a log line while _load_saved_agents explicitly documents surfacing errors — and no test covers the save path** (Lane: mods-app-art-bayes-bio-civ) — Evidence: `src/geo_infer_app/api/agent_api.py:509-528` vs the documented policy at :487-491. Next step: propagate the failure (or status bool consumed by create/delete); add an unwritable-path regression test. Probe: forced-failure test fails pre-fix, passes post-fix. Effort: S

**GS19-55 · MINOR · COG · load_cognitive_model always returns {} — silent AttributeError fallback on every call** (Lane: mods-climate-cog-comms-data-econ) — Evidence: `utils/helpers.py:104,116-117,136-138` (str declared, `.suffix` called, broad except; a `# type: ignore[attr-defined]` suppresses the exact static error); sibling save does the Path conversion (:168); public API via `utils/__init__.py:33,57`; zero tests. Next step: `model_path = Path(model_path)` + widen signature; round-trip unit test (json+yaml+invalid-path contract). Probe: lane round-trip assert. Effort: S

**GS19-56 · MINOR · COG · REST API test suite hard-fails (not skips) without optional flask, and dev extra does not carry flask** (Lane: mods-climate-cog-comms-data-econ) — Evidence: `pyproject.toml:43-53`; `tests/unit/test_rest_api.py:19-20,29`; CLIMATE's dev-extra precedent :47-54. Next step: importorskip in the test file or flask in the dev extra (ledger the choice). Probe: flask-less venv reports skip, not error. Effort: S

**GS19-57 · MINOR · COMMS · collaboration, streaming, and spatial-routing engines unreachable through the documented unified interface** (Lane: mods-climate-cog-comms-data-econ) — Evidence: docstring promises a unified interface (`__init__.py:134-135`); 12 components wired but nothing from core/{collaboration,streaming,spatial_routing}.py; every consumer deep-imports (tests at `test_collaboration_sessions.py:11` etc.). Next step: re-export the three managers (+coordinator/analytics) from the package root and __all__, wire CollaborationManager into the system lifecycle, deliver or correct the docstring. Probe: `from geo_infer_comms import CollaborationManager, StreamManager, AdvancedSpatialRouter` succeeds. Effort: S

**GS19-58 · MINOR · CLIMATE · preprocess_dataset silently ignores unsupported operations; preprocess/load have zero test coverage** (Lane: mods-climate-cog-comms-data-econ) — Evidence: `core/climate_data.py:138,146-157` (docstring advertises resample/regrid; dispatch falls through silently); tests grep: 0 coverage for both methods. Next step: else-branch raises ValueError naming the op (or explicit lenient contract + warning); implement or document resample/regrid absence; add unit tests. Probe: bogus-op probe raises post-fix. Effort: S

**GS19-59 · MINOR · EDU · docs/api_reference.md documents a nonexistent class (PersonalizedPathBuilder) and five nonexistent ProgressTracker methods** (Lane: mods-edu-emergency-energy-examples-forest) — Evidence: `docs/api_reference.md:192-262` vs `core/personalization.py:101`, `core/progress.py:160-595` (real API: track_progress, generate_competency_report, export_progress, identify_gaps, generate_analytics, identify_at_risk). Next step: rewrite both sections to the real classes; mechanically verify every documented name. Probe: hasattr-check script exits 0. Effort: S

**GS19-60 · MINOR · EDU · docs/index.md Architecture invents three subpackages and a Quick Start that crashes (education_standard kwarg does not exist)** (Lane: mods-edu-emergency-energy-examples-forest) — Evidence: `docs/index.md:49-70` vs `core/curriculum.py:107-110`. Next step: delete invented entries; PersonalizedPathBuilder→PersonalizedLearning; fix the constructor snippet. Probe: corrected snippet runs exit 0; grep clean. Effort: S

**GS19-61 · MINOR · EMERGENCY · docs/index.md architecture documents models/, api/endpoints.py, utils/hazard_mapping.py that do not exist; README deps contradict pyproject** (Lane: mods-edu-emergency-energy-examples-forest) — Evidence: `docs/index.md:77-82`; `pyproject.toml:33-35` (networkx runtime; spatial libs test-only). Next step: delete fabricated entries; align README Dependencies with pyproject. Probe: package imports + doc greps clean. Effort: S

**GS19-62 · MINOR · EMERGENCY · establish_command silently coerces unknown incident_type/scale values instead of failing** (Lane: mods-edu-emergency-energy-examples-forest) — Evidence: `core/coordinator.py:289-296` (typo 'wildfre'→OTHER; 'type9'→Type-3, mid-severity); sibling ResourceDeployer raises descriptively (`resources.py:124-128`); fallback path untested. Next step: descriptive ValueError mirroring the sibling; unit tests for both raises + no-coerced-registration. Probe: lane probe raises post-fix. Effort: S

**GS19-63 · MINOR · ENERGY · docs/index.md makes three false claims (REST API endpoints, pandas/scikit-learn core deps, version 0.1.0) backed by empty dead-code stub packages** (Lane: mods-edu-emergency-energy-examples-forest) — Evidence: `docs/index.md:83,93,97` vs `api/__init__.py:1` (3-line stub) and `pyproject.toml:7,21-24` (numpy+xarray only). Next step: delete the api/+utils/ stub packages (zero importers) and truth-up the doc. Probe: lane greps return 0; __all__ still 10. Effort: S

**GS19-64 · MINOR · EDU · Generated coding exercises ship starter code that imports a nonexistent spatial_analysis_lib module** (Lane: mods-edu-emergency-energy-examples-forest) — Evidence: `core/exercises.py:286-296` (emitted for every coding exercise); also a banned TODO-style "replace with your library" marker. Next step: make starter code importable (inline minimal stub or plain data structures); move guidance to prose. Probe: emitted starter code compiles. Effort: S

**GS19-65 · MINOR · EXAMPLES · Orchestrator execution engine (execute_workflow, all five strategies, recovery, convergence) has zero execution coverage anywhere in the repo** (Lane: mods-edu-emergency-energy-examples-forest) — Evidence: `core/module_orchestrator.py:457,502-516,970-972` (convergence catch converts malformed results into "never converged" silently); existing tests cover only condition eval + packaged-workflow loading; integration tests never touch the engine. Next step: execution test using the docstring-sanctioned APIConnector seam (sequential happy path + feedback_loop converged exit); narrow the :970-972 except. Probe: new test file passes. Effort: M

**GS19-66 · MINOR · FOREST · docs/index.md states version 0.2.0; package is at 0.3.0** (Lane: mods-edu-emergency-energy-examples-forest) — Evidence: `docs/index.md:90` vs `pyproject.toml:7` + `__init__.py:4`. Next step: update to 0.3.0; check whether the line is generated. Probe: importlib.metadata.version matches the doc. Effort: S

**GS19-67 · MINOR · IOT · SensorAPI is a public export with zero test coverage** (Lane: mods-git-health-insurance-intra-iot) — Evidence: zero test references; silent-degradation branch (HAS_CORE_MODULES=False) at `api/sensor_api.py:19-21,44-47` untested. Next step: unit test booting SensorAPI with a stub registry (register → POST measurement → spatial-filter shape) + healthy-install assertion. Probe: `-k sensor_api` green. Effort: S

**GS19-68 · MINOR · INTRA · Ships five source-less stale package dirs while its init docstring still claims a "knowledge management backbone"** (Lane: mods-git-health-insurance-intra-iot) — Evidence: `api/`, `models/`, `core/knowledge_base/`, `core/workflow/`, `core/ontology/` contain only stale __pycache__; `__init__.py:1` docstring vs accurate pyproject description. Next step: delete the dirs (+ the same pattern in GIT examples/); reword the docstring; run signpost regen check. Probe: no cache-only package dirs; corrected docstring printed. Effort: S

**GS19-69 · MINOR · LOG · ortools is a hard runtime dependency of utils/optimization.py but is declared nowhere** (Lane: mods-log-marine-math-metagov-norms) — Evidence: `utils/optimization.py:12-28,51` vs `pyproject.toml:36-50` (pulp only) and requirements.txt; only ortools reference in root pyproject is a mypy override. Next step: declare ortools in pyproject + requirements; keep the fail-fast guard; add one solve_tsp unit test. Probe: lane env-probe prints ok. Effort: S

**GS19-70 · MINOR · METAGOV · core.advanced_analysis (AdvancedGovernanceAnalyzer, 600+ lines) is unexported from both facades — a tested public-API orphan** (Lane: mods-log-marine-math-metagov-norms) — Evidence: `core/__init__.py:3-18`, `__init__.py:12-27` (every sibling exported, advanced_analysis absent); dedicated tests import the full path. Next step: export it (sibling pattern) or delete module+tests — no third state. Probe: hasattr+__all__ assert. Effort: S

**GS19-71 · MINOR · MATH · TheoremProver silently downgrades requested z3 backend to numpy when z3-solver (optional extra) is absent** (Lane: mods-log-marine-math-metagov-norms) — Evidence: `core/theorem_proving/prover.py:50-53,63-77` (warning + silent swap; numpy path "limited capabilities"); z3 only in the theorem-proving extra. Next step: raise naming the extra (mirror isabelle/lean ValueError + LOG's install-hint); update the two tests exercising the downgrade. Probe: explicit-backend assert. Effort: S

**GS19-72 · MINOR · MATH · MathConfig.configure() silently misroutes every documented kwarg (splits key on first underscore into a wrong section)** (Lane: mods-log-marine-math-metagov-norms) — Evidence: `config.py:156-164` (documented example writes section 'theorem' key 'proving_backend'); real sections :31-40; same example in docs/QUICK_START.md:24. Next step: accept dotted-style keys or dict-of-sections; raise on unknown prefixes; fix docstring; round-trip test. Probe: lane configure→get assert. Effort: S

**GS19-73 · MINOR · MATH · core/integration.py (663 lines, exported via core facade) is untested and its availability check is a tautology** (Lane: mods-log-marine-math-metagov-norms) — Evidence: `core/integration.py:36-52,61-97` (four branches, identical __import__); zero test references. Next step: delete module+export (nothing imports it) or collapse to one loop + pipeline tests. Probe: post-deletion import fails cleanly (or pipelines tested). Effort: S

**GS19-74 · MINOR · MARINE/LOG · Committed egg-info build metadata is stale (Version 0.2.0) and contradicts pyproject 0.3.0** (Lane: mods-log-marine-math-metagov-norms) — Evidence: `src/geo_infer_marine.egg-info/PKG-INFO:3`, `src/geo_infer_log.egg-info/PKG-INFO:3` vs both pyprojects. Next step: delete both committed egg-info dirs; let the toolchain regenerate. Probe: PKG-INFO grep returns nothing. Effort: S

**GS19-75 · MINOR · PEP · Visualization modules mutate the CWD filesystem at import time, contradicting the module's own import-purity guideline** (Lane: mods-ops-org-pep-place-req) — Evidence: `visualizations/{crm,hr,talent}_visuals.py:14-17` (module-level mkdir; residue visible at repo root); SKILL.md:154-155 forbids import-time state mutation. Next step: move mkdir into plot functions (create-on-write). Probe: import in a fresh cwd creates nothing. Effort: S

**GS19-76 · MINOR · PLACE · Bioregion volcano popups read fields the regional-layer producer never emits, rendering no-invention sentinels as data** (Lane: mods-ops-org-pep-place-req) — Evidence: `core/regional_layers.py:177-179` (honest sentinels) vs `core/bioregion_visualization.py:454-456,464-467` (renders 'Elevation: ? m' and the sentinel sentence as a lahar drainage); also document allow_missing_layers in the docstring (:266-278). Next step: render only producer-supplied fields (omit sentinel rows). Probe: grep probe clean post-fix. Effort: S

**GS19-77 · MINOR · PLACE · README dependency lists drift from pyproject.toml (stale shapely>=1.8.0 floor; missing urllib3/networkx)** (Lane: mods-ops-org-pep-place-req) — Evidence: `README.md:34`, `src/geo_infer_place/core/README.md:49` vs `pyproject.toml:37-40`. Next step: regenerate both dependency blocks from pyproject. Probe: grep counts 0/0 post-fix. Effort: S

**GS19-78 · MINOR · OPS · Explicit config path is silently ignored when it does not exist** (Lane: mods-ops-org-pep-place-req) — Evidence: `utils/config.py:35-36` vs documented contract :16-19 (env-var branch :38-42 already raises — asymmetry is accidental). Next step: raise FileNotFoundError for a provided-but-missing path; align docstring. Probe: lane probe prints ok post-fix. Effort: S

**GS19-79 · MINOR · OPS · SKILL.md claims unimplemented "Log aggregation: Structured log collection and querying"** (Lane: mods-ops-org-pep-place-req) — Evidence: `SKILL.md:21` vs src grep (only configure_logging/get_logger + metrics). Next step: reword to implemented behavior or route to the owning module. Probe: grep count 0 post-fix. Effort: S

**GS19-80 · MINOR · SIM · SystemDynamicsModel and CellularAutomata exported as public API with zero test coverage** (Lane: mods-risk-sec-sim-space-spm) — Evidence: `__init__.py:14-15,24-25`; `paradigms/system_dynamics.py:40-190`, `cellular_automata.py:15`; no test file references either. Next step: author test_system_dynamics.py (flow-rate resolution, integration, clamping, reset determinism) and test_cellular_automata.py (transition rule, grid evolution, boundaries). Probe: both files pass. Effort: S

**GS19-81 · MINOR · RISK · geo-infer-bayes declared simultaneously as required dep, optional 'integrations' extra, and optional guarded import** (Lane: mods-risk-sec-sim-space-spm) — Evidence: `pyproject.toml:45,49-52,57` vs guarded imports `civic_intel.py:26-34`, `core/risk_engine.py:70-73` and `__init__.py:26-28` ("a failure is a real packaging bug"). Next step: demote to the integrations extra only (matching the guarded design) and correct the __init__ comment — or keep required and delete the stubs. Probe: importlib.metadata requires() shows bayes only under the extra. Effort: S

**GS19-82 · MINOR · SPACE · Package __init__ nulls PlaceAnalyzer/SpatialUtils/GISManager on ImportError via unreachable fallbacks that mask packaging bugs** (Lane: mods-risk-sec-sim-space-spm) — Evidence: `__init__.py:31-78` (ImportWarning is default-filtered; guarded modules import only declared hard deps); RISK's explicit opposite policy at `__init__.py:26-28`. Next step: make the three imports unconditional (RISK policy) or switch to default-visible warnings + fail fast on nulled use. Probe: broken-internal-import scratch experiment raises. Effort: S

**GS19-83 · MINOR · TRANSPORT · docs document a RoutingEngine.route() signature that does not exist (mode/avoid/via) — quickstart example crashes with TypeError** (Lane: mods-test-time-transport-water) — Evidence: `docs/api_reference.md:106-117`, `docs/getting_started.md:117-122` vs `core/routing.py:87-93`. Next step: rewrite both to the real signature; cross-check remaining signatures in the page. Probe: lane signature+example probe. Effort: S

**GS19-84 · MINOR · TRANSPORT · Docs promise enumerated options the code rejects (model_type akcelik/hcm), a folium extra that is not declared, and a stale 0.2.0 version** (Lane: mods-test-time-transport-water) — Evidence: `docs/api_reference.md` (TrafficAnalyzer table) vs `core/traffic.py:78-85`; `docs/getting_started.md:13,20` vs pyproject (no folium anywhere) and __version__ 0.3.0. Next step: single doc-truth pass over both files. Probe: lane probe set. Effort: S

**GS19-85 · MINOR · TEST/GOVERNANCE · Module-local TODO marker survives in validate_packaging.py because the task-marker gate's own scan globs cover only src/ and tests/** (Lane: mods-test-time-transport-water) — Evidence: `validate_packaging.py:14` ("TODO REL-01") vs `validate_repo_contracts.py:60-64` (TASK_MARKER_SCAN_GLOBS = src+tests only). Next step: rephrase to cite the ledger row without the token; extend TASK_MARKER_SCAN_GLOBS to module-root scripts. Probe: marker absent + validator green. Effort: S

**GS19-86 · MINOR · TEST · TestDiscoverer's 'general' bucket double-counts every nested test file, contradicting its own comment and inflating statistics** (Lane: mods-test-time-transport-water) — Evidence: `core/test_discoverer.py:143-146,157,295-298,282-294` (recursive rglob re-lists unit/integration files into 'general'). Next step: make the general pass non-recursive or subtract bucketed paths; regression check in test_test_discoverer.py. Probe: general count == files directly under tests/. Effort: S

**GS19-87 · MINOR · TEST · module_health.DependencyChecker yields false 'missing' dependency verdicts (extras not stripped, wrong import-name mapping) and SystemValidator's floor is Python 3.9** (Lane: mods-test-time-transport-water) — Evidence: `core/module_health.py:196-202,244-251,255-257,135` ('coverage[toml]' probed as a module; pyyaml→'pyyaml' not 'yaml'; MIN_PYTHON (3,9) vs >=3.11). Next step: strip extras; add the distribution→import map; raise MIN_PYTHON to (3,11); update test_module_health.py. Probe: lane probe returns no missing deps where installed. Effort: S

**GS19-88 · MINOR · WATER · Ships two dead subpackages: geo_infer_water.utils and geo_infer_water.api are docstring-only and referenced nowhere** (Lane: mods-test-time-transport-water) — Evidence: both `__init__.py` are 3-line docstring stubs; package __init__ wires everything from .core; zero references module-wide. Next step: delete both directories (pure deletion, zero call-site migration). Probe: wheel build + WATER suites green. Effort: S

## Lane index

| Lane | Items filed |
| --- | --- |
| ci-gates | GS19-01, 02, 03, 21, 22, 23, 24 |
| packaging | GS19-04, 05, 25, 26, 27, 28, 29 |
| docs-truth | GS19-30, 31, 32, 33 |
| test-estate | GS19-06, 34, 35, 36, 37, 38, 39 |
| pipeline-perf-sec | GS19-07, 40, 41, 42, 43, 44, 45 |
| mods-act-agent-ai-ant-api | GS19-08, 09, 10, 46, 47, 48 |
| mods-app-art-bayes-bio-civ | GS19-49, 50, 51, 52, 53, 54 (+ folded into GS19-20) |
| mods-climate-cog-comms-data-econ | GS19-55, 56, 57, 58 |
| mods-edu-emergency-energy-examples-forest | GS19-59, 60, 61, 62, 63, 64, 65, 66 |
| mods-git-health-insurance-intra-iot | GS19-11, 12, 13, 14, 67, 68 |
| mods-log-marine-math-metagov-norms | GS19-15, 16, 69, 70, 71, 72, 73, 74 |
| mods-ops-org-pep-place-req | GS19-17, 18, 75, 76, 77, 78, 79 (+ folded into GS19-20) |
| mods-risk-sec-sim-space-spm | GS19-80, 81, 82 (+ folded into GS19-20) |
| mods-test-time-transport-water | GS19-19, 83, 84, 85, 86, 87, 88 |

## Execution order

Release-scale first, then fleet hygiene, then module code-truth. Wave 1
proposal (3 parallel lanes, disjoint file ownership — herdr
max_parallel_threads=3):

- **Lane 1 `release-ci`** (workflows + TEST governance): GS19-01 (durable
  half), 02, 03, 06, 21, 22, 23, 24, 36, 85. Files: `.github/workflows/*`,
  `GEO-INFER-TEST/{check_coverage_floor,rewrite_readme_agents,tests_lint_metric,validate_test_contracts,validate_packaging}.py`,
  `GEO-INFER-TEST/tests/conftest.py`, `GEO-INFER-TEST/docs/secret_scan_policy.md`.
  GS19-01's release *recovery* (re-run failed jobs) is an owner-authorized
  `gh` action, not lane work.
- **Lane 2 `packaging-metadata`** (45-module packaging + release-adjacent
  fixes): GS19-04, 05, 11, 25, 26, 27, 28, 49, 50, 69, 74. Files: module
  pyprojects/requirements/setup.py/Dockerfile/compose, uv.lock (via uv),
  egg-info deletions, tracked-pyc untrack.
- **Lane 3 `code-truth`** (silent fallbacks/security): GS19-07, 41, 42, 43,
  44, 45, 55, 58. Files: AG/AI/LOG/AGENT/SPACE/DATA/OPS/COMMS/COG/CLIMATE
  src+tests.

Waves 2+ cut from the remainder in tier order: Medium module blocks
(GS19-08/09/10 AGENT+API docs, 12-14 IOT/INSURANCE/HEALTH, 15/16 LOG/NORMS,
17/18 PEP, 19 TEST docs), then the Minor docs-truth batch (20, 21→done in
wave 1, 30-33, 59-64, 76-79, 83-84), then module test-gaps (65, 67, 80) and
runner/metadata fixes (35, 38, 39, 86, 87, 88).
","path":"/Users/hum/Documents/GitHub/HumOS/projects/outside_of_hum/GEO-INFER/SCOPE-2026-09-19.md"}
