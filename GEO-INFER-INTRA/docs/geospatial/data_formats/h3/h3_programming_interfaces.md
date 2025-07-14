# H3 Programming Interfaces

This document provides a comprehensive overview of H3 programming interfaces across different languages, enabling developers to integrate H3 functionality into their applications.

## Core C Library

The H3 Core Library is implemented in C, with its public API defined in `h3api.h`. This serves as the foundation for all language bindings.

### Installation

```bash
# From source
git clone https://github.com/uber/h3.git
cd h3
mkdir build
cd build
cmake ..
make
make install
```

### Basic Usage

```c
#include <h3/h3api.h>
#include <stdio.h>

int main() {
    // Convert lat/lng to H3 index
    LatLng location;
    location.lat = degsToRads(37.7749);
    location.lng = degsToRads(-122.4194);
    
    H3Index h3Index = latLngToCell(&location, 9);
    char h3String[17];
    h3ToString(h3Index, h3String, sizeof(h3String));
    
    printf("H3 index: %s\n", h3String);
    return 0;
}
```

### Key Functions

The C library provides over 120 API functions organized into several categories:

#### Indexing Functions

```c
// Convert coordinates to H3 index
H3Index latLngToCell(const LatLng *location, int resolution);

// Get the center coordinates of an H3 index
void cellToLatLng(H3Index h3, LatLng *center);

// Get the boundary of an H3 index
void cellToBoundary(H3Index h3, CellBoundary *boundary);
```

#### Hierarchical Operations

```c
// Get the parent of an H3 index at a specified resolution
H3Index cellToParent(H3Index h, int parentRes);

// Get the children of an H3 index at a specified resolution
int cellToChildren(H3Index h, int childRes, H3Index *children);

// Determine if one index is a descendant of another
int h3IsDescendant(H3Index h1, H3Index h2);
```

#### Traversal Functions

```c
// Get the neighbors of an H3 index
int cellToNeighbors(H3Index origin, H3Index *neighbors);

// Get all indices within k grid distance
int kRing(H3Index origin, int k, H3Index *out);

// Calculate the shortest path between two H3 indices
int h3Line(H3Index start, H3Index end, H3Index *out);
```

#### Region Operations

```c
// Fill a polygon with H3 cells
int polygonToCells(const GeoPolygon *polygon, int res, H3Index *out);

// Get the hexagons making up a specific ring at distance k
int hexRing(H3Index origin, int k, H3Index *out);
```

## Python Bindings (h3-py)

