# manuscript

Manuscript workspace within GEO-INFER.

## Contents

- `00_abstract.md`
- `01_introduction.md`
- `02_system_context.md`
- `03_methods.md`
- `04_artifacts_and_evidence.md`
- `05_reproducibility.md`
- `06_limitations_and_next_steps.md`
- `98_symbols_glossary.md`
- `99_references.md`
- `S01_source_surface.md`
- `SYNTAX.md`
- `config.yaml`
- `preamble.md`
- `references.bib`

## Public Interface

- `generate_research_artifacts.py:ModuleMetrics` (class)
- `generate_research_artifacts.py:FigureSpec` (class)
- `generate_research_artifacts.py:RepositoryInventory` (class)
- `generate_research_artifacts.py:VerificationResult` (class)
- `generate_research_artifacts.py:collect_inventory` (function)
- `generate_research_artifacts.py:generate_figures` (function)
- `generate_research_artifacts.py:write_figure_registry` (function)
- `generate_research_artifacts.py:run_verification` (function)
- `generate_research_artifacts.py:build_variables` (function)
- `generate_research_artifacts.py:substitute_manuscript_text` (function)
- `generate_research_artifacts.py:write_resolved_manuscript` (function)
- `generate_research_artifacts.py:generate` (function)
- `generate_research_artifacts.py:main` (function)


## Validation

```bash
uv run python GEO-INFER-TEST/validate_repo_contracts.py --skip-import-smoke
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
