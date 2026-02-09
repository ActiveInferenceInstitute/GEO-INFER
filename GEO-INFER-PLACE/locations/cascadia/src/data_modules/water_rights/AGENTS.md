# Agent
: water_rights

## Scope
 This directory contains water_rights components for the module. It provides 2 classes and 0 functions.

## Classes
 and Functions

### CascadianWaterRightsDataSources
 Manages the acquisition of water rights data for the Cascadia region.

**Methods**:
- `fetch_all_water_rights_data(target_hexagons: list) -> gpd.GeoDataFrame`: Fetches water rights data for all three states (CA, OR, WA).

### GeoInferWaterRights
 Processes and analyzes real water rights data within an H3 grid.

**Methods**:
- `acquire_raw_data() -> Path`: Acquire and cache raw water rights points for the target area.
- `run_analysis(target_hexagons: List[str]) -> Dict[str, Dict[str, Any]]`: Spatially joins real water rights data with H3 hexagons and aggregates metrics.

## Capabilities

- **2 classes** for core functionality

## Integration

- **Location**: `cascadia/src/data_modules/water_rights`
- **Type**: Directory Node
