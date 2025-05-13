# GEO-INFER-ART Examples

This directory contains example scripts demonstrating the usage of the GEO-INFER-ART module.

## Running Examples

### Run All Examples

To run all examples in sequence:

```bash
cd GEO-INFER-ART
python -m examples.run_all_examples
```

### Run Individual Examples

To run a specific example:

```bash
cd GEO-INFER-ART
python -m examples.artistic_map_generation
```

Or with a specific example number:

```bash
cd GEO-INFER-ART
python -m examples.artistic_map_generation 1  # Run only example 1
```

## Available Examples

### Artistic Map Generation (`artistic_map_generation.py`)

Demonstrates the core functionality of GEO-INFER-ART for creating artistic visualizations of geospatial data.

Examples included:
1. Basic GeoArt: Creating simple geospatial visualizations with different styles
2. Color Palettes: Creating and visualizing color palettes
3. Style Transfer: Applying artistic style transfer to maps
4. Generative Maps: Creating generative art from elevation data
5. Procedural Art: Creating procedural art from geographic coordinates
6. Place Art: Creating art based on specific locations
7. Cultural Maps: Creating maps with cultural and historical context

### Output

All examples save their output to the `output/` directory, which is created automatically if it doesn't exist.

## Creating New Examples

When adding new examples to the GEO-INFER-ART module, please follow these guidelines:

1. Use a descriptive filename that indicates the focus of the example
2. Include docstrings and comments to explain the purpose and functionality
3. Structure the example as a series of functions, each demonstrating a specific feature
4. Include error handling and fallbacks for missing data
5. Create a `run_all()` function that runs all examples in the script
6. Save outputs to the `output/` directory
7. Use the same command-line argument structure as existing examples

### Example Template

```python
#!/usr/bin/env python
"""
Example script demonstrating [feature] in GEO-INFER-ART.
"""

import os
from geo_infer_art import [relevant_components]

def ensure_directory(directory):
    """Create directory if it doesn't exist."""
    if not os.path.exists(directory):
        os.makedirs(directory)

def example_1_description():
    """Brief description of what this example demonstrates."""
    # Example code
    pass

def example_2_description():
    """Brief description of what this example demonstrates."""
    # Example code
    pass

def run_all():
    """Run all examples in this script."""
    example_1_description()
    example_2_description()
    # ...

if __name__ == "__main__":
    print("GEO-INFER-ART Example: [Title]")
    print("==============================")
    
    # Create output directory
    ensure_directory("output")
    
    # Run examples
    import sys
    if len(sys.argv) > 1:
        example_num = sys.argv[1]
        # Run specific example based on command-line argument
    else:
        run_all() 