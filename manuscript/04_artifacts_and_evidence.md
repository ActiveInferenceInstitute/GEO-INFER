# Artifacts and Evidence {#sec:artifacts_evidence}

## Evidence Inventory

| Surface | Role |
|---|---|
| `output/data/research_inventory.json` | Machine-readable repository measurements and source provenance. |
| `output/data/manuscript_variables.json` | Complete token map used for manuscript injection. |
| `output/data/research_verification.json` | Commands actually run, statuses, durations, and output tails. |
| `output/figures/figure_registry.json` | Figure labels, dynamic captions, generator paths, and hashes. |
| `output/manuscript/` | Resolved publication copies consumed by a renderer. |

## Current Measured Surface

The generated inventory contains `{{SOURCE_FILE_COUNT}}` Python source files,
`{{SOURCE_LINE_COUNT}}` measured non-empty source lines, `{{TEST_FILE_COUNT}}`
Python test files, `{{DOCUMENTATION_PAGE_COUNT}}` documentation pages, and
`{{VALIDATOR_FILE_COUNT}}` validator Python files. Test files are distributed as
`{{UNIT_TEST_FILE_COUNT}}` unit, `{{INTEGRATION_TEST_FILE_COUNT}}` integration,
`{{PERFORMANCE_TEST_FILE_COUNT}}` performance, and `{{H3_TEST_FILE_COUNT}}`
H3-named files where those categories are present in the checkout.

These are evidence-surface counts, not estimates of scientific validity. The
verification record currently reports `{{VERIFICATION_STATUS}}`; its exact
command-level outcomes are available in the generated JSON artifact.

## Generated Figures

The registry declares `{{FIGURE_COUNT}}` publication figures:

- [@fig:module_inventory] measures implementation and test surfaces across all
  modules.
- [@fig:research_spine] isolates the Active Inference, Bayesian, and RISK
  modules named by the research agenda.
- [@fig:validation_surface] compares discovered test categories with repository
  documentation and validator surfaces.

## Claim Discipline

A claim is manuscript-ready only when it has one of the following support types:

- A passing test or validator command.
- A generated output with a deterministic producer and provenance registry.
- A source ledger, manifest, or configuration file.
- A resolved entry in `references.bib` for external literature.
