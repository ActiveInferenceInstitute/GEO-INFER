# Agent
: scripts

## Scope
 This directory contains scripts components for the module. It provides 2 classes and 3 functions.

## Classes
 and Functions

### ClimateAnalysisSystem

**Methods**:
- `run_climate_analysis()`: Execute the climate analysis system.

### SpatialMicrobiomeIntegrator
 Main integration class for spatial microbiome-climate-soil analysis.

**Methods**:
- `load_biological_datasets(region_bbox: Tuple[float, float, float, float], max_samples: int) -> Dict[str, Any]`: Load all biological datasets for the specified region.
- `create_interactive_h3_visualization(biological_data: Dict[str, Any], map_center: Tuple[float, float], output_format: str) -> str`: Create interactive H3 visualization with clustering and biological overlays
- `run_complete_analysis(region_bbox: Tuple[float, float, float, float], max_samples: int, output_format: str) -> Dict[str, str]`: Run the spatial microbiome-climate-soil analysis.

### setup_logging
 `setup_logging()`

### main
 `main()` Main function to run the climate analysis system.

### main
 `main()` Main entry point for the spatial integration script.

## Capabilities

- **2 classes** for core functionality
- **3 functions** for utility operations

## Integration

- **Location**: `examples/climate_integration/spatial_microbiome_soil_climate/scripts`
- **Type**: Directory Node
