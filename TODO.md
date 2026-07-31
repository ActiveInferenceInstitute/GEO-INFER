# GEO-INFER open work ledger

> Last reviewed: 2026-07-30
> Scope: the 44-module workspace rooted at this repository.

This is the canonical open-only ledger. Completed historical work is retained
in Git history, release notes, and assessment receipts; it is deliberately not
relisted as unfinished work here.

## Open items

| ID | Scope | Open work | Behavior-based acceptance probe |
| --- | --- | --- | --- |
| VIZ-01 | EXAMPLES/ACT and location-specific dashboards | Extend the new deterministic visualization receipt contract beyond the SPACE and PLACE engines to the remaining example/ACT and Cascadia/Del Norte dashboard entry points. | A clean temporary-output run for each remaining entry point creates a finite, nonempty artifact plus a manifest containing the input hash, H3 version where applicable, and accessibility checks. |
| TEST-01 | All modules | Finish the release-quality performance and coverage gates and record their exact output after the clean unit/integration/contract/H3/documentation/skills gates. | The release receipt records exact commands, exit codes, test counts, coverage, performance results, and optional backend availability with no skipped or xfailed tests. |
| SIM-01 | SIM | Complete the production Mesa/agent integration rather than treating the current deterministic engine as the final simulation backend. | A real Mesa-backed scenario runs, records state/metric history, exports JSON/DataFrame artifacts, and preserves cancellation/error state. |
| DOMAIN-01 | COG/SPM/ANT/SEC/OPS/METAGOV/TRANSPORT/EMERGENCY/CIV/REQ/ORG/NORMS/ENERGY | Close the remaining module feature scopes documented by their current module contracts (cognitive attention/memory, GLM/convergence, threat/monitoring, governance, network flow, allocation, participatory mapping, traceability, and energy benchmarking). | Each module adds a focused acceptance test and a current status receipt; no roadmap claim is promoted to implemented behavior without that probe. |

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
The full-fleet coverage command is currently tracked as TEST-01 because the
single process did not produce a trustworthy receipt within the bounded run
and was stopped after sustained resource use in this environment; the unit,
integration, performance, contract, H3, documentation, and skills gates are
complete.
