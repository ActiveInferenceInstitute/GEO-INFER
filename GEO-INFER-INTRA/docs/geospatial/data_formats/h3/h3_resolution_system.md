# H3 Hierarchical Resolution System

This document provides a detailed explanation of the hierarchical resolution system in the H3 geospatial indexing framework, including its mathematical properties, use cases, and implementation details.

## Introduction to H3 Resolutions

The H3 system implements a multi-resolution hierarchy with 16 distinct resolution levels (0-15), providing a flexible framework for analyzing spatial phenomena at different scales. Each resolution level represents a different degree of spatial precision, allowing applications to choose the appropriate granularity for specific analytical needs.

## Resolution Hierarchy Structure

### Base Cells (Resolution 0)

At the coarsest level (resolution 0), H3 divides the Earth into 122 base cells:
- 110 hexagons
- 12 pentagons (at the vertices of the underlying icosahedron)

These base cells form the foundation of the H3 hierarchy and represent the largest spatial units in the system.

### Hierarchical Subdivision

As the resolution increases, each cell is further subdivided into approximately seven smaller cells, following an "aperture 7" approach:

- Resolution 0: 122 base cells
- Resolution 1: ~800 cells (122 × 7)
- Resolution 2: ~5,600 cells (800 × 7)
- Resolution 3: ~39,200 cells (5,600 × 7)

And so on, with each subsequent resolution having approximately 7 times more cells than the previous level.

### Visualization of the Hierarchy

```
Resolution 0:                 Resolution 1:
   ___________                    ___________
  /           \                  /     |     \
 /             \                /  1  / \  3  \
/               \              /     /   \     \
\               /              \  0 /  C  \ 6  /
 \             /                \   \     /   /
  \___________/                  \___\___/___/
                                    2  | 5
                                     4

Resolution 0 cell (C) subdivides into 7 children (0-6) at Resolution 1
```

### Cell Counts and Coverage

| Resolution | Global Cell Count | Percentage of Resolution 0 Cells | Cells in Continental US |
|------------|------------------|---------------------------------|-------------------------|
| 0 | 122 | 100% | ~10 |
| 1 | ~850 | 14.3% | ~60 |
| 2 | ~6,000 | 2.0% | ~400 |
| 3 | ~42,000 | 0.3% | ~2,800 |
| 4 | ~294,000 | 0.04% | ~20,000 |
| 5 | ~2,000,000 | 0.006% | ~140,000 |
| 6 | ~14,000,000 | 0.0008% | ~1,000,000 |
| 7 | ~98,000,000 | 0.0001% | ~7,000,000 |
| 8 | ~686,000,000 | 0.00002% | ~50,000,000 |
| 9 | ~4,800,000,000 | ~0.000003% | ~350,000,000 |
| 10+ | Trillions+ | <0.0000001% | Billions+ |

## Resolution Cell Characteristics

Each resolution level has specific geometric properties that make it suitable for different analysis tasks:

### Cell Dimensions

| Resolution | Average Hexagon Edge Length | Average Hexagon Area |
|------------|-------------------------------|----------------------|
| 0 | 1,107.71 km | 4,357,449.82 km² |
| 1 | 418.68 km | 609,788.44 km² |
| 2 | 158.24 km | 86,801.82 km² |
| 3 | 59.81 km | 12,393.73 km² |
| 4 | 22.61 km | 1,770.51 km² |
| 5 | 8.54 km | 252.93 km² |
| 6 | 3.23 km | 36.13 km² |
| 7 | 1.22 km | 5.16 km² |
| 8 | 461.35 m | 0.74 km² |
| 9 | 174.38 m | 0.11 km² |
| 10 | 65.91 m | 0.015 km² |
| 11 | 24.91 m | 0.0022 km² |
| 12 | 9.42 m | 0.00031 km² |
| 13 | 3.56 m | 0.000045 km² |
| 14 | 1.35 m | 0.0000064 km² |
| 15 | 0.51 m | 0.00000092 km² |

### Scale Comparison

To put these resolutions in perspective:

