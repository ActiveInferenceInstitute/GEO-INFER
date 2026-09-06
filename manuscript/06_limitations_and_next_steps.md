# Limitations and Next Steps {#sec:limitations_next_steps}

## Current Limitations

- Repository inventory counts measure implementation and verification surfaces;
  they do not establish domain validity, predictive accuracy, calibration, or
  causal efficacy.
- The generated figures summarize file-backed evidence surfaces and should not
  be read as benchmark results.
- A verification record is only as complete as the commands requested during
  the generation that produced it, and that generation is not necessarily this
  one: a build that requests none republishes the stored record instead of
  emptying it. This build reports `{{VERIFICATION_STATUS}}` with
  `{{VERIFICATION_UNRUN_COUNT}}` of the `{{VERIFICATION_DEFINED_COUNT}}`
  command groups its `{{VERIFICATION_RECORD_TIER}}` tier defines unrun, from a
  record {{VERIFICATION_RECORD_PROVENANCE}}, and
  exposes the command-level record for audit.
- The composition contract constrains interfaces, provenance, and refusal
  behavior. It is not a proof of correctness: no clause in it establishes that
  a free-energy value, a posterior, or a return level matches an external
  reference implementation or a field observation.
- Module theme membership is a declared editorial grouping, not a measured
  dependency structure. The manuscript reports no import graph, no coupling
  metric, and no evidence that the themes partition the framework's actual
  interactions.
- Documentation-page counts are scoped to `GEO-INFER-INTRA/docs/`, the
  cross-module documentation tree. No freshness, ownership, or staleness check
  runs over those pages, so the count says how many exist, not how many are
  current.
- External scientific claims require resolved entries in `references.bib` and
  should be expanded with domain-specific datasets and preregistered analyses.

## Next Steps

1. Extend the recorded evidence to the second tier: run
   `--full-validation --publication` with fixed data seeds so the unit,
   integration, performance, and H3-migration suites enter the record
   alongside the default tier, and archive `research_verification.json`,
   `research_inventory.json`, and the figure registry beside the rendered
   outputs.
2. Extend the inventory with domain datasets and benchmark results only when
   their producers emit machine-readable provenance and uncertainty.
3. Add preregistered comparisons for the Active Inference, Bayesian, and RISK
   research spine without replacing real model outputs with file-count proxies.
4. Add a documentation-freshness measurement so the documentation-page count
   can be qualified by currency rather than reported as a bare total.
5. Promote the composition contract's clauses into executable checks where they
   are not already covered by a module test, so the contract is verified by the
   same evidence record that reports the rest of the build.

## Boundary Note

Changing values must enter the manuscript through the generator. The tracked
source contains tokens; resolved output is disposable and must never be edited
by hand. The one tracked file the generator itself writes is
`manuscript/config.yaml`, for the reason recorded in the Reproducibility
section.
