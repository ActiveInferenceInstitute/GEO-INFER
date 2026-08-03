# Getting Started with Geospatial Analysis

This page is the entry point for geospatial work in GEO-INFER. It points to
the spatial concepts, H3 data format guides, and runnable first-analysis
tutorials; see the [geospatial hub](../index.md) for the full section.

## Prerequisites

- **Python 3.11+** and **uv** — set up the workspace as described in the
  [Installation Guide](../../getting_started/installation_guide.md).
- Basic familiarity with coordinate reference systems and vector/raster data
  (see [Spatial Concepts](../concepts/index.md)).

## Quick Start

```bash
git clone https://github.com/ActiveInferenceInstitute/GEO-INFER.git
cd GEO-INFER
uv sync --all-packages --all-extras
```

Verify the workspace:

```
```bash
python -m compileall GEO-INFER-*/src GEO-INFER-*/examples
uv run python GEO-INFER-TEST/validate_documentation.py --strict
```

## First Analysis

Follow the [First Analysis](../../getting_started/first_analysis.md) tutorial for
a runnable H3 plus Active Inference workflow, or the
[First Map](../../getting_started/first_map.md) tutorial to render your first
spatial map.

## Core Concepts

- [Coordinate Systems](../concepts/coordinate_systems.md) — geographic and
  projected coordinate systems.
- [Spatial Reference Systems](../concepts/spatial_reference_systems.md) —
  datums and EPSG codes.
- [Scale and Resolution](../concepts/scale_resolution.md) — multi-scale
  analysis.
- [Spatial Data Models](../concepts/spatial_data_models.md) — vector and
  raster models.
- [Uncertainty and Accuracy](../concepts/uncertainty_accuracy.md) — data
  quality.

## H3 Data Format

The H3 v4 guide is the canonical reference for the native hierarchical grid:

- [H3 Guide](../data_formats/h3/index.md) — API, architecture, and usage.
- [H3 Ecosystem](../data_formats/h3/ecosystem.md) — tools and platforms.

## Working with the SPACE Module

`geo_infer_space` provides H3 v4 indexing and spatial analytics:

```
```python
from geo_infer_space import latlng_to_cell, cell_to_latlng

cell = latlng_to_cell(37.7749, -122.4194, 9)
lat, lng = cell_to_latlng(cell)
```

See the [SPACE module page](../../modules/geo-infer-space.md) and the
[API Reference](../../api/reference.md).

## Next Steps

1. [Geospatial Algorithms](../algorithms/index.md) — indexing, geometry, and
   statistics.
2. [Spatial Analysis](../analysis/index.md) — analysis methods.
3. [Case Studies](../case_studies/index.md) — applied examples.
4. [Geospatial Standards](../standards/index.md) — OGC/ISO standards.

## Troubleshooting

- [Support hub](../../support/index.md) — FAQ and installation issues.
- [Installation Issues](../../support/installation_issues.md).
