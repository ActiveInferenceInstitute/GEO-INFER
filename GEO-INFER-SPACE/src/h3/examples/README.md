# H3 Examples

This directory contains comprehensive examples demonstrating the GEO-INFER H3 framework capabilities. All examples use only valid H3 v4 methods and generate outputs to the `output/` directory.

## Examples Overview

### 01_basic_operations.py
**Purpose**: Demonstrates fundamental H3 operations
**Features**:
- Coordinate conversion at multiple resolutions
- Cell property analysis (area, boundary, validation)
- Resolution comparison and scaling
- Input validation testing

**Outputs**:
- `01_coordinate_conversion.json` - Multi-resolution coordinate data
- `01_cell_properties.json` - Cell analysis results
- `01_resolution_comparison.csv` - Resolution scaling data
- `01_validation_results.json` - Validation test results

### 02_spatial_analysis.py
**Purpose**: Advanced spatial analysis and grid operations
**Features**:
- Grid disk and ring operations
- Distance calculations (great circle and grid)
- Path analysis between cells
- Spatial statistics and distribution analysis
- Nearest cell finding
- Cell density calculations

**Outputs**:
- `02_grid_operations.json` - Grid operation results
- `02_distance_calculations.csv` - Distance analysis data
- `02_path_analysis.json` - Path analysis results
- `02_spatial_statistics.json` - Spatial statistics
- `02_nearest_cell_analysis.json` - Nearest neighbor analysis
- `02_density_analysis.json` - Density calculations

### 03_hierarchical_operations.py
**Purpose**: Hierarchical H3 operations and relationships
**Features**:
- Parent-child relationships
- Hierarchy path navigation
- Ancestor and descendant analysis
- Multi-resolution operations
- Area scaling analysis

**Outputs**:
- `03_parent_child_relationships.json` - Parent-child data
- `03_hierarchy_path.json` - Hierarchy navigation
- `03_ancestors_descendants.json` - Ancestor/descendant analysis
- `03_hierarchical_analysis.json` - Multi-resolution analysis
- `03_multi_resolution_operations.json` - Resolution operations

### 04_data_conversion.py
**Purpose**: Data conversion and multi-channel fusion
**Features**:
- GeoJSON conversion (individual and collections)
- WKT conversion
- CSV export with metadata
- KML generation
- Shapefile data preparation
- Multi-channel dataset fusion
- Multiple export formats

**Outputs**:
- `04_geojson_conversion.json` - GeoJSON conversion data
- `04_wkt_conversion.json` - WKT conversion data
- `04_csv_conversion.json` - CSV conversion data
- `04_cells_data.csv` - Actual CSV file
- `04_kml_conversion.json` - KML conversion data
- `04_cells.kml` - Actual KML file
- `04_shapefile_data.json` - Shapefile data
- `04_multi_channel_fusion.json` - Multi-channel fusion
- `04_export_formats.json` - Export format summary
- `04_spatial_data_analysis.json` - Spatial analysis

### 05_visualization_outputs.py
**Purpose**: Static, animated, and interactive visualizations
**Features**:
- Static visualization data preparation
- Animated visualization frames (expansion, transition, path)
- Interactive visualization with properties
- Heatmap visualization with intensity
- Temporal visualization with time series
- Multiple export formats

**Outputs**:
- `05_static_visualization.json` - Static visualization data
- `05_static_visualization.geojson` - Static GeoJSON
- `05_static_visualization.csv` - Static CSV
- `05_animated_visualization.json` - Animation frames
- `05_interactive_visualization.json` - Interactive data
- `05_interactive_visualization.geojson` - Interactive GeoJSON
- `05_heatmap_visualization.json` - Heatmap data
- `05_heatmap_visualization.geojson` - Heatmap GeoJSON
- `05_temporal_visualization.json` - Temporal data
- `05_export_formats.json` - Export format data
- `05_export_visualization.geojson` - Export GeoJSON
- `05_export_visualization.csv` - Export CSV

### 06_comprehensive_workflow.py
**Purpose**: Complete end-to-end H3 analysis pipeline
**Features**:
- Step 1: Data ingestion and validation
- Step 2: Spatial analysis and statistics
- Step 3: Hierarchical analysis and relationships
- Step 4: Grid operations and spatial relationships
- Step 5: Data conversion and export
- Step 6: Advanced analysis and multi-resolution operations
- Step 7: Visualization preparation and output generation

