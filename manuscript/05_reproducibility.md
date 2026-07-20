# Reproducibility {#sec:reproducibility}

## Local Generation

Generate the inventory, figures, captions, variables, verification record,
and resolved manuscript copies directly from the checkout:

```bash
uv run python manuscript/generate_research_artifacts.py
uv run python manuscript/generate_research_artifacts.py --verify
uv run python manuscript/generate_research_artifacts.py --full-validation
```

The first command performs the source inventory and artifact generation. The
second records strict repository and research-model checks. The third adds the
full unit, integration, performance, and H3 suites. The generated JSON record
is the only source for the manuscript's verification summary.

## Reproducibility Contract

- Do not cite results that cannot be regenerated or directly traced.
- Keep generated outputs under `output/` and authored manuscript source under
  `manuscript/`.
- Keep private data, credentials, and unpublished sensitive details out of the manuscript.
- Record exact verification commands, commit, source hash, and figure registry
  before marking this manuscript publication-ready.
- Treat `passed`, `failed`, and `not run` as distinct states; never convert an
  absent verification record into a passing claim.

## Recorded Build

This source manuscript is resolved at commit `{{RESEARCH_COMMIT}}` on branch
`{{RESEARCH_BRANCH}}`, with commit date `{{RESEARCH_COMMIT_DATE}}`, source hash
`{{RESEARCH_SOURCE_HASH}}`, and Python `{{PYTHON_VERSION}}`. The recorded
verification summary is `{{VERIFICATION_STATUS}}`.
