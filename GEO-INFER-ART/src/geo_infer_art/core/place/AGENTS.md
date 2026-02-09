# Agent
: place

## Scope
 This directory contains place components for the module. It provides 2 classes and 1 functions.

## Classes
 and Functions

### CulturalMap
 A class for creating maps that integrate cultural and historical contexts of places.

**Methods**:
- `from_region(cls, region_name: str, cultural_theme: str, style: str) -> 'CulturalMap'`: Create a cultural map for a specific named region.
- `from_coordinates(cls, lat: float, lon: float, radius_km: float, cultural_theme: str, style: str) -> 'CulturalMap'`: Create a cultural map centered on specific coordinates.
- `add_narrative(narrative: str, position: str) -> 'CulturalMap'`: Add a cultural narrative as text on the map.
- `apply_cultural_style(style: str) -> 'CulturalMap'`: Apply a cultural artistic style to the map.
- `save(output_path: str) -> str`: Save the generated cultural map to a file.
- `show() -> None`: Display the generated cultural map.
- `add_interactive_storytelling(story_elements: List[Dict]) -> 'CulturalMap'`: Add interactive storytelling elements to the cultural map.
- `create_timeline_view(time_periods: List[str]) -> List['CulturalMap']`: Create a series of maps showing cultural evolution over time periods.
- `add_legend(legend_items: List[Dict]) -> 'CulturalMap'`: Add a legend to the cultural map.
- `export_with_layers(output_dir: str, layer_types: List[str]) -> List[str]`: Export the cultural map with separate layers for different elements.

### PlaceArt
 A class for creating art based on the unique characteristics of geographic locations.

**Methods**:
- `from_coordinates(cls, lat: float, lon: float, name: Optional[str], radius_km: float, style: str) -> 'PlaceArt'`: Create place-based art from geographic coordinates.
- `from_place_name(cls, place_name: str, style: str, include_data: bool) -> 'PlaceArt'`: Create place-based art from a named location.
- `add_metadata_overlay(position: str, opacity: float) -> 'PlaceArt'`: Add location metadata as an overlay on the artwork.
- `save(output_path: str) -> str`: Save the generated art to a file.
- `show() -> None`: Display the generated art.
- `create_series(styles: List[str], output_dir: str) -> List[str]`: Create a series of artworks for the same location with different styles.
- `blend_with_style(style: str, blend_ratio: float) -> 'PlaceArt'`: Blend the current artwork with another style.
- `add_artistic_elements(elements: List[str], **kwargs) -> 'PlaceArt'`: Add artistic elements to the place art.
- `get_location_info() -> Dict`: Get information about the location.
- `export_metadata(output_path: str) -> str`: Export location and generation metadata to a JSON file.

### coord_to_pixel
 `coord_to_pixel(lon, lat)` Convert geographic coordinates to pixel coordinates.

## Capabilities

- **2 classes** for core functionality
- **1 functions** for utility operations

## Integration

- **Location**: `src/geo_infer_art/core/place`
- **Type**: Directory Node
