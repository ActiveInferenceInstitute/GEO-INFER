# GEO-INFER-ART 🎨🗺️

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: CC BY-ND-SA 4.0](https://img.shields.io/badge/License-CC%20BY--ND--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nd-sa/4.0/)

## Overview

GEO-INFER-ART is a specialized module within the GEO-INFER framework focused on the intersection of art, aesthetics, and geospatial data. This module enables the transformation of geospatial information into artistic expressions, aesthetic visualizations, and generative art systems.

## Key Features

### 🌈 Geospatial Data Visualization as Art

- **Aesthetic Mapping**: Transform geospatial data into visually compelling and aesthetically pleasing representations
- **Stylistic Transformations**: Apply artistic styles to maps and geospatial visualizations
- **Color Theory Integration**: Implement sophisticated color palettes based on color theory for effective and beautiful maps

### 🏙️ Place-Based Artistic Expression

- **Location-Inspired Art**: Generate art based on the unique characteristics of geographic locations
- **Cultural Context Mapping**: Integrate cultural and historical contexts into artistic representations of place
- **Site-Specific Installations**: Tools for planning and visualizing site-specific art installations with geospatial integration

### 🖼️ Aesthetic Frameworks for Map Design

- **Cartographic Design Principles**: Implement best practices in map design with an aesthetic focus
- **Theme Generators**: Create cohesive visual themes for maps and geographic visualizations
- **Typography for Maps**: Specialized typography tools for geospatial labeling with artistic consideration

### 🧩 Generative Art Systems

- **Geo-Procedural Generation**: Create procedurally generated art using geographic features as seeds
- **Topographic Abstractions**: Generate abstract art based on elevation and other topographic data
- **Environmental Data Art**: Transform environmental monitoring data into dynamic visual art
- **Satellite Imagery Processing**: Convert satellite imagery into artistic representations

## Installation

```bash
pip install geo-infer-art
```

Or install from source:

```bash
git clone https://github.com/activeinference/GEO-INFER.git
cd GEO-INFER/GEO-INFER-ART
pip install -e .
```

## Quick Start

```python
from geo_infer_art import GeoArt, StyleTransfer, GenerativeMap

# Load geospatial data
geo_data = GeoArt.load_geojson("path/to/data.geojson")

# Apply artistic style transfer to a map
styled_map = StyleTransfer.apply(
    geo_data, 
    style="watercolor",
    color_palette="autumn"
)

# Generate procedural art based on terrain
terrain_art = GenerativeMap.from_elevation(
    region="grand_canyon",
    abstraction_level=0.7,
    style="contour_flow"
)

# Save outputs
styled_map.save("artistic_map.png")
terrain_art.save("terrain_abstract.png")
```

## Core Components

### Visualization and Aesthetics

- **GeoArt**: Create artistic visualizations of geospatial data
- **ColorPalette**: Manage color schemes for maps and visualizations
- **StyleTransfer**: Apply artistic styles to geospatial visualizations

### Generative Art

- **GenerativeMap**: Create generative art from elevation data
- **ProceduralArt**: Generate procedural art based on geographic features

### Place-Based Art

- **PlaceArt**: Create art based on specific locations
- **CulturalMap**: Create maps with cultural and historical context

## Examples

For detailed usage examples, see the [examples directory](examples/). You can run all examples with:

```bash
python -m examples.run_all_examples
```

Or run a specific example:

```bash
python -m examples.artistic_map_generation
```

## Testing

A comprehensive test suite is available in the [tests directory](tests/). Run all tests with:

```bash
python -m tests.run_all_tests
```

## Documentation

- [User Guide](docs/user_guide.md): Comprehensive guide to using GEO-INFER-ART
- [API Specification](docs/api_specification.md): Detailed API documentation
- [Architecture](docs/architecture.md): Overview of the module's architecture
- [Data Schemas](docs/data_schemas.md): Descriptions of data structures used in the module

## Project Structure

```
geo_infer_art/
├── api/               # API endpoints and interfaces
├── core/              # Core functionality
│   ├── visualization/ # Data visualization components
│   │   └── geo_art.py # GeoArt implementation
│   ├── generation/    # Generative art systems
│   │   ├── generative_map.py # Terrain-based art generation
│   │   └── procedural_art.py # Procedural art generation
│   ├── aesthetics/    # Aesthetic frameworks and transformations
│   │   ├── color_palette.py # Color palette management
│   │   └── style_transfer.py # Style transfer implementation
│   └── place/         # Place-based art tools
│       ├── place_art.py # Location-based art
│       └── cultural_map.py # Cultural context mapping
├── models/            # ML models for style transfer and generation
└── utils/             # Utility functions and helpers
    └── validators.py  # Input validation utilities
```

## Use Cases

- **Urban Planning Visualization**: Create aesthetically pleasing visualizations of urban planning scenarios
- **Environmental Data Art**: Transform climate and environmental data into compelling visual narratives
- **Cultural Mapping**: Represent cultural heritage and stories through artistic geospatial visualizations
- **Educational Tools**: Develop engaging visual materials for teaching geography and spatial concepts
- **Public Art Planning**: Design and visualize public art installations with geographic context

## Contributing

Contributions are welcome! Please see our [Contributing Guidelines](../CONTRIBUTING.md) for details.

## License

This project is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License - see the [LICENSE](../LICENSE) file for details. 