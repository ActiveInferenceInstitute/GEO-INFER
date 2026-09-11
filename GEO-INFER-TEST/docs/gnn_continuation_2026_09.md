# Paired model contracts and regional evidence

This continuation starts at GEO `634b61b9` and GNN `92255b125`. Both isolated
worktrees were clean. The original concurrently edited repositories were
preserved. GNN includes the explicitly documented prior fleet ancestry.

> History note (2026-09-07): the published history was rewritten to re-attribute
> hum-side personal commit identities to docxology
> <docxology@users.noreply.github.com>. Every commit SHA recorded in this
> receipt before that rewrite refers to pre-rewrite history and no longer
> resolves; the recorded evidence and run results remain valid, only the
> identifiers changed.

## Delivered contracts

- ACT legacy perception and policy evaluation now condition each observation
  once. Policy-only calls preserve the posterior and evidence; repeated calls,
  normalized counts, local recovery and replacement models are tested.
- Gaussian v2 exports explicit discrete F/G/H/Q/R, coordinate units, initial
  mean/covariance and measured vectors. Unequal dimensions reproduce analytic
  posterior, covariance, prediction and evidence. Contradictory source axes and
  indefinite/overflowing covariances fail visibly. Filtering does not select
  continuous controls.
- Factored JSON declares ordered dependencies and explicit multi-step policies.
  The bounded exact joint filter preserves correlations and evaluates future
  observations conditionally. Policy priors match enumeration, zero support
  remains excluded, and numeric overflow raises before selecting an action.
- SPACE sparse CSC interchange validates before allocation and transfers H3
  probability mass conservatively across resolutions, including pentagons. A
  1261-state case works beyond the dense v1 limit without dense allocation.
- TIME irregular schedules require the actual intervening action history and
  exact prediction count; missing intervals never imply resampling.
- GNN Step 7 uses explicit metadata, original source digests and contained
  source/output paths through both the API and numbered CLI. Defaults remain
  the five existing formats.

## Evidence and review

| Check | Observed result |
| --- | --- |
| Fresh original ACT/SPACE/TIME baseline | 1574 passed on Python 3.12 |
| Expanded full ACT/SPACE/TIME suite | 1716 passed each on Python 3.11 and 3.12, no failures/errors/skips |
| Subsequent factored overflow closure | Original reproduction raises ValueError; 19 focused cases passed and are included in the final full suites |
| Standalone source/wheel process probes | 43 passed locally; Windows execution belongs to the new hosted workflow |
| Wheel installation | ACT, SPACE, TIME and PLACE built, installed and imported in a fresh environment; all seven expanded Smith resources are packaged |
| PLACE acquisition and actual renderer | 47 passed on each Python version after independent clipping/transport review; live acquisition and offline replay passed |
| Repository contracts | All ten native gates passed, including 44 imports with zero warnings and current generated signposts |
| GNN native checks | Ruff formatting/lint clean; mypy 945 source files clean; strict docs zero issues |
| GNN complete suite | 4142 passed, three optional-tool skips (PyTorch and D2), no failures/errors or warning summary |
| GNN focused integration | 330 export/utils cases, then 31 baseline-correction cases passed |
| Paired export/inference | Categorical, H3, Gaussian and factored artifacts exported in a separate GNN environment and consumed on both GEO Python versions |

The configured advisor responded. Independent reviewers reproduced and verified
fixes for dimensional clipping, nonfinite regional source numbers, double conditioning, covariance overflow, contradictory declarations,
symlink escapes, duplicate metadata, and factored numeric overflow. The Cato
wrapper could not use the repository ISA; a fresh-context direct adversarial
review substituted for that tool and independently verified the overflow fix.
GitNexus indexes were built for both repositories and used for impact/change
review. Final publication is evidenced by PR check runs and remote SHAs, not
by the state of the original shared checkouts.

## Regional data

