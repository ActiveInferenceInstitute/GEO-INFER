# GEO-INFER Open Task & Backlog Ledger

> Last reviewed: 2026-09-11
> Scope: Multi-package repository (`GEO-INFER`) across workspace packages and 45 domain modules.
> Centralization Rule: All planned, open, or deferred engineering work across all modules is tracked exclusively in this ledger. Module source code and tests must never carry local task markers (`TODO`, `FIXME`, `XXX`, `HACK`).
> History note (2026-09-07): the published history was rewritten to re-attribute
> hum-side personal commit identities to docxology
> <docxology@users.noreply.github.com>. Every commit SHA recorded in this
> ledger, in CHANGELOG.md and in ISA.md before that rewrite refers to
> pre-rewrite history and no longer resolves; the recorded evidence and run
> results remain valid, only the identifiers changed. Future contributions
> from this checkout are authored as docxology.

---

## Open work and acceptance criteria

Completed implementation and deferred verification are tracked separately below.
Module names identify the responsible area, not an assigned person. Acquisition
items require an explicit area, source and resource budget before running them;
this ledger does not authorize full-region downloads or a package release.
Rows are tiered: **Major** needs external resources or is a release-scale
decision, **Medium** is self-serve multi-session engineering, **Minor** is a
bounded single-session change. Re-tiered 2026-09-07 from a nine-scout ledger
audit: the previously open rows verified current against the tree, delivered
claims were spot-checked, and module/package surfaces were swept for untracked
next steps.

### Major — external resources or release-scale decisions

| ID | Area / status | Bounded next step | Acceptance evidence / dependencies |
| --- | --- | --- | --- |
| **SPACE-01** | SPACE / deferred hardware verification | [DEFERRED-VERIFY] On supported physical hardware, run numeric distance and grouped-reduction parity for each backend claimed as supported (CuPy, Torch, JAX), including empty inputs, float64 precision, chunk boundaries and allocation failure. Keep H3 topology labeled as host CPU. | Record device/driver/library versions, actual backend diagnostics, CPU-reference tolerances, peak memory and separate cold/warm timings. Publish speed claims only for measured workloads; do not infer support from CPU fallback. Requires hardware. [Guide](GEO-INFER-SPACE/docs/GPU_ACCELERATION.md). |
| **PLACE-V14** | PLACE / regional layer acquisition open | Three source-backed layers are delivered (13 HU4 display polygons, 24 volcanoes, one convergent boundary). Obtain the remaining complete licensed `cascadia_bioregion_boundary.geojson`; retain the documented per-layer extent and interpretation. | Validate WGS84, required geometry types, stable feature identifiers, provenance and checksums; run actual-data renderer/integration checks (missing-layer behavior is fail-closed and pinned at `test_regional_layer_acquisition.py:73,81`). Keep missing-layer behavior explicit until data exists. Do not restore the former 12-volcano or earthquake-probability claims without evidence. |
| **PLACE-04** | PLACE / deferred Windows verification | [DEFERRED-VERIFY] Run the real regional download-worker loopback tests on Windows with the locked PLACE runtime. | Prove stalled-header/slow-drip deadlines, native process termination, pipe closure, batch failure preservation and exact replay on Windows; retain interpreter/OS versions. POSIX termination is verified and the worker starts no child processes. |
| **CODE-01** | Repository / recurring index refresh | [REFRESHED 2026-09-11] Fresh full `gitnexus analyze` on `main` at `e31693dc` (the incremental `run.cjs` path failed with an invalid-UTF-8 runtime error and the dirty-state detection forced a full rebuild, ~30 s): index rewritten in the worktree `.gitnexus/` store (gitignored; 65,872 nodes, 93,811 edges, 1,727 clusters, 300 flows, no embeddings; three files skipped >512 KB) and registered as `GEO-INFER` (branch `main`). Indexed/current-commit parity holds (`gitnexus status` reports ✅ up-to-date at the merge commit); the analyze's block injection into root `AGENTS.md` was stripped by the canonical signpost regen per the cadence note, and `CLAUDE.md`'s committed block was count-refreshed only. | Indexed/current-commit parity plus correct explicit-file Gaussian-contract (the GNN-repo exporter is outside this index) and sparse-transition lookups verified at the receipt SHA as recorded; direct source/caller review remains the documented fallback while no index exists. Recurring cadence: re-run `gitnexus analyze .` after major refactors or when `gitnexus status` reports stale, restoring generator-owned AGENTS.md/CLAUDE.md afterwards. |
| **REL-01** | Repository / release authorization and execution | Prep complete 2026-09-10: the `[Unreleased]` content folded into `## [0.2.0] - 2026-09-10` (Keep-a-Changelog fold; February content retained as a subsection; link refs updated), GEO-INFER-INSURANCE promoted 0.1.0→0.2.0 (pyproject `version`; Development Status kept at 3-Alpha to match the fleet classifier majority; the `KNOWN_VERSION_DEVIATIONS` entry removed), `validate_packaging --strict` green (45 modules, 0 errors/warnings). Remaining act: tag `v0.2.0` — the tag push alone fires `release.yml` (45-wheel build; no other wiring exists). Tagging remains withheld pending an explicit deliberate go/no-go (ledger header rule). |

### Medium — self-serve, multi-session

