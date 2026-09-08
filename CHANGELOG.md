# GEO-INFER Changelog

All notable changes to the GEO-INFER framework will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Deep horizon 2026-09-07 - maintenance-script conformance

- Close the HYG-05 drift: canonicalize the 10 non-canonical scripts under
  `GEO-INFER-INTRA/scripts/` with one bounded `ruff format` pass
  (`>=0.15.6,<0.16`), verified semantics-preserving by AST-dump equality on
  all 13 files in the scope.
- Convert the three E722 bare `except:` handlers (`audit_agents_docs.py`,
  `migrate_to_uv.py`) to `except BaseException:` — identical runtime
  semantics to a bare except, so no behavior change.
- Settle DOCS-04: `.aii/config.yaml` `tasks.test.cmd` now runs
  `uv run python GEO-INFER-TEST/run_unified_tests.py --category unit`
  instead of bare `python -m pytest`, matching the AGENTS.md test-command
  surfaces and the CI unit lane.
- Close HYG-06: delete the obsolete generator
  `update_documentation_signposts.py` (uninvoked dynamic orphan — CI runs
  only the canonical `rewrite_readme_agents.py --check`) and regenerate its
  generated README/AGENTS listings; no dangling references remain.

### Deep horizon 2026-09-07 - geo-code01 index refresh

- Refreshed the CODE-01 GitNexus index in the geo-code01 worktree: `gitnexus
  analyze` (GitNexus 1.6.9) indexed the tree at
  `61f697fc84f3070edeab8da80a3db7212bb086fd` (4,162 files, 64,530 nodes,
  90,952 edges, 1,623 clusters, 300 flows, no embeddings), wrote the local
  `.gitnexus/` store (now gitignored) and registered the repository in
  `~/.gitnexus/registry.json`. Indexed/current-commit parity and the
  explicit-file Gaussian-contract (`validate_gaussian_artifact`) and
  sparse-transition (`SparseTransitionArtifact`) lookups verified through
  `gitnexus context -r GEO-INFER`. `analyze` rewrites the AGENTS.md/CLAUDE.md
  context sections and creates `.claude/`; both were restored to the canonical
  generator output.
- Added the dated pre-rewrite history note to ISA.md: its recorded SHAs
  (including `fc62502c`, `cee1b5f0…`, `b45f108…` and the GNN-side
  identifiers) are historical after the published-history identity rewrite,
  and TODO.md and CHANGELOG.md already carried the note while ISA.md did not.
  All 12 historical identifiers in ISA.md are now covered by a file-level
  note, consistent with the other two ledger surfaces.
- Extended the dated pre-rewrite history notes to the two GEO-INFER-TEST GNN
  receipt files (`gnn_continuation_2026_09.md`, `gnn_space_time_2026_09.md`;
  22 further historical identifiers now covered), hardened the
  `autoresearch.sh` benchmark (ellipsis-truncated content digests excluded,
  receipt SHA must be a HEAD ancestor, dated-note requirement), and recorded
  the indexed branch name in the CODE-01 receipt.
- CODE-01 acceptance reconciliation: the Gaussian exporter lives in the GNN
  repository (artifacts are exported in a separate GNN environment per the
  continuation receipt), so the GEO-side explicit-file lookup target is the
  Gaussian contract surface (`validate_gaussian_artifact` /
  `GaussianGNNArtifact`), verified through the index receipt.

### Deep horizon 2026-09-07 - geo-render-lane

- Delivered the permanent in-repo CI render lane (ROOT-01): the manuscript
  job renders the manuscript in-runner through the repository's own render
  path (`scripts/render_manuscript_pdf.py`: generator hydration,
  published-section combine with the image-target-scoped figure-prefix
  rewrite, preamble injection, pandoc, XeLaTeX to a clean final pass) and
  then runs the 7 render-dependent root tests the main job excludes
  (6 × `test_manuscript_pdf_layout.py` plus the deselected paths test);
  receipts (PDF, combined document, LaTeX source, final log) upload as
  artifacts. The union of the tracked CI selections covers all 109 root
  tests per PR.
- The render pins the template text block to the measured geometry
  (430.00462 × 556.47656 pt), wraps code-block lines at spaces via fvextra,
  forbids 1-3-line widow/orphan remainders, and raises tolerance with 8em
  emergency stretch for the runner TeX's denser line breaking of
  machine-token paragraphs; LaTeX `!` errors, `Missing character` reports,
  and missing artifacts fail the build. The runner toolchain is a minimal
  fail-closed apt set plus a sha256-pinned pandoc 3.11 / pandoc-crossref
  0.3.25 pair.
- Added the ROOT-01 benchmark harness (`autoresearch.sh` +
  `GEO-INFER-TEST/render_lane_metric.py`): it collects the root battery,
  replays every tracked workflow's pytest selection through real pytest
  collection, and reports the union of collected test ids
  (`ci_root_tests_covered`, 102 → 109) plus local render-path health
  (`render_dependent_tests_local_passing`, 0 → 7).

### Deep horizon 2026-09-08 - tests hygiene (HYG-04)

- Cleared the module test suites' dead-import surface: the 398
  F401/F841/F811 hits (361 F401, 35 F841, 2 F811 across 214 files) in
  `GEO-INFER-*/tests` measured at the 2026-09-07 recount are 0, by the
  HYG-01 per-site method — pure dead imports and pointless assignments
  removed, sanctioned availability probes and deliberate re-exports
  preserved as redundant-alias re-exports (which F401 exempts), F841
  side-effect calls bare-called or underscore-prefixed. No `# noqa`, no
  test semantics changed; every touched file's test subset passes, and
  compileall plus full-suite collection cover the whole tree.
