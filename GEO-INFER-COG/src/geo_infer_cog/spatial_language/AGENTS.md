# Agent
: spatial_language

## Scope
 This directory contains spatial_language components for the module. It provides 3 classes and 0 functions.

## Classes
 and Functions

### SpatialEntity
 Represents a spatial entity extracted from text.

**Methods**:
- `to_geojson() -> Dict[str, Any]`: Convert to GeoJSON format.

### SpatialRelation
 Represents a spatial relationship extracted from text.

### SpatialLanguageProcessor
 Natural language processing for spatial and geographic content.

**Methods**:
- `extract_spatial_entities(text: str) -> List[SpatialEntity]`: Extract spatial entities from text using pattern matching.
- `extract_spatial_relations(text: str, entities: List[SpatialEntity]) -> List[SpatialRelation]`: Extract spatial relationships from text.
- `process_place_description(description: str) -> Dict[str, Any]`: Process and interpret a place description.

## Capabilities

- **3 classes** for core functionality

## Integration

- **Location**: `GEO-INFER-COG/src/geo_infer_cog/spatial_language`
- **Type**: Directory Node
