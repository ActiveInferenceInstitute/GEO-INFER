# H3 API Reference

This document provides a reference for the core H3 functions across different language bindings. It covers the essential operations for working with the H3 geospatial indexing system.

## Core Indexing Functions

### Point to H3 Cell

Converts a geographic coordinate (latitude, longitude) to an H3 cell index at the specified resolution.

| Language | Syntax | Example |
|----------|--------|---------|
| C | `H3Index h3_geo_to_h3(double lat, double lng, int res)` | `H3Index cell = h3_geo_to_h3(37.7749, -122.4194, 9);` |
| Python | `h3.geo_to_h3(lat, lng, resolution)` | `cell = h3.geo_to_h3(37.7749, -122.4194, 9)` |
| JavaScript | `h3.geoToH3(lat, lng, resolution)` | `const cell = h3.geoToH3(37.7749, -122.4194, 9);` |
| Java | `long geoToH3(double lat, double lng, int res)` | `long cell = h3.geoToH3(37.7749, -122.4194, 9);` |
| Go | `func GeoToH3(lat, lng float64, res int) H3Index` | `cell := h3.GeoToH3(37.7749, -122.4194, 9)` |

### H3 Cell to Center Point

Returns the geographic coordinates of the center point of an H3 cell.

| Language | Syntax | Example |
|----------|--------|---------|
| C | `void h3_h3_to_geo(H3Index h3, double *lat, double *lng)` | `double lat, lng; h3_h3_to_geo(cell, &lat, &lng);` |
| Python | `h3.h3_to_geo(h3_index)` | `lat, lng = h3.h3_to_geo(cell)` |
| JavaScript | `h3.h3ToGeo(h3Index)` | `const [lat, lng] = h3.h3ToGeo(cell);` |
| Java | `GeoCoord h3ToGeo(long h3)` | `GeoCoord center = h3.h3ToGeo(cell);` |
| Go | `func H3ToGeo(h H3Index) (lat, lng float64)` | `lat, lng := h3.H3ToGeo(cell)` |

### H3 Cell to Boundary

Returns the cell boundary as a series of geographic coordinates.

| Language | Syntax | Example |
|----------|--------|---------|
| C | `void h3_h3_to_geo_boundary(H3Index h3, GeoBoundary *gb)` | `GeoBoundary boundary; h3_h3_to_geo_boundary(cell, &boundary);` |
| Python | `h3.h3_to_geo_boundary(h3_index)` | `boundary = h3.h3_to_geo_boundary(cell)` |
| JavaScript | `h3.h3ToGeoBoundary(h3Index)` | `const boundary = h3.h3ToGeoBoundary(cell);` |
| Java | `List<GeoCoord> h3ToGeoBoundary(long h3)` | `List<GeoCoord> boundary = h3.h3ToGeoBoundary(cell);` |
| Go | `func H3ToGeoBoundary(h H3Index) [][]float64` | `boundary := h3.H3ToGeoBoundary(cell)` |

## Hierarchical Operations

### Get Parent Cell

Returns the parent cell at the specified resolution.

| Language | Syntax | Example |
|----------|--------|---------|
| C | `H3Index h3_h3_to_parent(H3Index h3, int parentRes)` | `H3Index parent = h3_h3_to_parent(cell, 8);` |
| Python | `h3.h3_to_parent(h3_index, parent_resolution)` | `parent = h3.h3_to_parent(cell, 8)` |
| JavaScript | `h3.h3ToParent(h3Index, parentRes)` | `const parent = h3.h3ToParent(cell, 8);` |
| Java | `long h3ToParent(long h3, int parentRes)` | `long parent = h3.h3ToParent(cell, 8);` |
| Go | `func H3ToParent(h H3Index, parentRes int) H3Index` | `parent := h3.H3ToParent(cell, 8)` |

### Get Children Cells

Returns the children cells at the specified resolution.