- Added the durable sanctioned-select gate to the ci.yml
  source-runtime-hygiene step: `ruff check GEO-INFER-*/tests --select
  F401,F841,F811` keeps the floor at zero.
- Extended the autoresearch harness (`autoresearch.sh` +
  `GEO-INFER-TEST/tests_lint_metric.py`) with the HYG-04 instrument:
  `tests_lint_hits` plus per-rule and top-file ASI diagnostics.

### Deep horizon 2026-09-08 - secret-scan gate (SEC-02)

- Added the fail-closed secret-scanning gate to ci.yml: gitleaks 8.30.1
  (sha256-pinned release tarball) scans the full git history on every pull
  request and every push to `main`; any non-allowlisted finding fails the
  job.
- Audited the 29 default-rule baseline findings (426 commits) site by
  site — none is a live credential: documented API examples, synthetic
  test-fixture credentials, and one historical untracked egg-info
  artifact. The committed `.gitleaks.toml` allowlists exactly those sites,
  file-path- and rule-scoped, each with a written justification.
- Documented the scan policy and the pre-rewrite-object rule in
  `GEO-INFER-TEST/docs/secret_scan_policy.md` (surfaced pre-rewrite
  objects are treated as historical, revoke-first, and recorded).
- Extended the autoresearch harness
  (`GEO-INFER-TEST/secret_scan_metric.py`) with the instrument:
  `secret_scan_findings` (29 → 0 after policy).

### Deep horizon 2026-09-08 - assessment-artifact banners (DOCS-03)

- Banner-marked all 27 tracked assessment artifacts (INTRA/EXAMPLES
  assessment_results plus the EXAMPLES documentation analysis) with a
  visible dated historical-artifact banner (markdown blockquote; JSON
  `_historical_artifact` key), so stale point-in-time snapshots —
  DEPENDENCY_ANALYSIS.md's wrong dependency counts,
  COMPREHENSIVE_DOCUMENTATION_ANALYSIS.md's contradicted claims — can no
  longer read as live guidance. The generated README/AGENTS pairs inside
  those directories are canonical generator output and are excluded.
- Recorded the recurring drift review: the per-commit
  `rewrite_readme_agents.py --check` in ci.yml is the cadence.
- Extended the autoresearch harness
  (`GEO-INFER-TEST/stale_assessment_metric.py`) with the instrument:
  `stale_assessment_artifacts` (27 → 0).

### Deep horizon 2026-09-08 - coverage floors (TEST-03)

- Measured per-module line coverage across all 45 modules (each module's
  unit and integration suites under pytest-cov, xdist -n 4; performance
  and system suites excluded and noted) and committed the baseline as
  `GEO-INFER-TEST/coverage_baseline.json` with a per-module floor =
  measured rounded down to the nearest 5 percent (rationale: floors catch
  coverage collapses, not refactor churn; sweep range 16.7-98.6).
- Enforcement is diff-scoped: `GEO-INFER-TEST/check_coverage_floor.py`
  re-measures only modules whose src or tests changed in the event and
  fails below the recorded floor; wired into ci.yml after the
  secret-scan step and proven both ways locally (raised floor exits 1,
  real floor exits 0).
- Extended the autoresearch harness
  (`GEO-INFER-TEST/coverage_baseline_metric.py`) with the instrument:
  `modules_missing_coverage_baseline` (45 → 0). The sweep script
  (`measure_module_coverage.py`) uses pytest-cov because plain
  `coverage run` cannot see xdist's execnet workers.

### Deep horizon 2026-09-08 - orchestrator coverage (EXAMPLES-01)

- Added the eight missing thin orchestrators (CLIMATE, EDU, EMERGENCY,
  ENERGY, FOREST, MARINE, TRANSPORT, WATER) on the delivered INSURANCE
  exemplar: `examples/module_orchestrators/<MOD>/scripts/run_orchestrator.py`
  plus `config/orchestrator_config.yaml` on the ACT pattern. Each drives
  one documented end-to-end operation through the module's real public API
  on deterministic synthetic data and was executed twice with exit 0 and
  byte-identical results; FOREST/MARINE real-data upgrades stay gated on
  the acquisition rule.
- Registry entries added to `generate_orchestrators.py`;
  `docs/index.md` gallery table and Examples-by-Module cross-reference
  updated — all 45 modules are now listed.
- Extended the autoresearch harness
  (`GEO-INFER-TEST/orchestrator_coverage_metric.py`) with the instrument:
  `modules_without_orchestrator_example` (8 → 0).

### Deep horizon 2026-09-08 - preview browser verification (DOCS-01)

- Executed the deferred browser verification of the 45 spatial preview
  cards with real Chromium (headless, Puppeteer) against a local server:
  all 45 pages load with Leaflet online, the map rendered, the static SVG
  fallback present, and zero console errors; accessible labels verified on
  every page.
- Cold-cache incognito CDN failure (unpkg.com and openstreetmap.org
  blocked at the CDP Fetch layer) degrades to the always-present
  `details#static-preview` SVG — the map container stays `display:none`
  via the page's own guard, zero page errors — and Enter on the details
  summary toggles the preview online and offline; the 375×667 viewport
  shows no horizontal overflow.
