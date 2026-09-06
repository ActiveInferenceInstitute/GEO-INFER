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
command-level outcomes are published per group in
[@tbl:verification_record].

## Verification Record

The verification record in `output/data/research_verification.json` is the
manuscript's only source of executed-command evidence. It is a schema-versioned
object holding whether full validation was requested and one result entry per
command group that ran, each carrying the group name, the exact command line,
a `passed` / `failed` / `not-run` status, the process return code, the wall
duration in seconds, and a tail of captured output. The record also carries
the commit and source fingerprint of the checkout its commands ran against,
because those commands take minutes while a render is bounded: a build that
executes none of them republishes the stored record rather than emptying it,
and the record's own stamps are what keep that republication honest. This
build publishes a verification record {{VERIFICATION_RECORD_PROVENANCE}}. A
build that runs no verification command cannot write an empty record over a
populated one, so a render taken mid-development degrades to a stated
provenance gap rather than to deleted evidence.

The generator defines command groups in two tiers. The default tier
byte-compiles every module source tree, example tree, and the manuscript
package, then runs the strict repository-contract, documentation, skills,
test-contract, model-contract, and reproducibility validators in
`GEO-INFER-TEST`. Passing `--full-validation` adds a second tier — the unit,
integration, performance, and H3-migration suites driven through the unified
test runner.

Which tier a record was measured at is a property of the record, not of the
build that republishes it, and it travels with the results for that reason.
The record published here was measured at the `{{VERIFICATION_RECORD_TIER}}`
tier, which defines `{{VERIFICATION_DEFINED_COUNT}}` command groups in total,
and every count below is taken against that definition. Reading the
denominator from the build's own request instead was what let this manuscript
publish nine passes and two failures against seven defined groups: the
numerator was counted over the whole record and the denominator over the tier
the build happened to ask for. `build_variables` now refuses to render a
record whose outcomes do not sum to its own defined-group count, and
`--check` refuses a published bundle whose counts disagree with the record
it republishes.

The record reports `{{VERIFICATION_STATUS}}`:
`{{VERIFICATION_PASS_COUNT}}` groups passed, `{{VERIFICATION_FAIL_COUNT}}`
failed, and `{{VERIFICATION_UNRUN_COUNT}}` of the
`{{VERIFICATION_DEFINED_COUNT}}` groups its tier defines produced no recorded
outcome.
The unrun count is derived from the record and the command definitions
together, so a group that is defined and skipped is counted as skipped rather
than silently disappearing from the denominator. A build invoked with
`--publication` writes the artifacts it measured and then exits non-zero
rather than certify a record that is empty or that contains a failed group, so
the measurement survives on disk while the build does not pass; a build
invoked without it publishes whatever the record holds, including failures.

{{VERIFICATION_TABLE}}

: Per-group verification record for this build. Every command group the
record's tier defines has a row: `Exit` is the process return code and
`Seconds` the wall duration observed, and a group that did not run is printed
as `not run` rather than omitted. {#tbl:verification_record}

[@tbl:verification_record] is the command-level evidence behind the summary
above. A failed group is published with its return code instead of being
summarised away, which is what makes `passed`, `failed`, and `not run` three
distinct published states rather than two.

The commands are minutes long and a render hydrates on a bounded timeout, so
the record is stamped with the source hash, commit, and tier it describes and
is reused whenever it still names them. Reuse is the default at every tier,
including a build that was not asked to verify: a stored record that still
describes this tree is this build's evidence, and overwriting it with an empty
one would delete a measured result and republish `not run` in its place. A
record that names a different tree is not this build's measurement, but it is
not discarded either: a build that ran no command carries it forward with its
own stamps and publishes the provenance gap, because a stated gap is worth
more than a deleted measurement. Only an absent, unreadable, or command-free
record can be replaced by an empty one. `--rerun-verification` declines the
shortcut, so a build that was asked to verify runs the commands again rather
than reusing a matching record; on its own it asks for no measurement, and it
never licenses deleting a record it does not replace.

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
