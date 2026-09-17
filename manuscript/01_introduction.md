# Introduction {#sec:introduction}

## Motivation

A large modular geospatial monorepo needs a paper-shaped account of its module
contract, active-inference spine, validation gates, and evidence boundaries.
GEO-INFER addresses this need by keeping spatial and probabilistic methods in
owned modules while treating tests, manifests, generated figures, and
documentation as linked research evidence rather than presentation-only
artifacts.

The framework-level claim behind that discipline is architectural: geospatial
inference composes, and the composition has to be inspectable. A spatial
index, a variational free-energy calculation, and a hazard return level are
useful separately, but the framework's reason to exist is that a value can
cross from one to the next — a place-scoped observation entering an active
inference step, a posterior entering a risk model — without either side
being rewritten. What makes such crossings inspectable is not the algorithms
but the boundaries: typed results, declared shapes, seeded generators, and
refusals that raise instead of substituting a plausible number. This
manuscript is the account of those boundaries, published from the same
checkout that implements them.

## Architecture at a Glance

The module set composes in layers that the theme map in
[@sec:system_context] makes explicit. The *spatial substrate* — indexing,
nested hierarchies, named places, and the temporal axis — owns geometry and
is depended on by everything above it. The *probabilistic machinery* —
Bayesian inference, active inference, statistical parametric mapping,
cognitive modeling, and simulation — owns the inference quantities that
consume spatial evidence. The *domain engines* — agents and orchestration,
governance and risk, and the applied sciences — turn those quantities into
decisions and domain claims. *Data, API and application* modules carry the
ingest, storage, service, and human-facing surfaces, and *infrastructure and
validation* modules own the repository's evidence loop: the unified test
framework, cross-module documentation, and repository tooling.

Three design rules hold the layers together. First, modules are added by
adding a directory: there is no central registration step and no shared
library that other modules must be edited to extend. Second, the research
spine — Active Inference through Bayesian inference to risk — is one
composable path through the module set, stated as a contract in
[@sec:methods] rather than implied by adjacency. Third, every claim the
framework makes about itself is bound to a measured surface: the per-module
catalog in [@sec:module_catalog] enumerates what each module exposes and
verifies, and the evidence sections report what was actually run.

## Contributions

This manuscript makes five concrete contributions:

1. A measured inventory of `{{MODULE_COUNT}}` modules, `{{SOURCE_FILE_COUNT}}`
   source files, and `{{TEST_FILE_COUNT}}` test files at source fingerprint
   `{{RESEARCH_SOURCE_HASH}}`, published per module and per theme rather than
   as a single total.
2. A composable research spine connecting Active Inference, Bayesian
   inference, and risk analysis through independently testable module
   boundaries, with the interface obligations at those boundaries stated
   explicitly rather than asserted.
3. A reproducible artifact pipeline that generates `{{FIGURE_COUNT}}`
   publication figures, registers captions, generator paths, and a per-figure
   content digest, and injects all volatile values into resolved manuscript
   copies.
4. A fail-closed evidence record that distinguishes available source surfaces
   from commands that were actually executed and passed, and a publication
   mode that fails rather than certify a build whose record is empty or
   contains a failed group.
5. A per-module catalog that enumerates every module's purpose, public
   interface, and test surface in one place, indexed by the generated module
   table and organized by the declared themes, so the module contract can be
   read module by module rather than inferred from the tree.

## Reader Orientation

The manuscript should be read with the repository commit and source hash in
view. The module inventory and validation surface describe what is present in
the checkout; they do not substitute for domain-specific empirical validation.
The measured surface of every module appears in [@tbl:module_inventory], the
interface obligations that make those modules composable appear in the
Composition Contract, the implementation and verification surfaces for the
Active Inference, Bayesian, and RISK modules are summarized in
[@fig:research_spine], and the Supplemental Module Catalog expands the same
inventory into one prose entry per module.