- Asset receipts recomputed from disk against all 45 manifests:
  180/180 artifacts match (sha256+bytes). The committed receipt lives at
  `GEO-INFER-INTRA/docs/modules/previews/verification/` (JSON + markdown +
  six printToPDF page versions; raster captureScreenshot is unavailable in
  the hidden headless browser, documented in the receipt).
- Extended the autoresearch harness
  (`GEO-INFER-TEST/preview_receipt_metric.py`) with the instruments:
  `docs01_verification_checks_open` (9 → 0) and
  `preview_receipt_mismatches`.

### September 7 root health and CI integration

- Run the root manuscript regression suite (102 of 109 tests) in the CI
  manuscript job after artifact verification; the render-dependent files stay
  scoped to the render lane (ROOT-01 in TODO.md). Convert the remaining
  `pytest.skip` calls in the root suites to explicit failures, matching the
  suite's no-skip policy.
- Harden declared dependency floors to post-CVE minima (urllib3>=2.0.6,
  requests>=2.31.0, aiohttp>=3.9.0, jinja2>=3.1.3) without moving the locked
  versions, add `pydocstyle` to the `all` extra, and drop its weaker duplicate
  `pymc>=4.0.0` pin.
- Retain system-test reports in CI and raise the test-job timeout to 60
  minutes; record the recurring CI-01 verification at `24c6741d`.
- Correct the module count (44 -> 45) left in SKILL.md, the INTRA developer
  and integration docs, the maintenance-script taxonomy comment and the `.aii`
  sidecar, and add INSURANCE to the SKILL.md and CLAUDE.md module tables.
- Stop tracking the three committed PLACE runtime region caches (root `cache/`
  and two `GEO-INFER-PLACE/locations/cascadia/**/cache/` copies, same cache
  key, all offline-regenerable); refresh the
  TODO.md ledger (dead ledger link, CODE-01 due note, new CI-02 and ROOT-01
  rows, HYG-03 receipt).
- Re-attribute all hum-side personal commit identities to docxology via a
  published-history rewrite across all branches; commit SHAs cited anywhere in
  the documentation before this date are pre-rewrite historical identifiers.
- Bound the CI ruff gate to `>=0.15.6,<0.16` across the workflow, the package
  extras and every documented command surface, reformat the six drifted
  manuscript suites, and land the safe action majors (setup-python v7.0.0,
  setup-uv v10.0.1, upload-artifact v7.0.1) after release-note review.
- Attribute the root package to docxology in the pyproject metadata.
- Re-render the manuscript via the docxology lane for this checkout (27
  pages, fail-closed green) and record receipts: all 109 root tests pass
  locally, including the 7 render-dependent ones.

### September 5 GNN, space/time and acquisition integration

- Add explicit GNN Gaussian and factored model contracts alongside categorical
  and H3 interchange, with bounded validation, source digests and reproducible
  inference traces. Preserve matrix axes, physical units and declared policies.
- Correct repeated observation conditioning during legacy policy evaluation;
  reject nonfinite policy scores and invalid covariance declarations.
- Add bounded sparse H3 transitions and conservative resolution transfers,
  including pentagons. Irregular temporal observations require explicit
  intervening actions and exact prediction counts.
- Extend source-backed regional display layers and the checksummed lower Smith
  envelope to 59 reaches. Supervise regional HTTP acquisition in an isolated
  process with a parent-enforced deadline and bounded cleanup.
- Pin the merged GNN companion revision. Run paired-contract and Linux/Windows
  import-probe checks on main pushes, and retain test-category artifacts before
  the unified runner cleans its output directory.
- Record verified main integration separately from physical GPU, complete browser,
  licensed-boundary and Windows regional-worker verification in [TODO.md](TODO.md).



### September 5 hardening ledger and compliance annex close-out

The September review ledger (`GEO-INFER-TEST/docs/hardening_2026_09.md`) and the
compliance annex (`GEO-INFER-TEST/docs/compliance_2026_09/`) were removed from the
working tree on 2026-09-05 as transient review artifacts. Their durable evidence is
preserved here and in the TODO.md CONSOL-01/COMPL-01 rows; the tracked ledger
remains restorable from git history. Verified annex shape: 46 audit-finding files
(44 modules plus `_ROOT.md` and `_BACKLOG.md`) and 46 fix-report files (43
per-module reports — MATH is the one audited module without a dedicated report —
plus 3 structural item reports).

**Verification record (from the ledger).** Baseline `fc62502c`: 8,213 pass / 16
failures (DATA wall-clock benchmark under concurrent load, SPACE numeric precision,
PLACE 14 absent-layer cases). Final pre-merge tree: 8,413 pass, zero failures.
Post-merge combined tree: 8,607 pass on Python 3.11.15 and 3.12.11 (44 modules).
Compliance wave on the unified runner: unit 44/44 → 45/45 after INSURANCE,
integration 44/44, performance 4/4, system 1/1, H3 2/2; repo contracts 0 errors /
0 warnings; skills 45/45 → 46/46; generated signposts 1,692 → 1,639 current. Model
reproducibility hash `d195004a4030f4362b0f9402b218a318864766f7f321ef77697a595db18f32dc`
on both interpreters. Post-consolidation wheel receipts supersede the pre-wave ones:
45 wheels, isolated-install import probes pass on 3.11 and 3.12 (macOS and Linux
ARM64 containers). Known limits: contract-validator 30s import probes can time out
for heavy modules (ANT, ART, IOT, MATH, RISK, INSURANCE) under concurrent load
(PERF-01); pre-wave isolated-install receipts described `b45f108`, not the current
tree.

