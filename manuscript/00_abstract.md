# Abstract {#sec:abstract}

GEO-INFER is a modular geospatial inference framework spanning spatial
analysis, active inference, Bayesian methods, domain modeling, agent
workflows, and repository validation. This manuscript is generated from the
tracked checkout at commit `{{RESEARCH_COMMIT}}`: the repository contains
`{{MODULE_COUNT}}` modules that ship a `src/` package, grouped into
`{{MODULE_THEME_COUNT}}` themes, with `{{SOURCE_FILE_COUNT}}` Python source
files and `{{TEST_FILE_COUNT}}` Python test files across its measured
evidence surfaces.

The research contribution is an auditable composition contract. Domain
modules own their implementations, cross-module workflows expose shared
spatial and probabilistic interfaces, and validation commands make
correctness, reproducibility, and documentation claims executable. The
Methods section states that contract term by term for the Active Inference,
Bayesian, and risk spine: the free-energy decomposition an inference call
returns, the sampler and diagnostic obligations a posterior estimate carries,
and the bounds a risk result must satisfy before it is reported. Figures,
captions, and quantitative statements in this manuscript are produced from
the same repository inventory and source fingerprint used to render it.

The current verification record is `{{VERIFICATION_STATUS}}` across
`{{VERIFICATION_PASS_COUNT}}` passing and `{{VERIFICATION_FAIL_COUNT}}`
failing commands: of the `{{VERIFICATION_DEFINED_COUNT}}` command groups this
build defines, `{{VERIFICATION_UNRUN_COUNT}}` did not run. A fresh
publication build must regenerate this section and refuse to represent unrun
or failed checks as evidence of success.
