# GEO-INFER-BIO Documentation

Welcome to the documentation for GEO-INFER-BIO, a specialized module within the GEO-INFER framework for bioinformatics analysis with spatial context.

## Overview

GEO-INFER-BIO provides comprehensive tools for analyzing biological sequences and their spatial distribution. It integrates sequence analysis, spatial mapping, and visualization capabilities to enable researchers to understand biological patterns across different scales and locations.

## Features

### Sequence Analysis
- DNA/RNA sequence analysis
- GC content calculation
- Motif finding
- Coding region prediction
- Sequence alignment

### Spatial Analysis
- Spatial distribution mapping
- Geographic pattern analysis
- Environmental correlation studies
- Population structure analysis

### Visualization
- Interactive spatial plots
- Sequence feature visualization
- Statistical distribution plots
- Geographic heatmaps

## Installation

```bash
pip install geo-infer-bio
```

## Quick Start

```python
from geo_infer_bio import SequenceAnalyzer, BioVisualizer

# Initialize analyzer
analyzer = SequenceAnalyzer()

# Load sequence data
sequences = analyzer.load_sequence("path/to/sequences.fasta")

# Perform analysis
results = analyzer.analyze_spatial_distribution(sequences, spatial_data)

# Visualize results
visualizer = BioVisualizer()
visualizer.plot_spatial_distribution(results)
```

## API Reference

### REST API
The REST API provides endpoints for:
- Sequence analysis
- File processing
- Spatial visualization
- Health monitoring

### GraphQL API
The GraphQL API offers flexible queries for:
- Complex sequence analysis
- Custom visualization generation
- Data filtering and aggregation
- Real-time updates

## Examples

### Basic Sequence Analysis
```python
from geo_infer_bio import SequenceAnalyzer

analyzer = SequenceAnalyzer()
sequence = "ATGCGTACGTAGCTAGCTAG"
gc_content = analyzer.calculate_gc_content(sequence)
motifs = analyzer.find_motifs(sequence)
```

### Spatial Analysis
```python
from geo_infer_bio import SequenceAnalyzer, BioVisualizer

analyzer = SequenceAnalyzer()
visualizer = BioVisualizer()

# Load data
sequences = analyzer.load_sequence("sequences.fasta")
spatial_data = pd.read_csv("locations.csv")

# Analyze
results = analyzer.analyze_spatial_distribution(sequences, spatial_data)

# Visualize
visualizer.plot_gc_distribution(results)
```

### API Usage
```python
import requests

# REST API
response = requests.post(
    "http://localhost:8000/analyze/sequence",
    json={
        "id": "seq1",
        "sequence": "ATGCGTACGTAGCTAGCTAG",
        "spatial_data": {
            "latitude": 40.7128,
            "longitude": -74.0060
        }
    }
)

# GraphQL API
query = """
query {
    analyzeSequence(sequenceData: {
        id: "seq1",
        sequence: "ATGCGTACGTAGCTAGCTAG",
        spatialData: {
            latitude: 40.7128,
            longitude: -74.0060
        }
    }) {
        sequenceId
        gcContent
        motifCount
        codingRegions
    }
}
"""
```

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

## License

This module is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citation

If you use GEO-INFER-BIO in your research, please cite:

```bibtex
@software{geo_infer_bio2024,
  title = {GEO-INFER-BIO: A Bioinformatics Module for the GEO-INFER Framework},
  author = {GEO-INFER Team},
  year = {2024},
  publisher = {GitHub},
  url = {https://github.com/yourusername/GEO-INFER/tree/main/GEO-INFER-BIO}
}
``` 