**API migrations.** SPACE lazy device selection, float64 parity and honest
host-only H3 reporting; TIME real WebSocket/Kafka ingestion with replay and
event-time buffers ([migration guide](GEO-INFER-TIME/docs/streaming_migration.md));
PLACE resumable checksummed hydrography with the bundled 34-reach Smith River
excerpt; raster `map_algebra` restricted to an allowlisted AST (4096 chars / 128
nodes); 45 preview bundles with real H3 res-7 geometry; civic-intel core
canonicalized in BAYES; `geospatial_ai` moved to `geo_infer_ai.models.predictive`;
GEO-INFER-INSURANCE split from RISK.

**Compliance-wave per-module fixes.**

| Module | Fix | Evidence |
| --- | --- | --- |
| ACT | Model renamed `ActiveInferenceModel` → `BaseActiveInferenceModel`; runtime/optional deps split | `models/base.py` rename |
| AG | Examples verified; `carbon_rate` initialized; equal-area CRS (EPSG:6933) | `core/sustainability.py`, `core/field_boundary.py` |
| AGENT | SKILL rewritten to real `BaseAgent`/BDI/Telemetry; phantom `GeoAgent` removed | fixwave#3: snippets executed |
| AI | SKILL rewritten to real 10-class ML API; fake `SpatialPipeline` deleted | fixwave#4: import probes |
| ANT | Hard cross-module imports → guarded try/except; prerequisites downgraded | `core/agent_base.py` pattern |
| API | SKILL rewritten to real `create_app`; fake APIs removed | fixwave#6: import probes |
| APP | SKILL + guide to real AgentManager/BDI; phantom dashboard moved to Roadmap | fixwave#7 |
| ART | SKILL/api-spec to real 10-class API; fictional classes removed | fixwave#8: imports executed |
| BAYES | Unimplemented prior/hierarchical claims removed; guarded PyMC import | fixwave#9: import probes |
| BIO | SKILL/docs to real sequence/climate/soil API; 958-line phantom schema addressed | fixwave#10: smoke calls |
| CIV | SKILL to real attendance/participation API; fake integrations removed | fixwave#11: smoke calls |
| CLIMATE | SPI gamma fix; real Thornthwaite PET; examples rewritten | fixwave#12: 110 passed |
| COG | `analyze_decision` return blocker fixed; same-package fallbacks removed | `decision/support.py` |
| COMMS | SKILL to real broker/router API; JWT policy documented honestly | fixwave#14: HS256, invalid → 401 |
| DATA | SKILL to real ingestion/ETL/storage API; all 20 findings addressed | fixwave#15: 357 passed |
| ECON | SKILL/examples to real market-design + spatial-econometrics API | fixwave#16: examples verified |
| EDU | Competency ordinal-compare fix; real GIS&T BoK standards | `core/progress.py` |
| EMERGENCY | SKILL to real 5-class API; phantom SAR APIs deleted | fixwave#18: examples run |
| ENERGY | SKILL to real 8-class renewable API; phantom LCOE/site-selector modules deleted | fixwave#19 |
| EXAMPLES | Fake snippets → real APIs; orchestrator fixed; tests added | fixwave#20: 78 passed, demos exit 0 |
| FOREST | SKILL/docs to real API; vectorized fragmentation; packaging trimmed | fixwave#21: 95 passed |
| GIT | `CloneConfig` subscript fix; `api/__init__` restored; schema rewrite | fixwave#22: 131 passed |
| HEALTH | SKILL to real symbols; CLI/env-analysis implemented | fixwave#23: 218 passed |
| INTRA | Phantom module references removed; schema via `importlib.resources` | fixwave#24: 51 passed |
| IOT | `BayesianSpatialInference` → `core.inference`; circular imports fixed | fixwave#25: 114 passed |
| LOG | `get_all_metrics` deadlock fixed; duplicates removed; CBC on arm64 | fixwave#26: 79 passed |
| MARINE | Coriolis guard consolidated; NaN priority guard; empty `api/` deleted | fixwave#27: 94 passed |
| METAGOV | Dead `models/` deleted; entity support fixed; `bounds_to_polygon` implemented | fixwave#29: 150 passed |
| NORMS | Missing deps declared with upper bounds; `setup.py` → shim | fixwave#30 |
| OPS | SKILL to real API; phantom `/backup` endpoints removed; `CacheConfig` added | fixwave#31: 161 passed |
| ORG | Phantom OpenAPI spec → design note; IRV tabulation; capacity weighting | fixwave#32: 97 passed |
| PEP | Fictional CRM → real 18-name API; shared `data_store` | fixwave#33: 84 passed |
| PLACE | Fictional backends removed; lazy `LOCATION_PRESETS`; outputs out of source tree | fixwave#34: 182 passed |
| REQ | P3IF fiction removed; 21-export `__all__`; canonical cycle detector | fixwave#35: 76 passed |
| RISK | geopandas/shapely declared; missing `__init__.py` packages created (wheel safety) | fixwave#36: 263 passed |
| SEC | RFC 6238 TOTP MFA (bypass closed); `password_salt` field fix | fixwave#37: 288 passed |
| SIM | SKILL to real surface; checkpoint RNG reproducibility | fixwave#38: 67 passed |
| SPACE | Synthetic-demo labeling; dead fallback flags removed; haversine dedup | fixwave#39: 152 passed |
| SPM | Broken `utils.visualization` import fixed; pymc3 → pymc | fixwave#40: 120 passed |
| TEST | Phantom `[project.scripts]` removed; 10 unused deps → extras | fixwave#41 |
| TIME | statsmodels hard dep; forecast dedupe; `decompose` raises; `inference_schedule.py` added | 497 passed |
| TRANSPORT | SKILL to real class-method API; dead `EmissionsCalculator` removed | fixwave#43: 103 passed |
| WATER | Mass-conserving `rainfall_runoff`; canonical `water_balance_closure` | fixwave#44: 84 passed |