- **Resolution 0-2**: Continental/subcontinental regions
- **Resolution 3-4**: Large countries, states, or provinces
- **Resolution 5-6**: Metropolitan areas, counties
- **Resolution 7-8**: Cities, large districts
- **Resolution 9-10**: Neighborhoods, campuses
- **Resolution 11-12**: City blocks, large buildings
- **Resolution 13-14**: Individual buildings, parks
- **Resolution 15**: Sub-building precision

## Mathematical Properties

### Scaling Factor

The H3 resolution system follows a consistent mathematical progression:

- **Edge Length Ratio**: Each finer resolution scales the edge length by approximately the square root of 7 (≈ 2.6457)
- **Area Ratio**: Each finer resolution has approximately 1/7th the area of cells at the next coarser resolution

The precise relationship can be expressed as:

$$EdgeLength(r+1) \approx \frac{EdgeLength(r)}{\sqrt{7}}$$

$$Area(r+1) \approx \frac{Area(r)}{7}$$

Where $r$ represents a resolution level.

### Area Consistency

Although H3 cells at the same resolution generally have similar areas, there is some variation:

- Area variance of up to ±4% at most resolutions
- Higher variance near icosahedron edges and vertices
- Consistency improves at finer resolutions

This property makes H3 suitable for area-based analyses where approximate uniformity is sufficient.

## Parent-Child Relationships

### Hierarchical Encoding

H3 uses a compact_cells bit representation to encode the hierarchical relationship between cells:

- The base cell is identified by a 7-bit value (0-121)
- Each subsequent resolution level adds 3 bits to identify which of the 7 children contains the location
- The resolution itself is stored in a 4-bit field

This encoding allows efficient traversal up and down the resolution hierarchy.

### Parent Calculation

To find the parent of an H3 index at a coarser resolution:

```python
# Python example
parent = h3.cell_to_parent(h3_index, parent_resolution)
```

The parent calculation truncates the 3 bits corresponding to the current resolution, effectively moving up the hierarchy.

### Children Calculation

To find all children of an H3 index at a finer resolution:

```python
# Python example
children = h3.cell_to_children(h3_index, child_resolution)
```

For a single resolution step, this produces approximately 7 children. Multiple resolution steps multiply this effect:

- 1 resolution step: ~7 children
- 2 resolution steps: ~49 children
- 3 resolution steps: ~343 children

### Approximate Containment

Unlike some other hierarchical systems (e.g., S2), H3's parent-child relationship is approximate rather than exact. A small portion (up to 0.5%) of a child cell's area may fall outside its parent cell's boundary.

This characteristic is a trade-off that allows H3 to maintain more consistent hexagonal shapes across resolutions.

## Resolution Selection Guidelines

Choosing the appropriate resolution is crucial for effective H3-based analysis. Here are guidelines for different application types:

### By Geographic Scale

| Geographic Scope | Recommended Resolutions | Approximate Cell Size |
|------------------|------------------------|----------------------|
| Global | 0-2 | 100-1000 km |
| Continental | 2-3 | 60-160 km |
| Country | 3-5 | 8-60 km |
| State/Province | 4-6 | 3-22 km |
| Metropolitan Area | 6-7 | 1-3 km |
| City | 7-8 | 400m-1.2km |
| Neighborhood | 8-9 | 150-450m |
| Block | 9-10 | 60-170m |
| Building | 11-12 | 10-25m |
| Sub-building | 13-15 | <4m |

### By Application Type

| Application Type | Recommended Resolutions | Rationale |
|------------------|------------------------|-----------|
| Administrative Boundaries | 5-7 | Balances precision with computational efficiency |
| Transportation Network | 8-9 | Captures road segments and intersections adequately |
| Population Density | 7-8 | Appropriate for census-like demographic analysis |
| Retail Analytics | 9-10 | Captures store-level patterns and foot traffic |
| Environmental Monitoring | 6-8 | Suitable for climate and ecological data |
| Mobile Signal Coverage | 8-10 | Matches typical cellular propagation characteristics |
| Urban Planning | 8-11 | Multiple scales for different urban features |
| Indoor Positioning | 13-15 | Provides sub-meter precision for indoor navigation |

### Performance Considerations

The resolution choice significantly impacts computational performance:

