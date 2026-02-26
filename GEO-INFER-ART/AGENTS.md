# GEO-INFER-ART: Agent Capabilities

<div align="center">
  <h3><a href="../README.md">🌍 GEO-INFER Core</a></h3>
  <a href="../AGENTS.md">🤖 Agent Architecture</a> •
  <a href="../README.md#-module-overview">📦 Module Index</a> •
  <a href="./README.md">📚 Module Documentation</a>
</div>

---

## Overview

The **GEO-INFER-ART** module provides artistic and visualization capabilities for agents, enabling cartographic design, data visualization, and generative art from geospatial data.

## Agent Capabilities

### 1. Cartographic Design

```python
from geo_infer_art import CartographicDesigner

# Create beautiful maps
designer = CartographicDesigner()

map_design = designer.create(
    data=spatial_data,
    style="watercolor",
    color_palette="earth_tones",
    labels=True,
    legend=True)

map_design.export("map.png", dpi=300)```

### 2. Data Visualization

```python
from geo_infer_art import GeoVisualizer

# Create data visualizations
viz = GeoVisualizer()

# 3D terrain visualization
terrain = viz.render_3d(
    dem=elevation_data,
    texture=satellite_imagery,
    exaggeration=2.0,
    camera_angle=45)

# Animated time series
animation = viz.animate(
    data=temporal_data,
    frames_per_second=10,
    output="timelapse.mp4")
```

### 3. Generative Art

```python
from geo_infer_art import GenerativeArtist

# Generate art from geo data
artist = GenerativeArtist()

artwork = artist.generate(
    source=city_streets,
    style="abstract_flow",
    colors=["#2C3E50", "#E74C3C", "#ECF0F1"],
    randomness=0.3)

artwork.save("city_art.svg")```

### 4. Infographic Generator

```python
from geo_infer_art import InfographicGenerator

# Create map infographics
infographic = InfographicGenerator()

result = infographic.create(
    title="Urban Growth 2020-2025",
    data=growth_statistics,
    map_extent=city_boundary,
    charts=["growth_rate", "population"],
    style="modern")
```

## Implementation Status

### Currently Implemented

| Feature | Status | Description |
|---------|--------|-------------|
| **Cartography** | ✅ Ready | Map styling |
| **3D Visualization** | ✅ Ready | Terrain, buildings |
| **Generative Art** | ✅ Ready | Algorithmic art |
| **Infographics** | ✅ Ready | Data stories |

### Aspirational/Planned Features

| Feature | Priority | Description |
|---------|----------|-------------|
| **ArtDirectorAgent** | 🔮 Medium | Style recommendations |
| **AnimationAgent** | 🔮 Medium | Complex animations |

## Use Cases

### City Visualization

```python
from geo_infer_art import CityVisualizer

city_viz = CityVisualizer(city="san_francisco")

# Generate city portrait
portrait = city_viz.create_portrait(
    style="isometric_3d",
    highlight=["landmarks", "transit"],
    time_of_day="golden_hour")
```

---

This AGENTS.md documents how GEO-INFER-ART provides artistic capabilities for agents.

**Last Updated**: 2026-02-25

**Claude Skill**: See [SKILL.md](./SKILL.md) for quick-reference API examples and integration map.