| Language | Syntax | Example |
|----------|--------|---------|
| C | `int h3_h3_to_children(H3Index h3, int childRes, H3Index *children)` | `H3Index children[MAX_SIZE]; h3_h3_to_children(cell, 10, children);` |
| Python | `h3.h3_to_children(h3_index, child_resolution)` | `children = h3.h3_to_children(cell, 10)` |
| JavaScript | `h3.h3ToChildren(h3Index, childRes)` | `const children = h3.h3ToChildren(cell, 10);` |
| Java | `List<Long> h3ToChildren(long h3, int childRes)` | `List<Long> children = h3.h3ToChildren(cell, 10);` |
| Go | `func H3ToChildren(h H3Index, childRes int) []H3Index` | `children := h3.H3ToChildren(cell, 10)` |

### Get Cell Resolution

Returns the resolution of an H3 cell.

| Language | Syntax | Example |
|----------|--------|---------|
| C | `int h3_h3_get_resolution(H3Index h3)` | `int res = h3_h3_get_resolution(cell);` |
| Python | `h3.h3_get_resolution(h3_index)` | `res = h3.h3_get_resolution(cell)` |
| JavaScript | `h3.h3GetResolution(h3Index)` | `const res = h3.h3GetResolution(cell);` |
| Java | `int h3GetResolution(long h3)` | `int res = h3.h3GetResolution(cell);` |
| Go | `func H3GetResolution(h H3Index) int` | `res := h3.H3GetResolution(cell)` |

### Get Cell Base Cell

Returns the base cell number (0-121) of an H3 cell.

| Language | Syntax | Example |
|----------|--------|---------|
| C | `int h3_h3_get_base_cell(H3Index h3)` | `int baseCell = h3_h3_get_base_cell(cell);` |
| Python | `h3.h3_get_base_cell(h3_index)` | `base_cell = h3.h3_get_base_cell(cell)` |
| JavaScript | `h3.h3GetBaseCell(h3Index)` | `const baseCell = h3.h3GetBaseCell(cell);` |
| Java | `int h3GetBaseCell(long h3)` | `int baseCell = h3.h3GetBaseCell(cell);` |
| Go | `func H3GetBaseCell(h H3Index) int` | `baseCell := h3.H3GetBaseCell(cell)` |

## Neighborhood Operations

### Get K-Ring

Returns all cells within distance k of the origin cell.

| Language | Syntax | Example |
|----------|--------|---------|
| C | `void h3_k_ring(H3Index origin, int k, H3Index *out)` | `H3Index neighbors[MAX_SIZE]; h3_k_ring(cell, 1, neighbors);` |
| Python | `h3.k_ring(h3_index, k)` | `neighbors = h3.k_ring(cell, 1)` |
| JavaScript | `h3.kRing(h3Index, k)` | `const neighbors = h3.kRing(cell, 1);` |
| Java | `List<Long> kRing(long h3, int k)` | `List<Long> neighbors = h3.kRing(cell, 1);` |
| Go | `func KRing(h H3Index, k int) []H3Index` | `neighbors := h3.KRing(cell, 1)` |

### Get K-Ring Distances

Returns all cells within distance k of the origin cell, along with their distances.

| Language | Syntax | Example |
|----------|--------|---------|
| C | `void h3_k_ring_distances(H3Index origin, int k, H3Index *out, int *distances)` | `H3Index neighbors[MAX_SIZE]; int distances[MAX_SIZE]; h3_k_ring_distances(cell, 2, neighbors, distances);` |
| Python | `h3.k_ring_distances(h3_index, k)` | `neighbors_with_distances = h3.k_ring_distances(cell, 2)` |
| JavaScript | `h3.kRingDistances(h3Index, k)` | `const rings = h3.kRingDistances(cell, 2);` |
| Java | `List<List<Long>> kRingDistances(long h3, int k)` | `List<List<Long>> rings = h3.kRingDistances(cell, 2);` |
| Go | `func KRingDistances(h H3Index, k int) [][]H3Index` | `rings := h3.KRingDistances(cell, 2)` |

