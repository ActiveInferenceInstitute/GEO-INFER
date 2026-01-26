---
title: "GEO-INFER-ART: Cartographic Design and Visualization"
description: "Beautiful maps, data visualization, and generative art from geospatial data"
purpose: "Create stunning visualizations, cartographic designs, and artistic maps"
module_type: "Visualization"
status: "Alpha"
last_updated: "2026-01-26"
dependencies: ["SPACE", "DATA"]
compatibility: ["GEO-INFER-SPACE", "GEO-INFER-DATA", "GEO-INFER-APP"]
tags: ["cartography", "visualization", "design", "art", "maps"]
difficulty: "Intermediate"
estimated_time: "40"
---

<div align="center">
  <h3><a href="../README.md">🌍 GEO-INFER Core</a></h3>
  <a href="../AGENTS.md">🤖 Agent Architecture</a> •
  <a href="../README.md#-module-overview">📦 Module Index</a> •
  <a href="./docs/">📚 Documentation</a>
</div>

---

# GEO-INFER-ART: Cartographic Design and Visualization

## Overview

**GEO-INFER-ART** provides artistic visualization capabilities:

- **Cartographic Design**: Professional map styling
- **3D Visualization**: Terrain and building renders
- **Generative Art**: Algorithmic art from geo data
- **Infographics**: Map-based data stories

## Features

### Cartographic Design

```python
from geo_infer_art import CartographicDesigner

# Create beautiful maps
designer = CartographicDesigner()

map_art = designer.create(
    data=city_data,
    style="watercolor",
    colors="earth_tones"
)

map_art.export("art_map.png", dpi=300)
```

### 3D Visualization

```python
from geo_infer_art import GeoVisualizer

# 3D terrain rendering
viz = GeoVisualizer()

terrain = viz.render_3d(
    dem=elevation_data,
    texture=satellite,
    exaggeration=2.0
)
```

### Generative Art

```python
from geo_infer_art import GenerativeArtist

# Generate art from geo data
artist = GenerativeArtist()

artwork = artist.generate(
    source=street_network,
    style="abstract_flow",
    randomness=0.3
)

artwork.save("city_art.svg")
```

### Animations

```python
from geo_infer_art import Animator

# Create map animations
animator = Animator()

animation = animator.create(
    data=temporal_data,
    type="timelapse",
    fps=30
)

animation.export("timelapse.mp4")
```

## Art Styles

| Style | Description |
|-------|-------------|
| **Watercolor** | Soft, artistic |
| **Minimalist** | Clean lines |
| **3D Isometric** | 3D projection |
| **Abstract** | Generative |
| **Vintage** | Retro maps |

## Integration Points

| Module | Integration |
|--------|-------------|
| **GEO-INFER-APP** | Dashboard viz |
| **GEO-INFER-DATA** | Data sources |
| **GEO-INFER-SPACE** | Geometry |

## Installation

```bash
uv pip install -e "./GEO-INFER-ART"
```

---

**Status**: Alpha

**Last Updated**: 2026-01-26