**Structural item reports.** `item1.md`: underwriting split RISK → INSURANCE (RISK
251 + INSURANCE 22 pass); `item-1.md`: `geospatial_ai` extraction ACT → AI (AI 114 +
ACT consumers 12 pass); `item1-civic-intel-consolidation.md`: civic-intel
canonicalization (BAYES 317 + 7 cross-module tests pass). The three similarly-named
files are distinct fixes, not duplicates.

**Audit shape.** ~53 blocker findings across 31 module files; dominant categories:
fictional/planned-API advertising in SKILL.md and docs (~25 modules),
dependency-ledger errors in both directions, wheel-exclusion packaging defects
(missing `__init__.py`, broken entry points, version drift), fake connectors and
fallbacks, and committed build artifacts. Finding files carried no per-finding
status markers; the fix table above is the resolution evidence. `_BACKLOG`'s open
rows (SPACE-01 hardware, DOCS-01 browser, TEST-02 Windows, CI-01 hosted CI,
PLACE-02/-V14 acquisitions) remain tracked in TODO.md.

**Hosted verification (CI-01) executed at `e87c7703`.** The GNN interchange
merge initially broke all three hosted workflows; each attributable failure was
diagnosed and fixed in-flight: `uv.lock` resolved against the consolidated
dependencies (`c4586205`), companion docs regenerated post-merge (`1655b7b1`),
the post-reorg INSURANCE governance pin committed into the generator
(`24c4bf81`), the generator canonicalized under ruff format (`da9c9453`), and
INTRA package-data aligned with the repo-wide resource-glob convention
(`e87c7703`). GEO-INFER CI (quality gate, repository contracts including
packaging, full per-module pytest battery on Python 3.11/3.12 Linux x86),
import-probe portability, paired GNN interchange and dependency-graph jobs all
pass at that SHA.

### September 5 hygiene, completion and report-cleanup wave

- HYG-01 executed as a cleanup wave: repo-wide F401/F841/F811 hygiene sweep,
  1,030 measured hits → 0 across 44 packages, with a per-site audit before
  every deletion (side-effect imports, try/except availability probes and
  externally-imported names preserved as redundant-alias re-exports; unused
  locals removed only where the RHS was pure, side-effect calls kept as bare
  calls; shadowed redefinitions removed). The sanctioned F821/F823/E721/E722
  gate and `compileall` are clean post-wave. Two real defects surfaced and
  were fixed en route: COMMS `rest_api.py` broadcast_message kept its live
  `user_id` assignment (a bare-call conversion had broken authenticated
  sender attribution; restored verbatim — the sanctioned gate caught the F821),
  and MATH `utils/parallel.py` restored a broken f-string progress log line.
- DOCS-02 completed: `geo-infer-insurance.md` conceptual page
  (template-consistent, real API only), INSURANCE row in the INTRA
  modules/index.md catalog, 45th deterministic preview bundle generated via
  the sanctioned builder (the 44 pre-existing bundles verified
  sha256-identical), EXAMPLES gallery + orchestrator-registry entries, and a
  thin INSURANCE orchestrator running the real assess → underwrite → premium
  → claim flow end-to-end.
- Tests: INSURANCE gains its first integration suite (deterministic
  underwrite → policy → claim end-to-end over the public API); TEST gains a
  bundled-seed uniqueness test pinning the true invariant — all bundled
  Crescent City seed copies are byte-identical, so first-match resolution is
  deterministic, and the BAYES packaged loader yields the same schema-v1
  contract.
- IOT: the 1,365-line monolithic `geo_infer_iot/__init__.py` extracted to
  `core/systems.py` (84-line `__init__` re-exporting the identical 38-name
  public surface, verified set-equal before/after); 107 IOT unit tests pass.
- HYG-02 executed: untracked runtime artifacts removed (GEO-INFER-RISK
  `outputs/`, GEO-INFER-NORMS `examples/output/`, and 18 stale `__pycache__`
  files for moved or deleted sources); zero tracked-file changes.
- Transient agent-cycle reports deleted (deep_review_2026_09_05.md plus three
  stale tracked assessment/execution reports) with references cleaned; the
  September review ledger and its compliance annex remain the durable
  evidence record. `manuscript/README.md` was resynced by the sanctioned
  writer (+1 line: the final generator inventory lists
  `refresh_config_metadata`); generated signposts 1639/1639 current.

### September 5 structural consolidation and wheel-receipt wave

- Executed the three recorded consolidation candidates. Civic-intel: the shared
  Crescent City ingestion core (schema constant + contract resolver + the single
  bundled `crescent-city-geo-intel.json`) is canonical in GEO-INFER-BAYES; ACT
  and RISK resolve the same objects via guarded delegation (identity pinned by
  cross-module tests) and keep their module-specific surfaces, so each
  consumer still computes when a sibling is absent (PLACE degradation test
  passes unchanged). `geospatial_ai`: the 1626-line spatial-ML toolkit moved
  verbatim from GEO-INFER-ACT/utils to
  `geo_infer_ai.models.predictive.geospatial_ai` with its 22-test suite; ACT
  dropped scikit-learn and gained a workspace dep on geo-infer-ai. Underwriting:
  split out of GEO-INFER-RISK into the new 45th module GEO-INFER-INSURANCE
  (underwriting engine, decisions, rules, pricing, policy, claims, portfolio,
  compliance), with all module-count pins updated (validators, INTRA
  MODULE_PROFILES and index, TEST ecosystem test, CLAUDE.md, ISA.md).