The [expanded Smith River acquisition](../../GEO-INFER-PLACE/src/geo_infer_place/hydrography/data/smith_expanded/ACQUISITION.md)
contains 59 source reaches with frozen IDs, page/final checksums, reproducible
cache reuse and full topology diagnostics. It is an envelope selection, not a
whole-watershed claim.

[Regional display sources](../../GEO-INFER-PLACE/docs/usgs_regional_layers.md)
supply 24 volcanoes, 13 HU4 polygons and one named convergent boundary using
explicit land/offshore windows. Actual renderer tests retain the missing
whole-bioregion boundary notice. No licensed full-boundary vector was verified.

## Browser, hardware and environment limits

Interceptor in Chrome 152 loaded all 44 indexed preview HTML sources with valid
SVG labels and seven real H3 polygons per page. The ACT page loaded 12 map tiles
and exposed labeled, focusable zoom controls. Blocking external scripts on a
local test server left the TIME static SVG visible; click toggling worked. A
390-pixel iframe had no horizontal overflow and remained usable without Leaflet.
Native Enter behavior was not established by the available keyboard automation,
and its screenshot routine omitted iframe content; these are not counted as
complete native keyboard or narrow-screen screenshot verification.

Physical CUDA hardware is absent. Torch MPS availability does not establish the
required float64 CUDA contract. No GPU speed claims were made.

The prior PROJ SQLite failure did not recur in the full fresh suite. Current
Python 3.12.13, pyproj 3.7.1, PROJ 9.5.1 and SQLite 3.53.1 passed database
quick-check and coordinate conversion with descriptor count 4 before/after the
probe. This is evidence of current success, not an established historical cause.
Controlled cold/warm import-performance comparisons remain open.

## Publication

