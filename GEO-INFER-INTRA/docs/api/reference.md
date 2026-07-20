# API Reference Policy

This repository contains several package APIs rather than one universal service
reference. The source-backed reference for a public symbol is its package
export, docstring, module README, and tests.

## Reference workflow

1. Find the owning module in the [module catalog](../modules/index.md).
2. Read the module root README and SKILL.
3. Inspect src/<package>/__init__.py and __all__.
4. Check the module's pyproject.toml for optional dependencies.
5. Run the module gate before relying on the behavior.

## Common public surfaces

- Active Inference: [ACT guide](../modules/geo-infer-act.md)
- Spatial/H3: [SPACE guide](../modules/geo-infer-space.md)
- Testing: [GEO-INFER-TEST API](../../../GEO-INFER-TEST/docs/api_reference.md)
- GeoJSON/FastAPI: [GEO-INFER-API docs](../../../GEO-INFER-API/docs/README.md)
- Cross-module patterns: [integration guide](../integration/index.md)

## Accuracy rule

Do not copy endpoint URLs, client classes, database schemas, deployment
architectures, or version numbers from historical assessment documents into a
current API page. If a public interface changes, update its owning module,
tests, README/SKILL, and this navigation page together.
