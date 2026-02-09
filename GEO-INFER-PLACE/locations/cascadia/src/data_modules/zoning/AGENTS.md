# Agent
: zoning

## Scope
 This directory contains zoning components for the module. It provides 2 classes and 0 functions.

## Classes
 and Functions

### CascadianZoningDataSources
 Manages the acquisition of zoning data from various state and county sources.

**Methods**:
- `fetch_all_zoning_data(bbox: tuple, force_refresh: bool) -> Path`: Fetches zoning data from all relevant sources and saves it.

### GeoInferZoning
 Processes and analyzes multi-source agricultural zoning data using real OSC H3 v4 methods,

**Methods**:
- `acquire_raw_data() -> Path`: Acquire raw zoning data for Del Norte county.
- `run_final_analysis(h3_data: Dict[str, Any]) -> Dict[str, Any]`: Performs real comprehensive, multi-source zoning analysis on H3-indexed data using OSC H3 v4 methods.

## Capabilities

- **2 classes** for core functionality

## Integration

- **Location**: `cascadia/src/data_modules/zoning`
- **Type**: Directory Node