**Outputs**:
- `06_step1_data_ingestion.json` - Step 1 results
- `06_step2_spatial_analysis.json` - Step 2 results
- `06_step3_hierarchical_analysis.json` - Step 3 results
- `06_step4_grid_operations.json` - Step 4 results
- `06_step5_data_conversion.json` - Step 5 results
- `06_workflow_cells.geojson` - Workflow GeoJSON
- `06_workflow_cells.csv` - Workflow CSV
- `06_step6_advanced_analysis.json` - Step 6 results
- `06_step7_visualization_preparation.json` - Step 7 results
- `06_interactive_cities.geojson` - Interactive cities
- `06_workflow_summary.json` - Complete workflow summary

## Key Methods Used

All examples use only valid H3 v4 methods from the modular framework:

### Core Operations
- `latlng_to_cell()` - Convert coordinates to H3 cell
- `cell_to_latlng()` - Convert H3 cell to coordinates
- `cell_to_boundary()` - Get cell boundary coordinates
- `cell_area()` - Calculate cell area
- `get_resolution()` - Get cell resolution
- `is_valid_cell()` - Validate cell index
- `is_pentagon()` - Check if cell is pentagon

### Traversal Operations
- `grid_disk()` - Get cells within k steps
- `grid_ring()` - Get cells exactly k steps away
- `grid_path_cells()` - Find path between cells
- `grid_distance()` - Calculate grid distance
- `great_circle_distance()` - Calculate great circle distance
- `grid_neighbors()` - Get neighboring cells

### Indexing Operations
- `cell_to_center_child()` - Get center child
- `cell_to_children()` - Get all children
- `cell_to_parent()` - Get parent cell

### Hierarchy Operations
- `get_hierarchy_path()` - Navigate hierarchy
- `get_ancestors()` - Get ancestor cells
- `get_descendants()` - Get descendant cells

### Conversion Operations
- `cell_to_geojson()` - Convert cell to GeoJSON
- `cells_to_geojson()` - Convert cells to GeoJSON collection
- `cells_to_csv()` - Convert cells to CSV
- `cells_to_kml()` - Convert cells to KML
- `cells_to_wkt()` - Convert cells to WKT
- `cells_to_shapefile_data()` - Convert cells to shapefile data

### Analysis Operations
- `analyze_cell_distribution()` - Analyze cell distribution
- `calculate_spatial_statistics()` - Calculate spatial statistics
- `find_nearest_cell()` - Find nearest cell
- `calculate_cell_density()` - Calculate cell density
- `analyze_resolution_distribution()` - Analyze resolution distribution

## Running Examples

All examples can be run directly:

```bash
python3 01_basic_operations.py
python3 02_spatial_analysis.py
python3 03_hierarchical_operations.py
python3 04_data_conversion.py
python3 05_visualization_outputs.py
python3 06_comprehensive_workflow.py
```

Each example will:
1. Execute all demonstrations
2. Generate comprehensive outputs to the `output/` directory
3. Display progress and results
4. Confirm successful completion

## Output Structure

All outputs are organized in the `output/` directory with clear naming conventions:
- `0X_` prefix indicates the example number
- Descriptive names indicate the content type
- Multiple formats (JSON, CSV, GeoJSON, KML) for different use cases
- Both metadata files and actual data files

## Framework Integration

These examples demonstrate:
- **Thin Orchestrators**: Examples focus on orchestration while all real logic resides in modular files
- **Valid H3 v4 Methods**: Only uses tested, valid H3 v4 API methods
- **Comprehensive Coverage**: Demonstrates all major H3 operations and use cases
- **Real Data Processing**: Works with actual geospatial data and coordinates
- **Multiple Output Formats**: Generates data in various formats for different applications
- **Error Handling**: Robust error handling for edge cases and invalid inputs

## Technical Notes

- All examples use local modular imports rather than the installed H3 package
- Error handling is implemented for operations that may fail (e.g., distant cells)
- Output files are properly structured and contain comprehensive metadata
- Examples demonstrate both individual operations and complex workflows
- All generated data is suitable for further analysis or visualization 