| ID | Area / status | Bounded next step | Acceptance evidence / dependencies |
| --- | --- | --- | --- |
| **TEST-GNN-01** | TEST / Python 3.12 PROJ SQLite disk-I/O cause | Investigate the failure observed during the combined ACT/SPACE/TIME test process; a fresh integrity probe and all 587 SPACE tests passed separately, and the continuation receipt records non-recurrence with versions (Python 3.12.13, pyproj 3.7.1, PROJ 9.5.1, SQLite 3.53.1) — establish the historical cause, not just current success. | Minimal import/order reproduction, loaded PROJ/GDAL/SQLite versions and file-descriptor state; correct a reproducible cause without suppressing CRS tests or declaring an unverified environment fix. 2026-09-10 bounded investigation delivered (dated section in the continuation receipt): the exact historical version combination reproduced clean across 400 CRS iterations, concurrent-process stress clean — leading hypothesis transient concurrent-access contention on the shared embedded proj.db; exact trigger honestly unexplained. 2026-09-11 follow-up probe (dated section in the receipt): combined ACT/SPACE/TIME CRS subsets in one pytest process ×8 (1,557 tests), intra-process thread hammering (~42,800 CRS ops) and a simultaneous pytest+thread storm — all clean on the current build (Python 3.12.11, SQLite 3.50.4); this weakens the internal-concurrency half of the hypothesis, while `journal_mode=delete` on the shared in-worktree proj.db plus live-observed co-tenant worktree edits during the clean runs keep external interference a demonstrated always-present factor; still open (no minimal reproducer; not the decisive full-suite combined run). [Receipt](GEO-INFER-TEST/docs/gnn_continuation_2026_09.md). |

### Minor — bounded single-session changes

| ID | Area / status | Bounded next step | Acceptance evidence / dependencies |
| --- | --- | --- | --- |
| **TEST-04** | TEST / advisor review repeat | [DEFERRED-VERIFY] The configured advisor exited with an error during the September GNN campaign so no advisor review ran (gnn_space_time_2026_09.md): repeat the advisor review when the service is available. | 2026-09-10 probe: the configured advisor is Cato via Codex CLI 0.153.2; ChatGPT-account auth rejects the gpt-5.2 slug (HTTP 400) and no OPENAI_API_KEY is configured, so no review could run — probe appended to the continuation receipt. Unblocking is an account-level auth decision (codex login --with-api-key). 2026-09-11 re-check: environment still exposes no OPENAI_API_KEY and the CLI auth state is unchanged — remains blocked on the account-level decision. |

## Completed-record reset (2026-09-11)

The delivered-capabilities table, the completed-audit log and the dated
receipt sections were cleared on 2026-09-11 as part of the repo-wide
scoping reset that precedes the fresh minor/medium/major pass over the
package and all 45 modules. All prior records remain restorable from git
history, and standing receipts live in `GEO-INFER-TEST/docs/` and the
CHANGELOG.
The fresh pass itself lands as `SCOPE-2026-09-11.md`.

## Campaign execution record (2026-09-11)

The full 189-item spec was executed the same day in six reviewed waves,
each pushed with CI green (probe-confirmed bug fixes; 82 silent-fabrication
fixes across 36 modules; packaging coherence with a single integration
re-lock; 21 test-gap closures; 29 docs/API-honesty fixes including the new
`validate_doc_imports.py` gate; 31 CI/structural items via
[PR #28](https://github.com/ActiveInferenceInstitute/GEO-INFER/pull/28)).
The campaign is recorded in CHANGELOG under
`## [0.2.0] - 2026-09-11 - repo-wide quality campaign`. All spec items are
delivered; the ledger's open rows below are the survivors.

Additional Minor rows surfaced during release verification (2026-09-12):

| ID | Area / status | Bounded next step | Acceptance evidence / dependencies |
| --- | --- | --- | --- |
| **PYC-01** | Repository / gitignore | [DELIVERED 2026-09-12, PR #32] Re-ignore `__pycache__`/`*.pyc` under the GS-023 packaged-config negation (`GEO-INFER-*/src/**/config/`), which had overridden the global pycache rules. | `git check-ignore -v` on a config-nested `.pyc` matches the re-ignore rule; future `git add -A` cannot commit bytecode under packaged config trees. |
| **LOG-EXC-01** | LOG / follow-up from GS-223 | The sibling routers `api/routes.py`, `api/supply_chain.py`, `api/delivery.py` still carry the blanket `except Exception -> HTTP 400`; `delivery.py:347` additionally fabricates zero depot coverage on shape-parse failure. Adopt the shared `geo_infer_log.api.errors.ErrorHandlerMiddleware` + `except ValueError` swap; make the fallback raise or log-and-propagate. | TestClient probe: TypeError from a handler yields 500 INTERNAL_ERROR (no internal text) on all three routers; malformed shape raises instead of fabricating coverage. |
| **OPS-LOG-01** | OPS / follow-up | OPS test fixtures leave `log_file` CWD-relative, creating root `logs/geo_infer_ops.log` on local runs (contracts gate then flags the dir). Point OPS test fixtures' `log_file` at `tmp_path`. | Full OPS suite leaves no repo-root `logs/` directory. |

---


## GNN interoperability follow-up (September 2026)

TEST-GNN-01 (Python 3.12 PROJ SQLite disk-I/O cause) is tiered **Medium** in
the open-work table above with the continuation-receipt evidence; this section
is retained only as a pointer for existing links.


