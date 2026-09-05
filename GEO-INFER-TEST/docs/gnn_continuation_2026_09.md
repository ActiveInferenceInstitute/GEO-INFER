# Paired model contracts and regional evidence

This continuation starts at GEO `634b61b9` and GNN `92255b125`. Both isolated
worktrees were clean. The original concurrently edited repositories were
preserved. GNN includes the explicitly documented prior fleet ancestry.

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
