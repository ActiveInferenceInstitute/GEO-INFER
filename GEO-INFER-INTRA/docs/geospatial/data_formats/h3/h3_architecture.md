# H3 Technical Architecture

This document provides a detailed explanation of the technical architecture underlying the H3 geospatial indexing system.

## Core Design Principles

H3 was designed with the following principles in mind:

1. **Hierarchical structure** - To support multi-resolution analysis
2. **Hexagonal grid cells** - To provide consistent neighbor relationships
3. **Global coverage** - With minimized distortion
4. **Efficient encoding** - Using 64-bit integers
5. **Computational efficiency** - For spatial operations

## Icosahedral Foundation

The foundation of the H3 grid system is a sphere-circumscribed icosahedron with a Dymaxion orientation. 

### Icosahedron Orientation

H3 uses a specific orientation of the icosahedron that places all 12 icosahedron vertices in ocean areas to minimize disruption to land-based analyses. This strategic placement ensures that the unavoidable pentagonal cells (at icosahedron vertices) are primarily in oceanic regions.

### Projection Method

H3 employs an inverse face-centered polyhedral gnomonic projection to map the grid onto Earth's surface. This provides:

- A coordinate reference system based on spherical coordinates
- Compatibility with WGS84/EPSG:4326 authalic radius
- Minimal distortion compared to traditional map projections

The gnomonic projection introduces a linear distortion of approximately 0.33% due to the spherical nature of Earth.

## Hexagonal Grid Structure

### Why Hexagons?

The choice of hexagons as the primary cell shape offers several advantages:

1. **Equidistant neighbors**: All adjacent hexagons are the same distance from the center cell
2. **Single neighbor class**: Unlike squares which have both edge and corner neighbors
3. **Optimal perimeter-to-area ratio**: Hexagons approximate circles more closely than other shapes that can tile a plane
4. **Reduced visual distortion**: Hexagonal grids provide more intuitive representations of proximity relationships

### Pentagon Necessity

While H3 is primarily a hexagonal system, it must include 12 pentagons (one at each vertex of the icosahedron) per resolution level to maintain a closed grid on the sphere. This is a mathematical necessity when tiling a sphere with mostly hexagonal cells.

## Hierarchical Resolution System

### Resolution Levels

H3 implements 16 distinct resolution levels (0-15) with the following characteristics:

| Resolution | Average Hexagon Edge Length | Average Hexagon Area |
|------------|-------------------------------|----------------------|
| 0          | 1107.71 km                   | 4,357,449.82 km² |
| 1          | 418.68 km                    | 609,788.44 km² |
| 2          | 158.24 km                    | 86,801.82 km² |
| 3          | 59.81 km                     | 12,393.73 km² |
| 4          | 22.61 km                     | 1,770.51 km² |
| 5          | 8.54 km                      | 252.93 km² |
| 6          | 3.23 km                      | 36.13 km² |
| 7          | 1.22 km                      | 5.16 km² |
| 8          | 461.35 m                     | 0.74 km² |
| 9          | 174.38 m                     | 0.11 km² |
| 10         | 65.91 m                      | 0.015 km² |
| 11         | 24.91 m                      | 0.0022 km² |
| 12         | 9.42 m                       | 0.00031 km² |
| 13         | 3.56 m                       | 0.000045 km² |
| 14         | 1.35 m                       | 0.0000064 km² |
| 15         | 0.51 m                       | 0.00000092 km² |

### Aperture-7 Subdivision

H3 uses an aperture-7 subdivision strategy, where each cell is divided into seven smaller cells at the next finer resolution. This creates:

- A consistent hierarchy across resolution levels
- Each finer resolution scaling by approximately the square root of 7
- Hexagons at each resolution having approximately 1/7th the area of hexagons at the next coarser resolution

## Cell Indexing

### 64-bit Integer Representation

H3 encodes cell locations into 64-bit integers with the following bit layout:

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|0|0|0|0|0|0|0|0|0|0|0|0|       Cell Base Index             |Mod|
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                    Cell Base Index (continued)                 |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

The components of an H3 cell index include:
- 1 bit: Reserved and set to 0
- 4 bits: Indicates the H3 Cell index mode
- 3 bits: Reserved and set to 0
- 4 bits: Cell resolution (0-15)
- 7 bits: Base cell (0-121)
- 3 bits for each resolution digit from resolution 1 up to the cell's resolution

### Index Properties

H3 indices have several important properties:

1. **Hierarchical ordering**: An H3 index is always lower than the indices of its children
2. **Spatial locality**: Neighboring cells tend to have similar indices
3. **Efficient operations**: Bitwise operations can derive parent-child relationships

## Mathematical Properties

### Area Variation

While H3 cells at the same resolution are designed to have approximately equal areas, there is some variation:

- Up to 4% area variance between cells at the same resolution
- Higher variance near the icosahedron edges and vertices

### Distance Properties

Hexagonal cells provide consistent distance properties:
- Center-to-center distance between adjacent hexagons varies by only ±5% (compared to ±41% in square grids)
- All six neighbors of a hexagon are equidistant from the center cell

### Scale Factor

The relationship between resolution levels follows a consistent scale factor:
- Edge length ratio between consecutive resolutions: approximately √7 ≈ 2.6457
- Area ratio between consecutive resolutions: approximately 1:7

## References

1. [H3 Core Library Overview](https://h3geo.org/docs/core-library/overview/)
2. [H3 Indexing Highlights](https://h3geo.org/docs/highlights/indexing/)
3. [Uber Engineering Blog: H3](https://www.uber.com/blog/h3/)
4. [H3 Cell Index](https://h3geo.org/docs/library/index/cell/) 