### Get Hex Ring

Returns all cells at exactly distance k from the origin cell.

| Language | Syntax | Example |
|----------|--------|---------|
| C | `int h3_hex_ring(H3Index origin, int k, H3Index *out)` | `H3Index ring[MAX_SIZE]; h3_hex_ring(cell, 1, ring);` |
| Python | `h3.hex_ring(h3_index, k)` | `ring = h3.hex_ring(cell, 1)` |
| JavaScript | `h3.hexRing(h3Index, k)` | `const ring = h3.hexRing(cell, 1);` |
| Java | `List<Long> hexRing(long h3, int k)` | `List<Long> ring = h3.hexRing(cell, 1);` |
| Go | `func HexRing(h H3Index, k int) []H3Index` | `ring := h3.HexRing(cell, 1)` |

### Get H3 Distance

Returns the grid distance between two H3 cells.

| Language | Syntax | Example |
|----------|--------|---------|
| C | `int h3_h3_distance(H3Index a, H3Index b)` | `int distance = h3_h3_distance(cell1, cell2);` |
| Python | `h3.h3_distance(origin, destination)` | `distance = h3.h3_distance(cell1, cell2)` |
| JavaScript | `h3.h3Distance(origin, destination)` | `const distance = h3.h3Distance(cell1, cell2);` |
| Java | `int h3Distance(long a, long b)` | `int distance = h3.h3Distance(cell1, cell2);` |
| Go | `func H3Distance(a, b H3Index) int` | `distance := h3.H3Distance(cell1, cell2)` |

## Polygon Operations

### Polygon to H3 Cells

Fills a polygon with H3 cells at the specified resolution.

| Language | Syntax | Example |
|----------|--------|---------|
| C | `int h3_polyfill(const GeoPolygon *polygon, int res, H3Index *out)` | `H3Index cells[MAX_SIZE]; h3_polyfill(&polygon, 9, cells);` |
| Python | `h3.polyfill(polygon, resolution, geo_json=False)` | `cells = h3.polyfill(polygon, 9)` |
| JavaScript | `h3.polyfill(polygon, resolution, geoJson)` | `const cells = h3.polyfill(polygon, 9, true);` |
| Java | `List<Long> polyfill(List<GeoCoord> points, List<List<GeoCoord>> holes, int res)` | `List<Long> cells = h3.polyfill(polygon, holes, 9);` |
| Go | `func Polyfill(polygon [][]float64, holes [][][]float64, res int) []H3Index` | `cells := h3.Polyfill(polygon, holes, 9)` |

### H3Set to Polygon

Converts a set of H3 cells to a polygon (or MultiPolygon).

| Language | Syntax | Example |
|----------|--------|---------|
| C | `int h3_h3_set_to_linked_geo(const H3Index *h3Set, const int numHexes, LinkedGeoPolygon *out)` | `LinkedGeoPolygon polygon; h3_h3_set_to_linked_geo(cells, cellCount, &polygon);` |
| Python | `h3.h3_set_to_multi_polygon(h3_set, geo_json=False)` | `polygon = h3.h3_set_to_multi_polygon(cells)` |
| JavaScript | `h3.h3SetToMultiPolygon(h3Set, geoJson)` | `const polygon = h3.h3SetToMultiPolygon(cells, true);` |
| Java | `List<List<List<GeoCoord>>> h3SetToMultiPolygon(Collection<Long> h3Indices)` | `List<List<List<GeoCoord>>> polygon = h3.h3SetToMultiPolygon(cells);` |
| Go | `func H3SetToMultiPolygon(h3Set []H3Index, geoJSON bool) [][][]float64` | `polygon := h3.H3SetToMultiPolygon(cells, true)` |

## Utility Functions

### Compact and Uncompact

Compacts a set of cells to the highest resolution possible while preserving coverage.

