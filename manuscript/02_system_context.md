# System Context {#sec:system_context}

## Project Boundary

GEO-INFER is a `{{MODULE_COUNT}}`-module geospatial inference framework for
spatial analysis, active inference, domain modeling, agent workflows, and
repository validation. The current checkout reports `{{MODULES_WITH_TESTS_COUNT}}`
modules with test files and `{{DOCUMENTATION_PAGE_COUNT}}` maintained
documentation pages. H3-backed spatial indexing is treated as a hierarchical
geospatial evidence surface rather than a claim of exact geometric containment
[@h3_docs].

## Source Surfaces

- `{{MODULE_NAMES}}`
- `GEO-INFER-TEST/`
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
