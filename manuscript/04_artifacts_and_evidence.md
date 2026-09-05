# Artifacts and Evidence {#sec:artifacts_evidence}

## Evidence Inventory

| Surface | Role |
|---|---|
| `output/data/research_inventory.json` | Machine-readable repository measurements and source provenance. |
| `output/data/manuscript_variables.json` | Complete token map used for manuscript injection. |
| `output/data/research_verification.json` | Commands actually run, statuses, return codes, durations, and output tails. |
| `figure_registry.json` under `output/figures` | Figure labels, dynamic captions, generator paths, and a SHA-256 digest of each written image. |
| `output/manuscript/` | Resolved publication copies consumed by a renderer. |

: Evidence inventory of generated artifacts. Every row is written by
`manuscript/generate_research_artifacts.py` in the same pass and describes the
same build; none of them is authored by hand. {#tbl:evidence_inventory}

## Current Measured Surface

The generated inventory contains `{{SOURCE_FILE_COUNT}}` Python source files,
`{{SOURCE_LINE_COUNT}}` measured non-empty source lines, `{{TEST_FILE_COUNT}}`
Python test files, `{{DOCUMENTATION_PAGE_COUNT}}` cross-module documentation
pages under `GEO-INFER-INTRA/docs/`, and `{{VALIDATOR_FILE_COUNT}}`
`validate_*.py` validator scripts in `GEO-INFER-TEST`. Test files are
partitioned by the directory they live in into `{{UNIT_TEST_FILE_COUNT}}`
unit, `{{INTEGRATION_TEST_FILE_COUNT}}` integration,
`{{PERFORMANCE_TEST_FILE_COUNT}}` performance, and `{{OTHER_TEST_FILE_COUNT}}`
other; those four are mutually exclusive and sum to `{{TEST_FILE_COUNT}}`,
and the build fails if they do not. H3 coverage is a cross-cutting tag rather
than a fifth partition: `{{H3_TEST_FILE_COUNT}}` test files carry `h3` in
their filename, and they are distributed across the categories above.

These are evidence-surface counts, not estimates of scientific validity. The
verification record currently reports `{{VERIFICATION_STATUS}}`; its exact
command-level outcomes are available in the generated JSON artifact.

## Verification Record

The verification record in `output/data/research_verification.json` is the
manuscript's only source of executed-command evidence. It is a schema-versioned
object holding whether full validation was requested and one result entry per
command group that ran, each carrying the group name, the exact command line,
a `passed` / `failed` / `not-run` status, the process return code, the wall
duration in seconds, and a tail of captured output.

The generator defines command groups in two tiers, and this build defines
`{{VERIFICATION_DEFINED_COUNT}}` of them in total. The default tier
byte-compiles every module source tree, example tree, and the manuscript
package, then runs the strict repository-contract, documentation, skills,
test-contract, model-contract, and reproducibility validators in
`GEO-INFER-TEST`. Passing `--full-validation` adds a second tier — the unit,
integration, performance, and H3-migration suites driven through the unified
test runner — and raises the defined-group count accordingly.

For this build the record reports `{{VERIFICATION_STATUS}}`:
`{{VERIFICATION_PASS_COUNT}}` groups passed, `{{VERIFICATION_FAIL_COUNT}}`
failed, and `{{VERIFICATION_UNRUN_COUNT}}` of the
`{{VERIFICATION_DEFINED_COUNT}}` defined groups produced no recorded outcome.
The unrun count is derived from the record and the command definitions
together, so a group that is defined and skipped is counted as skipped rather
than silently disappearing from the denominator. A build invoked with
`--publication` refuses to produce artifacts while that record is empty; the
present build was not invoked that way, and the absence of executed evidence
is stated rather than repaired.

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
