# Knowledge Base

The GEO-INFER knowledge base is the structured documentation hub in this
repository: conceptual explanations, how-to guides, troubleshooting, FAQ, best
practices, and reference material organized by topic. It serves users,
developers, and automated agents.

## What Lives Here

- [Best Practices](best_practices/index.md) — recommended approaches for data,
  performance, workflows, and collaboration.
- [User Guide](../user_guide/index.md) — everyday usage.
- [Support and Troubleshooting](../support/index.md) — FAQ, installation
  issues, and error triage.
- [Tutorials](../tutorials/index.md) — step-by-step guides.
- [Terminology](../terminology.md) — shared vocabulary.
- [Data Dictionary](../data_dictionary.md) — data field definitions.

## Article Structure

Knowledge articles follow the repository documentation conventions
(see the [Documentation Guide](../documentation_guide.md) and
[DOCUMENTATION_STANDARDS.md](../DOCUMENTATION_STANDARDS.md)):

- **Summary** — brief overview (1-2 sentences).
- **Body** — content structured by article type.
- **Related articles** — links to connected information.
- **Examples** — practical usage examples grounded in real module exports.
- **References** — citations and external resources.

## Article Types

| Type | Purpose | Example |
|------|---------|---------|
| Concept | Explain theoretical ideas | "What is Spatial Autocorrelation?" |
| How-To | Step-by-step instructions | "How to Create a Map" |
| Troubleshooting | Solve specific problems | "Fixing CRS Mismatches" |
| Reference | Technical specifications | "H3 v4 API Reference" |
| Best Practice | Recommended approaches | "Best Practices for Spatial Indexing" |
| FAQ | Common questions and answers | "FAQ: Coordinate Systems" |
| Case Study | Real-world examples | "Urban Heat Island Analysis Case Study" |

## Contribution Process

1. **Identify a gap** — check the [module catalog](../modules/index.md) and
   existing pages first.
2. **Draft** — follow the [Documentation Guide](../documentation_guide.md)
   conventions; ground every claim in tracked files or passing validators.
3. **Review** — open a pull request; see
   [CONTRIBUTING.md](../../../CONTRIBUTING.md).
4. **Validate** — run the documentation gates listed in the
   [main documentation index](../index.md#documentation-validation).

## Integration with Other Components

- **Documentation System** — the docs hub itself; see
  [index.md](../index.md).
- **Ontology** — standardized terminology and relationships; see
  [Ontology](../ontology/index.md).
- **Workflows** — patterns and orchestration; see
  [Workflows](../workflows/index.md).

## Best Practices for Knowledge Management

- **Maintain clarity** — use plain language and clear explanations.
- **Ensure accuracy** — verify information against code and validators before
  publishing.
- **Keep content current** — regenerate signposts with
  `rewrite_readme_agents.py` and re-run `validate_documentation.py --strict`.
- **Focus on user needs** — structure information to answer common questions.
- **Provide examples** — include practical examples and use cases.
- **Link related content** — create connections between related articles.

## Related Resources

- [User Guide](../user_guide/index.md)
- [Ontology Management](../ontology/index.md)
- [Geospatial hub](../geospatial/index.md)
- [Contributing Guide](../../../CONTRIBUTING.md)
- [API Documentation](../api/index.md)
