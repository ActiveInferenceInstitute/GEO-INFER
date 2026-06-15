# GEO-INFER-TEST

Unified testing framework for quality assurance across all GEO-INFER modules with automated testing, performance benchmarks, and integration validation.

## Contents

- `config/`
- `docs/`
- `examples/`
- `src/`
- `tests/`
- `rewrite_readme_agents.py`
- `run_unified_tests.py`
- `setup.py`
- `validate_act_geospatial_contract.py`
- `validate_act_script_orchestration.py`
- `validate_active_inference_contract.py`
- `validate_h3_active_inference_contract.py`
- `validate_repo_contracts.py`
- `validate_skills.py`
- `.cursorrules`
- `SKILL.md`
- `TESTING.md`
- `pyproject.toml`
- `requirements.txt`

## Public Interface

- `rewrite_readme_agents.py:ModuleInfo` (class)
- `rewrite_readme_agents.py:git_ls_files` (function)
- `rewrite_readme_agents.py:read_pyproject` (function)
- `rewrite_readme_agents.py:requirement_lines` (function)
- `rewrite_readme_agents.py:discover_modules` (function)
- `rewrite_readme_agents.py:module_for` (function)
- `rewrite_readme_agents.py:tracked_doc_files` (function)
- `rewrite_readme_agents.py:direct_contents` (function)
- `rewrite_readme_agents.py:public_symbols` (function)
- `rewrite_readme_agents.py:purpose_for` (function)
- `rewrite_readme_agents.py:test_command` (function)
- `rewrite_readme_agents.py:render_root_readme` (function)
- `rewrite_readme_agents.py:render_root_agents` (function)
- `rewrite_readme_agents.py:render_readme` (function)
- `rewrite_readme_agents.py:render_agents` (function)
- `rewrite_readme_agents.py:main` (function)
- `run_unified_tests.py:CommandResult` (class)
- `run_unified_tests.py:Module` (class)
- `run_unified_tests.py:SuiteReport` (class)
- `run_unified_tests.py:discover_geo_infer_modules` (function)

## Module Metadata

- Module: `GEO-INFER-TEST`
- Package: `geo_infer_test`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-TEST`
- Tests: `uv run python GEO-INFER-TEST/run_unified_tests.py --module TEST`

## Dependencies

- `coverage[toml]>=7.0.0`
- `factory-boy>=3.2.0`
- `faker>=18.0.0`
- `geopandas>=0.10.0`
- `hypothesis>=6.0.0`
- `jinja2>=3.1.0`
- `jsonschema>=4.0.0`
- `locust>=2.0.0`
- `matplotlib>=3.5.0`
- `memory-profiler>=0.60.0`
- `numpy>=1.20.0`
- `pandas>=1.3.0`

## Validation

```bash
uv sync --all-packages --all-extras
uv run python GEO-INFER-TEST/run_unified_tests.py --module TEST
```

Repo-wide contract checks:

```bash
uv run python GEO-INFER-TEST/validate_repo_contracts.py --strict-source-language --skip-import-smoke
uv run python GEO-INFER-TEST/validate_skills.py --check-xrefs
```

`validate_repo_contracts.py` enforces module inventory, signposts, package casing, root uv workspace files, minimum test inventory, source/test task-marker hygiene, local-link integrity, generated-artifact hygiene, H3 dependency metadata, and library logging configuration.

## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
