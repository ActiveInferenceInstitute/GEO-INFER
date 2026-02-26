---
name: geo-infer-art
description: Generative geospatial art and cartographic visualization. Use when creating artistic map visualizations, generative spatial art, interactive cartographic displays, animation sequences, or aesthetically-focused geographic rendering.
prerequisites:
  required:
    - geo-infer-space
  recommended:
    - geo-infer-data
difficulty: beginner
estimated_time: 30min
examples_dir: ../GEO-INFER-EXAMPLES/examples/
---

# GEO-INFER-ART

## Instructions

### Core Capabilities

- **Generative art**: Algorithmic spatial pattern generation, fractal landscapes
- **Cartographic design**: Aesthetic map styling, color palettes, typography
- **Interactive display**: mplcursors-based interactive map exploration
- **Animation**: Temporal spatial animation sequences, GIF/video export
- **Style transfer**: Apply artistic styles to geographic data visualizations

### Key Imports

```python
from geo_infer_art.core.geo_art import GeoArtGenerator
from geo_infer_art.core.cartography import CartographicDesigner
from geo_infer_art.core.animation import SpatialAnimator
from geo_infer_art.core.style import StyleTransfer
```

## Examples

```python
from geo_infer_art.core.geo_art import GeoArtGenerator

generator = GeoArtGenerator()
artwork = generator.create(
    data=spatial_data,
    style="watercolor",
    interactive=True  # Enables mplcursors hover
)
artwork.save("output.png", dpi=300)
```

## Guidelines

- Interactive features use real mplcursors + matplotlib (not `ax.plot([0],[0])`)

### Integrations

- Integrates with SPACE for H3-based spatial patterns
- Test: `uv run python -m pytest GEO-INFER-ART/tests/ -v`
