# Best Practices

This section contains curated best practices for working with geospatial data
and tools within the GEO-INFER framework. These practices follow the
repository's validation and hygiene contracts; see the
[repository overview](../../overview.md) and
[DOCUMENTATION_STANDARDS.md](../../DOCUMENTATION_STANDARDS.md).

## Data Management

- **Use standard directory structures** — organize geospatial data with
  consistent directory structures to improve discoverability and management.
- **Document metadata** — include metadata with geospatial datasets; see the
  [Geospatial Standards](../../geospatial/standards/index.md) page for ISO
  19115 and FGDC references.
- **Version control** — track changes to datasets and analysis code in git;
  keep generated artifacts out of the repository (see the root README
  "Artifact and Output Hygiene" section).

## Data Quality

- **Validate coordinate reference systems** — always validate and document the
  CRS of datasets; see
  [Coordinate Systems](../../geospatial/concepts/coordinate_systems.md).
- **Check for topological errors** — regularly check vector data for overlaps,
  gaps, and self-intersections.
- **Automate validation** — use the repository validators and test suites for
  incoming changes:
  `uv run python GEO-INFER-TEST/validate_documentation.py --strict` and the
  module test gates.

## Performance Optimization

- **Use spatial indexing** — implement spatial indexes (H3 v4) for large
  vector datasets to improve query performance; see the
  [H3 guide](../../geospatial/data_formats/h3/index.md).
- **Choose appropriate formats** — select raster/vector formats and compression
  based on access patterns.
- **Cache repeated work** — design caching strategies for frequently accessed
  data; see [Performance Optimization](../../advanced/performance_optimization.md).

## Workflow Design

- **Design for reproducibility** — create workflows that are fully documented
  and reproducible.
- **Parameterize workflows** — use clearly defined parameters that can be
  modified without changing the workflow structure.
- **Implement error handling** — handle common geospatial processing issues;
  see [Troubleshooting](../../support/index.md).

## Contributing Best Practices

We encourage contributions to the best practices knowledge base. To contribute:

1. Review existing practices to avoid duplication.
2. Write the practice following the
   [Documentation Guide](../../documentation_guide.md) conventions.
3. Include concrete examples grounded in real module exports.
4. Submit the contribution following the
   [contribution guidelines](../../../../CONTRIBUTING.md).

## Related Resources

- [Tutorials](../../tutorials/index.md)
- [Support and FAQ](../../support/index.md)
- [Troubleshooting Guides](../../support/troubleshooting.md)