- Rebuilt wheel receipts on the final tree: 45 source-matching wheels with
  isolated-install import probes on Python 3.11 and 3.12
  (`build_package_wheels.py --verify`), both exit 0.
- Cleaned the remaining 12 source-language debt hits to zero warnings by
  rewording honest prose (cloud/stream connectors, SIM toy models, SPACE
  synthetic labeling, TRANSPORT bbox docs, AGENT $CONFIG docs); no behavior
  changed.
- Full gate suite on the final tree: unified unit 45/45, integration 44 (no
  failures; INSURANCE ships unit tests only), performance 4/4, system 1/1,
  H3 2/2; repo contracts 0 errors 0 warnings (on an idle host; import-probe
  30s timeouts for heavy modules appear only under concurrent load and remain
  PERF-01); skills 46/46; ACT contract, model contracts (seed 42), model
  audit, ruff F821/F823/E721/E722 all clean; generated signposts 1639/1639
  current.
- INSURANCE starts at 0.1.0 while the other modules remain 0.2.0; version
  alignment is a release decision (CI-01), not assumed here.

### September 5 repository-wide compliance and coherence wave

- Ran a 47-report per-module audit (44 modules + import-graph, backlog, and root
  surfaces) against runtime, packaging, documentation, and test contracts; fixed
  all blocker and major findings per module with behavior-pinning regression
  tests. Every module suite passes locally (details in the review ledger).
- Rewrote 30+ SKILL.md files and ~20 broken example scripts against the real
  public APIs; removed all advertised-but-nonexistent APIs (planned capabilities
  now carry explicit "Roadmap (not implemented)" notes with no code snippets).
- Fixed real code defects, including: an OPS CacheManager/Config schema mismatch,
  a LOG metrics deadlock, COMMS JWT-fallback auth bypass, SEC MFA bypass (now
  RFC 6238 TOTP), BAYES Poisson-likelihood factorial error, COG analyze_decision
  returning None, GIT CloneConfig subscript crash, RISK wheel-excluded
  subpackages (missing __init__.py), EDU progress-export/level-comparison bugs,
  IOT permanently-disabled Bayesian inference API, and CLIMATE broken drought
  run detection and quantile mapping.
- Normalized packaging: every setup.py reduced to a thin shim delegating to
  pyproject (canonical surface); removed all phantom console entry points
  (AGENT, SEC now have real scripts); undeclared runtime dependencies added and
  unused heavy dependencies pruned or moved to documented optional extras
  (torch/tensorflow in AI, pytest-in-runtime in API, 10 unused test tools in
  TEST, etc.); requirements.txt files synced to pyproject.
- Declared previously undeclared cross-module dependencies (ACT->space/time,
  IOT->bayes/space, RISK->bayes/data/math/space/time, and 8 more) via
  [project.dependencies] + [tool.uv.sources] workspace pins or documented
  integrations extras; removed BIO's phantom declarations.
- Replaced fabricated data with real behavior: SPACE place_analyzer now labels
  synthetic analysis explicitly, TRANSPORT equity coverage computes from zone
  demographics, COMMS spatial routing no longer fabricates recipients, IOT
  adaptive sampling derives candidates from coverage gaps, SEC threat
  indicators load from configurable YAML.
- Deleted dead/stub surfaces: WATER WatershedAnalyzer (real D8 owner is
  WatershedDelineator), OPS core/backup duplicate package, ANT empty api/models
  subpackages, REQ/MARINE/ORG/EDU empty shell subpackages, AG's fake-fallback
  mock blocks, placeholder `assert True` tests in COMMS/LOG/SIM/TRANSPORT.
- Replaced fabricated geodesy with correct projections: AG field areas in
  EPSG:6933 equal-area, metric-CRS buffering/distances, RISK spatial-correlation
  cos(lat) scaling, IOT interpolation unit fix.
- Updated AG/edu-style phrasing in root docs where commands or counts changed;
  CI now runs the `system` test category alongside unit/integration/performance.
- Deleted empty stray root directories (`repos/`, `del_norte_dashboard/`) and
  fixed the PLACE cwd-relative dashboard default that created them.


- Deliver real WebSocket/Kafka ingestion with explicit replay and acknowledgements
  after processing; preserve upstream adapter injection and broker timestamps.
- Add lazy GPU capability checks, bounded float64 spatial kernels and explicit
  host-only H3 topology diagnostics. Physical GPU validation remains deferred.
- Package resumable, checksummed USGS hydrography acquisition and a 34-reach lower
  Smith River pilot; retain explicit missing-data, offline and projection controls.
- Regenerate all 44 H3 preview bundles with deterministic geometry/assets,
  illustrative-data labels, provenance and an offline fallback.
- Replace unrestricted raster expression execution with a bounded allowlisted AST;
  reject filesystem access, output mutation and incompatible raster alignment.
- Verify fresh wheel metadata, code and resources; require complete isolated-import
  receipts and terminate timed-out process groups. Keep dependency parity and
  passive-logging gates from the upstream integration.
- Align runtime versions with distribution metadata, fix CI formatting and merge
  the upstream fix wave without rewriting published history.
