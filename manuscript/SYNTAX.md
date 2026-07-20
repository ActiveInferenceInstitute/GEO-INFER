# Manuscript Syntax - GEO-INFER

This manuscript uses the shared template conventions from `docs/guides/manuscript-semantics.md` in the sibling template repository.

## Section Labels

| File | H1 | Label |
|---|---|---|
| `00_abstract.md` | Abstract | `{#sec:abstract}` |
| `01_introduction.md` | Introduction | `{#sec:introduction}` |
| `02_system_context.md` | System Context | `{#sec:system_context}` |
| `03_methods.md` | Methods | `{#sec:methods}` |
| `04_artifacts_and_evidence.md` | Artifacts and Evidence | `{#sec:artifacts_evidence}` |
| `05_reproducibility.md` | Reproducibility | `{#sec:reproducibility}` |
| `06_limitations_and_next_steps.md` | Limitations and Next Steps | `{#sec:limitations_next_steps}` |
| `S01_source_surface.md` | Supplemental Source Surface | `{#sec:source_surface}` |
| `98_symbols_glossary.md` | Symbols and Glossary | `{#sec:symbols_glossary}` |
| `99_references.md` | References | `{#sec:references}` |

## Citations

Use Pandoc citation syntax only, for example `[@real_key]`. Every key must exist in `references.bib` before it appears in prose.

## Figures

Generated figures are produced by `generate_research_artifacts.py`, registered
with dynamic captions, and live under `../output/figures/` in the authored
manuscript source. They are referenced with labels such as:

```markdown
![Generated caption text.](../output/figures/example.png){#fig:example width=80%}
```

The generator rewrites the relative figure path for resolved copies under
`output/manuscript/`, and rejects unresolved uppercase variable tokens.

## Claims

Changing quantitative claims must be represented by `{{TOKENS}}` in authored
sections and computed by the manuscript generator. Publication claims require
source-backed artifacts, passing verification, and resolved bibliography
entries.
