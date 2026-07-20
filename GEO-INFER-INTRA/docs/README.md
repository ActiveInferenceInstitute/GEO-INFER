# GEO-INFER-INTRA/docs

Docs workspace within `GEO-INFER-INTRA`.

## Contents

- `advanced/`
- `alphaearth/`
- `api/`
- `architecture/`
- `deployment/`
- `developer_guide/`
- `examples/`
- `geospatial/`
- `getting_started/`
- `guides/`
- `integration/`
- `knowledge_base/`
- `materiality/`
- `modules/`
- `ontology/`
- `realms/`
- `security/`
- `support/`
- `tnfd/`
- `tutorials/`
- `user_guide/`
- `workflows/`
- `DOCUMENTATION_IMPROVEMENTS.md`
- `DOCUMENTATION_IMPROVEMENTS_SUMMARY.md`
- `DOCUMENTATION_STANDARDS.md`
- `active_inference_guide.md`
- `api_schema.yaml`
- `bayesian_inference_guide.md`
- `data_dictionary.md`
- `documentation_guide.md`
- `examples_gallery.md`
- `geospatial_standards.md`
- `index.md`
- `installation.md`
- `module_readme_template.md`
- `overview.md`
- `research_grade_inference_contracts.md`
- `temporal_analysis_guide.md`
- `terminology.md`

## Public Interface

- No public Python symbols are defined directly in this directory.

## Module Metadata

- Module: `GEO-INFER-INTRA`
- Package: `geo_infer_intra`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-INTRA`
- Tests: `uv run python GEO-INFER-TEST/run_unified_tests.py --module INTRA`

## Dependencies

- `fastapi>=0.100.0`
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
