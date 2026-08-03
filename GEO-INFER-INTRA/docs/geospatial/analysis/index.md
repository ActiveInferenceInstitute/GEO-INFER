# Spatial Analysis

This section covers spatial analysis methods, techniques, and applications
that enable users to examine geographic patterns, relationships, and trends in
spatial data.

## Contents

- [Spatial Concepts](../concepts/index.md) — coordinate systems, scale and
  resolution, spatial data models, and uncertainty.
- [Algorithms](../algorithms/index.md) — indexing, geometric, interpolation,
  and statistical algorithms.
- [Case Studies](../case_studies/index.md) — applied examples across domains.
- [Visualization](../visualization/index.md) — mapping and visualization
  techniques.
- [Data Formats](../data_formats/index.md) — H3 and other data formats.
- [Geospatial Standards](../standards/index.md) — OGC, ISO, and metadata
  standards.

## Core Analysis Types

### Vector Analysis

Operations performed on vector data (points, lines, polygons):

- **Overlay Operations** — union, intersection, identity, clip, erase.
- **Proximity Analysis** — buffers, Thiessen/Voronoi polygons, distance
  calculations.
- **Geometric Measurements** — area, length, perimeter, centroid.

### Raster Analysis

Operations performed on raster data (grids/images):

- **Local Operations** — cell-by-cell calculations.
- **Focal Operations** — analysis using a neighborhood around each cell.
- **Zonal Operations** — analysis based on zones or regions.
- **Global Operations** — calculations across the entire raster.

### Network Analysis

Analysis of connected linear features:

- **Optimal Routing** — shortest path, traveling salesperson problem.
- **Service Area Analysis** — areas accessible within constraints.
- **Origin-Destination Analysis** — flow and allocation between locations.

### Statistical Analysis

Methods for understanding spatial patterns:

- **Spatial Autocorrelation** — measuring spatial dependency (Moran's I,
  Geary's C; see the [MATH module page](../../modules/geo-infer-math.md)).
- **Hot Spot Analysis** — identifying clusters of high/low values
  (Getis-Ord Gi*).
- **Regression Analysis** — analyzing relationships between variables.

## Workflow Integration

Spatial analysis can be integrated into GEO-INFER workflows through:

- Pre-defined analysis templates.
- Custom analysis scripts.
- Analysis chaining and parameter passing.
- Results visualization and interpretation.

See the [Workflow System](../../workflows/index.md) for details.

## Applications

Spatial analysis supports various applications including:

- Urban planning and land use analysis.
- Environmental monitoring and modeling.
- Emergency management and disaster response.
- Market analysis and location optimization.
- Transportation planning and optimization.
- Public health and epidemiology.

## Related Resources

- [Analysis Algorithms](../algorithms/index.md)
- [Workflow System](../../workflows/index.md)
- [Visualization Techniques](../visualization/index.md)
- [SPACE module page](../../modules/geo-infer-space.md)
