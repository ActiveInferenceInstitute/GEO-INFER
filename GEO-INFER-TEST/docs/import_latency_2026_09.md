# Import-Latency Investigation Receipt — PERF-01 (2026-09-10)

Ledger row: **PERF-01** — native ART/pandas import-latency investigation.
Scope: bounded evidence collection only. **No source changes were made.**

## Machine and environment

| Item | Value |
|---|---|
| Machine | Apple M5 (arm64), local APFS SSD, `/tmp` on same volume as uv cache |
| OS | macOS (Darwin 25.6.0) |
| Python | CPython 3.12.13 (uv-managed) |
| geo-infer-act | 0.2.0 (installed from local source) |
| pandas | 3.0.5 |
| numpy | 1.26.4 |
| scipy | 1.17.1 |
| matplotlib | 3.11.1 |
| seaborn | 0.13.2 |
| h3 | 4.5.0 |
| inferactively-pymdp | 1.0.3 |
| arviz | 0.23.4 (transitive dep, emits FutureWarning on import) |
| pyarrow | NOT installed (not a dependency of geo-infer-act; excluded from all measurements) |
| uv | /opt/homebrew/bin/uv, cache at `~/.cache/uv` |

## Method

1. Two fresh venvs built with the repo's Python 3.12.13:
   - **venv A** — `uv pip install -e ./GEO-INFER-ACT` (editable)
   - **venv B** — `uv pip install ./GEO-INFER-ACT` (non-editable, wheel built from source)
2. Install wall times (`time` around `uv pip install`):
   - A (editable, cache partially cold): **14.0 s**
   - B (non-editable, cache-hot): **3.6 s** (first attempt; re-run 3.3 s, of which wheel build 2.9 s)
3. Import probes run as separate processes via a guarded wrapper (`subprocess` + child-side `faulthandler.dump_traceback_later(120, exit=True)` + parent hard timeout of 300 s). A rep counts only if the literal stdout line `IMPORTED <__file__> <version>` appears — rc through pipes is explicitly not trusted (an earlier naive probe using GNU `timeout` measured garbage 0.02 s values because `timeout` does not exist on this Mac; those numbers were discarded, not reported).
4. Cold = first import ever in a freshly created venv (by definition one rep per venv; `.pyc` compilation included). Warm = 3 reps after caches exist. `bounded reps: 3 per timing; tail not chased`.
5. Attribution via `python -X importtime` (stderr captured; top cumulative offenders ranked).
6. Native stack traces: only required if an import exceeded the 120 s guard. **None did** — the guard never fired, so no stack traces were collected.

## Timing tables

### Import wall-clock (separate processes, required-stdout probes)

| Target | Condition | venv / install mode | min / median / max | reps |
|---|---|---|---|---|
| `import pandas` | warm | A (editable) | 2.16 / 2.54 / 2.57 s | 3 |
| `import pandas` | warm | B (non-editable) | 2.82 / 2.93 / 3.60 s | 3 |
| `import pandas` | cold (first import, fresh venv E) | non-editable | 18.42 s | 1 |
| `import geo_infer_act` | cold (first import, fresh venv C) | editable | 63.80 s | 1 |
| `import geo_infer_act` | cold (first import, fresh venv D) | non-editable | 65.11 s | 1 |
| `import geo_infer_act` | warm | A (editable) | 13.85 / 14.46 / 17.35 s | 3 |
| `import geo_infer_act` | warm | B (non-editable) | 11.66 / 13.77 / 13.87 s | 3 |

Corroboration: an incidental earlier run that installed both venvs and then performed the first-ever import in each took ~142 s wall total (≈3.3 s install + two first-imports) — consistent with the ~64 + ~65 s cold figures above.

### `importtime` attribution (venv A, warm)

- `import pandas`: cumulative 0.92 s (dominated by `numpy`, 0.55 s cum). Total modules: standard pandas surface.
- `import geo_infer_act`: cumulative **12.9 s** across **1782 modules**. Top cumulative offenders:
  - `scipy.signal` — 6.16 s (pulled via `geo_infer_act.utils.math`)
  - `scipy.stats` — 2.76 s
  - `pandas` — 2.71 s (re-imported inside the ACT import graph)
  - `matplotlib.pyplot` — 2.29 s (pulled via `geo_infer_act.utils.visualization`)
  - remaining ~1.0 s spread over the ACT package itself and transitive deps (arviz/xarray visible in the graph).

Interpretation: the ACT import cost is not pandas-specific — `scipy.signal` and eager `matplotlib.pyplot`/`pandas` imports from `geo_infer_act.utils` account for the bulk of the 12.9 s warm baseline.

## Does the ~120 s timeout reproduce?

**No — not on this machine.** The worst single observed import (cold `geo_infer_act`, first-ever import, non-editable install) was **65.1 s**, roughly half of the historical ~120 s threshold. The 120 s faulthandler guard never fired; all probes completed with verified `IMPORTED` stdout. Warm imports settle at 12–17 s.

Plausible mechanism for the historical observations (hypothesis, not measured here): cold imports at ~65 s on an M5 with local SSD leave only ~1.85× headroom to 120 s. On slower disks, network-mounted home directories, cold uv/pip caches, CPU-throttled containers, or first-import storms (many processes compiling the same 1782-module graph concurrently), the cold figure can plausibly exceed 120 s. We did not construct those constrained conditions and make no claim about them.

## Editable vs non-editable, and macOS filesystem observations

- Editable and non-editable installs show **no meaningful import-time difference** (cold: 63.8 s vs 65.1 s, within rep-to-rep noise; warm medians 14.5 s vs 13.8 s). Install-mode choice does not affect import latency.
- Default uv link mode on APFS is clone (copy-on-write): installed `pandas` `.so` inode differs from the cache-archive inode. Explicit `--link-mode hardlink` produced an `nlink=2` file but **not** against the original cache archive entry (uv re-materialized a fresh archive copy and linked to that). Neither mode measurably changes import timing; both venv variants measured within noise.
- `/tmp` and `~/.cache/uv` are on the same APFS volume, so clone/hardlink fast paths apply; a cross-volume cache would force full copies.
- Editable installs write `.pyc` caches into the repo source tree (`GEO-INFER-ACT/src/geo_infer_act/__pycache__/`) — an observed side effect worth knowing when diagnosing "cold" claims.

## What is NOT claimed

1. **No import-speed guarantee.** These numbers are one machine, one OS, one Python (3.12.13), one uv cache state. They are evidence, not a service-level bound.
2. The **600-second correctness bound is not relabeled as a performance fix.** It remains a correctness backstop. This receipt changes nothing about it.
3. No claim that the historical ~120 s timeouts were misreported — only that they **did not reproduce** under the conditions measured here (warm uv cache, local SSD, unconstrained CPU).
4. No claim about constrained environments (network filesystems, cold caches, throttled CPU, Windows/Linux) — not tested.
5. Cold results are single-rep by construction (a "cold" rep cannot repeat within the same venv); warm results carry 3 reps each.
6. No fixes were applied or proposed in this receipt (e.g., lazy `matplotlib.pyplot` / `scipy.signal` imports in `geo_infer_act.utils` are an obvious follow-up candidate but are out of scope for PERF-01's evidence-only mandate).

## Provenance

- Probes: `/tmp/perf01_probe.py` (guarded wrapper), importtime dumps at `/tmp/perf01-pandas-importtime.txt` and `/tmp/perf01-act-importtime.txt`.
- Venvs used: `/tmp/perf01-a` … `/tmp/perf01-f` (throwaway; safe to delete).
- Report copy: `/tmp/ledger-closeout/report-perf-01.md`.
