# Documentation Improvements Summary

The GEO-INFER documentation hub follows a Divio-style structure: tutorials
(learning-oriented), how-to guides (problem-oriented), technical reference
(information-oriented), and explanation (understanding-oriented).

This page summarizes the current documentation organization. For maintenance
workflow and history, see
[DOCUMENTATION_IMPROVEMENTS.md](DOCUMENTATION_IMPROVEMENTS.md); for
authoring conventions, see
[DOCUMENTATION_STANDARDS.md](DOCUMENTATION_STANDARDS.md).

## Documentation Structure

- **Getting Started hub** — [index](getting_started/index.md),
  [Installation](getting_started/installation_guide.md),
  [First Analysis](getting_started/first_analysis.md),
  [Active Inference Basics](getting_started/active_inference_basics.md).
- **User Guide** — [index](user_guide/index.md),
  [Cookbook](user_guide/cookbook.md),
  [Installation](user_guide/installation.md).
- **Developer Guide** — [index](developer_guide/index.md),
  [Testing](developer_guide/testing_guide.md),
  [Contributing](developer_guide/contributing.md).
- **Architecture** — [index](architecture/index.md),
  [Overview](architecture/overview.md),
  [Module Catalog](architecture/module_catalog.md).
- **Module Catalog** — [index](modules/index.md), one page per module.
- **Geospatial** — [index](geospatial/index.md), concepts, algorithms,
  analysis, data formats (including [H3](geospatial/data_formats/h3/index.md)),
  case studies, standards.
- **Ontology** — [index](ontology/index.md) and modeling guides.
- **Workflows** — [index](workflows/index.md),
  [Active Inference Workflows](workflows/active_inference_workflows.md).
- **Support** — [index](support/index.md), [FAQ](support/faq.md),
  [Troubleshooting](support/troubleshooting.md).
- **Tutorials** — [index](tutorials/index.md).

## Documentation Rules

- Commands use `uv run` from the repository root unless a page explicitly says
  otherwise.
- Examples must import real symbols from current package exports.
- H3 examples use the v4 API; v3 names are not supported.
- Test and model claims must be backed by a current command.
- Generated `README.md`/`AGENTS.md` files are refreshed by
  `GEO-INFER-TEST/rewrite_readme_agents.py`.

## Validation

From the repository root:

```bash
uv run python GEO-INFER-TEST/rewrite_readme_agents.py --check
uv run python GEO-INFER-TEST/validate_documentation.py --strict
uv run python GEO-INFER-TEST/validate_repo_contracts.py --strict-source-language
uv run python GEO-INFER-TEST/validate_skills.py --check-xrefs
```
