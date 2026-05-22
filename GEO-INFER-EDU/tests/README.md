# GEO-INFER-EDU/tests

Tests workspace within `GEO-INFER-EDU`.

## Contents

- `integration/`
- `unit/`
- `conftest.py`
- `test_curriculum.py`
- `test_exercise_generator.py`
- `test_exercises.py`
- `test_personalization.py`
- `test_professional.py`
- `test_progress.py`

## Public Interface

- `conftest.py:sample_coordinates` (function)
- `conftest.py:sample_geodataframe` (function)
- `conftest.py:tmp_output_dir` (function)
- `conftest.py:school_locations_gdf` (function)
- `conftest.py:population_density_gdf` (function)
- `conftest.py:education_config` (function)

## Module Metadata

- Module: `GEO-INFER-EDU`
- Package: `geo_infer_edu`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-EDU`
- Tests: `uv run python -m pytest GEO-INFER-EDU/tests`

## Dependencies

- Dependencies are declared in `pyproject.toml` or inherited from the workspace.

## Validation

```bash
uv run python -m pytest GEO-INFER-EDU/tests
```

## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
