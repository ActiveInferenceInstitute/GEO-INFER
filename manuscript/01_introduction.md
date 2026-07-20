# Introduction {#sec:introduction}

## Motivation

A large modular geospatial monorepo needs a paper-shaped account of its module
contract, active-inference spine, validation gates, and evidence boundaries.
GEO-INFER addresses this need by keeping spatial and probabilistic methods in
owned modules while treating tests, manifests, generated figures, and
documentation as linked research evidence rather than presentation-only
artifacts.

## Contributions

This manuscript makes four concrete contributions:

1. A measured inventory of `{{MODULE_COUNT}}` modules, `{{SOURCE_FILE_COUNT}}`
   source files, and `{{TEST_FILE_COUNT}}` test files at source fingerprint
   `{{RESEARCH_SOURCE_HASH}}`.
2. A composable research spine connecting Active Inference, Bayesian inference,
   and risk analysis through independently testable module boundaries.
3. A reproducible artifact pipeline that generates `{{FIGURE_COUNT}}`
   publication figures, registers captions and provenance, and injects all
   volatile values into resolved manuscript copies.
4. A fail-closed evidence record that distinguishes available source surfaces
   from commands that were actually executed and passed.

## Reader Orientation

The manuscript should be read with the repository commit and source hash in
view. The module inventory and validation surface describe what is present in
the checkout; they do not substitute for domain-specific empirical validation.
The implementation and verification surfaces for the Active Inference,
Bayesian, and RISK modules are summarized in [@fig:research_spine].
