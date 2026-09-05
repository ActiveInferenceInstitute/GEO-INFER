# Supplemental Source Surface {#sec:source_surface}

This supplement records the source surfaces used by the generated manuscript
evidence bundle. The current source fingerprint is
`{{RESEARCH_SOURCE_HASH}}` at commit `{{RESEARCH_COMMIT}}`.

| Surface | Role |
|---|---|
| `GEO-INFER-*/src/` | Python implementation surface measured per module. |
| `GEO-INFER-*/tests/` | Module behavior and contract evidence surface. |
| `GEO-INFER-TEST/` | Repository validators, unified suites, and reproducibility checks. |
| `GEO-INFER-INTRA/docs/` | Cross-module conceptual and user-facing documentation. |
| `GEO-INFER-INTRA/docs/research_grade_inference_contracts.md` | Authored source for the ACT, BAYES, and RISK interface obligations reproduced in the Composition Contract. |
| `GEO-INFER-ACT/src/geo_infer_act/core/types.py` | Typed results — `FreeEnergyBreakdown`, `PolicyEvaluation`, `ActiveInferenceStepResult` — that the contract is expressed over. |
| `pyproject.toml` and `uv.lock` | Project version and environment provenance. |
| `output/data/` | Generated inventory, variables, verification, and manifest records. |
| `output/figures` | Generated figures and their caption and provenance registry. |

: Tracked source surfaces measured by the evidence bundle. The first four rows
are measured populations; the two file-level rows are pinned authored sources
that the Composition Contract reproduces, so a rename in the checkout is
visible here. {#tbl:source_surface}

## Authored and Generated Boundary

[@tbl:source_surface] lists what is measured. This subsection records who
writes what, which is the invariant the Reproducibility contract depends on.

| Path | Written by | Tracked |
|---|---|---|
| `manuscript/0*.md`, `manuscript/9*.md`, `manuscript/S*.md` | Author | yes |
| `manuscript/references.bib` | Author | yes |
| `manuscript/preamble.md` | Author | yes |
| `manuscript/generate_research_artifacts.py` | Author | yes |
| `manuscript/config.yaml` | Author, except four generator-owned fields marked in place | yes |
| `output/data/`, `output/figures`, `output/manuscript/` | Generator | no |
| `output/pdf/`, `output/web/` | Renderer | no |

: Authored versus generated files. Every tracked file under `manuscript/` is
authored except the four fields in `config.yaml` that the renderer forces the
generator to resolve in place; everything under `output/` is disposable and is
rebuilt from the checkout. {#tbl:authored_generated}

## Reproducing This Build

The command that regenerates every measured value, figure, caption, and
resolved manuscript copy in this document, and that a publication build must
use, is:

```bash
uv run python manuscript/generate_research_artifacts.py --full-validation --publication
```

That invocation refuses to proceed against a dirty working tree, runs both
tiers of verification command group, and refuses to finish while the evidence
record is empty. Dropping `--publication` produces a working-tree build whose
commit stamp is suffixed to record that it is not a clean checkout. Adding
`--check` to a plain invocation verifies the published token map against the
measured checkout without writing anything.

## External References

Each externally-supported claim area in this manuscript resolves to a verified
BibTeX entry rather than to a repository-derived count:

- Active inference and the free-energy formulation
  [@friston_free_energy_2010; @parr_active_inference_2022], and the
  `inferactively-pymdp` backend the categorical path depends on
  [@heins_pymdp_2022].
- Bayesian posterior estimation and convergence diagnostics
  [@gelman_bda_2014].
- Extreme-value return levels underlying the risk module's Gumbel fit
  [@coles_extremes_2001].
- The H3 hierarchical spatial index [@h3_docs].

The generator fails the build on a citation with no entry, and names any entry
that no section cites, so this list and `references.bib` cannot drift apart
silently.
