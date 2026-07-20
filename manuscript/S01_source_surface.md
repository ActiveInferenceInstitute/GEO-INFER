# Supplemental Source Surface {#sec:source_surface}

This supplement records the source surfaces used by the generated manuscript
evidence bundle. The current source fingerprint is
`{{RESEARCH_SOURCE_HASH}}` at commit `{{RESEARCH_COMMIT}}`.

| Surface | Role |
|---|---|
| `GEO-INFER-*/src/` | Importable implementation surface measured per module. |
| `GEO-INFER-*/tests/` | Module behavior and contract evidence surface. |
| `GEO-INFER-TEST/` | Repository validators, unified suites, and reproducibility checks. |
| `GEO-INFER-INTRA/docs/` | Cross-module conceptual and user-facing documentation. |
| `pyproject.toml` and `uv.lock` | Project version and environment provenance. |
| `output/data/` | Generated inventory, variables, verification, and manifest records. |
| `output/figures/` | Generated figures and their caption/provenance registry. |

## Expansion Checklist

- Confirm which files are authored source and which are generated.
- Confirm which commands reproduce the current outputs.
- Confirm that all changing values are tokens in the tracked manuscript source.
- Confirm that every figure is present in the registry and carries a complete caption.
- Confirm which external references need verified BibTeX entries.
- Confirm whether any private material must be summarized rather than quoted or copied.
