# GEO-INFER Ideal State Artifact

Last updated: 2026-05-18

This artifact defines the ideal state for GEO-INFER hardening work. It is not a
roadmap by itself; it is the verification target that implementation plans and
release gates should measure against.

## Active Inference Spine

The canonical Active Inference implementation is `GEO-INFER-ACT`.

Ideal state criteria:

- ACT exposes stable typed result contracts: `FreeEnergyBreakdown`, `PolicyEvaluation`, and `ActiveInferenceStepResult`.
- Categorical free energy reports `F = complexity - accuracy` with finite normalized probability terms.
- Expected free energy reports epistemic, pragmatic, entropy, risk, and selection probability terms.
- Policy selection evaluates all candidates by expected free energy; deterministic mode selects the lowest value.
- Stochastic policy selection is seedable through `PolicySelector(random_seed=...)`.
- `ActiveInferenceModel.step(..., return_result=True)` returns a typed result without breaking tuple-return compatibility.
- BAYES and MATH support ACT instead of duplicating incompatible Active Inference contracts.
- AGENT and SIM adapters either call ACT or document equivalent expected-free-energy semantics.

Verification:

```bash
uv run python GEO-INFER-TEST/validate_active_inference_contract.py
uv run --package geo-infer-act --extra dev python -m pytest GEO-INFER-ACT/tests -q
```

## Bayesian And Math Foundations

Ideal state criteria:

- `GEO-INFER-BAYES` mean-field and full-rank variational inference paths run without guarded `NotImplementedError`.
- Full-rank VI uses a Cholesky covariance factor and finite posterior samples.
- `GEO-INFER-MATH` convenience imports do not require Flask or other web dependencies.
- Flask-backed MATH APIs are reachable through the documented `web` extra.

Verification:

```bash
uv run --package geo-infer-bayes --extra dev python -m pytest GEO-INFER-BAYES/tests -q
uv run --package geo-infer-math --extra dev python -m pytest GEO-INFER-MATH/tests -q
```

## Repo-Wide Contracts

Ideal state criteria:

- Exactly 44 `GEO-INFER-*` modules are present.
- Every module has `README.md`, `AGENTS.md`, `SKILL.md`, and `pyproject.toml`.
- Python package directories use lowercase `geo_infer_<module>` casing.
- `pyproject.toml` is the canonical packaging surface; `setup.py` is compatibility only.
- Existing `setup.py` files parse successfully.
- Optional dependency failures degrade gracefully or are reported as warnings by contract checks.
- Source-language debt involving mock/stub/fake/placeholder terms is tracked and driven down.

## Modular Hygiene

Ideal state criteria:

- Root `pyproject.toml`, `uv.lock`, and `.python-version` define the shared uv environment.
- Root `[tool.uv.workspace]` covers all `GEO-INFER-*` modules.
- Each module keeps at least four pytest files under `tests/`.
- Planned work is tracked in root `TODO.md` or issues, not source/test task markers.
- Importable libraries never configure process-wide logging; CLI entrypoints may configure handlers.

Verification:

```bash
uv run python GEO-INFER-TEST/validate_skills.py --check-xrefs
uv run python GEO-INFER-TEST/validate_repo_contracts.py
uv run python GEO-INFER-TEST/validate_repo_contracts.py --strict-source-language
```

## Documentation And Signposting

Ideal state criteria:

- Root `README.md`, `CLAUDE.md`, `PAI.md`, `TODO.md`, and INTRA docs describe verified commands.
- Active Inference tutorials use current `geo_infer_act` APIs and run as written.
- Module docs do not claim package casing or package capabilities that conflict with the filesystem.
- Generated assessment outputs are clearly treated as historical artifacts unless regenerated.

## Release Evidence

Each hardening pass should record:

- Baseline failures observed before changes.
- Files changed for source, tests, validators, and docs.
- Exact commands run and pass/fail outcomes.
- Known residual warnings, especially optional dependency import warnings and source-language debt.
