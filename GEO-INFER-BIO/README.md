# GEO-INFER-BIO

Bioinformatics and biological data analysis with geospatial context for spatial omics, landscape genetics, phylogeography, and microbial ecology.

## Contents

- `docs/`
- `examples/`
- `src/`
- `tests/`
- `setup.py`
- `Dockerfile`
- `SKILL.md`
- `docker-compose.yml`
- `pyproject.toml`
- `requirements.txt`

## Public Interface

- No public Python symbols are defined directly in this directory.

## Module Metadata

- Module: `GEO-INFER-BIO`
- Package: `geo_infer_bio`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-BIO`
- Tests: `uv run python GEO-INFER-TEST/run_unified_tests.py --module BIO`

## Dependencies

- `numpy>=1.21.0`
- `pandas>=1.3.0`
- `scipy>=1.7.0`
- `biopython>=1.79`
- `networkx>=2.6.0`
- `scikit-learn>=0.24.0`
- `matplotlib>=3.4.0`
- `seaborn>=0.11.0`
- `geopandas>=0.9.0`
- `shapely>=1.8.0`
- `fastapi>=0.100.0`
- `uvicorn>=0.15.0`


## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module BIO
```


## Visualization Contracts

- Biological plotting helpers validate required columns, finite coordinates and
  values, sequence inputs, and geographic bounds before rendering.
- Plot helpers return their Matplotlib figure and create nested output parents;
  saved figures are closed after writing to avoid leaking global figure state.

## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
