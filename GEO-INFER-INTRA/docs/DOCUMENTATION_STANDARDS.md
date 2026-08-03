# GEO-INFER Documentation Standards

This document establishes standards for creating, maintaining, and
contributing to GEO-INFER documentation. These standards ensure consistency,
quality, and usability across all documentation artifacts and follow the
repository contracts enforced by `GEO-INFER-TEST/validate_documentation.py`.

## Documentation Layers

1. **Repository guidance** — root `README.md`, `AGENTS.md`, `CONTRIBUTING.md`,
   `SECURITY.md`, `CHANGELOG.md`, `TODO.md`, and `SKILL.md`.
2. **Conceptual and workflow guidance** — the `GEO-INFER-INTRA/docs/` hub,
   organized by audience and topic.
3. **Executable module guidance** — each module's `README.md`, `AGENTS.md`,
   `SKILL.md`, `examples/`, `tests/`, and public source exports.

If a page conflicts with importable code or a passing contract validator, the
source and validator are authoritative; open a documentation issue.

## Current-State Policy

- Documentation must describe current, discoverable repository state.
- Do not advertise planned or aspirational APIs unless the implementation,
  export path, and validation command exist in this checkout.
- Generated `README.md` and `AGENTS.md` files are refreshed by
  `GEO-INFER-TEST/rewrite_readme_agents.py`; edit the generator when the
  generated documentation contract changes, never the signposts by hand.
- Historical assessment artifacts are not contractual; test and model claims
  must be backed by a current command.

## Authoring Conventions

### Markdown

- Use ATX headings (`#` to `######`) with a single `#` title per page.
- Use fenced code blocks with a language tag (```
` ```python `
```
).
- Use descriptive link text; prefer relative links between hub pages.
- Tables use GFM pipe syntax with a header separator row.
- Keep lines under ~100 characters where practical.

### Commands

- Commands use `uv run` from the repository root unless a page explicitly says
  otherwise.
- Example commands must be runnable and must reference real scripts or module
  entry points.

### Code Examples

- Examples must import real symbols from the current package exports.
- State coordinate systems, units, and expected artifact locations.
- H3 examples use the v4 API (`latlng_to_cell`, `cell_to_latlng`,
  `grid_disk`, and related names); v3 names are not supported.

### Links

- Verify relative links resolve from the page's own directory; anchors must
  match real GFM heading slugs in the target page.
- External links must point at real resources; do not invent domains.

## Module Documentation Template

A module documentation template is available at
[module_readme_template.md](module_readme_template.md). The template covers:
overview, key concepts, core features, API reference, use cases, integration,
troubleshooting, performance, and related documentation.

## Content Guidelines

### Language and Style

- **Clarity**: use simple, direct language.
- **Precision**: be technically accurate and specific.
- **Consistency**: use established terminology (see
  [Terminology](terminology.md)).
- **Objectivity**: avoid marketing language and hype.

### Accuracy Checklist

- [ ] Technical information verified against code.
- [ ] Code examples import real symbols and run.
- [ ] API signatures match implementation.
- [ ] Version information current.
- [ ] Links functional and accurate.

## Documentation Validation

From the repository root:

```
```bash
uv run python GEO-INFER-TEST/rewrite_readme_agents.py --check
uv run python GEO-INFER-TEST/validate_documentation.py --strict
uv run python GEO-INFER-TEST/validate_repo_contracts.py --strict-source-language
uv run python GEO-INFER-TEST/validate_skills.py --check-xrefs
git diff --check
```

For a focused change, run the affected module gate after the documentation
checks. Keep generated output under `.geo-infer-test-results/` or an explicit
temporary directory; do not commit repository-root runtime artifacts.
