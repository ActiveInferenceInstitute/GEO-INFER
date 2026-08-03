# Documentation Hub Maintenance

This page records how the GEO-INFER documentation hub is maintained and
improved. It is the operational companion to the
[Documentation Guide](documentation_guide.md) and
[Documentation Standards](DOCUMENTATION_STANDARDS.md).

## Current State

- The documentation hub (`GEO-INFER-INTRA/docs/`) is organized by audience and
  topic: getting started, user guide, developer guide, architecture, module
  catalog, geospatial, ontology, workflows, support, and tutorials.
- The repository root and module-level `README.md`/`AGENTS.md` files are
  generated signposts maintained by
  `GEO-INFER-TEST/rewrite_readme_agents.py`; never edit them by hand.
- The canonical navigation entry point is
  [GEO-INFER-INTRA/docs/index.md](index.md).

## Improvement Workflow

1. **Scope** — identify the gap against the
   [module catalog](modules/index.md) and existing hub pages.
2. **Draft** — follow the conventions in
   [Documentation Standards](DOCUMENTATION_STANDARDS.md); ground every claim
   in tracked files or passing validators. Do not advertise planned APIs.
3. **Validate** — run the documentation gates from the repository root:

```bash
uv run python GEO-INFER-TEST/rewrite_readme_agents.py --check
uv run python GEO-INFER-TEST/validate_documentation.py --strict
uv run python GEO-INFER-TEST/validate_skills.py --check-xrefs
git diff --check
```

4. **Submit** — open a pull request; see
   [CONTRIBUTING.md](../../CONTRIBUTING.md).

## Historical Notes

- A 2026-08-02 documentation deep-review pass restored 148 newline-collapsed
  markdown files, repaired broken links and fabricated URLs, and rewrote
  hub pages to match repository reality. See the root
  [REVIEW_LOG_2026-08-02.md](../../REVIEW_LOG_2026-08-02.md) and
  [TODO.md](../../TODO.md) for the scoped findings.
