# GEO-INFER Framework

GEO-INFER is a 44-module geospatial inference monorepo for spatial analysis, active inference, domain modeling, agent workflows, and repository validation.

## Current Repository Facts

| Metric | Value |
| --- | ---: |
| Modules | 44 |
| Python source files | 884 |
| Python test files | 441 |
| Tracked README.md files | 830 |
| Tracked AGENTS.md files | 827 |

## Quick Start

```bash
uv sync --all-packages --all-extras
uv run python GEO-INFER-TEST/validate_repo_contracts.py --strict-source-language --skip-import-smoke
uv run python GEO-INFER-TEST/run_unified_tests.py --category unit
```

## Module Index

| Module | Package | Source files | Test files |
| --- | --- | ---: | ---: |
| `GEO-INFER-ACT` | `geo_infer_act` | 39 | 23 |
| `GEO-INFER-AG` | `geo_infer_ag` | 15 | 9 |
| `GEO-INFER-AGENT` | `geo_infer_agent` | 26 | 13 |
| `GEO-INFER-AI` | `geo_infer_ai` | 15 | 11 |
| `GEO-INFER-ANT` | `geo_infer_ant` | 21 | 7 |
| `GEO-INFER-API` | `geo_infer_api` | 13 | 9 |
| `GEO-INFER-APP` | `geo_infer_app` | 13 | 7 |
| `GEO-INFER-ART` | `geo_infer_art` | 21 | 7 |
| `GEO-INFER-BAYES` | `geo_infer_bayes` | 32 | 13 |
| `GEO-INFER-BIO` | `geo_infer_bio` | 9 | 7 |
| `GEO-INFER-CIV` | `geo_infer_civ` | 8 | 6 |
| `GEO-INFER-CLIMATE` | `geo_infer_climate` | 13 | 7 |
| `GEO-INFER-COG` | `geo_infer_cog` | 20 | 11 |
| `GEO-INFER-COMMS` | `geo_infer_comms` | 19 | 7 |
| `GEO-INFER-DATA` | `geo_infer_data` | 23 | 19 |
| `GEO-INFER-ECON` | `geo_infer_econ` | 34 | 12 |
| `GEO-INFER-EDU` | `geo_infer_edu` | 7 | 6 |
| `GEO-INFER-EMERGENCY` | `geo_infer_emergency` | 7 | 6 |
| `GEO-INFER-ENERGY` | `geo_infer_energy` | 11 | 8 |
| `GEO-INFER-EXAMPLES` | `geo_infer_examples` | 4 | 4 |
| `GEO-INFER-FOREST` | `geo_infer_forest` | 11 | 8 |
| `GEO-INFER-GIT` | `geo_infer_git` | 20 | 7 |
| `GEO-INFER-HEALTH` | `geo_infer_health` | 18 | 9 |
| `GEO-INFER-INTRA` | `geo_infer_intra` | 11 | 7 |
| `GEO-INFER-IOT` | `geo_infer_iot` | 16 | 7 |
| `GEO-INFER-LOG` | `geo_infer_log` | 18 | 8 |
| `GEO-INFER-MARINE` | `geo_infer_marine` | 12 | 8 |
| `GEO-INFER-MATH` | `geo_infer_math` | 66 | 16 |
| `GEO-INFER-METAGOV` | `geo_infer_metagov` | 23 | 12 |
| `GEO-INFER-NORMS` | `geo_infer_norms` | 19 | 8 |
| `GEO-INFER-OPS` | `geo_infer_ops` | 23 | 11 |
| `GEO-INFER-ORG` | `geo_infer_org` | 8 | 6 |
| `GEO-INFER-PEP` | `geo_infer_pep` | 33 | 9 |
| `GEO-INFER-PLACE` | `geo_infer_place` | 29 | 14 |
| `GEO-INFER-REQ` | `geo_infer_req` | 8 | 6 |
| `GEO-INFER-RISK` | `geo_infer_risk` | 29 | 10 |
| `GEO-INFER-SEC` | `geo_infer_sec` | 21 | 9 |
| `GEO-INFER-SIM` | `geo_infer_sim` | 14 | 4 |
| `GEO-INFER-SPACE` | `geo_infer_space` | 83 | 29 |
| `GEO-INFER-SPM` | `geo_infer_spm` | 26 | 16 |
| `GEO-INFER-TEST` | `geo_infer_test` | 13 | 19 |
| `GEO-INFER-TIME` | `geo_infer_time` | 15 | 13 |
| `GEO-INFER-TRANSPORT` | `geo_infer_transport` | 7 | 6 |
| `GEO-INFER-WATER` | `geo_infer_water` | 11 | 7 |

## Modular Hygiene

- Root `pyproject.toml`, `uv.lock`, and `.python-version` are the canonical uv environment surfaces.
- Sync the full workspace with `uv sync --all-packages --all-extras` before repo-wide validation.
- Each module owns importable behavior under `src/` and keeps at least four pytest files under `tests/`.
- Planned work belongs in root `TODO.md` or a tracked issue, not source or test task markers.
- Importable libraries use `logging.getLogger(__name__)`; process-wide logging configuration belongs in CLI entrypoints.

## Validation

- Repository contracts: `uv run python GEO-INFER-TEST/validate_repo_contracts.py --strict-source-language`
- Skill contracts: `uv run python GEO-INFER-TEST/validate_skills.py --check-xrefs`
- Unit tests: `uv run python GEO-INFER-TEST/run_unified_tests.py --category unit`
- Integration tests: `uv run python GEO-INFER-TEST/run_unified_tests.py --category integration`
- H3 contracts: `uv run python GEO-INFER-TEST/run_unified_tests.py --h3-migration`

## Documentation Policy

README.md and AGENTS.md files describe current, discoverable repository state. Do not add aspirational APIs to these files unless the implementation, export path, and validation command exist in this checkout.
