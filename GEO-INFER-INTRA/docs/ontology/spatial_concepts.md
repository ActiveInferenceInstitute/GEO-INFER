# Spatial Concepts

This document describes the spatial concepts defined in the GEO-INFER-INTRA ontology system, which provide a standardized vocabulary for spatial entities, relationships, and properties.

## Core Spatial Entities

The ontology defines the following core spatial entities:

| Concept | Definition | Properties |
|---------|------------|------------|
| `SpatialFeature` | Any identifiable entity with a spatial extent | `hasGeometry`, `hasCRS`, `hasIdentifier` |
| `Point` | Zero-dimensional geometry representing a location | `hasCoordinates`, `hasElevation` |
| `Line` | One-dimensional geometry connecting points | `hasVertices`, `hasLength` |
| `Polygon` | Two-dimensional geometry bounded by lines | `hasVertices`, `hasArea`, `hasPerimeter` |
| `Raster` | Gridded representation of continuous spatial data | `hasResolution`, `hasBounds`, `hasDataType` |
| `Vector` | Collection of discrete spatial features | `hasFeatures`, `hasAttributes` |
| `Region` | Defined geographical area with boundaries | `hasBoundary`, `hasName`, `hasDescription` |
| `Network` | Connected system of nodes and edges | `hasNodes`, `hasEdges`, `hasConnectivity` |

## Spatial Relationships

The ontology defines the following spatial relationships:

| Relationship | Definition | Domain | Range |
|--------------|------------|--------|-------|
| `contains` | Entity A fully contains entity B | `SpatialFeature` | `SpatialFeature` |
| `within` | Entity A is fully within entity B | `SpatialFeature` | `SpatialFeature` |
| `intersects` | Entity A shares any space with entity B | `SpatialFeature` | `SpatialFeature` |
| `touches` | Entity A shares boundary points with B without overlapping | `SpatialFeature` | `SpatialFeature` |
| `disjoint` | Entity A has no spatial overlap with entity B | `SpatialFeature` | `SpatialFeature` |
| `crosses` | Entity A crosses entity B | `Line` | `Line` or `Polygon` |
| `overlaps` | Entity A partially overlaps entity B | `SpatialFeature` | `SpatialFeature` |
| `adjacentTo` | Entity A is adjacent to entity B | `SpatialFeature` | `SpatialFeature` |
| `connectedTo` | Entity A is connected to entity B | `Node` | `Node` |

## Spatial Properties

The ontology defines the following spatial properties:

| Property | Definition | Domain | Range |
|----------|------------|--------|-------|
| `hasGeometry` | Specifies the geometry of a spatial feature | `SpatialFeature` | `Geometry` |
| `hasCRS` | Specifies the coordinate reference system | `SpatialFeature` | `CoordinateReferenceSystem` |
| `hasCoordinates` | Specifies the coordinates of a point | `Point` | `Coordinates` |
| `hasArea` | Specifies the area of a polygon | `Polygon` | `xsd:double` |
| `hasPerimeter` | Specifies the perimeter of a polygon | `Polygon` | `xsd:double` |
| `hasLength` | Specifies the length of a line | `Line` | `xsd:double` |
| `hasResolution` | Specifies the resolution of a raster | `Raster` | `Resolution` |
| `hasBounds` | Specifies the bounding box of a feature | `SpatialFeature` | `BoundingBox` |
| `hasElevation` | Specifies the elevation of a point | `Point` | `xsd:double` |
| `hasDistance` | Specifies the distance between features | `SpatialFeature` | `xsd:double` |

## Coordinate Reference Systems

The ontology includes definitions for common coordinate reference systems:

| CRS | Definition | EPSG Code |
|-----|------------|-----------|
| `WGS84` | World Geodetic System 1984 | EPSG:4326 |
| `WebMercator` | Web Mercator projection | EPSG:3857 |
| `UTM` | Universal Transverse Mercator | EPSG:32601-32660 (N), EPSG:32701-32760 (S) |
| `NAD83` | North American Datum 1983 | EPSG:4269 |
| `ETRS89` | European Terrestrial Reference System 1989 | EPSG:4258 |
| `GDA94` | Geocentric Datum of Australia 1994 | EPSG:4283 |

## Spatial Metrics

The ontology defines the following spatial metrics:

| Metric | Definition | Formula |
|--------|------------|---------|
| `EuclideanDistance` | Straight-line distance between two points | √[(x₂-x₁)² + (y₂-y₁)²] |
| `ManhattanDistance` | Sum of absolute differences between coordinates | |x₂-x₁| + |y₂-y₁| |
| `HaversineDistance` | Great-circle distance between two points on a sphere | 2r·arcsin(√[sin²((φ₂-φ₁)/2) + cos(φ₁)cos(φ₂)sin²((λ₂-λ₁)/2)]) |
| `MinkowskiDistance` | Generalization of Euclidean and Manhattan distances | (Σ|xᵢ-yᵢ|ᵖ)^(1/p) |

## Usage Example

The following example shows how to use the spatial concepts in Python code:

```python
from geo_infer_intra.ontology import OntologyManager

# Initialize the ontology manager
ontology_manager = OntologyManager()

# Load the spatial concepts ontology
spatial_ontology = ontology_manager.load_ontology("spatial")

# Get all spatial relationships
relationships = spatial_ontology.get_instances_of("SpatialRelationship")

# Find all features that can have area
area_features = spatial_ontology.get_domain_of_property("hasArea")

# Get the definition of a concept
contains_def = spatial_ontology.get_definition("contains")
print(f"Definition of 'contains': {contains_def}")

# Check if a relationship is transitive
is_transitive = spatial_ontology.is_transitive("contains")
print(f"Is 'contains' transitive? {is_transitive}")
```

## Extending Spatial Concepts

To extend the spatial concepts ontology with custom concepts:

1. Create a new ontology file that imports the core spatial concepts
2. Define your new concepts, relationships, or properties
3. Establish the relationships with existing concepts
4. Register your extension with the ontology manager

See [Ontology Extension](extension.md) for detailed instructions. 