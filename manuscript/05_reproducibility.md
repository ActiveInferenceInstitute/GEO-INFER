# Reproducibility {#sec:reproducibility}

## Local Generation

Generate the inventory, figures, captions, variables, verification record,
and resolved manuscript copies directly from the checkout:

```bash
uv run python manuscript/generate_research_artifacts.py
uv run python manuscript/generate_research_artifacts.py --verify
uv run python manuscript/generate_research_artifacts.py --full-validation
uv run python manuscript/generate_research_artifacts.py \
    --full-validation --publication
uv run python manuscript/generate_research_artifacts.py --check
```

The first command performs the source inventory and artifact generation. The
second records strict repository and research-model checks. The third adds the
full unit, integration, performance, and H3 suites. The fourth is the
publication build: it refuses to run against a dirty working tree, refuses to
run without verification, and refuses to finish while the evidence record is
empty. The fifth writes nothing and exits non-zero when the published token
map no longer matches the measured checkout, so a render either regenerates or
refuses. The generated JSON record is the only source for the manuscript's
verification summary.

## Reproducibility Contract

- Do not cite results that cannot be regenerated or directly traced.
- Keep generated outputs under `output/` and authored manuscript source under
  `manuscript/`, with the single declared exception recorded below.
- Keep private data, credentials, and unpublished sensitive details out of the manuscript.
- Record exact verification commands, commit, source hash, and figure registry
  before marking this manuscript publication-ready.
- Treat `passed`, `failed`, and `not run` as distinct states; never convert an
  absent verification record into a passing claim.

## Generator-Owned Tracked Source

One tracked file under `manuscript/` is written by the generator rather than
by an author: `manuscript/config.yaml`. The renderer copies the tracked
`config.yaml` over the token-resolved copy in `output/manuscript/` before
rendering, so a variable token left in that file would reach the title page
verbatim instead of being substituted. Four fields are therefore resolved into
the tracked file by the generator and marked `# generator-owned` in place: the
project version, the title-page date, the publication year, and the licence.
Everything else in `config.yaml`, and every other file under `manuscript/`,
is authored.

The title-page date is derived from the last commit that touched anything
other than `config.yaml` itself. That choice makes the value a fixed point:
recording the refreshed file creates a newer commit, and a date derived from
`HEAD` could never settle. The `--check` mode compares the tracked
`config.yaml` against the published token map, so a title page that describes
a different build than the evidence bundle beside it fails rather than
shipping.

## Recorded Build

This source manuscript is resolved at commit `{{RESEARCH_COMMIT}}` on branch
`{{RESEARCH_BRANCH}}`, with commit date {{RESEARCH_COMMIT_DATE}}, source hash
`{{RESEARCH_SOURCE_HASH}}`, and Python `{{PYTHON_VERSION}}`. The count of
uncommitted working-tree entries when these values were measured was
`{{RESEARCH_TREE_DIRTY_FILE_COUNT}}`; anything other than zero means the
measurements describe files on disk rather than the named commit, and the
commit stamp above carries a `-dirty` or `-unverified` suffix to say so. The
recorded verification summary is `{{VERIFICATION_STATUS}}`.
