# Agent
: improvements

## Scope
 This directory contains improvements components for the module. It provides 2 classes and 0 functions.

## Classes
 and Functions

### CascadianImprovementsDataSources
 Manages acquisition and processing of building footprints and estimated property values.

**Methods**:
- `fetch_all_improvements_data(target_hexagons: list) -> gpd.GeoDataFrame`: Fetches building footprints and Zillow data, merges them, and returns

### GeoInferImprovements
 Processes and analyzes improvements data within an H3 grid.

**Methods**:
- `acquire_raw_data() -> Path`: Acquire raw improvements data for Del Norte county.
- `run_final_analysis(h3_data: Dict[str, Any]) -> Dict[str, Any]`: Perform improvements analysis on H3-indexed data.

## Capabilities

- **2 classes** for core functionality

## Integration

- **Location**: `cascadia/src/data_modules/improvements`
- **Type**: Directory Node
