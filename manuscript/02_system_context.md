# System Context {#sec:system_context}

## Project Boundary

GEO-INFER is a `{{MODULE_COUNT}}`-module geospatial inference framework for
spatial analysis, active inference, domain modeling, agent workflows, and
repository validation. The current checkout reports
`{{MODULES_WITH_TESTS_COUNT}}` modules with test files and
`{{DOCUMENTATION_PAGE_COUNT}}` cross-module documentation pages under
`GEO-INFER-INTRA/docs/`. H3-backed spatial indexing is treated as a
hierarchical geospatial evidence surface rather than a claim of exact
geometric containment [@h3_docs].

## Module Inventory

A module is a top-level directory named `GEO-INFER-<NAME>` that ships one
installable package under `src/`, its own `tests/` tree, and its own
`README.md` and `AGENTS.md`. Nothing in the framework is a shared library that
other modules must be edited to extend: a module is added by adding a
directory, and it becomes part of the measured surface below without any
central registration step.

The generator groups the measured modules into `{{MODULE_THEME_COUNT}}`
themes. The grouping is an editorial one, declared in the generator beside the
research-focus list and mirroring the module-theme table in `README.md`; it is
not derived from imports or from a dependency graph. It is nonetheless
enforced: the build refuses to run if a measured module is unthemed, if a
theme names a module that is not in the checkout, or if a module is declared
twice, so a module cannot silently disappear from this table.

{{MODULE_TABLE}}

: Measured module inventory at commit `{{RESEARCH_COMMIT}}`, grouped by
declared theme. Source and test files are counted per module by the same
inventory pass that produces every other quantity in this manuscript; the
counts describe implementation and evidence surfaces, not correctness.
{#tbl:module_inventory}

The themes divide the framework by the kind of claim each module is
responsible for. *Spatial and place-based* modules own geometry, indexing,
time, and the environmental domains layered on them. *Bayesian and active
inference* modules own the probabilistic machinery: numerical and statistical
primitives in `GEO-INFER-MATH`, variational and expected free energy in
`GEO-INFER-ACT`, samplers and posterior diagnostics in `GEO-INFER-BAYES`,
statistical parametric mapping in `GEO-INFER-SPM`, cognitive modeling in
`GEO-INFER-COG`, and scenario simulation in `GEO-INFER-SIM`. *Agents and AI
orchestration* modules turn those methods into acting systems — autonomous and
swarm agents, machine-learning services, operations orchestration, and
messaging. *Governance, risk and domain* modules apply them to decisions with
consequences: hazard and risk modeling, insurance underwriting, economics,
norms and compliance, security, and health. *Data, API and applications*
modules own ingest, storage, service interfaces, and the human-facing
surfaces. *Infrastructure and validation* modules own the repository's own
evidence: the unified test framework in `GEO-INFER-TEST`, cross-module
documentation in `GEO-INFER-INTRA`, worked integration examples in
`GEO-INFER-EXAMPLES`, and repository tooling.

Theme membership is a statement about intent, not about size or maturity.
[@tbl:module_inventory] shows the spread directly: the largest module in the
checkout is `GEO-INFER-SPACE`, and several modules carry more test files than
source files.

## Spatial Substrate

The framework's spatial substrate is the part every other theme depends on,
and it is carried by three modules.

`GEO-INFER-SPACE` owns indexing and geometry. Its
`SpatialIndexingInterface` is a backend-dispatching facade rather than a
direct H3 binding, so H3 is one implementation of a spatial index and not a
hard dependency of the framework's spatial API. H3 resolution choice is itself
a guarded operation: `geo_infer_space.core.h3_policy` estimates cell counts
from the published average cell area at each resolution 0 through 15, selects
the finest resolution whose estimated grid stays within a soft target, and
raises `H3HardCapExceededError` rather than allocating a grid beyond a hard
cell cap. The policy module deliberately imports no H3 runtime, so the guard
remains importable in an environment where the H3 backend is absent. Above the
flat grid, `geo_infer_space.nested` maintains parent-child hexagon hierarchies
with boundary detection, message passing across boundaries, and lumping,
splitting, and aggregation operations — the structure that lets an inference
run at one resolution be related to a coarser or finer one.

`GEO-INFER-PLACE` binds analyses to named places. `PlaceInterface` is a single
entry point that orchestrates location-specific analyzers, data acquisition,
and temporal analysis for a configured region, so a place-scoped study is a
configuration of shared machinery rather than a fork of it.

`GEO-INFER-TIME` owns the temporal axis under the same discipline. Its
`inference_schedule` validates that a sequence of timestamps is timezone-aware,
ordered, and exactly aligned to the declared model step, and raises on a
missing interval instead of interpolating one: a gap in observations is
treated as something the model must be asked to predict, not something the
scheduler may fill. Offsets are normalized to UTC before instants are
compared.

## Source Surfaces

- `GEO-INFER-*/src/` and `GEO-INFER-*/tests/`
- `GEO-INFER-TEST/`
- `GEO-INFER-INTRA/docs/`
- `README.md`
- `AGENTS.md`
- `pyproject.toml`
- `uv.lock`

The source surface contains `{{SOURCE_FILE_COUNT}}` Python files and
`{{SOURCE_LINE_COUNT}}` non-empty source lines. The three research-focus
modules contain `{{ACT_SOURCE_FILE_COUNT}}`,
`{{BAYES_SOURCE_FILE_COUNT}}`, and
`{{RISK_SOURCE_FILE_COUNT}}` source files respectively, with corresponding
test surfaces of `{{ACT_TEST_FILE_COUNT}}`, `{{BAYES_TEST_FILE_COUNT}}`, and
`{{RISK_TEST_FILE_COUNT}}` files.

## Template Boundary

The manuscript is rendered locally from `output/manuscript/` after the project
pipeline resolves its variables. The tracked `manuscript/` directory remains
the authored source; `output/` contains disposable figures, JSON evidence, and
resolved copies generated from this checkout.