The [h3-py](https://github.com/uber/h3-py) package provides Python bindings for the H3 Core Library.

### Installation

```bash
pip install h3
```

### Basic Usage

```python
import h3

# Convert a lat/lng point to an H3 index
lat, lng = 37.7749, -122.4194  # San Francisco
h3_index = h3.latlng_to_cell(lat, lng, 9)
print(f"H3 index: {h3_index}")  # '8928308281fffff'

# Get the center coordinates of an H3 index
center_coords = h3.cell_to_latlng(h3_index)
print(f"Center: {center_coords}")  # (37.77671781098822, -122.41968744914311)

# Get the boundary of an H3 index
boundary = h3.cell_to_latlng_boundary(h3_index)
print(f"Boundary: {boundary}")  # List of (lat, lng) tuples
```

### Key Functions

Python function names generally follow a pattern of converting the camelCase C functions to snake_case:

#### Indexing Functions

```python
# Convert coordinates to H3 index
h3_index = h3.latlng_to_cell(lat, lng, resolution)

# Get the center coordinates of an H3 index
center = h3.cell_to_latlng(h3_index)

# Get the boundary of an H3 index
boundary = h3.cell_to_latlng_boundary(h3_index)
```

#### Hierarchical Operations

```python
# Get the parent of an H3 index
parent = h3.cell_to_parent(h3_index, parent_resolution)

# Get the children of an H3 index
children = h3.cell_to_children(h3_index, child_resolution)

# Compact a set of H3 indices
compact_cellsed = h3.compact_cells_cells_cells(h3_indices)

# Uncompact_cells a set of H3 indices
uncompact_cells_cellsed = h3.uncompact_cells_cells_cells_cells(h3_indices, resolution)
```

#### Traversal Functions

```python
# Get all indices within k distance
neighbors = h3.grid_disk(h3_index, k)

# Get indices within k distance as nested rings
nested_rings = h3.grid_disk_distances(h3_index, k)

# Calculate the grid distance between two indices
distance = h3.grid_distance(h3_index1, h3_index2)

# Get a line of indices between two points
line = h3.grid_path_cells(h3_index1, h3_index2)
```

#### Region Operations

```python
# Fill a polygon with H3 cells
cells = h3.polygon_to_cells(geo_json, resolution)

# Get the hexagons in a specific ring
ring = h3.grid_ring_unsafe(h3_index, k)
```

### NumPy Integration

The h3-py package provides vectorized operations for NumPy:

```python
import numpy as np
import h3.numpy as h3np

# Vectorized coordinate to H3 conversion
latlngs = np.array([
    [37.7749, -122.4194],
    [37.3382, -121.8863]
])
indices = h3np.latlng_to_cell(latlngs, 9)

# Vectorized H3 to coordinate conversion
centers = h3np.cell_to_latlng(indices)
```

### Pandas Integration

With the [h3-pandas](https://h3-pandas.readthedocs.io/) package:

```python
import pandas as pd
import h3pandas

# Create a DataFrame with geometry
df = pd.DataFrame({
    'lat': [37.7749, 37.3382],
    'lng': [-122.4194, -121.8863]
})

# Add H3 indices
df_with_h3 = df.h3.latlng_to_cell(lat_col='lat', lng_col='lng', resolution=9)

# Spatial aggregation
aggregated = df.h3.spatial_aggregate('value', resolution=7, operation='mean')
```

## JavaScript Bindings (h3-js)

The [h3-js](https://github.com/uber/h3-js) package provides JavaScript bindings for the H3 Core Library.

### Installation

```bash
# npm
npm install h3-js

# yarn
yarn add h3-js
```

### Basic Usage

```javascript
const h3 = require('h3-js');

// Convert a lat/lng point to an H3 index
const lat = 37.7749;
const lng = -122.4194;
const h3Index = h3.latLngToCell(lat, lng, 9);
console.log(`H3 index: ${h3Index}`);  // '8928308281fffff'

// Get the center coordinates of an H3 index
const center = h3.cellToLatLng(h3Index);
console.log(`Center: ${center}`);  // { lat: 37.77671781098822, lng: -122.41968744914311 }

// Get the boundary of an H3 index
const boundary = h3.cellToBoundary(h3Index);
console.log(`Boundary: ${boundary}`);  // Array of {lat, lng} objects
```

### Key Functions

JavaScript function names primarily use camelCase consistent with the C API:

#### Indexing Functions

```javascript
// Convert coordinates to H3 index
const h3Index = h3.latLngToCell(lat, lng, resolution);

// Get the center coordinates of an H3 index
const center = h3.cellToLatLng(h3Index);

// Get the boundary of an H3 index
const boundary = h3.cellToBoundary(h3Index);
```

#### Hierarchical Operations

```javascript
// Get the parent of an H3 index
const parent = h3.cellToParent(h3Index, parentResolution);

// Get the children of an H3 index
const children = h3.cellToChildren(h3Index, childResolution);

// Compact a set of H3 indices
const compact_cellsed = h3.compact_cells_cellsCells(h3Indices);

// Uncompact_cells a set of H3 indices
const uncompact_cells_cellsed = h3.uncompact_cells_cells_cellsCells(h3Indices, resolution);
```

#### Traversal Functions

```javascript
// Get all indices within k distance
const neighbors = h3.kRing(h3Index, k);

// Get indices within k distance as nested rings
const nestedRings = h3.kRingDistances(h3Index, k);

// Calculate the grid distance between two indices
const distance = h3.gridDistance(h3Index1, h3Index2);

// Get a line of indices between two points
const line = h3.gridPathCells(h3Index1, h3Index2);
```

#### Region Operations

```javascript
// Fill a polygon with H3 cells
const cells = h3.polygonToCells(geoJson.coordinates, resolution);

// Get the hexagons in a specific ring
const ring = h3.hexRing(h3Index, k);
```

### Integration with Mapping Libraries

#### Leaflet Integration

```javascript
// Function to convert H3 index to Leaflet polygon
function h3ToLeaflet(h3Index) {
    const boundary = h3.cellToBoundary(h3Index);
    return boundary.map(({lat, lng}) => [lat, lng]);
}

// Create Leaflet polygon for H3 cell
const h3Index = h3.latLngToCell(37.7749, -122.4194, 9);
const polygonCoords = h3ToLeaflet(h3Index);
const polygon = L.polygon(polygonCoords).addTo(map);
```

#### Mapbox GL Integration

```javascript
// Add H3 hexagons to Mapbox GL
const h3Indices = h3.kRing(h3.latLngToCell(37.7749, -122.4194, 9), 2);
const features = h3Indices.map(h3Index => {
    const boundary = h3.cellToBoundary(h3Index);
    return {
        type: 'Feature',
        properties: {
            h3Index: h3Index
        },
        geometry: {
            type: 'Polygon',
            coordinates: [boundary.map(({lat, lng}) => [lng, lat])]
        }
    };
});

map.addSource('h3-hexagons', {
    type: 'geojson',
    data: {
        type: 'FeatureCollection',
        features: features
    }
});

map.addLayer({
    id: 'h3-layer',
    type: 'fill',
    source: 'h3-hexagons',
    paint: {
        'fill-color': '#088',
        'fill-opacity': 0.5,
        'fill-outline-color': '#000'
    }
});
```

## Java Bindings (h3-java)

The [h3-java](https://github.com/uber/h3-java) package provides Java bindings for the H3 Core Library.

### Installation

```xml
<!-- Maven -->
<dependency>
    <groupId>com.uber</groupId>
    <artifactId>h3</artifactId>
    <version>4.1.1</version>
</dependency>
```

```groovy
// Gradle
implementation 'com.uber:h3:4.1.1'
```

### Basic Usage

```java
import com.uber.h3core.H3Core;
import com.uber.h3core.util.GeoCoord;

import java.io.IOException;
import java.util.List;

public class H3Example {
    public static void main(String[] args) throws IOException {
        // Initialize H3 Core
        H3Core h3 = H3Core.newInstance();
        
        // Convert lat/lng to H3 index
        double lat = 37.7749;
        double lng = -122.4194;
        String h3Index = h3.latLngToCell(lat, lng, 9);
        System.out.println("H3 index: " + h3Index);  // '8928308281fffff'
        
        // Get the center coordinates of an H3 index
        GeoCoord center = h3.cellToLatLng(h3Index);
        System.out.println("Center: " + center.lat + ", " + center.lng);
        
        // Get the boundary of an H3 index
        List<GeoCoord> boundary = h3.cellToBoundary(h3Index);
        System.out.println("Boundary: " + boundary);
    }
}
```

### Key Functions

Java method names follow a camelCase approach:

#### Indexing Functions

```java
// Convert coordinates to H3 index
String h3Index = h3.latLngToCell(lat, lng, resolution);

// Get the center coordinates of an H3 index
GeoCoord center = h3.cellToLatLng(h3Index);

// Get the boundary of an H3 index
List<GeoCoord> boundary = h3.cellToBoundary(h3Index);
```

#### Hierarchical Operations

```java
// Get the parent of an H3 index
String parent = h3.cellToParent(h3Index, parentResolution);

// Get the children of an H3 index
List<String> children = h3.cellToChildren(h3Index, childResolution);

// Compact a set of H3 indices
List<String> compact_cellsed = h3.compact_cells_cellsCells(h3Indices);

// Uncompact_cells a set of H3 indices
List<String> uncompact_cells_cellsed = h3.uncompact_cells_cells_cellsCells(h3Indices, resolution);
```

#### Traversal Functions

```java
// Get all indices within k distance
List<String> neighbors = h3.kRing(h3Index, k);

// Get indices within k distance as nested rings
List<List<String>> nestedRings = h3.kRingDistances(h3Index, k);

// Calculate the grid distance between two indices
int distance = h3.gridDistance(h3Index1, h3Index2);

// Get a line of indices between two points
List<String> line = h3.gridPathCells(h3Index1, h3Index2);
```

#### Region Operations

```java
// Fill a polygon with H3 cells
List<GeoCoord> polygon = // list of boundary coordinates
List<String> cells = h3.polygonToCells(polygon, holes, resolution);

// Get the hexagons in a specific ring
List<String> ring = h3.hexRing(h3Index, k);
```

### Integration with GIS Libraries

```java
import org.locationtech.jts.geom.Coordinate;
import org.locationtech.jts.geom.GeometryFactory;
import org.locationtech.jts.geom.Polygon;

// Convert H3 cell to JTS Polygon
public Polygon h3ToJtsPolygon(String h3Index, H3Core h3, GeometryFactory factory) {
    List<GeoCoord> boundary = h3.cellToBoundary(h3Index);
    Coordinate[] coordinates = new Coordinate[boundary.size() + 1];
    
    for (int i = 0; i < boundary.size(); i++) {
        GeoCoord coord = boundary.get(i);
        coordinates[i] = new Coordinate(coord.lng, coord.lat);
    }
    // Close the ring
    coordinates[boundary.size()] = coordinates[0];
    
    return factory.createPolygon(coordinates);
}
```

## Go Bindings (h3-go)

The [h3-go](https://github.com/uber/h3-go) package provides Go bindings for the H3 Core Library.

### Installation

```bash
go get github.com/uber/h3-go/v4
```

### Basic Usage

```go
package main

import (
    "fmt"
    "github.com/uber/h3-go/v4"
)

func main() {
    // Convert lat/lng to H3 index
    lat := 37.7749
    lng := -122.4194
    resolution := 9
    h3Index := h3.LatLngToCell(h3.LatLng{Lat: lat, Lng: lng}, resolution)
    fmt.Printf("H3 index: %#x\n", h3Index)
    
    // Get the center coordinates of an H3 index
    center := h3.CellToLatLng(h3Index)
    fmt.Printf("Center: %v\n", center)
    
    // Get the boundary of an H3 index
    boundary := h3.CellToBoundary(h3Index)
    fmt.Printf("Boundary: %v\n", boundary)
}
```

### Key Functions

Go function names follow the same camelCase convention as the C API:

#### Indexing Functions

```go
// Convert coordinates to H3 index
h3Index := h3.LatLngToCell(h3.LatLng{Lat: lat, Lng: lng}, resolution)

// Get the center coordinates of an H3 index
center := h3.CellToLatLng(h3Index)

// Get the boundary of an H3 index
boundary := h3.CellToBoundary(h3Index)
```

#### Hierarchical Operations

```go
// Get the parent of an H3 index
parent := h3.CellToParent(h3Index, parentResolution)

// Get the children of an H3 index
children := h3.CellToChildren(h3Index, childResolution)

// Compact a set of H3 indices
compact_cellsed := h3.CompactCells(h3Indices)

// Uncompact_cells a set of H3 indices
uncompact_cells_cellsed := h3.Uncompact_cellsCells(h3Indices, resolution)
```

#### Traversal Functions

```go
// Get all indices within k distance
neighbors := h3.KRing(h3Index, k)

// Calculate the grid distance between two indices
distance := h3.GridDistance(h3Index1, h3Index2)

// Get a line of indices between two points
line := h3.GridPathCells(h3Index1, h3Index2)
```

#### Region Operations

```go
// Fill a polygon with H3 cells
polygon := h3.Polygon{
    Exterior: []h3.LatLng{
        {Lat: 37.8036, Lng: -122.4089},
        {Lat: 37.7096, Lng: -122.4089},
        {Lat: 37.7096, Lng: -122.3599},
        {Lat: 37.8036, Lng: -122.3599},
        {Lat: 37.8036, Lng: -122.4089},
    },
}
cells := h3.PolygonToCells(polygon, resolution)

// Get the hexagons in a specific ring
ring := h3.HexRing(h3Index, k)
```

## R Bindings (h3r)

The [h3r](https://github.com/crazycapivara/h3-r) package provides R bindings for the H3 Core Library.

### Installation

```r
# From CRAN
install.packages("h3")

# From GitHub
devtools::install_github("crazycapivara/h3-r")
```

### Basic Usage

```r
library(h3)

# Convert lat/lng to H3 index
lat <- 37.7749
lng <- -122.4194
resolution <- 9
h3_index <- latlng_to_cell(lat, lng, resolution)
cat("H3 index:", h3_index, "\n")  # '8928308281fffff'

# Get the center coordinates of an H3 index
center <- cell_to_latlng(h3_index)
cat("Center:", center, "\n")

# Get the boundary of an H3 index
boundary <- cell_to_latlng_boundary(h3_index)
print(boundary)
```

### Key Functions

R function names follow the snake_case convention:

#### Indexing Functions

```r
# Convert coordinates to H3 index
h3_index <- latlng_to_cell(lat, lng, resolution)

# Get the center coordinates of an H3 index
center <- cell_to_latlng(h3_index)

# Get the boundary of an H3 index
boundary <- cell_to_latlng_boundary(h3_index)
```

#### Hierarchical Operations

```r
# Get the parent of an H3 index
parent <- h3_to_parent(h3_index, parent_resolution)

# Get the children of an H3 index
children <- h3_to_children(h3_index, child_resolution)

# Compact a set of H3 indices
compact_cellsed <- compact_cells_cells(h3_indices)

# Uncompact_cells a set of H3 indices
uncompact_cells_cellsed <- uncompact_cells_cells_cells(h3_indices, resolution)
```

#### Traversal Functions

```r
# Get all indices within k distance
neighbors <- grid_disk(h3_index, k)

# Calculate the grid distance between two indices
distance <- grid_distance(h3_index1, h3_index2)

# Get a line of indices between two points
line <- h3_line(h3_index1, h3_index2)
```

#### Integration with sf Package

```r
library(sf)
library(h3)
library(dplyr)

# Convert H3 cells to sf polygons
h3_to_sf <- function(h3_indices) {
  boundaries <- lapply(h3_indices, function(idx) {
    coords <- cell_to_latlng_boundary(idx)
    # Convert to polygon format and close the ring
    poly_coords <- rbind(coords, coords[1, ])
    st_polygon(list(poly_coords[, c("lng", "lat")]))
  })
  
  sf_obj <- st_sf(
    h3_index = h3_indices,
    geometry = st_sfc(boundaries, crs = 4326)
  )
  
  return(sf_obj)
}

# Example usage
indices <- grid_disk("8928308281fffff", 2)
sf_hexagons <- h3_to_sf(indices)

# Plot with ggplot2
library(ggplot2)
ggplot() +
  geom_sf(data = sf_hexagons, aes(fill = h3_index), alpha = 0.7) +
  theme_minimal()
```

## Additional Language Bindings

### .NET (H3.NET)

```csharp
using H3;
using H3.Model;

// Initialize H3 api
var h3Api = H3Api.Instance;

// Convert lat/lng to H3 index
var latLng = new LatLng(37.7749, -122.4194);
var h3Index = h3Api.LatLngToCell(latLng, 9);
Console.WriteLine($"H3 index: {h3Index}");

// Get the center coordinates of an H3 index
var center = h3Api.CellToLatLng(h3Index);
Console.WriteLine($"Center: {center.Lat}, {center.Lng}");

// Get the boundary of an H3 index
var boundary = h3Api.CellToBoundary(h3Index);
Console.WriteLine($"Boundary: {string.Join(", ", boundary)}");
```

### Ruby (h3_ruby)

```ruby
require 'h3'

# Convert lat/lng to H3 index
lat = 37.7749
lng = -122.4194
resolution = 9
h3_index = H3.ll_to_cell(lat, lng, resolution)
puts "H3 index: #{h3_index}"

# Get the center coordinates of an H3 index
center = H3.cell_to_ll(h3_index)
puts "Center: #{center}"

# Get the boundary of an H3 index
boundary = H3.cell_to_boundary(h3_index)
puts "Boundary: #{boundary}"
```

### Rust (h3ron)

```rust
use h3ron::H3Cell;
use h3ron::geo::{Coordinate, Point};

fn main() {
    // Convert lat/lng to H3 index
    let lat = 37.7749_f64;
    let lng = -122.4194_f64;
    let resolution = 9;
    let h3_index = H3Cell::from_coordinate(
        &Coordinate { x: lng, y: lat },
        resolution
    ).unwrap();
    println!("H3 index: {}", h3_index);
    
    // Get the center coordinates of an H3 index
    let center = h3_index.to_coordinate();
    println!("Center: {}, {}", center.y, center.x);
    
    // Get the boundary of an H3 index
    let boundary = h3_index.to_boundary();
    println!("Boundary: {:?}", boundary);
}
```

## Common API Patterns Across Languages

Despite language-specific variations, H3 bindings follow common patterns:

1. **Naming Conventions**: 
   - C, Java, Go, JavaScript: `camelCase` (e.g., `latLngToCell`)
   - Python, R: `snake_case` (e.g., `latlng_to_cell` or `lat_lng_to_cell`)

2. **Core Functionality**:
   - Converting between coordinates and indices
   - Working with hierarchical relationships
   - Traversing the grid
   - Processing geographical regions

3. **Data Structures**:
   - H3 indices are represented as hexadecimal strings in most high-level languages
   - Coordinates are typically represented as lat/lng pairs
   - Boundaries are collections of coordinates defining a polygon

4. **Memory Management**:
   - Low-level bindings handle allocation/deallocation of H3 resources
   - High-level bindings abstract memory management away

## Performance Considerations

When using H3 bindings, consider the following:

1. **Batch Operations**: Most bindings provide vectorized or batch operations that are more efficient than individual calls.

2. **Memory Overhead**: Some bindings create temporary objects which can impact performance for large-scale operations.

3. **Binding Overhead**: The C API will typically outperform higher-level language bindings for performance-critical applications.

4. **Language-Specific Optimizations**:
   - Python: Use NumPy vectorized operations whenever possible
   - JavaScript: Prefer array-based batch operations
   - Java: Use primitive arrays instead of collections for large datasets

## References

1. [H3 Core Library Documentation](https://h3geo.org/docs/core-library/overview/)
2. [h3-py: Python Bindings for H3](https://github.com/uber/h3-py)
3. [h3-js: JavaScript Bindings for H3](https://github.com/uber/h3-js)
4. [h3-java: Java Bindings for H3](https://github.com/uber/h3-java)
5. [h3-go: Go Bindings for H3](https://github.com/uber/h3-go)
6. [h3r: R Bindings for H3](https://github.com/crazycapivara/h3-r)
7. [H3.NET: .NET Bindings for H3](https://github.com/pocketken/H3.net) 