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
