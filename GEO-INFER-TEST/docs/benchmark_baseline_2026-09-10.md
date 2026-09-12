# Parametric Load Benchmark Baselines — 2026-09-10

Closes ledger row **PERF-02**. Baselines for
`GEO-INFER-TEST/tests/unit/test_parametric_load_benchmarks.py` (delivered by TEST-01).

## Measurement environment

| Item | Value |
|---|---|
| Date | 2026-09-10 |
| Hardware | Apple M5 (arm64), macOS 25.6.0 (Darwin 25.6.0) |
| Python | 3.12.11 (Clang 20.1.4 build) |
| numpy | 1.26.4 |
| scipy | 1.16.1 |
| shapely | 2.1.1 |
| h3 | 4.5.0 |
| Git SHA of measured tree | `c0115779d05369c1ba63f5009f7de53e4bb3d3d5` |
| Invocation | `uv run --no-sync python -m pytest GEO-INFER-TEST/tests/unit/test_parametric_load_benchmarks.py -q -p no:cacheprovider` |

## Baseline table

Per-scenario timings measured on this tree + machine. Run 1 includes warmup effects
(first-touch imports, allocator, JIT-less but cold caches); run 2 is the steady-state
reference. Throughput = 100,000 points / call time.

| Scenario | Run 1 (cold) | Run 2 (warm) | pytest `--durations` (warm) |
|---|---|---|---|
| H3 conversion, 100k pts @ res 9 (`test_h3_high_volume_conversion_throughput`) | 0.754 s (132,713 ops/s) | 0.464 s (215,726 ops/s) | 0.73 s |
| Vectorized point-in-polygon, 100k pts (`test_vectorized_geometry_load_throughput`) | 0.010 s (~9.9M pts/s) | 0.040 s (~2.5M pts/s) | 0.02 s |

Notes:

- PIP throughput is noisy (0.010–0.040 s spread across runs, ≈4x) because the raw call
  is ~10–40 ms; treat any single run as approximate. The in-suite assertion floor
  (>50k pts/s) has ~500x headroom, so noise there is not a risk.
- H3 conversion (pure-Python loop over `h3.latlng_to_cell`) is the dominant scenario;
  use the **warm** figure (≈0.46–0.73 s for 100k) as the canonical baseline.
- Whole-suite wall time is dominated by interpreter/import startup (~78–150 s under
  `uv run` on this machine); that overhead is environmental and NOT part of the
  scenario baselines above. Do not trend suite wall time.

## Regression threshold policy

- **Flag rule:** on a same-class machine (Apple M5-class arm64, Python 3.12, same
  package versions), any scenario whose call time exceeds **2x its recorded warm
  baseline** (H3: > 1.5 s for 100k; PIP: > 0.08 s for 100k) flags a performance
  investigation **before any performance claim is made or shipped**.
- Deviations are investigated, never suppressed: do not loosen assertions, skip
  scenarios, or re-record the baseline to make a flag disappear. Either the code
  regressed (fix it) or the environment changed (re-record explicitly, per below,
  with a dated new baseline file — never overwrite this one).
- Sub-threshold variance (≤2x) is acceptable measurement noise; no action.
- **In-suite assertion floors** (`tests/unit/test_parametric_load_benchmarks.py`):
  H3 > **130k ops/s** (~0.77 s per 100k) and PIP > **50k pts/s** (~2 s per
  100k). These floors are loose CI smoke guards derived from the same baselines
  above (H3 ≈ 2x the warm figure; PIP keeps large headroom because its raw call
  is ~10–40 ms and noisy) — they are deliberately looser than the 2x-flag rule,
  which remains a **manual pre-publication check** before any performance claim
  is shipped (see flag rule above).

## Machine-dependence caveat

These baselines are **per-machine-class**. They are valid only on Apple M5-class
arm64 hardware under macOS 25.6.0 with Python 3.12 / numpy 1.26.4 / h3 4.5.0 /
shapely 2.1.1 / scipy 1.16.1. On new hardware, OS, Python, or major package
versions, **re-record** this baseline (new dated file under `GEO-INFER-TEST/docs/`)
before applying the 2x threshold; comparing cross-machine numbers against this table
is invalid.
