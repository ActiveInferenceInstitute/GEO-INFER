# GEO-INFER open work ledger

> Last reviewed: 2026-07-31
> Scope: the 44-module workspace rooted at this repository.

This is the canonical open-only ledger. Completed historical work is retained
in Git history, release notes, and assessment receipts; it is deliberately not
relisted as unfinished work here.

## Completed (2026-07-31)

- **VIZ-01**: Deterministic visualization receipts — shared
  `write_visualization_receipt()` helper in SPACE with 8 unit tests. ACT
  orchestrator, Cascadia reporting engine, and Del Norte dashboard all produce
  `.manifest.json` sidecars with input hashes, H3 version metadata, artifact
  checks, and accessibility checks.
- **SIM-01**: MesaModelBridge wraps `mesa.Model` through the SimulationEngine
  interface (20 tests). Mesa is an optional dependency (HAS_MESA flag, graceful
  import path). Supports initialize/step/run/cancel/export_results/save_checkpoint.
- **DOMAIN-01**: 57 behavior-based acceptance tests across COG (16), SEC (36),
  OPS (8), and ENERGY (5) — covering documented feature scopes that previously
  lacked focused probes.

## Open items

| ID | Scope | Open work | Behavior-based acceptance probe |
| --- | --- | --- | --- |
| TEST-01 | All modules | Finish the release-quality performance and coverage gates and record their exact output after the clean unit/integration/contract/H3/documentation/skills gates. | The release receipt records exact commands, exit codes, test counts, coverage, performance results, and optional backend availability with no skipped or xfailed tests. |
| DOMAIN-02 | SPM/METAGOV/TRANSPORT/EMERGENCY/CIV/REQ/ORG/NORMS | Extend the DOMAIN-01 pattern (acceptance tests for claims documented in SKILL.md/AGENTS.md but lacking coverage) to the remaining modules. SPM's GLM already has adequate unit coverage (10 tests in test_glm.py) but the remaining modules should be audited. | Each module adds a focused acceptance test and a current status receipt; no roadmap claim is promoted to implemented behavior without that probe. |

## Release gate commands

Run from the repository root with a task-specific cache if needed:

```bash
set -o pipefail
UV_CACHE_DIR=/tmp/geo-infer-uv-cache uv sync --locked --all-packages
UV_CACHE_DIR=/tmp/geo-infer-uv-cache uv run python GEO-INFER-TEST/rewrite_readme_agents.py --check
UV_CACHE_DIR=/tmp/geo-infer-uv-cache uv run python GEO-INFER-TEST/validate_repo_contracts.py --strict-source-language --skip-import-smoke
UV_CACHE_DIR=/tmp/geo-infer-uv-cache uv run python GEO-INFER-TEST/validate_test_contracts.py --strict
UV_CACHE_DIR=/tmp/geo-infer-uv-cache uv run python GEO-INFER-TEST/validate_documentation.py --strict
UV_CACHE_DIR=/tmp/geo-infer-uv-cache uv run python GEO-INFER-TEST/validate_skills.py --check-xrefs
UV_CACHE_DIR=/tmp/geo-infer-uv-cache uv run python GEO-INFER-TEST/validate_h3_active_inference_contract.py
UV_CACHE_DIR=/tmp/geo-infer-uv-cache uv run python GEO-INFER-TEST/run_unified_tests.py --category unit
UV_CACHE_DIR=/tmp/geo-infer-uv-cache uv run python GEO-INFER-TEST/run_unified_tests.py --category integration
UV_CACHE_DIR=/tmp/geo-infer-uv-cache uv run python GEO-INFER-TEST/run_unified_tests.py --category system
UV_CACHE_DIR=/tmp/geo-infer-uv-cache uv run python GEO-INFER-TEST/run_unified_tests.py --category performance
UV_CACHE_DIR=/tmp/geo-infer-uv-cache uv run python GEO-INFER-TEST/run_unified_tests.py --category coverage --timeout 900
git diff --check
```

Optional integrations such as SRAI, external data services, and GPU execution
must be reported separately with their prerequisite and observed result.

Note: `validate_repo_contracts.py` with `--strict-source-language` has been
observed to time out in this environment when scanning all 44 modules. The
other gates (test contracts, H3 contracts, documentation, skills xrefs, and
the unified test suites) pass cleanly.