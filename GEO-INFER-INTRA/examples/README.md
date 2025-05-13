# GEO-INFER-INTRA Examples

This directory contains example code and usage scenarios for the GEO-INFER-INTRA module.

## Directory Structure

```
examples/
├── api/               # API usage examples
├── knowledge_base/    # Knowledge base examples
├── ontology/          # Ontology management examples
├── tutorials/         # Tutorial code examples
└── workflows/         # Workflow examples
```

## API Examples

The `api/` directory contains examples demonstrating how to use the GEO-INFER-INTRA API:

- `api_client.py` - Basic API client usage
- `authentication.py` - Authentication examples
- `documentation_api.py` - Documentation API examples
- `knowledge_base_api.py` - Knowledge Base API examples
- `ontology_api.py` - Ontology API examples
- `workflow_api.py` - Workflow API examples

## Knowledge Base Examples

The `knowledge_base/` directory contains examples for working with the knowledge base:

- `search_kb.py` - Searching the knowledge base
- `create_article.py` - Creating knowledge base articles
- `export_article.py` - Exporting articles in different formats
- `custom_kb_extension.py` - Creating custom knowledge base extensions

## Ontology Examples

The `ontology/` directory contains examples for working with ontologies:

- `load_ontology.py` - Loading and exploring ontologies
- `create_extension.py` - Creating ontology extensions
- `query_ontology.py` - Querying ontology concepts
- `mapping_domains.py` - Mapping between domain ontologies
- `visualization.py` - Visualizing ontology relationships

## Tutorial Examples

The `tutorials/` directory contains complete code examples for the tutorials:

- `getting_started/` - Code for getting started tutorials
- `workflow_examples/` - Code for workflow tutorials
- `ontology_examples/` - Code for ontology tutorials
- `kb_examples/` - Code for knowledge base tutorials

## Workflow Examples

The `workflows/` directory contains example workflows:

- `land_cover_classification.json` - Land cover classification workflow
- `change_detection.json` - Change detection workflow
- `data_preprocessing.json` - Data preprocessing workflow
- `spatial_analysis.json` - Spatial analysis workflow
- `visualization_workflow.json` - Data visualization workflow

## Running the Examples

Most examples can be run directly using Python:

```bash
python examples/api/api_client.py
```

Workflow examples can be loaded and executed using the workflow API or CLI:

```bash
# Using the CLI
geo-infer-intra workflow load examples/workflows/land_cover_classification.json
geo-infer-intra workflow execute land_cover_classification

# Using Python
python -c "from geo_infer_intra.client import WorkflowClient; client = WorkflowClient(); client.load_workflow('examples/workflows/land_cover_classification.json'); client.execute_workflow('land_cover_classification')"
```

## Documentation

For more detailed documentation, see the [GEO-INFER-INTRA Documentation](../docs/index.md). 