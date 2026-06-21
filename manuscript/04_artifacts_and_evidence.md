# Artifacts and Evidence {#sec:artifacts_evidence}

## Evidence Inventory

| Surface | Role |
|---|---|
| `GEO-INFER-*/` | Source directory to inspect before turning prose into claims. |
| `GEO-INFER-TEST/` | Source directory to inspect before turning prose into claims. |
| `README.md` | Source file or ledger to inspect before turning prose into claims. |
| `ISA.md` | Source file or ledger to inspect before turning prose into claims. |
| `TODO.md` | Source file or ledger to inspect before turning prose into claims. |
| `pyproject.toml` | Source file or ledger to inspect before turning prose into claims. |

## Current Evidence Status

This scaffold does not yet bind figures, tables, benchmarks, or claims to generated outputs. When the project has a stable artifact manifest, summarize it here and move reproducible tables or figures into `../output/` before referencing them.

## Claim Discipline

A claim is manuscript-ready only when it has one of the following support types:

- A passing test or validator command.
- A generated output with a deterministic producer.
- A source ledger, manifest, or configuration file.
- A resolved entry in `references.bib` for external literature.
