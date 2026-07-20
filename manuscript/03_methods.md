# Methods {#sec:methods}

## Research Construction Method

The manuscript pipeline performs a deterministic source-first pass. It
discovers every `GEO-INFER-*` directory containing `src/`, measures Python
source and test surfaces, reads the project version from `pyproject.toml`, and
records the current Git commit, branch, commit date, and source fingerprint.
The inventory is written to `output/data/research_inventory.json` before any
prose is resolved.

The research focus is the composable path from Active Inference through
Bayesian inference to risk analysis [@friston_free_energy_2010;
@parr_active_inference_2022; @heins_pymdp_2022]. The pipeline does not synthesize results
or infer performance from file counts; it reports implementation and evidence
surfaces separately, then delegates behavioral claims to the repository's
validators and test suites.

## Figure and Caption Method

The figure producer builds `{{FIGURE_COUNT}}` figures from the same measured
inventory used for the manuscript variables. Figure files, captions, labels,
generator paths, commit, and source hash are written to
`output/figures/figure_registry.json`. Each caption is a complete sentence
that names the population, encoding, provenance, and interpretation boundary.

![{{MODULE_INVENTORY_CAPTION}}](../output/figures/module_inventory.png){#fig:module_inventory width=95%}

![{{RESEARCH_SPINE_CAPTION}}](../output/figures/research_spine.png){#fig:research_spine width=85%}

![{{VALIDATION_SURFACE_CAPTION}}](../output/figures/validation_surface.png){#fig:validation_surface width=90%}

## Evidence Promotion and Verification

Research claims are promoted in this order:

1. Discover the source surface and write a provenance-bearing inventory.
2. Generate figures and captions from measured data, failing if a declared
   figure is absent or unregistered.
3. Run the strict repository, documentation, skills, model, reproducibility,
   and source checks; optionally run the full unit, integration, performance,
   and H3 suites.
4. Inject every volatile value into `output/manuscript/` and reject unresolved
   uppercase tokens.
5. Review the resolved manuscript and registry together before publication.

## Template Compliance

Each publication section has one H1 label, every figure uses labeled Pandoc
image syntax, captions are sourced from the figure registry, and generated
copies contain no unresolved variable tokens.