| Resolution | Approximate Cells (Continental US) | Relative Computation Cost |
|------------|-----------------------------------|--------------------------|
| 5 | ~140,000 | 1x |
| 6 | ~1,000,000 | 7x |
| 7 | ~7,000,000 | 49x |
| 8 | ~50,000,000 | 350x |
| 9 | ~350,000,000 | 2,500x |

This exponential growth means that increasing resolution by 2 levels increases computation requirements by roughly 50 times.

## Multi-resolution Operations

H3 provides several operations that work across different resolution levels:

### Compaction

The `compact_cells_cells` operation optimizes representation by using the coarsest possible cells to represent a set of hexagons:

```python
# Python example of compact_cellsion
detailed_cells = [...]  # Many cells at resolution 9
compact_cellsed_cells = h3.compact_cells_cells(detailed_cells)  # Converts to a mixed-resolution set
```

This operation can significantly reduce the number of cells needed to represent an area:
- Before: 10,000 cells at resolution 9
- After: ~1,500 mixed-resolution cells (resolutions 5-9)

### Uncompact_cellsion

The inverse operation, `uncompact_cells_cells`, expands a mixed-resolution set to a specific uniform resolution:

```python
# Python example of uncompact_cells_cellsion
mixed_resolution_cells = [...]  # Cells at various resolutions
uniform_cells = h3.uncompact_cells_cells_cells(mixed_resolution_cells, 9)  # All at resolution 9
```

### Resolution-appropriate Analysis

Many analysis workflows involve multiple resolution levels:

1. **Coarse Analysis**: Initial processing at lower resolutions (5-7)
2. **Refinement**: Increasing resolution in areas of interest (7-9)
3. **Detailed Analysis**: Fine-resolution analysis of specific features (9-12)
4. **Aggregation**: Upscaling results to presentation resolution (6-8)

This multi-resolution approach optimizes computational resources while maintaining appropriate precision.

## Practical Examples

### Ride-sharing Demand Analysis

Uber uses different H3 resolutions to analyze ride demand patterns:

```python
# Example workflow for ride demand analysis
# 1. Aggregate individual ride requests to resolution 9
request_density = {}
for lat, lng in ride_requests:
    h3_cell = h3.latlng_to_cell(lat, lng, 9)
    request_density[h3_cell] = request_density.get(h3_cell, 0) + 1

# 2. Identify high-demand areas at resolution 9
high_demand_cells = [cell for cell, count in request_density.items() if count > threshold]

# 3. Compact for analytical efficiency
compact_cellsed_high_demand = h3.compact_cells_cells(high_demand_cells)

# 4. Visualize at resolution 7 for dashboard
visualization_cells = {}
for cell in high_demand_cells:
    parent = h3.cell_to_parent(cell, 7)
    visualization_cells[parent] = visualization_cells.get(parent, 0) + 1
```

### Environmental Analysis

Environmental scientists analyzing forest cover might use:

```python
# Example of multi-resolution environmental analysis
# 1. Initial continental classification at resolution 4
landcover_r4 = classify_satellite_imagery(resolution=4)

# 2. Identify forest regions
forest_cells_r4 = [cell for cell, class_type in landcover_r4.items() if class_type == 'forest']

# 3. Uncompact_cells forest areas to higher resolution for detailed analysis
forest_cells_r7 = h3.uncompact_cells_cells_cells(forest_cells_r4, 7)

# 4. Analyze forest fragmentation at higher resolution
fragmentation_metrics = analyze_fragmentation(forest_cells_r7)

# 5. Reaggregate metrics to watershed level (resolution 5)
watershed_metrics = {}
for cell, metric in fragmentation_metrics.items():
    watershed = h3.cell_to_parent(cell, 5)
    if watershed not in watershed_metrics:
        watershed_metrics[watershed] = []
    watershed_metrics[watershed].append(metric)
```

## Resolution Interoperability

### Converting Between Systems

When working with multiple spatial indexing systems, approximate resolution equivalents can be helpful:

| H3 Resolution | Geohash Precision | S2 Level | Approximate Cell Size |
|---------------|-------------------|----------|----------------------|
| 2 | 2 | 3-4 | ~150 km |
| 5 | 4 | 8-9 | ~8 km |
| 7 | 5-6 | 12 | ~1 km |
| 9 | 7 | 15 | ~150 m |
| 12 | 9 | 20 | ~10 m |
| 15 | 11-12 | 24-25 | ~0.5 m |

