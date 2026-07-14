# GEO-INFER-TEST

Unified testing framework for quality assurance across all GEO-INFER modules with automated testing, performance benchmarks, and integration validation.

## Contents

- `config/`
- `docs/`
- `examples/`
- `src/`
- `tests/`
- `rewrite_readme_agents.py`
- `run_model_audit.py`
- `run_unified_tests.py`
- `setup.py`
- `validate_act_geospatial_contract.py`
- `validate_act_script_orchestration.py`
- `validate_active_inference_contract.py`
- `validate_h3_active_inference_contract.py`
- `validate_model_contracts.py`
- `validate_repo_contracts.py`
- `validate_skills.py`
- `validate_test_contracts.py`
- `.cursorrules`
- `SKILL.md`
- `TESTING.md`
- `pyproject.toml`
- `requirements.txt`

## Public Interface

- `rewrite_readme_agents.py:ModuleInfo` (class)
- `rewrite_readme_agents.py:git_ls_files` (function)
- `rewrite_readme_agents.py:tracked_files` (function)
- `rewrite_readme_agents.py:read_pyproject` (function)
- `rewrite_readme_agents.py:requirement_lines` (function)
- `rewrite_readme_agents.py:discover_modules` (function)
- `rewrite_readme_agents.py:module_for` (function)
- `rewrite_readme_agents.py:tracked_doc_files` (function)
- `rewrite_readme_agents.py:direct_contents` (function)
- `rewrite_readme_agents.py:public_symbols` (function)
- `rewrite_readme_agents.py:purpose_for` (function)
- `rewrite_readme_agents.py:test_command` (function)
- `rewrite_readme_agents.py:validation_commands` (function)
- `rewrite_readme_agents.py:module_readme_notes` (function)
- `rewrite_readme_agents.py:module_agent_notes` (function)
- `rewrite_readme_agents.py:render_root_readme` (function)
- `rewrite_readme_agents.py:render_root_agents` (function)
- `rewrite_readme_agents.py:render_readme` (function)
- `rewrite_readme_agents.py:render_agents` (function)
- `rewrite_readme_agents.py:expected_doc_files` (function)

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


## Strict Testing Contracts

- `src/geo_infer_test/testing.py` exports deterministic RNG, local filesystem,
  HTTP, SQLite, and service fixtures plus finite/probability/matrix/model and
  visualization-manifest assertions.
- `validate_test_contracts.py --strict` validates every module inventory,
  primary marker, forbidden pytest control, syntax tree, and behavior-test
  docstring.
- `validate_model_contracts.py` checks representative ACT model contracts;
  `run_model_audit.py` emits finite statistics, a PNG visualization, SHA-256
  sidecars, and a deterministic manifest.

## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
