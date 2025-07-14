# H3 Code Examples

This document provides practical code examples for common H3 operations across various programming languages.

## Basic Indexing Operations

### Python

```python
import h3

# Convert lat/lng to H3 cell
lat, lng = 37.7749, -122.4194  # San Francisco
resolution = 9
h3_index = h3.latlng_to_cell(lat, lng, resolution)
print(f"H3 index: {h3_index}")  # 8928308280fffff

# Convert H3 cell to lat/lng (center point)
center_lat, center_lng = h3.cell_to_latlng(h3_index)
print(f"Center: {center_lat}, {center_lng}")

# Get the boundary of an H3 cell
boundary = h3.cell_to_latlng_boundary(h3_index)
print(f"Boundary: {boundary}")  # List of [lat, lng] coordinates
```

### JavaScript

```javascript
const h3 = require('h3-js');

// Convert lat/lng to H3 cell
const lat = 37.7749;
const lng = -122.4194;
const resolution = 9;
const h3Index = h3.geoToH3(lat, lng, resolution);
console.log(`H3 index: ${h3Index}`);  // 8928308280fffff

// Convert H3 cell to lat/lng (center point)
const [centerLat, centerLng] = h3.h3ToGeo(h3Index);
console.log(`Center: ${centerLat}, ${centerLng}`);

// Get the boundary of an H3 cell
const boundary = h3.h3ToGeoBoundary(h3Index);
console.log(`Boundary:`, boundary);  // Array of [lat, lng] coordinates
```

### Java

```java
import com.uber.h3core.H3Core;
import com.uber.h3core.util.GeoCoord;
import java.util.List;

public class H3Example {
    public static void main(String[] args) throws Exception {
        H3Core h3 = H3Core.newInstance();
        
        // Convert lat/lng to H3 cell
        double lat = 37.7749;
        double lng = -122.4194;
        int resolution = 9;
        String h3Index = h3.geoToH3Address(lat, lng, resolution);
        System.out.println("H3 index: " + h3Index);  // 8928308280fffff
        
        // Convert H3 cell to lat/lng (center point)
        GeoCoord center = h3.h3ToGeo(h3Index);
        System.out.println("Center: " + center.lat + ", " + center.lng);
        
        // Get the boundary of an H3 cell
        List<GeoCoord> boundary = h3.h3ToGeoBoundary(h3Index);
        System.out.println("Boundary points: " + boundary.size());
    }
}
```

## Hierarchical Operations

### Python

```python
import h3

# Generate an H3 index
h3_index = h3.latlng_to_cell(37.7749, -122.4194, 9)  # Resolution 9

# Get the parent at resolution 7
parent = h3.cell_to_parent(h3_index, 7)
print(f"Parent: {parent}")

# Get all children at resolution 10
children = h3.cell_to_children(h3_index, 10)
print(f"Number of children: {len(children)}")  # Approximately 7

# Get the resolution of an H3 index
resolution = h3.get_resolution(h3_index)
print(f"Resolution: {resolution}")  # 9
```

### JavaScript

```javascript
const h3 = require('h3-js');

// Generate an H3 index
const h3Index = h3.geoToH3(37.7749, -122.4194, 9);  // Resolution 9

// Get the parent at resolution 7
const parent = h3.h3ToParent(h3Index, 7);
console.log(`Parent: ${parent}`);

// Get all children at resolution 10
const children = h3.h3ToChildren(h3Index, 10);
console.log(`Number of children: ${children.length}`);  // Approximately 7

// Get the resolution of an H3 index
const resolution = h3.h3GetResolution(h3Index);
console.log(`Resolution: ${resolution}`);  // 9
```

## Neighborhood Operations

### Python

```python
import h3

# Generate an H3 index
h3_index = h3.latlng_to_cell(37.7749, -122.4194, 9)

# Get all neighbors within 1 step (k-ring)
neighbors = h3.grid_disk(h3_index, 1)
print(f"Number of cells in 1-ring: {len(neighbors)}")  # 7 (including origin)

# Get a ring of cells at exactly distance 2
ring = h3.grid_ring_unsafe(h3_index, 2)
print(f"Number of cells in 2-ring: {len(ring)}")  # 12

# Calculate grid distance between two indexes
other_index = h3.latlng_to_cell(37.7850, -122.4050, 9)
distance = h3.grid_distance(h3_index, other_index)
print(f"Grid distance: {distance}")
```

### JavaScript

