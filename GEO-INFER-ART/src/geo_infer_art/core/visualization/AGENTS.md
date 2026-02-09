# Agent
: visualization

## Scope
 This directory contains visualization components for the module. It provides 4 classes and 1 functions.

## Classes
 and Functions

### GeoArt
 A class for creating artistic visualizations of geospatial data.

**Methods**:
- `load_geojson(cls, file_path: str) -> 'GeoArt'`: Load geospatial data from a GeoJSON file.
- `load_raster(cls, file_path: str) -> 'GeoArt'`: Load geospatial data from a raster file (e.g., GeoTIFF).
- `apply_style(style: str, color_palette: Optional[Union[str, ColorPalette]], line_width: float, alpha: float, background_color: str, map_style: Optional[Union[str, 'MapStyle']], legend: bool, title: Optional[str]) -> 'GeoArt'`: Apply an artistic style to the geospatial data.
- `save(output_path: str, dpi: int) -> str`: Save the visualization to a file.
- `show() -> None`: Display the visualization.
- `create_animation(output_path: str, style_sequence: List[str], duration: float, fps: int, **kwargs) -> str`: Create an animated visualization cycling through different styles.
- `add_interactive_elements(interactive_type: str) -> 'GeoArt'`: Add interactive elements to the visualization.
- `export_svg(output_path: str) -> str`: Export the visualization as an SVG file.
- `get_colorbar(label: str) -> 'GeoArt'`: Add a colorbar to the visualization.
- `set_projection(projection: str) -> 'GeoArt'`: Set the map projection for the visualization.
- `add_annotations(annotations: List[Dict]) -> 'GeoArt'`: Add text or graphical annotations to the visualization.
- `apply_filter(filter_type: str, **kwargs) -> 'GeoArt'`: Apply a spatial or visual filter to the data.
- `create_realtime_visualization(data_callback: Callable[[], Union[gpd.GeoDataFrame, np.ndarray]], update_interval: float, style: str, max_updates: Optional[int], output_file: Optional[str], **kwargs) -> 'RealtimeVisualization'`: Create a real-time visualization that updates with live data.
- `create_3d_visualization(elevation_data: Optional[np.ndarray], z_column: Optional[str], **kwargs) -> 'GeoArt3D'`: Create a 3D visualization of the geospatial data.
- `create_interactive_web_map(output_file: str, tiles: str, **kwargs) -> str`: Create an interactive web-based map using Folium.
- `create_plotly_visualization(plot_type: str, **kwargs) -> Any`: Create an interactive Plotly visualization.
- `optimize_for_performance(target_resolution: Optional[Tuple[int, int]], simplify_tolerance: Optional[float], cache_data: bool) -> 'GeoArt'`: Optimize the visualization for better performance.
- `create_multi_scale_visualization(scales: List[str], **kwargs) -> Dict[str, 'GeoArt']`: Create visualizations at multiple scales.
- `apply_custom_algorithm(algorithm_function: Callable, algorithm_name: str, **params) -> 'GeoArt'`: Apply a custom algorithm to the geospatial data.

### RealtimeVisualization
 A class for managing real-time geospatial visualizations.

**Methods**:
- `start(use_threading: bool) -> None`: Start the real-time visualization.
- `stop() -> None`: Stop the real-time visualization.
- `save_snapshot(filename: Optional[str]) -> str`: Save a snapshot of the current visualization.

### GeoArt3D
 A class for creating 3D artistic visualizations of geospatial data.

**Methods**:
- `create_3d_surface(output_file: Optional[str], **kwargs) -> Any`: Create a 3D surface visualization.
- `create_3d_animation(**kwargs) -> Any`: Create an animated 3D visualization.

### MapStyle
 A class for managing map styling and theming.

**Methods**:
- `create_themed_style(cls, theme: str, color_palette: Optional[Union[str, ColorPalette]], **kwargs) -> 'MapStyle'`: Create a style based on a visual theme.
- `apply_to_axes(ax: plt.Axes, data_bounds: Optional[Tuple]) -> None`: Apply the style to matplotlib axes.
- `get_colormap() -> LinearSegmentedColormap`: Get a matplotlib colormap based on the style colors.
- `get_color_list() -> List[str]`: Get the list of colors for this style.
- `get_line_width() -> float`: Get the default line width for this style.
- `get_background_color() -> str`: Get the background color for this style.

### animate
 `animate(frame_num)`

## Capabilities

- **4 classes** for core functionality
- **1 functions** for utility operations

## Integration

- **Location**: `src/geo_infer_art/core/visualization`
- **Type**: Directory Node