| Language | Syntax | Example |
|----------|--------|---------|
| C | `int h3_compact(const H3Index *h3Set, H3Index *compactedSet, const int numHexes)` | `H3Index compacted[MAX_SIZE]; h3_compact(cells, compacted, cellCount);` |
| Python | `h3.compact(h3_set)` | `compacted = h3.compact(cells)` |
| JavaScript | `h3.compact(h3Set)` | `const compacted = h3.compact(cells);` |
| Java | `List<Long> compact(Collection<Long> h3Indices)` | `List<Long> compacted = h3.compact(cells);` |
| Go | `func Compact(h3Set []H3Index) []H3Index` | `compacted := h3.Compact(cells)` |

Uncompacts a set of cells to the specified resolution.

| Language | Syntax | Example |
|----------|--------|---------|
| C | `int h3_uncompact(const H3Index *compactedSet, const int numCompacted, H3Index *h3Set, const int maxHexes, const int res)` | `H3Index uncompacted[MAX_SIZE]; h3_uncompact(compacted, compactedCount, uncompacted, MAX_SIZE, 10);` |
| Python | `h3.uncompact(h3_set, resolution)` | `uncompacted = h3.uncompact(compacted, 10)` |
| JavaScript | `h3.uncompact(compactedSet, resolution)` | `const uncompacted = h3.uncompact(compacted, 10);` |
| Java | `List<Long> uncompact(Collection<Long> h3Indices, int res)` | `List<Long> uncompacted = h3.uncompact(compacted, 10);` |
| Go | `func Uncompact(compacted []H3Index, res int) []H3Index` | `uncompacted := h3.Uncompact(compacted, 10)` |

### Area and Edge Length

Calculates the area of an H3 cell in square kilometers or square meters.

| Language | Syntax | Example |
|----------|--------|---------|
| C | `double h3_cell_area_km2(H3Index h3)` | `double area = h3_cell_area_km2(cell);` |
| Python | `h3.cell_area(h3_index, unit='km2')` | `area = h3.cell_area(cell, unit='km2')` |
| JavaScript | `h3.cellArea(h3Index, unit)` | `const area = h3.cellArea(cell, 'km2');` |
| Java | `double cellArea(long h3, AreaUnit unit)` | `double area = h3.cellArea(cell, AreaUnit.km2);` |
| Go | `func CellArea(h H3Index, unit string) float64` | `area := h3.CellArea(cell, "km2")` |

Calculates the length of a cell edge in kilometers or meters.

| Language | Syntax | Example |
|----------|--------|---------|
| C | `double h3_edge_length_km(H3Index h3)` | `double length = h3_edge_length_km(cell);` |
| Python | `h3.edge_length(h3_index, unit='km')` | `length = h3.edge_length(cell, unit='km')` |
| JavaScript | `h3.edgeLength(h3Index, unit)` | `const length = h3.edgeLength(cell, 'km');` |
| Java | `double edgeLength(long h3, LengthUnit unit)` | `double length = h3.edgeLength(cell, LengthUnit.km);` |
| Go | `func EdgeLength(h H3Index, unit string) float64` | `length := h3.EdgeLength(cell, "km")` |

## Verification Functions

### Is Valid Cell

Checks if an H3 index is valid.

| Language | Syntax | Example |
|----------|--------|---------|
| C | `int h3_h3_is_valid(H3Index h3)` | `bool isValid = h3_h3_is_valid(cell);` |
| Python | `h3.h3_is_valid(h3_index)` | `is_valid = h3.h3_is_valid(cell)` |
| JavaScript | `h3.h3IsValid(h3Index)` | `const isValid = h3.h3IsValid(cell);` |
| Java | `boolean h3IsValid(long h3)` | `boolean isValid = h3.h3IsValid(cell);` |
| Go | `func H3IsValid(h H3Index) bool` | `isValid := h3.H3IsValid(cell)` |

### Are Neighbors

Checks if two H3 cells are neighbors.