```javascript
const h3 = require('h3-js');

// Generate an H3 index
const h3Index = h3.geoToH3(37.7749, -122.4194, 9);

// Get all neighbors within 1 step (k-ring)
const neighbors = h3.kRing(h3Index, 1);
console.log(`Number of cells in 1-ring: ${neighbors.length}`);  // 7 (including origin)

// Get a ring of cells at exactly distance 2
const ring = h3.hexRing(h3Index, 2);
console.log(`Number of cells in 2-ring: ${ring.length}`);  // 12

// Calculate grid distance between two indexes
const otherIndex = h3.geoToH3(37.7850, -122.4050, 9);
const distance = h3.h3Distance(h3Index, otherIndex);
console.log(`Grid distance: ${distance}`);
```

## Polygon Operations

### Python

```python
import h3

# Define a polygon (CCW is required)
polygon = {
    'type': 'Polygon',
    'coordinates': [[
        [-122.4089, 37.813],
        [-122.3986, 37.8132],
        [-122.3987, 37.8027],
        [-122.4089, 37.813]
    ]]
}

# Fill the polygon with hexagons
hexagons = h3.polygon_to_cells(polygon, 9, geo_json=True)
print(f"Number of hexagons: {len(hexagons)}")

# Convert H3 cells back to a polygon
cells_to_polygon = [hexagons[0], hexagons[1], hexagons[2]]
multi_polygon = h3.cells_to_h3shape(cells_to_polygon, geo_json=True)
print(f"Multi-polygon structure: {len(multi_polygon)} polygon(s)")
```

### JavaScript

```javascript
const h3 = require('h3-js');

// Define a polygon
const polygon = {
  type: 'Polygon',
  coordinates: [[
    [-122.4089, 37.813],
    [-122.3986, 37.8132],
    [-122.3987, 37.8027],
    [-122.4089, 37.813]
  ]]
};

// Fill the polygon with hexagons
const hexagons = h3.polygon_to_cells(polygon, 9, true);
console.log(`Number of hexagons: ${hexagons.length}`);

// Convert H3 cells back to a polygon
const cellsToPolygon = [hexagons[0], hexagons[1], hexagons[2]];
const multiPolygon = h3.h3SetToMultiPolygon(cellsToPolygon, true);
console.log(`Multi-polygon structure: ${multiPolygon.length} polygon(s)`);
```

## Compact and Uncompact_cells

### Python

```python
import h3

# Define a polygon
polygon = {
    'type': 'Polygon',
    'coordinates': [[
        [-122.4089, 37.813],
        [-122.3986, 37.8132],
        [-122.3987, 37.8027],
        [-122.4089, 37.813]
    ]]
}

# Fill the polygon with hexagons at fine resolution
hexagons = h3.polygon_to_cells(polygon, 10, geo_json=True)
print(f"Original hexagons at res 10: {len(hexagons)}")

# Compact the set of hexagons (use mixed resolutions)
compact_cellsed = h3.compact_cells_cells(hexagons)
print(f"Compacted hexagons: {len(compact_cellsed)}")

# Count cells by resolution
by_resolution = {}
for h in compact_cellsed:
    res = h3.get_resolution(h)
    by_resolution[res] = by_resolution.get(res, 0) + 1
print(f"Cells by resolution: {by_resolution}")

# Uncompact_cells back to resolution 10
uncompact_cells_cellsed = h3.uncompact_cells_cells_cells(compact_cellsed, 10)
print(f"Uncompact_cellsed cells: {len(uncompact_cells_cellsed)}")
```

### JavaScript

```javascript
const h3 = require('h3-js');

// Define a polygon
const polygon = {
  type: 'Polygon',
  coordinates: [[
    [-122.4089,, 37.813],
    [-122.3986, 37.8132],
    [-122.3987, 37.8027],
    [-122.4089, 37.813]
  ]]
};

// Fill the polygon with hexagons at fine resolution
const hexagons = h3.polygon_to_cells(polygon, 10, true);
console.log(`Original hexagons at res 10: ${hexagons.length}`);

// Compact the set of hexagons (use mixed resolutions)
const compact_cellsed = h3.compact_cells_cells(hexagons);
console.log(`Compacted hexagons: ${compact_cellsed.length}`);

// Count cells by resolution
const byResolution = {};
for (const h of compact_cellsed) {
  const res = h3.h3GetResolution(h);
  byResolution[res] = (byResolution[res] || 0) + 1;
}
console.log(`Cells by resolution:`, byResolution);

// Uncompact_cells back to resolution 10
const uncompact_cells_cellsed = h3.uncompact_cells_cells_cells(compact_cellsed, 10);
console.log(`Uncompact_cellsed cells: ${uncompact_cells_cellsed.length}`);
```

## Integration Examples

### Visualization with Folium (Python)

