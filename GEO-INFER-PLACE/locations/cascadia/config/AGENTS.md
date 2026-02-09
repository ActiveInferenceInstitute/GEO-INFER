# Agent
: config

## Scope
 This directory contains config components for the module. It provides 1 classes and 1 functions.

## Classes
 and Functions

### CountyBoundaryLoader
 Loads and manages county boundary data for the Cascadia analysis

**Methods**:
- `get_county_info(county_key: str) -> Optional[Dict[str, Any]]`: Get county information from configuration
- `load_county_geometry(county_key: str) -> Optional[Union[Polygon, Dict[str, Any]]]`: Load county geometry from GeoJSON file
- `download_county_boundary(county_key: str) -> bool`: Download county boundary from official sources
- `get_all_county_geometries(target_counties: Dict[str, List[str]]) -> Dict[str, Dict[str, Any]]`: Get geometries for all target counties
- `validate_geometry(geometry: Union[Dict[str, Any], Polygon]) -> bool`: Validate that a geometry is suitable for H3 geo_to_cells

### create_county_boundary_loader
 `create_county_boundary_loader() -> CountyBoundaryLoader` Factory function to create a county boundary loader

## Capabilities

- **1 classes** for core functionality
- **1 functions** for utility operations

## Integration

- **Location**: `GEO-INFER-PLACE/locations/cascadia/config`
- **Type**: Directory Node
