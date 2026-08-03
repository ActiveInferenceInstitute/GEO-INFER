# Knowledge Base Usage

This guide explains how to use the GEO-INFER-INTRA Knowledge Base: the
structured collection of best practices, guides, and reference articles that
live in the INTRA documentation hub.

## What the Knowledge Base Is

The Knowledge Base is a set of Markdown articles maintained under
[`docs/knowledge_base/`](../knowledge_base/index.md) in the INTRA module:

- `docs/knowledge_base/index.md` — hub and overview of the collection.
- `docs/knowledge_base/best_practices/` — expert recommendations for
  working with geospatial data, workflows, and documentation (data
  management, performance optimization, workflow design, data quality
  assurance, and related topics).

Because the articles are plain Markdown files in the repository, they are
versioned with the code, reviewed through normal pull requests, and render on
GitHub and in any Markdown tool.

## Browsing the Knowledge Base

Start at the [Knowledge Base index](../knowledge_base/index.md) and follow the
links by category. In a local checkout you can also browse the directory
directly:

```bash
# List all knowledge base articles
ls GEO-INFER-INTRA/docs/knowledge_base
```

## Searching the Knowledge Base

Use your editor or a text search to find articles:

```bash
# Search article titles and content
grep -rni "performance optimization" GEO-INFER-INTRA/docs/knowledge_base
```

GitHub's repository search (search box with `repo:ActiveInferenceInstitute/
GEO-INFER` and a keyword) searches the same files, including article tags and
titles.

## Understanding Knowledge Categories

The Knowledge Base organizes articles by category directories:

### Best Practices

Best practices are expert recommendations for working with geospatial data
and tools. They cover topics such as:

- Data management
- Performance optimization
- Workflow design
- Data quality assurance

Browse them under
[`docs/knowledge_base/best_practices/`](../knowledge_base/best_practices/index.md).

### Frequently Asked Questions (FAQs)

FAQs and other reference material answer common questions about the GEO-INFER
framework and geospatial processing: installation and configuration, common
usage scenarios, feature explanations, and integration with other tools.
Articles appear throughout the hub; the
[FAQ page](../support/faq.md) collects the most common questions.

## Contributing to the Knowledge Base

Contributions are made by editing the Markdown articles:

1. Find the article you want to change (or create a new one under the
   appropriate category directory).
2. Edit it as Markdown, following the
   [documentation guide](../documentation_guide.md) for structure, tone, and
   link conventions.
3. Submit the change as a pull request following the repository's
   [contributing guide](../../../CONTRIBUTING.md).

The repository validators check documentation structure and links on every
pull request, so keep new articles linked from the
[Knowledge Base index](../knowledge_base/index.md) and from related pages.

## Knowledge Base Integration

Knowledge articles are linked from relevant documentation throughout the hub:
- **Documentation**: articles appear under the Knowledge Base section of the
  [docs index](../index.md).
- **Workflows**: workflow and best-practice articles are referenced from
  workflow pages and the developer guide.
- **Support**: troubleshooting content links to the
  [Troubleshooting Guide](../support/troubleshooting.md).

## Troubleshooting

If an article link is broken or content looks stale:

1. Check the file exists under the
   [Knowledge Base index](../knowledge_base/index.md).
2. Run the documentation validator to find broken links:

```bash
uv run python GEO-INFER-TEST/validate_documentation.py --strict
```

3. For content errors, open an issue or fix the article in a pull request.
