# GEO-INFER open work ledger

> Last reviewed: 2026-08-13
> Scope: the multi-package workspace rooted at this repository.

This is the canonical open-only ledger. Completed work belongs in code, tests,
validation receipts, and Git history rather than in active backlog rows.
The 2026-08-13 performance and coverage campaign is recorded in
[`RELEASE_EVIDENCE_2026-08-13.md`](RELEASE_EVIDENCE_2026-08-13.md).

| ID | Scope | Open work | Behavior-based acceptance probe |
| --- | --- | --- | --- |
| REPRO-01 | Randomized and seeded workflows | Replace remaining process-global NumPy random-state calls and unstable hash-derived seeds with explicit generators or stable seeds. | Repeated runs with the same declared seed, including separate Python processes, produce the same relevant outputs without mutating global RNG state. |
| SEC-02b | AG / AI / DATA / GIT / OPS pickle consumers | Define and enforce the trusted-data boundary for model, cache, and storage pickle loads. | Untrusted serialized input is rejected before deserialization; trusted loads are explicit, documented, and covered by adversarial tests. |
| STATS-05 | SPM random-field-theory inference | Implement and validate full cluster-extent correction; the current first-order excursion approximation is not that method. | Known-null simulation demonstrates calibrated family-wise error for the implemented cluster-extent procedure and documents its assumptions. |
| PKG-V7 | Installed-package configuration discovery | Remove configuration lookups that depend on walking outward from `__file__`; use package resources or explicit injected paths. | A wheel installed into a clean environment resolves its packaged or supplied configuration from an unrelated working directory. |
| OUTPUT-01 | Remaining CWD-relative configuration and output paths | Route repository-relative configuration and generated output through explicit configuration or injected `Path` values. | Tests run from an unrelated temporary working directory and write only beneath the configured destination. |
| PLACE-V14 | Cascadia ecological GeoJSON inputs | Source and track the volcano, subduction-zone, major-watershed, and bioregion-boundary layers referenced by `cascadia_config.yaml`; record each layer's authoritative origin, date, transformation, and license rather than synthesizing coordinates to satisfy tests. | The four inputs pass provenance review and the Cascadia bioregion integration suite passes without missing-file failures or skips; any expected feature counts and geographic bounds are reconciled to the cited sources. |
| SUPPLY-01 | PyPI distribution naming for INTRA / SPACE / ACT / MATH / SIM | Confirmed 2026-08-18: `geo-infer-intra`, `geo-infer-space`, `geo-infer-act`, and `geo-infer-math` exist on PyPI as unrelated 0.0.1 "Reserved name placeholder. No code, no functionality." releases owned by `monkeydluffy1961`, not this project — real squatted names. No README/AGENTS/getting-started doc in this repo currently instructs a bare `pip install geo-infer-*` (all point to `uv pip install -e ./GEO-INFER-<MODULE>`), but `GEO-INFER-SIM/src/geo_infer_sim/core/mesa_bridge.py:117` raises an `ImportError` that tells the caller to run `` `pip install geo-infer-sim[mesa]` ``, and `geo-infer-sim` is not yet registered on PyPI (404 as of this check) — squattable today under the same pattern. Reserve/publish the real `geo-infer-sim` name (and audit any other still-unregistered `geo-infer-*` names actively referenced in error text or docs) before that message ships to more users, or rewrite the message to point only at the editable-install path. | No repository doc, docstring, or runtime error message instructs `pip install <name>` for a `geo-infer-*` PyPI distribution this project does not itself own and control; every install pointer resolves to `uv pip install -e ./GEO-INFER-<MODULE>` or a verified, project-controlled PyPI release. |

## Verification notes (2026-08-18)

- PyPI squatting on `geo-infer-intra`, `geo-infer-space`, `geo-infer-act`, and
  `geo-infer-math` was confirmed directly against the PyPI JSON API
  (`https://pypi.org/pypi/<name>/json`) on 2026-08-18; see SUPPLY-01.
- A previously circulated figure of "803 unresolved doc links across 94
  files" does not reproduce. Running the same link-existence method used by
  `GEO-INFER-TEST/validate_documentation.py` (which itself only checks its
  30-page authoritative allowlist and passes) across all 2,114 tracked
  Markdown files in this repository found 57 broken relative links in 7
  files (67 in 11 files if fenced code blocks are not excluded from the
  scan). That gap is unexplained; treat "803 / 94" as unverified rather than
  re-citing it until someone reproduces it with a documented method.
