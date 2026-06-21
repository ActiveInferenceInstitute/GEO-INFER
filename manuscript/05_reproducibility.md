# Reproducibility {#sec:reproducibility}

## Local Commands

Start with the project-local README and AGENTS instructions. Then validate this manuscript surface through the sibling template checkout:

```bash
uv run python -m infrastructure.orchestration link-projects
uv run python -m infrastructure.validation.cli markdown projects/<lifecycle>/<project>/manuscript/
```

Replace `<lifecycle>/<project>` with the qualified sidecar path for this project.

## Reproducibility Contract

- Do not cite results that cannot be regenerated or directly traced.
- Keep generated outputs under `output/` and manuscript source under `manuscript/`.
- Keep private data, credentials, and unpublished sensitive details out of the manuscript.
- Record exact verification commands before marking this manuscript publication-ready.
