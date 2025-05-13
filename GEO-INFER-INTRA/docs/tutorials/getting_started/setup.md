# Setting Up GEO-INFER-INTRA

This tutorial will guide you through the process of setting up GEO-INFER-INTRA for first-time use.

## Prerequisites

Before starting, ensure you have the following prerequisites installed:

- Python 3.9 or higher
- pip (Python package manager)
- Git (for source installation)
- A text editor of your choice

## Step 1: Install GEO-INFER-INTRA

You can install GEO-INFER-INTRA using pip:

```bash
# Create and activate a virtual environment (recommended)
python -m venv geo-infer-env
source geo-infer-env/bin/activate  # On Windows: geo-infer-env\Scripts\activate

# Install from PyPI
pip install geo-infer-intra
```

Alternatively, you can install from source:

```bash
# Clone the repository
git clone https://github.com/geo-infer/geo-infer-intra.git
cd geo-infer-intra

# Install in development mode
pip install -e .
```

## Step 2: Create a Configuration File

Create a configuration file by copying the example configuration:

```bash
# Create the configuration directory if it doesn't exist
mkdir -p ~/.geo-infer/

# Copy the example configuration
cp $(pip show geo-infer-intra | grep Location | cut -d ' ' -f 2)/geo_infer_intra/config/example.yaml ~/.geo-infer/config.yaml
```

Or if you installed from source:

```bash
cp config/example.yaml ~/.geo-infer/config.yaml
```

## Step 3: Edit the Configuration File

Open the configuration file in your text editor:

```bash
nano ~/.geo-infer/config.yaml
```

Update the configuration with your settings:

```yaml
# GEO-INFER-INTRA Configuration

# General settings
general:
  debug_mode: false
  log_level: INFO
  log_file: ~/.geo-infer/logs/intra.log

# Documentation settings
documentation:
  server:
    host: 127.0.0.1
    port: 8000
  content_dir: ~/.geo-infer/docs
  theme: material

# Ontology settings
ontology:
  base_dir: ~/.geo-infer/ontologies
  default_format: turtle

# Knowledge base settings
knowledge_base:
  storage_type: elasticsearch
  elasticsearch:
    host: localhost
    port: 9200
    index_prefix: geo-infer-kb

# Workflow settings
workflow:
  storage_dir: ~/.geo-infer/workflows
  execution:
    parallel: true
    max_workers: 4
```

Save the file and exit the editor.

## Step 4: Initialize the System

Initialize GEO-INFER-INTRA to set up the required directories and download initial content:

```bash
geo-infer-intra init
```

This command will:
- Create necessary directories
- Download and install default ontologies
- Set up the knowledge base
- Initialize the documentation system
- Download example workflows

## Step 5: Start the Documentation Server

Start the documentation server to access the web interface:

```bash
geo-infer-intra docs serve
```

This will start the documentation server on http://127.0.0.1:8000 (or the host/port specified in your configuration).

## Step 6: Verify the Installation

Open a new terminal window and run:

```bash
# Activate the virtual environment if you created one
source geo-infer-env/bin/activate  # On Windows: geo-infer-env\Scripts\activate

# Check the version
geo-infer-intra --version

# Run a system check
geo-infer-intra check
```

The system check should report that all components are functioning correctly.

## Next Steps

Now that you have GEO-INFER-INTRA set up, you can:

- Explore the [Documentation System](documentation.md)
- Learn about the [Knowledge Base](knowledge_base.md)
- Navigate the [Ontologies](ontologies.md)
- Create your [First Workflow](first_workflow.md)

## Troubleshooting

If you encounter issues during setup:

- Check that all prerequisites are installed
- Verify that the configuration file is correctly formatted
- Ensure that all specified directories exist and are writable
- Check the log file for error messages
- Consult the [Troubleshooting Guide](../troubleshooting.md)

If problems persist, please [open an issue](https://github.com/geo-infer/geo-infer-intra/issues) on the GitHub repository. 