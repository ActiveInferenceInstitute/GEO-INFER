# Pin-Freshness Review Receipt — 2026-Q3

Reviewed: 2026-09-10
Cadence: quarterly; next review due 2026-12.
Method: CI-02 wave method (2026-09-07) — inventory exact pins, look up latest release per family, and for every available SAFE MAJOR a one-line release-note review plus an explicit decision (hold / bump candidate). Standing caveat: **release-note review precedes any bump** — no pin is changed by this receipt; it documents the review only.

Scope inventoried from: `.github/workflows/{ci,gnn-interchange,import-probes,release}.yml`, `pyproject.toml` (quality extra + all extra), and `uv.lock` (locked dependency surface; ruff resolved 0.15.6, pytest resolved 8.4.1).

## Per-pin table

| Family | Where | Current | Latest | Decision | Note |
|---|---|---|---|---|---|
| ruff (pinned range) | ci.yml ×4, pyproject `quality` + `all` | `>=0.15.6,<0.16` (lock: 0.15.6) | 0.16.7 | **Bump candidate (2026-12)** | SAFE MAJOR 0.15→0.16 available. Release-note review: 0.16.0 expands the default rule set to 413 (from 59) and formats Markdown code blocks by default; the CI gate's explicit `--select F821,F823,E721,E722` is unaffected (its rules survive the default-set reshuffle, incl. E721 which left the defaults), and `format --check` runs only on changed `*.py`, so Markdown defaults are dormant here. Candidate because validation must confirm the repository-wide hygiene contracts tolerate the 413-rule default expansion before the `<0.16` cap moves. |
| actions/checkout (SHA) | ci.yml ×2, gnn-interchange.yml ×2, import-probes.yml, release.yml | SHA #9c091bb2 → v7.0.0 | v7.0.1 | Hold | Patch delta within v7; no SAFE MAJOR available. Not worth a receipt-only churn; pick up with any next pin move. |
| actions/setup-python (SHA) | ci.yml ×2, import-probes.yml, release.yml | SHA #5fda3b95 → v7.0.0 | v7.0.0 | Hold | Already at latest release; no delta. |
| astral-sh/setup-uv (SHA) | ci.yml ×2, gnn-interchange.yml, import-probes.yml, release.yml | SHA #20cfd1bf → v10.0.1 | v10.1.0 | Hold | Minor delta within v10; no SAFE MAJOR available. Same-major minors ride along when the next major reviews. |
| uv CLI version (setup-uv `version:`) | ci.yml ×2, gnn-interchange.yml, import-probes.yml, release.yml | 0.10.7 | 0.12.13 | **Bump candidate (2026-12)** | SAFE MAJOR 0.10→0.12 available. uv 0.12 is a toolchain-major whose effect is mediated by `uv sync --locked` against uv.lock; the bump precondition is a one-line check that 0.12 lockfile-format handling accepts the current uv.lock (to be confirmed against the uv 0.12 release notes at bump time). |
| actions/upload-artifact (SHA) | ci.yml ×5, gnn-interchange.yml, import-probes.yml, release.yml | SHA #043fb46d → v7.0.1 | v7.0.1 | Hold | Already at latest release; no delta. |
| gitleaks (tarball + sha256) | ci.yml `Install pinned gitleaks` | v8.30.1 | v8.30.1 | Hold | Already at latest release; sha256-pinned, no delta. |
| pandoc (tarball + sha256) | ci.yml manuscript job | 3.11 | 3.11 (2026-08-29) | Hold | Already at latest release; the pandoc/pandoc-crossref pair is crossref-coupled and sha256-pinned, no delta. |
| pandoc-crossref (tarball + sha256) | ci.yml manuscript job | v0.3.25 | v0.3.25a (2026-09-06) | Hold | Delta is an `a` rebuild tag of the same 0.3.25 base (action SHA retarget, not a version bump); no SAFE MAJOR available. Revisit only if a v0.3.26+ appears. |
| pytest (standalone probe pin) | import-probes.yml | ==8.4.2 (lock: 8.4.1) | 9.1.1 | **Bump candidate (2026-12)** | SAFE MAJOR 8→9 available. Release-note review: 9.0.0 adds subtests as a first-class alternative to parametrization; the head of the notes shows feature-forward framing, and the standalone probe environment is hermetic (`pip install pytest==8.4.2 build==1.3.0`, no plugins). Candidate: retarget the probe pin to 9.x next quarter; the major-bump risk review (removed deprecations / plugin-hook surface) is deferred to bump time alongside the probe smoke run. |
| build (standalone probe pin) | import-probes.yml | ==1.3.0 | 1.6.1 | Hold | No SAFE MAJOR available (1.3→1.6, same major); the probe's sdist build path is stable across build minors. |

## Summary

- 3 families already at latest release (setup-python, upload-artifact, gitleaks; pandoc at 3.11 current).
- 0 SAFE MAJOR jumps executed this review; 3 SAFE MAJORs recorded as bump candidates for 2026-12 (ruff 0.16.x, uv 0.12.x, pytest 9.x). Each carries a stated gate: ruff's precondition is release-note-reviewed here; the uv and pytest preconditions are deferred to bump time and must be confirmed against their release notes before any cap/pin moves.
- Holds are justified above: 5 same-major/no-delta families ride along at the next review rather than churning pins receipt-only.
- The pinned ruff range `>=0.15.6,<0.16` and the locked `uv.lock` surface were verified against the live tree; no pin was touched.
