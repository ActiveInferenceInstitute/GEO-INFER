# GEO-INFER Agent Instructions

Use this file as the repository-level operating contract for automated agents working in GEO-INFER.

## Repository Scope

- Root path: `/Users/4d/Documents/GitHub/GEO-INFER`
- Modules: `GEO-INFER-ACT`, `GEO-INFER-AG`, `GEO-INFER-AGENT`, `GEO-INFER-AI`, `GEO-INFER-ANT`, `GEO-INFER-API`, `GEO-INFER-APP`, `GEO-INFER-ART`, `GEO-INFER-BAYES`, `GEO-INFER-BIO`, `GEO-INFER-CIV`, `GEO-INFER-CLIMATE`, `GEO-INFER-COG`, `GEO-INFER-COMMS`, `GEO-INFER-DATA`, `GEO-INFER-ECON`, `GEO-INFER-EDU`, `GEO-INFER-EMERGENCY`, `GEO-INFER-ENERGY`, `GEO-INFER-EXAMPLES`, `GEO-INFER-FOREST`, `GEO-INFER-GIT`, `GEO-INFER-HEALTH`, `GEO-INFER-INTRA`, `GEO-INFER-IOT`, `GEO-INFER-LOG`, `GEO-INFER-MARINE`, `GEO-INFER-MATH`, `GEO-INFER-METAGOV`, `GEO-INFER-NORMS`, `GEO-INFER-OPS`, `GEO-INFER-ORG`, `GEO-INFER-PEP`, `GEO-INFER-PLACE`, `GEO-INFER-REQ`, `GEO-INFER-RISK`, `GEO-INFER-SEC`, `GEO-INFER-SIM`, `GEO-INFER-SPACE`, `GEO-INFER-SPM`, `GEO-INFER-TEST`, `GEO-INFER-TIME`, `GEO-INFER-TRANSPORT`, `GEO-INFER-WATER`
- Package manager: `uv`
- Python target: 3.11+

## Required Workflow

1. Inspect the relevant module before editing.
2. Keep functionality in the owning module under `src/`.
3. Keep scripts and examples as thin orchestration surfaces.
4. Update README.md and AGENTS.md when behavior, commands, exports, or dependencies change.
5. Run the narrowest relevant test first, then the repo contract validators.

## Standard Commands

```bash
uv sync --all-extras
uv run python GEO-INFER-TEST/validate_repo_contracts.py --strict-source-language
uv run python GEO-INFER-TEST/validate_skills.py --check-xrefs
uv run python GEO-INFER-TEST/run_unified_tests.py --category unit
uv run python GEO-INFER-TEST/run_unified_tests.py --category integration
uv run python GEO-INFER-TEST/run_unified_tests.py --h3-migration
```

## Documentation Contract

Agent-facing documentation must be operational: current paths, commands, package names, public exports, test surfaces, and failure triage. Do not advertise planned APIs in AGENTS.md; use issues, roadmaps, or implementation status files for future work.
