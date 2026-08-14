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