- Document API migrations and separate deferred verification from regional data
  acquisition in [TODO.md](TODO.md). Pre-merge and combined-tree evidence and
  platform limits are preserved in the September 5 hardening close-out section
  below.

### Added

- A dated validation receipt for the 2026-08-13 performance and isolated
  module-coverage campaign, including failed-attempt evidence, optional-backend
  availability, artifact digests, and the all-extras CuPy build boundary.
- Typed, redacted email-provider delivery failures and regression tests for
  SMTP, SendGrid, and AWS SES integrations.
- A deterministic Cascadia validation profile shared by the focused and
  comprehensive compatibility entry points.
- Documentation hub refresh covering installation, first spatial inference,
  architecture, module selection, H3 v4 usage, developer workflow, testing,
  and contribution guidance.
- Root documentation map linking conceptual INTRA guides to source-backed
  module README/SKILL files and executable GEO-INFER-TEST gates.

- Unified test runner `GEO-INFER-TEST/run_unified_tests.py` with `--module`, `--category`, and `--h3-migration` flags
- Cross-module integration tests covering SPACE↔TIME, AGENT↔ACT, and DATA↔API interactions
- `WATER` module WQI calculation and 2D Gaussian pollution plume modeling
- `MARINE` module ocean monitoring, Blue Carbon estimation, and Marine Protected Area analysis
- `FOREST` module NDVI health monitoring, wildfire risk index (FWI), and carbon sequestration
- `ENERGY` module renewable site suitability mapping and LCOE benchmarking
- `CLIMATE` module climate change adaptation modeling with Bayesian uncertainty quantification


### Changed and Fixed (2026-09-02 fix wave)

- Merged `codex/act-categorical-runtime` hardening into `main`; the
  2026-09-02 fix wave then applied real-implementation, contract, and
  hygiene corrections across all modules, with the repository validators
  (`validate_test_contracts.py --strict`, `validate_model_contracts.py
  --strict --seed 42`, `run_model_audit.py --seed 42 --reproducible`,
  `validate_active_inference_contract.py`) re-run against the result.
- **MATH**: replaced simplified numerics with real implementations for
  kriging, CP and Tucker tensor decompositions, BA estimation, and theorem
  verification; added a unified Moran variance implementation used across
  the spatial-statistics paths.
- **DATA**: added SQL/GraphQL identifier validation on query surfaces and
  restricted decompression to envelope payloads only.
- **API**: required `SECRET_KEY` for signed operations and hardened CORS
  configuration.
- **TIME**: replaced mock stream transports with real WebSocket and Kafka
  adapters behind the optional `streaming` extra (`websockets`, `aiokafka`).
- **EMERGENCY**: replaced simplified evacuation routing with a real
  `networkx`-based routing implementation.
- **SIM**: fixed the pause/resume state machine so transitions respect the
  declared run states.
- **LOG**: restored compatibility with `networkx` 3.x APIs.
- **RISK**: implemented the previously missing-but-advertised `api`
  (`RiskAPI`, `ModelRegistry`, `ResultsFormatter`) and peril-model export
  surfaces against the existing engine, with export-contract tests.
- **ECON**: removed duplicate shadowing class definitions and the undefined
  `ConsumerTheoryModels` export so every `__all__` name resolves.
