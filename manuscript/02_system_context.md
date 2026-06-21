# System Context {#sec:system_context}

## Project Boundary

A 44-module geospatial inference framework for spatial analysis, active inference, domain modeling, agent workflows, and repository validation.

## Source Surfaces

- `GEO-INFER-*/`
- `GEO-INFER-TEST/`
- `README.md`
- `ISA.md`
- `TODO.md`
- `pyproject.toml`

## Template Boundary

The private project lives in the sidecar repository. Rendering and validation run through the sibling public template checkout after `link-projects` mirrors the project into `template/projects/` as a local symlink.
