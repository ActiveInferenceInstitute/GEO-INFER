# Manuscript - GEO-INFER

This directory is a template-format manuscript scaffold for:

**GEO-INFER: Geospatial Inference Framework**

A 44-module geospatial inference framework for spatial analysis, active inference, domain modeling, agent workflows, and repository validation.

## File Inventory

- `config.yaml`
- `preamble.md`
- `references.bib`
- `00_abstract.md`
- `01_introduction.md`
- `02_system_context.md`
- `03_methods.md`
- `04_artifacts_and_evidence.md`
- `05_reproducibility.md`
- `06_limitations_and_next_steps.md`
- `S01_source_surface.md`
- `98_symbols_glossary.md`
- `99_references.md`
- `AGENTS.md`
- `README.md`
- `SYNTAX.md`

## Source Surfaces

| Surface | Role |
|---|---|
| `GEO-INFER-*/` | Source directory to inspect before turning prose into claims. |
| `GEO-INFER-TEST/` | Source directory to inspect before turning prose into claims. |
| `README.md` | Source file or ledger to inspect before turning prose into claims. |
| `ISA.md` | Source file or ledger to inspect before turning prose into claims. |
| `TODO.md` | Source file or ledger to inspect before turning prose into claims. |
| `pyproject.toml` | Source file or ledger to inspect before turning prose into claims. |

## Verification

From the sibling template checkout, after `link-projects` has synced the sidecar:

```bash
uv run python -m infrastructure.orchestration link-projects
uv run python -m infrastructure.validation.cli markdown projects/working/GEO-INFER/manuscript/
```

Render only after replacing scaffold prose with project-bound evidence and checking any project-local gates documented in the repository root.
