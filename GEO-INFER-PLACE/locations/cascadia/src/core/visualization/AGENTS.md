# Agent
: visualization

## Scope
 This directory contains visualization components for the module. It provides 4 classes and 8 functions.

## Classes
 and Functions

### ComprehensiveVisualizationEngine
 visualization engine for Cascadia framework.

**Methods**:
- `create_interactive_h3_map(h3_data: Dict[str, Any], data_sources: Dict[str, Any], target_hexagons: List[str], output_filename: str, initial_visible_layers: Optional[List[str]], include_layers: Optional[List[str]], module_status: Optional[Dict[str, Any]], redevelopment_scores: Optional[Dict[str, float]]) -> Path`: Create an interactive H3-based map with multiple layers.
- `create_static_visualizations(h3_data: Dict[str, Any], data_sources: Dict[str, Any], redevelopment_scores: Dict[str, float]) -> Dict[str, Path]`: Create static visualizations for reports and presentations.
- `create_dashboard(h3_data: Dict[str, Any], data_sources: Dict[str, Any], redevelopment_scores: Dict[str, float], summary: Dict[str, Any]) -> Path`: Create a dashboard with all visualizations.
- `export_visualization_data(h3_data: Dict[str, Any], data_sources: Dict[str, Any], redevelopment_scores: Dict[str, float]) -> Dict[str, Path]`: Export visualization data for external tools.

### CascadiaDatashaderVisualizer
 Efficient visualization of Cascadia H3 data using Datashader.

**Methods**:
- `prepare_h3_dataframe(unified_data: Dict, redevelopment_scores: Dict) -> pd.DataFrame`: Convert H3 unified data to pandas DataFrame for Datashader processing.
- `create_redevelopment_heatmap(df: pd.DataFrame, plot_width: int, plot_height: int) -> hv.Image`: Create an efficient heatmap of redevelopment potential scores.
- `create_module_coverage_plot(df: pd.DataFrame, module_name: str, plot_width: int, plot_height: int) -> hv.Image`: Create coverage plot for a specific module.
- `create_comprehensive_dashboard(unified_data: Dict, redevelopment_scores: Dict) -> str`: Create a Datashader-based dashboard.
- `create_lightweight_json_export(unified_data: Dict, redevelopment_scores: Dict) -> str`: Create a lightweight JSON export for web-based visualization.

### CascadiaDeepscatterVisualizer
 Efficient web-based visualization of Cascadia H3 data using Deepscatter.

**Methods**:
- `prepare_deepscatter_data(unified_data: Dict, redevelopment_scores: Dict) -> List[Dict]`: Convert H3 data to Deepscatter format.
- `create_deepscatter_html(data_points: List[Dict], title: str) -> str`: Create a Deepscatter HTML visualization.
- `create_lightweight_csv_export(data_points: List[Dict]) -> str`: Create a lightweight CSV export for external visualization tools.

### InteractiveH3Visualization
 Interactive H3-based visualization system for Cascadia framework.

**Methods**:
- `create_comprehensive_map(h3_data: Dict[str, Any], data_sources: Dict[str, Any], target_hexagons: List[str], output_filename: str) -> Path`: Create a interactive map with all data layers.
- `create_layer_specific_map(module_name: str, module_data: Dict[str, Any], target_hexagons: List[str], output_filename: Optional[str]) -> Path`: Create a map focused on a specific data layer.
- `export_map_data(h3_data: Dict[str, Any], data_sources: Dict[str, Any]) -> Dict[str, Any]`: Export map data for external analysis.

### create_comprehensive_visualization_engine
 `create_comprehensive_visualization_engine(output_dir: Path) -> ComprehensiveVisualizationEngine` Create a visualization engine instance.

### most_common
 `most_common(key_candidates: List[str]) -> str`

### create_datashader_visualization
 `create_datashader_visualization(backend, output_dir: Path) -> Dict[str, str]` Create efficient Datashader visualizations for Cascadia data.

### create_deepscatter_visualization
 `create_deepscatter_visualization(backend, output_dir: Path) -> Dict[str, str]` Create efficient Deepscatter visualizations for Cascadia data.

### create_interactive_h3_visualization
 `create_interactive_h3_visualization(output_dir: Path) -> InteractiveH3Visualization` Create an interactive H3 visualization instance.

### create_static_plots
 `create_static_plots(backend, output_dir: Path) -> Dict[str, str]` Create simple static plots for Cascadia data.

### create_summary_statistics
 `create_summary_statistics(unified_data: Dict, redevelopment_scores: Dict) -> Dict` Create summary statistics for visualization.

### create_data_export
 `create_data_export(unified_data: Dict, redevelopment_scores: Dict) -> Dict` Create data export for external visualization tools.

## Capabilities

- **4 classes** for core functionality
- **8 functions** for utility operations

## Integration

- **Location**: `cascadia/src/core/visualization`
- **Type**: Directory Node
