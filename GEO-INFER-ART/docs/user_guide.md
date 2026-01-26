# GEO-INFER-ART User Guide

## Getting Started

### Installation

```bash
uv pip install -e "./GEO-INFER-ART"
```

### Quick Start

```python
from geo_infer_art import CartographicDesigner

# Load your data
import geopandas as gpd
data = gpd.read_file("my_data.geojson")

# Create beautiful map
designer = CartographicDesigner()
map_img = designer.create(data, style="watercolor")

# Save
map_img.save("my_map.png")
```

## Creating Maps

### Basic Map

```python
from geo_infer_art import CartographicDesigner

designer = CartographicDesigner()
map_img = designer.create(
    data=city_boundaries,
    style="minimalist",
    colors="monochrome"
)
```

### Multi-Layer Map

```python
designer.add_layer(water_bodies, style="water")
designer.add_layer(roads, style="roads")
designer.add_layer(buildings, style="buildings")

map_img = designer.render()
```

## Styling Options

| Style | Best For |
|-------|----------|
| `watercolor` | Artistic, decorative |
| `minimalist` | Clean infographics |
| `vintage` | Historical feel |
| `satellite` | Photorealistic |

## 3D Visualization

```python
from geo_infer_art import GeoVisualizer

viz = GeoVisualizer()
scene = viz.render_3d(
    dem=elevation,
    texture=satellite,
    exaggeration=2.0
)
scene.save("3d_terrain.png")
```

## Creating Animations

```python
viz = GeoVisualizer()
animation = viz.animate(
    data=temporal_data,
    fps=30
)
animation.save("timelapse.mp4")
```

## Generative Art

```python
from geo_infer_art import GenerativeArtist

artist = GenerativeArtist()
artwork = artist.generate(
    source=street_network,
    style="abstract_flow"
)
artwork.save("city_art.svg")
```

---

**Last Updated**: 2026-01-26