- **COG**/**AI**: threaded deterministic seeded `np.random.Generator`
  instances through stochastic code paths.
- **OPS**: reduced module-level logging to a single `getLogger(__name__)`
  entry point.
- **HEALTH**/**CLIMATE**/**MARINE**/**TRANSPORT**/**FOREST**/**EDU**/**WATER**:
  module-specific real-implementation, contract, and hygiene fixes from the
  same fix wave.
- **EXAMPLES**: replaced placeholder orchestration scripts with real
  end-to-end module orchestrators.

### Changed

- The unified coverage runner now executes each module in an isolated pytest
  subprocess, rejects skips/xfails from JUnit evidence, emits aggregate
  coverage JSON, and removes stale per-module receipts before a run.
- GEO-INFER-AI spatial feature transforms reuse the training centroid and
  clear it on a coordinate-free refit; RISK cross-validation now evaluates a
  fitted mean-loss baseline per fold and validates finite samples.
- Cascadia configuration and validation no longer depend on the caller's
  working directory; the ownership data source resolves its tracked URL
  configuration from the framework root.
- **PEP 8 package naming normalization completed** — all 44 modules now use lowercase `geo_infer_<module>` package directories (`geo_infer_forest`, `geo_infer_marine`, `geo_infer_energy`, `geo_infer_water` included). Stale docs referencing mixed-case paths corrected.
- **TIME module**: `sklearn` now guarded with a `HAS_SKLEARN` flag and `LinearRegression` raises an actionable `RuntimeError` when unavailable; `requirements.txt` lists `scikit-learn>=1.6.1` to match `pyproject.toml`.
- **BAYES module**: Full-rank variational inference now uses a scalar Cholesky covariance approximation; vector-valued full-rank parameters raise a clear `ValueError`, while mean-field inference remains available for vector parameters.
- **COMMS module**: REST models now use the repository's Pydantic v2/FastAPI contract, preserve intentional HTTP errors, and isolate per-instance CORS configuration.
- **Repository toolchain**: Module-level mypy configurations now target the supported Python 3.11 baseline consistently.

### Fixed

- Removed stale COMMS integration exports for modules that do not exist and
  corrected MIME imports used by real email attachments.
- Replaced vacuous/skipped Cascadia validation scripts with strict real
  backend, H3, configuration, and module-initialization checks.
- Corrected the INTRA system-test workspace root, removed a wall-clock HEALTH
  assertion, and made root matplotlib cleanup explicit and test-covered.
- Strict repository terminology no longer mistakes completed SIM acceptance
  evidence for module-local planned work.
- Documentation drift: README, CLAUDE.md, AGENTS.md and module-level docs updated to reflect completed lowercase normalization.
- Replaced stale INTRA navigation and examples that referenced nonexistent
  API, deployment, workflow, and package paths with current repository links.
- WATER pollution plume dispersion now derives its grid extent from
  `grid_resolution`, computes `plume_area_km2` from the actual grid cell size
  instead of the nominal resolution, and guards zero diffusion/time so
  concentration fields stay finite and the reported area is no longer
  underestimated.

---

## [0.2.0] - 2026-02-25

### Added

- PAI Algorithm integration (`PAI.md`): 7-phase OBSERVE→LEARN methodology for GEO-INFER development
- `GEO-INFER-SPM`: Statistical Parametric Mapping module (spatial GLM, random field theory)
- `GEO-INFER-EXAMPLES`: Cross-module integration demonstrations and entry-point tutorials
- Root-level `.agents/` directory with framework-wide development rules and standards
- Backend-agnostic spatial dispatch pattern (`SpatialIndexingInterface`) in SPACE module

### Changed

- **SPACE module**: Fully migrated to H3 v4 API (`latlng_to_cell`, `cell_to_latlng`, `geo_to_cells`)
- **PLACE module**: Fully migrated to H3 v4 API (FULLY MIGRATED status)
- **Environmental modules**: Groundwork for lowercase package dir normalization landed (completed in Unreleased).
- **Zero-Mock Policy**: Enforced across all 44 modules — every function has real algorithmic logic
- **BAYES module**: GaussianProcess upgraded to real Cholesky decomposition; model comparison uses LOO/WAIC/DIC/BIC/AIC
- **ACT module**: Free energy calculation hardened with proper NumPy array handling
- License standardized to CC BY-NC-SA 4.0 across all 44 modules
- All 44 modules now maintain minimum 4 test files (unit, integration, performance, system)

### Fixed

- Interpolation bug in `GEO-INFER-TIME` temporal analysis
- F-string formatting issues in `GEO-INFER-AI` and `GEO-INFER-COG`
- Import compatibility issues in `GEO-INFER-AGENT` and `GEO-INFER-ANT`
- 13 source bugs across applied domain modules (HEALTH, ECON, RISK, AG, BIO)
- 7 source bugs across governance modules (NORMS, METAGOV, SEC, COMMS)
- Zero illegitimate `pass` stubs (remaining `pass` only in abstract methods, exception handlers, import guards)

---

## [0.1.0] - 2026-01-26

### Added

- Initial release of GEO-INFER framework
- **Core Modules**:
  - GEO-INFER-ACT: Active Inference implementation
  - GEO-INFER-BAYES: Bayesian inference and probabilistic modeling
  - GEO-INFER-SPACE: Spatial operations and H3 indexing
  - GEO-INFER-TIME: Temporal analysis and forecasting
  - GEO-INFER-DATA: Data management and ETL
  - GEO-INFER-MATH: Mathematical foundations
  - GEO-INFER-AI: Machine learning and deep learning

- **Agent Framework**:
  - GEO-INFER-AGENT: Agent orchestration
  - GEO-INFER-ANT: Swarm intelligence
  - GEO-INFER-NORMS: Normative reasoning
  - GEO-INFER-METAGOV: Meta-governance

- **Domain Applications**:
  - GEO-INFER-AG: Precision agriculture
  - GEO-INFER-BIO: Biodiversity and ecology
  - GEO-INFER-CLIMATE: Climate analysis
  - GEO-INFER-ECON: Spatial economics
  - GEO-INFER-EDU: Educational technology
  - GEO-INFER-EMERGENCY: Emergency management
  - GEO-INFER-ENERGY: Energy systems
  - GEO-INFER-FOREST: Forest monitoring
  - GEO-INFER-HEALTH: Public health
  - GEO-INFER-LOG: Logistics and supply chain
  - GEO-INFER-MARINE: Marine analysis
  - GEO-INFER-RISK: Risk assessment
  - GEO-INFER-TRANSPORT: Transportation
  - GEO-INFER-WATER: Water resources

- **Infrastructure**:
  - GEO-INFER-API: API infrastructure
  - GEO-INFER-APP: Application development
  - GEO-INFER-COMMS: Communications
  - GEO-INFER-IOT: IoT integration
  - GEO-INFER-OPS: DevOps and operations
  - GEO-INFER-SEC: Security
  - GEO-INFER-TEST: Testing framework

- **Visualization & UX**:
  - GEO-INFER-ART: Cartographic design
  - GEO-INFER-COG: Cognitive spatial reasoning
  - GEO-INFER-CIV: Civic engagement
  - GEO-INFER-PLACE: Place-based analysis

- **Analysis**:
  - GEO-INFER-SIM: Simulation framework
  - GEO-INFER-SPM: Statistical parametric mapping

---

## Version History

| Version | Date | Description |
|---------|------|-------------|
| 0.2.0 | 2026-02-25 | Second beta release |
| 0.1.0 | 2026-01-26 | Initial release |

---

[Unreleased]: https://github.com/ActiveInferenceInstitute/GEO-INFER/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/ActiveInferenceInstitute/GEO-INFER/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/ActiveInferenceInstitute/GEO-INFER/releases/tag/v0.1.0