| Language | Syntax | Example |
|----------|--------|---------|
| C | `int h3_h3_indexes_are_neighbors(H3Index a, H3Index b)` | `bool areNeighbors = h3_h3_indexes_are_neighbors(cell1, cell2);` |
| Python | `h3.h3_indexes_are_neighbors(origin, destination)` | `are_neighbors = h3.h3_indexes_are_neighbors(cell1, cell2)` |
| JavaScript | `h3.h3IndexesAreNeighbors(origin, destination)` | `const areNeighbors = h3.h3IndexesAreNeighbors(cell1, cell2);` |
| Java | `boolean h3IndexesAreNeighbors(long a, long b)` | `boolean areNeighbors = h3.h3IndexesAreNeighbors(cell1, cell2);` |
| Go | `func H3IndexesAreNeighbors(origin, destination H3Index) bool` | `areNeighbors := h3.H3IndexesAreNeighbors(cell1, cell2)` |

### Is Pentagon

Checks if an H3 cell is a pentagon.

| Language | Syntax | Example |
|----------|--------|---------|
| C | `int h3_h3_is_pentagon(H3Index h3)` | `bool isPentagon = h3_h3_is_pentagon(cell);` |
| Python | `h3.h3_is_pentagon(h3_index)` | `is_pentagon = h3.h3_is_pentagon(cell)` |
| JavaScript | `h3.h3IsPentagon(h3Index)` | `const isPentagon = h3.h3IsPentagon(cell);` |
| Java | `boolean h3IsPentagon(long h3)` | `boolean isPentagon = h3.h3IsPentagon(cell);` |
| Go | `func H3IsPentagon(h H3Index) bool` | `isPentagon := h3.H3IsPentagon(cell)` |

## Database Extensions

### PostgreSQL (h3-pg)

The h3-pg extension provides H3 functions in PostgreSQL:

```sql
-- Point to H3 cell
SELECT h3_geo_to_h3(37.7749, -122.4194, 9);

-- H3 cell to center point
SELECT h3_to_geo('8928308280fffff');

-- H3 cell to boundary
SELECT h3_to_geo_boundary('8928308280fffff');

-- Get K-Ring
SELECT h3_k_ring('8928308280fffff', 1);

-- Polyfill
SELECT h3_polyfill(
  ST_GeomFromText('POLYGON((-122.4089 37.813, -122.3986 37.8132, -122.3987 37.8027, -122.4089 37.813))'),
  9
);
```

### BigQuery (UDFs)

Example H3 UDFs for Google BigQuery:

```sql
-- Point to H3 cell (requires JavaScript UDF)
SELECT h3.geoToH3(37.7749, -122.4194, 9) AS h3_index;

-- H3 operations via BQ JS UDFs
SELECT 
  h3.h3ToParent(h3_index, 8) AS parent,
  h3.h3GetResolution(h3_index) AS resolution,
  h3.h3IsValid(h3_index) AS is_valid
FROM your_table;
```

## Complete Code Examples

### Basic H3 Operations (Python)

```python
import h3
import folium

# Convert a point to H3 cell
lat, lng = 37.7749, -122.4194
resolution = 9
h3_index = h3.geo_to_h3(lat, lng, resolution)
print(f"H3 Index: {h3_index}")

# Get the center point of the cell
center_lat, center_lng = h3.h3_to_geo(h3_index)
print(f"Center: {center_lat}, {center_lng}")

# Get the boundary of the cell
boundary = h3.h3_to_geo_boundary(h3_index)
print(f"Boundary vertices: {len(boundary)}")

# Get the parent cell at resolution 7
parent = h3.h3_to_parent(h3_index, 7)
print(f"Parent: {parent}")

# Get the 7 children cells at resolution 10
children = h3.h3_to_children(h3_index, 10)
print(f"Number of children: {len(children)}")

# Get neighbors (k-ring with k=1)
neighbors = h3.k_ring(h3_index, 1)
print(f"Neighbors count: {len(neighbors)}")

# Calculate grid distance to another cell
another_cell = h3.geo_to_h3(lat + 0.01, lng + 0.01, resolution)
distance = h3.h3_distance(h3_index, another_cell)
print(f"Grid distance: {distance}")

# Visualize with Folium
m = folium.Map(location=[lat, lng], zoom_start=13)

# Add the main cell
boundary_points = [(p[0], p[1]) for p in h3.h3_to_geo_boundary(h3_index)]
folium.Polygon(
    locations=boundary_points,
    color='blue',
    fill=True,
    fill_color='blue',
    fill_opacity=0.4,
    popup=f"H3 Index: {h3_index}"
).add_to(m)

# Add the neighbors
for neighbor in neighbors:
    if neighbor != h3_index:  # Skip the center cell
        neighbor_boundary = [(p[0], p[1]) for p in h3.h3_to_geo_boundary(neighbor)]
        folium.Polygon(
            locations=neighbor_boundary,
            color='red',
            fill=True,
            fill_color='red',
            fill_opacity=0.2,
            popup=f"Neighbor: {neighbor}"
        ).add_to(m)

# Save to HTML
m.save('h3_cells.html')
```