```python
import h3
import folium

# Generate a central H3 cell
center_lat, center_lng = 37.7749, -122.4194
resolution = 9
h3_index = h3.latlng_to_cell(center_lat, center_lng, resolution)

# Get k-ring of neighbors
k = 2
neighbors = h3.grid_disk(h3_index, k)

# Create map centered on central cell
m = folium.Map(location=[center_lat, center_lng], zoom_start=13)

# Add central cell in blue
central_boundary = h3.cell_to_latlng_boundary(h3_index)
folium.Polygon(
    locations=[(p[0], p[1]) for p in central_boundary],
    color='blue',
    fill=True,
    fill_color='blue',
    fill_opacity=0.4,
    popup=f"Central cell: {h3_index}"
).add_to(m)

# Add neighbors in red with decreasing opacity by distance
for neighbor in neighbors:
    if neighbor != h3_index:  # Skip central cell
        distance = h3.grid_distance(h3_index, neighbor)
        opacity = 0.6 / distance  # Decrease opacity with distance
        
        neighbor_boundary = h3.cell_to_latlng_boundary(neighbor)
        folium.Polygon(
            locations=[(p[0], p[1]) for p in neighbor_boundary],
            color='red',
            fill=True,
            fill_color='red',
            fill_opacity=opacity,
            popup=f"Neighbor: {neighbor}, Distance: {distance}"
        ).add_to(m)

# Save map to HTML file
m.save('h3_neighbors.html')
```

### H3 with GeoJSON in JavaScript (Browser)

```html
<!DOCTYPE html>
<html>
<head>
    <title>H3 Map Example</title>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
    <script src="https://unpkg.com/h3-js@3.7.2/dist/h3-js.umd.js"></script>
    <style>
        #map { height: 600px; }
    </style>
</head>
<body>
    <div id="map"></div>
    <script>
        // Initialize map
        const map = L.map('map').setView([37.7749, -122.4194], 13);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; OpenStreetMap contributors'
        }).addTo(map);
        
        // Generate a central H3 cell
        const centerLat = 37.7749;
        const centerLng = -122.4194;
        const resolution = 9;
        const h3Index = h3.geoToH3(centerLat, centerLng, resolution);
        
        // Get k-ring of neighbors
        const k = 2;
        const neighbors = h3.kRing(h3Index, k);
        
        // Create GeoJSON features
        const features = [];
        
        // Add all cells to GeoJSON
        neighbors.forEach(cellId => {
            const isPentagon = h3.h3IsPentagon(cellId);
            const distance = h3.h3Distance(h3Index, cellId);
            const isCentral = cellId === h3Index;
            
            const vertices = h3.h3ToGeoBoundary(cellId, true);
            
            features.push({
                type: 'Feature',
                properties: {
                    h3Index: cellId,
                    resolution: h3.h3GetResolution(cellId),
                    isCentral,
                    distance,
                    isPentagon
                },
                geometry: {
                    type: 'Polygon',
                    coordinates: [vertices]
                }
            });
        });
        
        // Add GeoJSON to map with styling
        L.geoJSON(features, {
            style: function(feature) {
                const props = feature.properties;
                if (props.isCentral) {
                    return { color: 'blue', fillColor: 'blue', fillOpacity: 0.4, weight: 2 };
                } else {
                    // Decrease opacity with distance
                    const opacity = 0.6 / props.distance;
                    return { color: 'red', fillColor: 'red', fillOpacity: opacity, weight: 1 };
                }
            },
            onEachFeature: function(feature, layer) {
                const props = feature.properties;
                layer.bindPopup(`
                    <b>H3 Index:</b> ${props.h3Index}<br>
                    <b>Resolution:</b> ${props.resolution}<br>
                    <b>Distance:</b> ${props.distance}<br>
                    <b>Pentagon:</b> ${props.isPentagon ? 'Yes' : 'No'}
                `);
            }
        }).addTo(map);
    </script>
</body>
</html>
```

### PostgreSQL with H3 Extension

