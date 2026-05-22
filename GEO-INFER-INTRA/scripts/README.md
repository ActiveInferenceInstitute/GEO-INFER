# GEO-INFER-INTRA/scripts

Scripts workspace within `GEO-INFER-INTRA`.

## Contents

- `maintenance/`
- `add_missing_deps.py`
- `analyze_module_dependencies.py`
- `audit_agents_docs.py`
- `cleanup_pyproject_deps.py`
- `fix_existing_pyproject.py`
- `fix_installation_issues.py`
- `migrate_to_uv.py`
- `validate_dependencies.py`
- `validate_uv_migration.py`
- `validate_uv_setup.py`

## Public Interface

- `add_missing_deps.py:add_dependencies` (function)
- `add_missing_deps.py:main` (function)
- `analyze_module_dependencies.py:extract_imports_from_file` (function)
- `analyze_module_dependencies.py:extract_imports_from_module` (function)
- `analyze_module_dependencies.py:normalize_package_name` (function)
- `analyze_module_dependencies.py:parse_pyproject_dependencies` (function)
- `analyze_module_dependencies.py:analyze_module` (function)
- `analyze_module_dependencies.py:main` (function)
- `audit_agents_docs.py:ImportExtractor` (class)
- `audit_agents_docs.py:ModuleChecker` (class)
- `audit_agents_docs.py:audit_agents_file` (function)
- `audit_agents_docs.py:main` (function)
- `cleanup_pyproject_deps.py:normalize_dep_name` (function)
- `cleanup_pyproject_deps.py:deduplicate_dependencies` (function)
- `cleanup_pyproject_deps.py:cleanup_pyproject` (function)
- `cleanup_pyproject_deps.py:main` (function)
- `fix_existing_pyproject.py:convert_pep_from_poetry` (function)
- `fix_existing_pyproject.py:fix_health_pyproject` (function)
- `fix_existing_pyproject.py:main` (function)
- `fix_installation_issues.py:relax_version_constraints` (function)

## Module Metadata

- Module: `GEO-INFER-INTRA`
- Package: `geo_infer_intra`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-INTRA`
- Tests: `uv run python GEO-INFER-TEST/run_unified_tests.py --module INTRA`

## Dependencies

- `fastapi>=0.95.0`
- `pydantic>=2.0.0`
- `sqlalchemy>=2.0.0`
- `elasticsearch>=8.0.0`
- `rdflib>=6.0.0`
- `mkdocs>=1.4.0`
- `celery>=5.2.0`
- `pyyaml>=6.0`
- `jsonschema>=4.0.0`
- `typer>=0.7.0`
- `rich>=12.0.0`
- `uvicorn>=0.20.0`

## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module INTRA
```

## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
