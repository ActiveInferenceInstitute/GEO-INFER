# User Guide

This guide provides comprehensive information for users of GEO-INFER-INTRA, covering installation, configuration, and everyday usage.

## Contents

- [Installation](installation.md)
- [Configuration](configuration.md)
- [Getting Started](getting_started.md)
- [Documentation Server](documentation_server.md)
- [Knowledge Base Usage](knowledge_base_usage.md)
- [Workflow Management](workflow_usage.md)
- [Ontology Access](ontology_access.md)
- [Troubleshooting](troubleshooting.md)

## Quick Start

For those who want to get up and running quickly:

1. Installation
   ```bash
   pip install -e .
   ```

2. Configuration
   ```bash
   cp config/example.yaml config/local.yaml
   # Edit local.yaml with your configuration
   ```

3. Running the Documentation Server
   ```bash
   python -m geo_infer_intra.docs serve
   ```

See the [Getting Started](getting_started.md) guide for more detailed instructions. 