```sql
-- Ensure h3-pg extension is installed
CREATE EXTENSION IF NOT EXISTS h3;

-- Create a table with H3 indexes
CREATE TABLE IF NOT EXISTS poi_locations (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    h3_index H3INDEX NOT NULL,
    resolution INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert some sample data
INSERT INTO poi_locations (name, h3_index, resolution)
VALUES 
    ('Ferry Building', h3_latlng_to_cell(37.7956, -122.3934, 9), 9),
    ('Golden Gate Park', h3_latlng_to_cell(37.7694, -122.4862, 9), 9),
    ('Twin Peaks', h3_latlng_to_cell(37.7544, -122.4477, 9), 9);

-- Find POIs within 5 cells of a location
WITH center AS (
    SELECT h3_latlng_to_cell(37.7749, -122.4194, 9) AS h3_index
)
SELECT 
    p.name,
    p.h3_index,
    cell_to_latlng(p.h3_index) AS center_point,
    grid_distance(center.h3_index, p.h3_index) AS distance
FROM 
    poi_locations p, 
    center
WHERE 
    grid_distance(center.h3_index, p.h3_index) <= 5
ORDER BY 
    distance;

-- Find POIs within a polygon
WITH area AS (
    SELECT ST_GeomFromText('POLYGON((-122.51 37.77, -122.43 37.81, -122.38 37.77, -122.35 37.73, -122.51 37.77))') AS geom
)
SELECT 
    p.name,
    p.h3_index,
    cell_to_latlng(p.h3_index) AS center_point
FROM 
    poi_locations p,
    area
WHERE 
    ST_Contains(area.geom, ST_SetSRID(ST_Point(cell_to_latlng(p.h3_index)[1], cell_to_latlng(p.h3_index)[0]), 4326));
```

## Utility Functions

### Python

```python
import h3

# Calculate the area of a cell
h3_index = h3.latlng_to_cell(37.7749, -122.4194, 9)

# Area in square kilometers
area_km2 = h3.cell_area(h3_index, unit='km^2')
print(f"Cell area: {area_km2:.6f} km²")

# Area in square meters
area_m2 = h3.cell_area(h3_index, unit='m^2')
print(f"Cell area: {area_m2:.2f} m²")

# Edge length in kilometers
edge_km = h3.edge_length(h3_index, unit='km')
print(f"Edge length: {edge_km:.6f} km")

# Edge length in meters
edge_m = h3.edge_length(h3_index, unit='m')
print(f"Edge length: {edge_m:.2f} m")

# Check if an index is valid
is_valid = h3.is_valid_cell(h3_index)
print(f"Is valid: {is_valid}")

# Check if an index is a pentagon
is_pentagon = h3.is_pentagon(h3_index)
print(f"Is pentagon: {is_pentagon}")

# Check if two cells are neighbors
neighbor = h3.grid_ring_unsafe(h3_index, 1)[0]  # Get one neighbor
are_neighbors = h3.are_neighbor_cells(h3_index, neighbor)
print(f"Are neighbors: {are_neighbors}")
```

### JavaScript

```javascript
const h3 = require('h3-js');

// Calculate the area of a cell
const h3Index = h3.geoToH3(37.7749, -122.4194, 9);

// Area in square kilometers
const areaKm2 = h3.cellArea(h3Index, 'km2');
console.log(`Cell area: ${areaKm2.toFixed(6)} km²`);

// Area in square meters
const areaM2 = h3.cellArea(h3Index, 'm2');
console.log(`Cell area: ${areaM2.toFixed(2)} m²`);

// Edge length in kilometers
const edgeKm = h3.edgeLength(h3Index, 'km');
console.log(`Edge length: ${edgeKm.toFixed(6)} km`);

// Edge length in meters
const edgeM = h3.edgeLength(h3Index, 'm');
console.log(`Edge length: ${edgeM.toFixed(2)} m`);

// Check if an index is valid
const isValid = h3.h3IsValid(h3Index);
console.log(`Is valid: ${isValid}`);

// Check if an index is a pentagon
const isPentagon = h3.h3IsPentagon(h3Index);
console.log(`Is pentagon: ${isPentagon}`);

// Check if two cells are neighbors
const neighbor = h3.hexRing(h3Index, 1)[0];  // Get one neighbor
const areNeighbors = h3.h3IndexesAreNeighbors(h3Index, neighbor);
console.log(`Are neighbors: ${areNeighbors}`);
```

## Performance Tips

1. **Use compact_cells/uncompact_cells_cells** for efficiently representing regions with mixed resolutions
2. **Pre-compute** H3 indexes for static geometries
3. **Choose appropriate resolution** to balance precision and performance
4. **Cache results** of computationally expensive operations
5. **Batch operations** when possible instead of processing cells individually
6. **Use grid distances** instead of geographic distances when appropriate
7. **Consider using specialized database extensions** for large-scale operations

## References

- [H3 Documentation](https://h3geo.org/docs/)
- [Python API Reference](https://h3geo.org/docs/api/python)
- [JavaScript API Reference](https://h3geo.org/docs/api/javascript)
- [Java API Reference](https://h3geo.org/docs/api/java)
- [H3-pg PostgreSQL Extension](https://github.com/zachasme/h3-pg) 