GNN companion revision: `89f3b5e7961aaadc5c8c5b842daeb1a5dface6c3`,
[PR 25](https://github.com/ActiveInferenceInstitute/GeneralizedNotationNotation/pull/25).
The GEO pairing manifest pins that immutable commit. Paired CI and Windows
portability workflows retain both revisions and test/artifact receipts. Package
releases and version tags are outside this change. Hosted GNN corrections add
entity-safe XML parsing and make the CI matrix select the declared interpreter;
183 targeted cases and 138 separate Python 3.12 cases passed, with Bandit clear
of medium/high findings.

Published GEO implementation: `b0c07568372191ffc71efd924e4f6c4525c9a4f2`,
[PR 8](https://github.com/ActiveInferenceInstitute/GEO-INFER/pull/8). Both topic
refs matched their remote SHAs. GNN hosted documentation, dependency, MCP,
security and CodeQL checks passed after the CI corrections; its test jobs and
GEO hosted jobs were still running when this publication receipt was written.
The first Windows probe run established child-process cleanup but exposed two
test-only Unix assumptions (path separators and line endings); the assertions
now compare native paths and exact original source bytes.

The [pinned paired run](https://github.com/ActiveInferenceInstitute/GEO-INFER/actions/runs/33938901328)
passed on hosted Linux Python 3.11 and 3.12, exporting all four contracts from
GNN `89f3b5e79` and consuming them at GEO `b0c07568`. Both checkout identities
and artifact digests are retained in the workflow artifacts.

[Corrected portability CI](https://github.com/ActiveInferenceInstitute/GEO-INFER/actions/runs/33939067638)
passed all 43 cases in each of four jobs at GEO `6630aaf3`: Windows and Linux,
Python 3.11 and 3.12. Both Windows jobs explicitly passed real source and
installed-wheel descendant termination tests (Windows CPython 3.11.9 / 3.12.10
AMD64). This completes TEST-02; native hardware/browser tasks remain separate.

The [nonpublishing wheel workflow](https://github.com/ActiveInferenceInstitute/GEO-INFER/actions/runs/33938902942)
built all 44 wheels and passed isolated installations, origin/resource probes and
completion receipts at `b0c07568`. Subsequent GEO changes at `6630aaf3` affect
only probe assertions and verification documentation, not packaged source.

Final companion pin: `ffebd394b62fe300f43f5cbc99af4d454bd85098`. This adds only a
coverage-configuration correction: the intended 50% floor moves from the
unrecognized run section to the report section. The retained hosted line data
reports 54.3539%, passes at 50%, and fails a 55% negative control; configuration
warnings are eliminated. Inference/export source is unchanged from `89f3b5e79`.

A final CI reporting correction uploads each attempted test category immediately,
before the runner cleans its shared output directory. Unit, integration and
performance retain separate JUnit artifacts per interpreter; H3 retains only its
own summary. Missing expected reports fail visibly. A cold-Windows diagnostic
fixture now allows three seconds before its timeout, preserving the package-stack
assertion and ten-second blocked import; production deadlines are unchanged.

## Main integration baseline and final PR checks

At GEO `cee1b5f08c2acad435b7d8864db4461b3be58c88`,
[all final hosted categories passed](https://github.com/ActiveInferenceInstitute/GEO-INFER/actions/runs/33941489793):
7497 unit, 1276 integration and 52 performance tests on each of Python 3.11
and 3.12, zero failures/errors/skips, plus two H3 validators per interpreter.
All eight category artifacts were retained (184 XML reports and eight summaries).
[Both paired jobs](https://github.com/ActiveInferenceInstitute/GEO-INFER/actions/runs/33941489772)
and [all four portability jobs](https://github.com/ActiveInferenceInstitute/GEO-INFER/actions/runs/33941489777)
also passed at that revision. These receipts supersede the pending-job status
in the earlier chronological publication notes.

GNN PR 25 merged to `main` at `903b9c3391ce277292fd1f3d5626e5fbd66d354a`,
preserving the reviewed `ffebd394b` ancestry and exactly the same source tree.
All eleven pre-merge checks passed; each CI-selected suite passed 3612 tests
and skipped 14 on Python 3.11/3.12/3.13, with the 50% coverage floor enforced.
The GEO manifest now pins this GNN main commit. Paired interchange and
Linux/Windows import-probe workflows also run on pushes to GEO main, retaining
revision-specific receipts after integration.

The disposable GNN graph index was rebuilt without deleting the previous index.
Its recorded commit matches merged `903b9c339`; explicit Gaussian and factored
exporter lookups resolve to the correct files. This closes the earlier failed
FTS-refresh finding for that revision. Future source changes still require
index refresh and lookup validation.

## Supervised regional acquisition

The regional downloader now runs in a private Python worker launched with
`-I`. Its parent enforces the remaining shared five-minute network budget,
terminates a stalled worker and reaps it within a separate one-second cleanup
budget. Local geometry and serialization retain checks between phases.
Byte/feature limits, exact offline replay and existing artifacts on failure
are preserved. Requests reject redirects and the worker never starts children.

Both full PLACE suites passed 416 tests with no failures/errors/skips on
Python 3.11 and 3.12. Fifty-one focused cases passed, including real slow-drip
responses, stalled headers, gzip expansion limits and failure preservation.
An independent interruption probe verified KeyboardInterrupt propagation,
worker reaping, closed pipes and disconnected HTTP streams.

A newly built PLACE wheel matched the complete source/resource inventory.
Installed outside the checkout in a fresh locked environment, its actual
worker returned exact bytes and a slow-drip request timed out in 2.003 seconds
against a two-second deadline, with the worker reaped. The other 43 package
sources remain unchanged from the earlier complete hosted wheel receipt.
Windows execution of this regional worker remains a separate PLACE-04 check;
the existing Windows source/wheel import-probe results cover a different tool.

[GNN main CI](https://github.com/ActiveInferenceInstitute/GeneralizedNotationNotation/actions/runs/33943799538)
passed on the exact merge commit `903b9c3391ce277292fd1f3d5626e5fbd66d354a`,
including all three Python jobs and security. This is post-merge evidence,
separate from the earlier green PR runs.

## Completed main integration

GEO PR 8 merged at `6f15c1000c258accdc765c6d05be7cd49ac0b285` after all nine checks
passed on `2241e645`. The merge tree is identical to that validated PR head.
Both Python 3.11 and 3.12 passed 7497 unit, 1300 integration and 52 performance
tests (8849 each), with zero failures/errors/skips, plus both H3 validators.
[Hosted category receipts](https://github.com/ActiveInferenceInstitute/GEO-INFER/actions/runs/33944569278)
and [all 44 isolated wheel receipts](https://github.com/ActiveInferenceInstitute/GEO-INFER/actions/runs/33944647126)
cover the final packaged source, including the supervised regional worker.

[The paired run](https://github.com/ActiveInferenceInstitute/GEO-INFER/actions/runs/33944569311)
verifies clean GEO `2241e645` against merged GNN `903b9c3391ce277292fd1f3d5626e5fbd66d354a`.
All four artifact hashes and discrete trace values match exactly across Python
versions; every numerical trace leaf is finite and agrees within absolute
1e-7 (largest difference 5.96e-8, with no relative tolerance). Replay within
each runtime is deterministic. Local committed runs additionally produced
identical traces; the hosted cross-runtime result is numerical agreement.

Both PR merge SHAs matched remote main and the isolated checkouts. Original
concurrent working edits were preserved. The documentation closeout adds no
packaged source changes; subsequent main workflow receipts are linked from
the merged PR and retained by the main-triggered workflows.

A final bounded Interceptor attempt could not establish native Enter behavior:
the tool reported success but the page received no key/click event. Newly
created window IDs disappeared before resizing, so a real narrow screenshot
could not be captured without affecting an unrelated window. Owned tabs and
the test server were closed. These tool limitations leave DOCS-01 deferred.

## Advisor probe (2026-09-10)

TEST-04 re-probe: the configured advisor is the Cato cross-vendor adversarial
audit, surfaced through the Codex CLI. Probe found codex-cli 0.153.2 installed
but authenticated via ChatGPT account with no OPENAI_API_KEY set. One bounded
invocation (`codex exec -m gpt-5.2` with a trivial prompt) failed with
`ERROR status 400: The 'gpt-5.2' model is not supported when using Codex with a
ChatGPT account.` (exit 1). Cato remains unavailable; TEST-04 advisor review is
re-deferred as of 2026-09-10. Resolution requires switching Codex auth to an
API-key account (an account-level decision).

## 2026-09-10 investigation of the historical PROJ SQLite disk-I/O failure (TEST-GNN-01)

A bounded probe matrix investigated the one-time Python 3.12 combined-process failure
(32 SPACE failures/errors reporting a PROJ SQLite disk-I/O error; fresh-process rerun
passed all 587 SPACE tests, per the SPACE/TIME receipt). Full detail is in the
investigation report at /tmp/ledger-closeout/report-test-gnn-01.md; probes live in
/tmp/ledger-closeout/.

Method and results:

| Probe | Setup | Result |
| --- | --- | --- |
| (a) Current environment | This workstation's GEO `.venv` | Python 3.12.11, SQLite 3.50.4, pyproj 3.7.1, PROJ 9.5.1; embedded `proj.db` `PRAGMA quick_check` = `ok`. The interpreter build differs from the recorded 3.12.13/SQLite 3.53.1 (different build, not a record error). |
| (b) Import order | ACT→SPACE→TIME, TIME→SPACE→ACT, SPACE→ACT→TIME; 2 reps each = 6 direct import+CRS/H3 smoke runs | All 6 passed with identical numerical outputs (4326→3857 transform and H3 cell identical across orders). No PROJ/SQLite error. |
| (b) pytest | `tests/unit/test_spatial_functions.py` (29 tests, includes CRS transform tests), alone and paired with `tests/integration/test_act_agent_ant_coordination.py` | All passed. |
| (c) Exact historical versions | Throwaway uv venv: CPython 3.12.13, SQLite 3.53.1, pyproj 3.7.1, PROJ 9.5.1 — exactly the recorded combination | Two runs of a 200-iteration CRS/transform/authority loop (cold and warm): zero errors, `quick_check` = `ok`. |
| (d) Concurrent processes | 3 iterations of two simultaneous pytest processes on `test_spatial_functions.py`, same tree and same embedded `proj.db` | 6 × 29 tests, all `errors="0" failures="0" skipped="0"`; no disk-I/O text in any output. |

Structural observation: on this machine every PROJ-opening process shares one
embedded SQLite database, `GEO-INFER/.venv/lib/python3.12/site-packages/pyproj/
proj_dir/share/proj/proj.db`, which lives inside the git worktree. The historical
failure occurred in a single long-running combined multi-module process — the setup
that holds that file open longest while other processes operate on the same tree.

Classification: transient concurrent-access contention on the shared embedded
`proj.db` is the most plausible cause — consistent with failure in one process, full
recovery in a fresh process, stable integrity and descriptor count, and zero
recurrence across 8 fresh single-process smoke/pytest runs, 6 concurrent-pair
processes and 400 CRS iterations on the exact historical version combination.
Environmental stale cache is effectively ruled out (integrity `ok` before and after,
no cache reset needed). What remains honestly unexplained: the exact trigger. There
is no reproducer; the single historical occurrence cannot be inspected
retroactively, and what other processes may have held or scanned the tree at that
moment is unknown. Contention is consistent with the evidence, not demonstrated by it.

Closing the row fully requires one of: a reproducible minimal case (for example an
exclusive lock or induced I/O failure on `proj.db` while a CRS opens, matching the
historical error text), or three consecutive clean full combined-process suite runs on
Python 3.12 with this probe matrix recorded per cycle, plus recording the interpreter
build and SQLite version (not just "Python 3.12") in every future receipt. No CRS
test was weakened and no environment fix is claimed.

## 2026-09-11 combined-process and intra-thread PROJ probe (TEST-GNN-01 follow-up)

Bounded next probe (~2 min compute) targeting the two surfaces the 2026-09-10
matrix never exercised: (1) the historical trigger shape itself, i.e. CRS
touching ACT+SPACE+TIME unit tests collected and run TOGETHER in ONE pytest
process, and (2) intra-process thread concurrency on `proj.db` (the 2026-09-10
probe (d) covered concurrent processes only). Environment re-verified: Python
3.12.11, SQLite 3.50.4, pyproj 3.7.1, PROJ 9.5.1; embedded `proj.db`
`quick_check` `ok`, `journal_mode=delete`, no WAL or journal sidecars, before
and after all runs.

Test selection note (current tree): the 2026-09-10 reference to
`tests/unit/test_spatial_functions.py` resolves to
`GEO-INFER-TEST/tests/unit/test_spatial_functions.py` (29 tests, still present,
geopandas CRS transform suite). The 2026-09-10 probes ran it alone and paired
with one ACT integration file; today it is included inside the combined
selection instead. Current SPACE CRS touching is: 7 unit files
(`test_spatial_utils.py` and `test_gis_submodule.py` carry the transform
coverage; `test_spatial_methods.py` is H3 mock only, no CRS). ACT and TIME have
no CRS touching unit tests in the current tree (ACT's `sample_geodataframe`
fixture has no unit consumers; TIME unit is pure time series), so one
representative file each (`ACT/tests/unit/test_h3.py`,
`TIME/tests/test_event_detection.py`) preserved the combined three package
import shape.

Probe A: combined one process pytest, 5 reps of the 216 test selection, then
one corrected rep adding `test_spatial_functions.py` (245 tests). Exact
command shape (per rep, only the file list and junitxml name changed):

```
env PROJ_DEBUG=2 uv run --no-sync pytest -q -p no:cacheprovider --junitxml=/tmp/probe-gnn01-0911/<run>.xml GEO-INFER-SPACE/tests/unit/test_spatial_utils.py GEO-INFER-SPACE/tests/unit/test_gis_submodule.py GEO-INFER-SPACE/tests/unit/test_analytics_comprehensive.py GEO-INFER-SPACE/tests/unit/test_data_integrator.py GEO-INFER-SPACE/tests/unit/test_place_analyzer.py GEO-INFER-SPACE/tests/unit/test_io_modules.py GEO-INFER-SPACE/tests/unit/test_raster_expression_security.py GEO-INFER-ACT/tests/unit/test_h3.py GEO-INFER-TIME/tests/test_event_detection.py GEO-INFER-TEST/tests/unit/test_spatial_functions.py
```

Probe B: intra-process threads in one interpreter, barrier synchronized
first open of `proj.db` (script `/tmp/probe-gnn01-0911/thread_crs_probe.py`):
`uv run --no-sync python /tmp/probe-gnn01-0911/thread_crs_probe.py 8 150`
(1,200 CRS/transform/Geod ops with numeric assertions), then `32 500` twice
(16,000 ops each).

Probe C (escalation, 2 reps): the combined pytest run and a 16 thread x 300 op
probe executed concurrently against the same `proj.db` (long lived process plus
intra process storm).

Outcomes, all clean:

| Probe | Result |
| --- | --- |
| A | 5 x 216 tests and 1 x 245 tests: `errors="0" failures="0" skipped="0"`, exit 0; test time 9.7 to 12.2 s per rep |
| B | 1,200 + 16,000 + 16,000 threaded ops: 0 exceptions, transforms numerically asserted |
| C | both parts exit 0 concurrently, 2 reps: 216 tests plus 4,800 threaded ops per rep |
| Integrity | `quick_check` and `integrity_check` `ok` after all runs; `journal_mode` unchanged; no sidecar files appeared |

Instrumentation limitation, recorded honestly: `PROJ_DEBUG=2/3` produced zero
output under this pyproj build (verified directly on a minimal `CRS.from_epsg`
run); a ctypes `proj_log_func` handler installed on PROJ's default context
captured 0 lines because pyproj drives private per object contexts. No
PROJ/SQLite diagnostic stream was obtainable, so the stderr lane is vacuous
here, not a positive absence of logging claim. No error signature was captured
because no error occurred; the historical verbatim message remains unavailable.

Co-tenant activity, recorded as observed evidence: this worktree was not
quiet during the probe. This lane's session started with a clean tree at
e31693dc and touched only this receipt file, yet four files outside the lane
were modified by concurrent co-tenant work: `CLAUDE.md` and `TODO.md` just
before the window, and inside it
`GEO-INFER-RISK/src/geo_infer_risk/civic_intel.py` at 09:24:54 (overlapping
probe C) and `CHANGELOG.md` at 09:28:57 (overlapping the corrected combined
rep). This is the external
tree-churn class the 2026-09-10 analysis left unverified, occurring live
during clean CRS runs; it makes concurrent interference on the tree a
demonstrated, always-present factor here rather than a hypothetical one,
while still not reproducing the failure.

Inference: eight combined process pytest runs (5 x 216 + 2 x 216 storm + 1 x
245 = 1,557 tests) plus ~42,800 threaded CRS operations, with both surfaces
simultaneously, found no recurrence on this build. This weakens the case that
intra process or multi process PROJ/SQLite contention alone reproduces the
failure, since every internal concurrency surface is now clean; it does not
overturn the leading hypothesis, because the historical run's decisive variable
(what external processes held or scanned the tree at that moment) is not
recreatable retroactively, and `journal_mode=delete` on the shared in worktree
`proj.db` still leaves external interference contention plausible. The exact
trigger remains unexplained; no repro exists. Status of the 2026-09-10 closure
criteria: not closed (no minimal reproducer; these bounded runs are not three
consecutive full suite combined runs). No test was weakened, skipped, or
suppressed, and no environment fix is claimed.