### Polyfill and Compaction (JavaScript)

```javascript
const h3 = require('h3-js');
const fs = require('fs');

// Define a polygon (GeoJSON format)
const polygon = {
  type: 'Polygon',
  coordinates: [[
    [-122.4089, 37.813],
    [-122.3986, 37.8132],
    [-122.3987, 37.8027],
    [-122.4089, 37.813]
  ]]
};

// Fill the polygon with hexagons at resolution 9
const hexagons = h3.polyfill(polygon, 9, true);
console.log(`Generated ${hexagons.length} hexagons`);

// Compact the hexagons (use mixed resolutions)
const compacted = h3.compact(hexagons);
console.log(`Compacted to ${compacted.length} mixed-resolution hexagons`);

// Convert back to GeoJSON for visualization
const features = [];

// Add the original polygon
features.push({
  type: 'Feature',
  properties: { type: 'original' },
  geometry: polygon
});

// Add the compacted hexagons
for (const h3Index of compacted) {
  const resolution = h3.h3GetResolution(h3Index);
  const boundary = h3.h3ToGeoBoundary(h3Index, true);
  
  features.push({
    type: 'Feature',
    properties: { 
      h3Index,
      resolution,
      type: 'hexagon'
    },
    geometry: {
      type: 'Polygon',
      coordinates: [boundary]
    }
  });
}

// Save as GeoJSON
const geojson = {
  type: 'FeatureCollection',
  features
};

fs.writeFileSync('h3_polyfill.geojson', JSON.stringify(geojson, null, 2));
```

## Language-specific Resources

For more detailed information about the API in each language, refer to:

- **C Library**: [H3 Core API](https://h3geo.org/docs/api/indexing)
- **Python**: [h3-py Documentation](https://h3geo.org/docs/binding/python)
- **JavaScript**: [h3-js Documentation](https://h3geo.org/docs/binding/javascript)
- **Java**: [h3-java Documentation](https://h3geo.org/docs/binding/java)
- **Go**: [h3-go Documentation](https://github.com/uber/h3-go)
- **PostgreSQL**: [h3-pg Documentation](https://github.com/bytesandbrains/h3-pg)

## Function Categories Reference

| Category | Description | Key Functions |
|----------|-------------|--------------|
| Indexing | Convert between coordinates and H3 indices | `geo_to_h3`, `h3_to_geo`, `h3_to_geo_boundary` |
| Hierarchy | Navigate the H3 hierarchy | `h3_to_parent`, `h3_to_children`, `h3_get_resolution` |
| Traversal | Traverse the H3 grid | `k_ring`, `hex_ring`, `h3_distance` |
| Regions | Work with collections of H3 cells | `polyfill`, `h3_set_to_multi_polygon` |
| Optimization | Optimize H3 indices | `compact`, `uncompact` |
| Inspection | Inspect H3 indices | `h3_is_valid`, `h3_is_pentagon` |
| Metrics | Calculate metrics for H3 indices | `cell_area`, `edge_length` | 