### Cross-system Workflows

Some applications combine different systems:

```python
# Example of cross-system workflow
# 1. Receive data indexed with Geohash
geohash_data = {"9q8yy": 150, "9q8yz": 75, ...}

# 2. Convert to H3 for analysis
h3_data = {}
for gh, value in geohash_data.items():
    # Convert geohash centroid to lat/lng
    lat, lng = geohash_to_latlon(gh)
    # Determine appropriate H3 resolution based on geohash precision
    h3_res = 9 if len(gh) >= 6 else 7
    h3_cell = h3.latlng_to_cell(lat, lng, h3_res)
    h3_data[h3_cell] = value

# 3. Perform H3-based analysis
results = analyze_with_h3(h3_data)

# 4. Output in S2 format for visualization service
s2_results = {}
for h3_cell, result in results.items():
    lat, lng = h3.cell_to_latlng(h3_cell)
    s2_cell = s2sphere.CellId.from_lat_lng(
        s2sphere.LatLng.from_degrees(lat, lng)
    ).parent(15)
    s2_results[s2_cell.id()] = result
```

## Implementation Details

### Resolution Representation in H3 Indices

Within the 64-bit H3 index, the resolution is encoded in a 4-bit field:

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|0|0|0|0|0|0|0|0|M|M|M|M|  RES |0|0|0|      BASE CELL           |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                    CELL POSITION AT RES 1-15                   |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

Where:
- `RES` is the 4-bit resolution field (0-15)
- `BASE CELL` identifies one of the 122 base cells
- `CELL POSITION` encodes the position within the hierarchy (3 bits per resolution level)

### Resolution Transitions

Unlike some hierarchical systems, H3 uses a consistent bit pattern for transitions between any resolution levels:

```
Function h3_to_parent(h3_index, parent_res):
    1. Verify parent_res is less than current resolution
    2. Mask off bits corresponding to levels finer than parent_res
    3. Update resolution field to parent_res
    4. Return modified index
```

## Limitations and Edge Cases

### Pentagon Cells

The 12 pentagon cells (and their descendants) have different properties than hexagons:

- Different neighbor relationship pattern (5 neighbors instead of 6)
- Slightly different area and edge length characteristics
- Special handling required for some operations like k-ring when pentagons are involved

Applications should be aware of pentagon edge cases, especially near icosahedron vertices.

### Resolution Boundaries

Some operations have resolution limits:

- Maximum resolution: 15
- Practical compact_cellsion limit: ~5 resolution levels at once
- Memory constraints for very large resolution transitions (e.g., parent(15) → children(15))

### Area Consistency

While H3 cells at the same resolution have similar areas, they are not exactly equal:

- Area variation of up to ±4% at the same resolution
- Applications requiring precise equal-area binning need additional normalization

## Best Practices

### Resolution Selection

1. **Test at multiple resolutions**: Before committing to a specific resolution, test performance at 2-3 different levels
2. **Think hierarchically**: Design analyses to leverage multiple resolutions
3. **Consider data density**: Match resolution to the typical spacing of input data points
4. **Factor in computation limits**: Be aware of the exponential growth in cell count with increasing resolution

### Multi-resolution Operations

1. **Use compact_cellsion**: Whenever representing complex shapes or regions
2. **Leverage resolution transitions**: Use coarse resolutions for initial filtering, then refine
3. **Store multi-resolution indices**: For large datasets, store indices at multiple resolutions to avoid recomputation
4. **Standardize resolution interfaces**: When sharing data between systems, define resolution standards

## References

1. [H3 Resolution Tables](https://h3geo.org/docs/core-library/restable/)
2. [Uber Engineering Blog: H3 Resolution Hierarchy](https://www.uber.com/blog/h3/)
3. [H3 Hierarchical Grid Design](https://h3geo.org/docs/core-library/overview/)
4. [H3 API Documentation](https://h3geo.org/docs/api/indexing/)
5. [Choosing Appropriate H3 Resolutions](https://h3geo.org/docs/highlights/indexing/) 