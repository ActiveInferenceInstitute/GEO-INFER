# GEO-INFER-TEST

Unified testing framework for quality assurance across all GEO-INFER modules with automated testing, performance benchmarks, and integration validation.

## Contents

- `config/`
- `demo/`
- `docs/`
- `examples/`
- `src/`
- `tests/`
- `build_package_wheels.py`
- `import_probe.py`
- `rewrite_readme_agents.py`
- `run_model_audit.py`
- `run_unified_tests.py`
- `setup.py`
- `validate_act_geospatial_contract.py`
- `validate_act_script_orchestration.py`
- `validate_active_inference_contract.py`
- `validate_documentation.py`
- `validate_h3_active_inference_contract.py`
- `validate_logging_hygiene.py`
- `validate_model_contracts.py`
- `validate_packaging.py`
- `validate_repo_contracts.py`
- `validate_skills.py`
- `validate_test_contracts.py`
- `SKILL.md`
- `TESTING.md`
- `pyproject.toml`
- `requirements.txt`

## Public Interface

- `build_package_wheels.py:BuildResult` (class)
- `build_package_wheels.py:BuildSummary` (class)
- `build_package_wheels.py:validate_wheel_contents` (function)
- `build_package_wheels.py:build_wheel` (function)
- `build_package_wheels.py:verify_wheels` (function)
- `build_package_wheels.py:install_and_verify` (function)
- `build_package_wheels.py:main` (function)
- `import_probe.py:run_import_probe` (function)
- `rewrite_readme_agents.py:ModuleInfo` (class)
- `rewrite_readme_agents.py:git_ls_files` (function)
- `rewrite_readme_agents.py:tracked_files` (function)
- `rewrite_readme_agents.py:read_pyproject` (function)
- `rewrite_readme_agents.py:requirement_lines` (function)
- `rewrite_readme_agents.py:discover_modules` (function)
- `rewrite_readme_agents.py:module_for` (function)
- `rewrite_readme_agents.py:repository_doc_files` (function)
- `rewrite_readme_agents.py:direct_contents` (function)
- `rewrite_readme_agents.py:public_symbols` (function)
- `rewrite_readme_agents.py:purpose_for` (function)
- `rewrite_readme_agents.py:test_command` (function)

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
- `h3>=4.5.0,<5`
- `hypothesis>=6.0.0`
- `jinja2>=3.1.0`
- `jsonschema>=4.0.0`
- `locust>=2.0.0`
- `matplotlib>=3.5.0`
- `memory-profiler>=0.60.0`
- `numpy>=1.20.0`


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
- `validate_documentation.py --strict` validates the maintained documentation
  hub's relative links and rejects known stale current-state claims.
- `validate_model_contracts.py` checks representative ACT model contracts;
  `run_model_audit.py` emits finite statistics, a PNG visualization, SHA-256
  sidecars, and a deterministic manifest.

## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
