# Agent
: h3

## Scope
 This directory contains h3 components for the module. It provides 25 classes and 56 functions.

## Classes
 and Functions

### H3SpatialAnalyzer
 Spatial analysis for H3 grids.

**Methods**:
- `analyze_spatial_autocorrelation(value_column: str) -> Dict[str, Any]`: Analyze spatial autocorrelation using Moran's I statistic.
- `detect_hotspots(value_column: str, method: str) -> Dict[str, Any]`: Detect spatial hotspots and coldspots using local spatial statistics.
- `find_hotspots(value_column: str, threshold_percentile: float) -> List[H3Cell]`: Find hotspot cells based on value threshold.

### H3ClusterAnalyzer
 Clustering analysis for H3 grids.

**Methods**:
- `density_based_clustering(value_column: str, min_density: float, eps_rings: int) -> Dict[str, Any]`: Perform density-based clustering using H3 spatial relationships.
- `hierarchical_clustering(value_column: str, linkage_method: str) -> Dict[str, Any]`: Perform hierarchical clustering on H3 grid cells.
- `simple_clustering(value_column: str, num_clusters: int) -> Dict[str, Any]`: Perform simple k-means-style clustering on cell values.

### H3DensityAnalyzer
 Density analysis for H3 grids.

**Methods**:
- `calculate_kernel_density(point_column: str, bandwidth_rings: int, kernel_type: str) -> Dict[str, Any]`: Calculate kernel density estimation using H3 spatial relationships.
- `analyze_density_patterns(value_column: str) -> Dict[str, Any]`: Analyze density patterns and identify clusters, gaps, and gradients.
- `calculate_density_surface(value_column: str, radius_cells: int) -> Dict[str, Any]`: Calculate density surface using kernel density estimation.

### H3NetworkAnalyzer
 Network analysis for H3 grids.

**Methods**:
- `analyze_flow_patterns(origin_column: str, destination_column: str, flow_volume_column: str) -> Dict[str, Any]`: Analyze flow patterns between H3 cells.
- `calculate_accessibility(impedance_column: str, max_rings: int) -> Dict[str, Any]`: Calculate accessibility measures for each H3 cell.
- `detect_network_communities(flow_threshold: float) -> Dict[str, Any]`: Detect communities in the H3 network based on flow patterns.
- `analyze_connectivity_patterns() -> Dict[str, Any]`: Analyze connectivity patterns in the grid.

### H3TemporalAnalyzer
 Temporal analysis for H3 grids.

**Methods**:
- `analyze_temporal_patterns(timestamp_column: str, value_column: str, temporal_resolution: str) -> Dict[str, Any]`: Analyze temporal patterns in H3 grid data.
- `detect_temporal_anomalies(timestamp_column: str, value_column: str, method: str, threshold: float) -> Dict[str, Any]`: Detect temporal anomalies in H3 grid data.
- `analyze_temporal_trends(value_column: str) -> Dict[str, Any]`: Analyze temporal trends in grid values.
- `detect_anomalies(value_column: str, threshold_std: float) -> Dict[str, Any]`: Detect temporal anomalies in grid values.

### H3Cell
 Represents a single H3 hexagonal cell with metadata and operations.

**Methods**:
- `from_coordinates(cls, lat: float, lng: float, resolution: int, **properties) -> 'H3Cell'`: Create H3Cell from latitude/longitude coordinates.
- `neighbors(k: int) -> List['H3Cell']`: Get neighboring cells within k distance.
- `parent(parent_resolution: Optional[int]) -> Optional['H3Cell']`: Get parent cell at coarser resolution.
- `children(child_resolution: Optional[int]) -> List['H3Cell']`: Get child cells at finer resolution.
- `distance_to(other: 'H3Cell') -> int`: Calculate grid distance to another cell.
- `is_neighbor(other: 'H3Cell') -> bool`: Check if another cell is a direct neighbor.
- `to_geojson() -> Dict[str, Any]`: Convert cell to GeoJSON feature.

### H3Grid
 Manages collections of H3 cells with operations and analytics.

**Methods**:
- `add_cell(cell: H3Cell)`: Add a cell to the grid.
- `remove_cell(cell_index: str) -> bool`: Remove a cell from the grid.
- `get_cell(cell_index: str) -> Optional[H3Cell]`: Get cell by index.
- `has_cell(cell_index: str) -> bool`: Check if grid contains cell.
- `from_polygon(cls, polygon_coords: List[Tuple[float, float]], resolution: int, name: str) -> 'H3Grid'`: Create H3Grid from polygon coordinates.
- `from_center(cls, lat: float, lng: float, resolution: int, k: int, name: str) -> 'H3Grid'`: Create H3Grid centered on coordinates with k-ring.
- `compact() -> 'H3Grid'`: Compact cells to mixed resolutions for efficiency.
- `uncompact(target_resolution: int) -> 'H3Grid'`: Uncompact cells to uniform resolution.
- `total_area() -> float`: Calculate total area of all cells in km².
- `bounds() -> Tuple[float, float, float, float]`: Get bounding box of all cells.
- `center() -> Tuple[float, float]`: Get center coordinates of the grid.
- `resolutions() -> Set[int]`: Get set of all resolutions in the grid.
- `filter_by_resolution(resolution: int) -> 'H3Grid'`: Filter cells by resolution.
- `to_geojson() -> Dict[str, Any]`: Convert grid to GeoJSON FeatureCollection.
- `to_dataframe()`: Convert grid to pandas DataFrame.

### H3Analytics
 analytics for H3 grids and cells.

**Methods**:
- `basic_statistics() -> Dict[str, Any]`: Calculate basic grid statistics.
- `connectivity_analysis() -> Dict[str, Any]`: Analyze connectivity between cells.
- `density_analysis(reference_area_km2: Optional[float]) -> Dict[str, Any]`: Analyze cell density patterns.
- `resolution_analysis() -> Dict[str, Any]`: Analyze resolution distribution and patterns.
- `spatial_distribution() -> Dict[str, Any]`: Analyze spatial distribution patterns.
- `generate_report() -> Dict[str, Any]`: Generate analytics report.

### H3Visualizer
 Visualization utilities for H3 grids and analytics.

**Methods**:
- `create_folium_map(**kwargs) -> 'folium.Map'`: Create interactive Folium map of the H3 grid.
- `save_geojson(filepath: str)`: Save grid as GeoJSON file.

### H3Validator
 Validation utilities for H3 operations and data integrity.

**Methods**:
- `validate_h3_index(h3_index: str) -> Dict[str, Any]`: Validate H3 index format and properties.
- `validate_coordinates(lat: float, lng: float) -> Dict[str, Any]`: Validate latitude/longitude coordinates.
- `validate_resolution(resolution: int) -> Dict[str, Any]`: Validate H3 resolution parameter.
- `validate_grid(cls, grid: H3Grid) -> Dict[str, Any]`: Validate entire H3Grid for consistency and integrity.

### H3Dataset
 Container for H3 grid datasets with metadata and utilities.

**Methods**:
- `add_metadata(key: str, value: Any)`: Add metadata entry.
- `get_metadata(key: str, default: Any) -> Any`: Get metadata entry.
- `validate() -> Dict[str, Any]`: Validate dataset integrity.
- `export_json(filepath: str)`: Export dataset to JSON file.

### H3DataLoader
 Utilities for loading H3 datasets from various sources.

**Methods**:
- `from_geojson(filepath: str, name: str) -> H3Dataset`: Load H3Dataset from GeoJSON file.
- `from_csv(filepath: str, h3_column: str, resolution_column: str, name: str) -> H3Dataset`: Load H3Dataset from CSV file.

### H3DataExporter
 Utilities for exporting H3 datasets to various formats.

**Methods**:
- `to_geojson(dataset: H3Dataset, filepath: str)`: Export dataset to GeoJSON file.
- `to_csv(dataset: H3Dataset, filepath: str)`: Export dataset to CSV file.

### H3Backend
 H3 backend implementation for spatial operations.

**Methods**:
- `name() -> str`: Return the backend name.
- `version() -> str`: Return the backend version.
- `is_available() -> bool`: Check if the backend is available and functional.
- `get_capabilities() -> Dict[str, Any]`: Return the backend's capabilities.
- `latlng_to_cell(lat: float, lng: float, resolution: int) -> str`: Convert lat/lng coordinates to H3 cell.
- `cell_to_latlng(cell: str) -> tuple[float, float]`: Convert H3 cell back to lat/lng coordinates.
- `polygon_to_cells(polygon: Dict[str, Any], resolution: int) -> List[str]`: Convert polygon to list of H3 cells.
- `get_cell_neighbors(cell: str, k: int) -> List[str]`: Get neighboring cells around a given cell.
- `get_cell_distance(cell1: str, cell2: str) -> int`: Calculate the grid distance between two H3 cells.
- `compact_cells(cells: List[str]) -> List[str]`: Compact a list of cells into a more efficient representation.
- `uncompact_cells(compacted_cells: List[str], resolution: int) -> List[str]`: Uncompact cells back to individual cell identifiers.
- `get_cell_parent(cell: str, resolution: int) -> str`: Get the parent of a cell at a coarser resolution.
- `get_cell_children(cell: str, resolution: int) -> List[str]`: Get children of a cell at a finer resolution.
- `get_cell_path(start_cell: str, end_cell: str) -> List[str]`: Get the path of cells between two cells.
- `get_cell_ring(cell: str, k: int) -> List[str]`: Get the ring of cells at distance k.
- `analyze_hotspots(data: Dict[str, Any]) -> Dict[str, Any]`: Analyze spatial hotspots in H3-indexed data.
- `compute_proximity(points: List[tuple[float, float]]) -> Dict[str, Any]`: Compute proximity analysis between points using H3.
- `get_cell_resolution(cell: str) -> int`: Get the resolution level of an H3 cell.
- `get_cell_boundary(cell: str) -> List[Tuple[float, float]]`: Get the boundary coordinates of an H3 cell.
- `get_cell_area(cell: str, unit: str) -> float`: Get the area of an H3 cell in square kilometers.
- `cells_to_multipolygon(cells: List[str]) -> Dict[str, Any]`: Convert a list of H3 cells to a GeoJSON MultiPolygon geometry.
- `find_clusters(cells: List[str], values: List[float], min_cluster_size: int, distance_threshold: int) -> Dict[str, Any]`: Find spatial clusters of cells based on values and proximity.
- `calculate_density(cells: List[str], values: List[float], kernel_radius: int) -> Dict[str, Any]`: Calculate density values across cells using kernel smoothing.
- `spatial_join(cells_a: List[str], cells_b: List[str], join_type: str) -> Dict[str, Any]`: Join two sets of cells based on spatial relationships.
- `interpolate_values(cells: List[str], values: List[float], target_cells: List[str], method: str) -> Dict[str, Any]`: Interpolate values at target cell locations using source cells.
- `is_valid_cell(cell: str) -> bool`: Check if an H3 cell identifier is valid.
- `validate_resolution(resolution: int) -> Dict[str, Any]`: Validate that a resolution is within the valid H3 range.
- `validate_coordinates(lat: float, lng: float) -> Dict[str, Any]`: Validate lat/lng coordinates are within valid ranges.
- `are_neighbors(cell1: str, cell2: str) -> bool`: Check if two H3 cells are neighbors (adjacent).
- `is_pentagon(cell: str) -> bool`: Check if an H3 cell is a pentagon (12 per resolution).
- `is_res_class_iii(cell: str) -> bool`: Check if cell is Class III resolution (aperture 7 rotation).
- `get_base_cell(cell: str) -> int`: Get the base cell number (0-121) for any H3 cell.
- `get_icosahedron_faces(cell: str) -> List[int]`: Get the icosahedron faces a cell intersects.
- `get_pentagons(resolution: int) -> List[str]`: Get all 12 pentagon cells at a given resolution.
- `get_cells_at_resolution(cells: List[str], target_resolution: int) -> List[str]`: Convert a mixed-resolution set of cells to a uniform resolution.
- `get_directed_edge(origin: str, destination: str) -> str`: Get the directed edge from origin to destination cell.
- `edge_to_cells(edge: str) -> Tuple[str, str]`: Get the origin and destination cells of a directed edge.
- `get_cell_edges(cell: str) -> List[str]`: Get all directed edges originating from a cell.
- `get_edge_boundary(edge: str) -> List[Tuple[float, float]]`: Get the geographic boundary of a directed edge.
- `cell_to_local_ij(origin: str, cell: str) -> Tuple[int, int]`: Get the local IJ coordinates of a cell relative to an origin.
- `local_ij_to_cell(origin: str, i: int, j: int) -> str`: Convert local IJ coordinates back to a cell identifier.
- `great_circle_distance(lat1: float, lng1: float, lat2: float, lng2: float, unit: str) -> float`: Calculate great circle distance between two points.
- `cell_to_geodesic_area(cell: str, unit: str) -> float`: Get the geodesic (accurate) area of an H3 cell.
- `average_edge_length(resolution: int, unit: str) -> float`: Get the average edge length for cells at a resolution.
- `line_to_cells(start_lat: float, start_lng: float, end_lat: float, end_lng: float, resolution: int) -> List[str]`: Convert a line segment to H3 cells it passes through.
- `point_distance_to_cell_center(lat: float, lng: float, cell: str) -> float`: Calculate distance from a point to a cell's center.
- `get_resolution_stats(resolution: int) -> Dict[str, Any]`: Get statistics about a given H3 resolution level.
- `validate_cell_set(cells: List[str]) -> Dict[str, Any]`: Validate a set of H3 cells comprehensively.

### H3MLFeatureEngine
 H3 Machine Learning Feature Engineering.

**Methods**:
- `create_spatial_features(target_column: str, neighbor_rings: int) -> Dict[str, Any]`: Create spatial features for machine learning models.
- `create_demand_forecasting_features(demand_column: str, time_column: str) -> Dict[str, Any]`: Create features specifically for demand forecasting models.

### H3DisasterResponse
 H3 methods for disaster response and environmental monitoring.

**Methods**:
- `analyze_evacuation_zones(hazard_column: str, population_column: str, evacuation_radius_km: float) -> Dict[str, Any]`: Analyze evacuation zones based on hazard locations.
- `monitor_environmental_changes(baseline_column: str, current_column: str, change_threshold: float) -> Dict[str, Any]`: Monitor environmental changes using H3 spatial analysis.

### H3PerformanceOptimizer
 H3 Performance Optimization and Benchmarking.

**Methods**:
- `benchmark_h3_operations(test_coordinates: List[Tuple[float, float]], resolutions: List[int]) -> Dict[str, Any]`: Benchmark H3 operations performance.
- `optimize_grid_resolution(area_km2: float, target_cells: int, analysis_type: str) -> Dict[str, Any]`: Recommend optimal H3 resolution for given area and analysis type.

### H3Utils
 General utility functions for H3 operations.

**Methods**:
- `validate_h3_index_format(h3_index: str) -> bool`: Validate H3 index format (basic check).
- `estimate_resolution_from_area(area_km2: float) -> int`: Estimate appropriate H3 resolution based on desired area.
- `format_area(area_km2: float) -> str`: Format area value with appropriate units.
- `calculate_grid_bounds(cells: List) -> Tuple[float, float, float, float]`: Calculate bounding box for a list of cells.
- `generate_grid_summary(cells: List) -> Dict[str, Any]`: Generate summary statistics for a grid of cells.

### H3Converter
 Conversion utilities for H3 data formats.

**Methods**:
- `cells_to_coordinates(cells: List) -> List[Tuple[float, float]]`: Extract coordinates from H3 cells.
- `cells_to_dict(cells: List) -> List[Dict[str, Any]]`: Convert H3 cells to list of dictionaries.
- `dict_to_geojson(cell_dict: Dict[str, Any]) -> Dict[str, Any]`: Convert cell dictionary to GeoJSON feature.

### H3Optimizer
 Optimization utilities for H3 operations.

**Methods**:
- `time_operation(operation_name: str, func, *args, **kwargs)`: Time an operation and record performance statistics.
- `get_performance_report() -> Dict[str, Any]`: Get performance statistics report.
- `suggest_optimizations(cells: List) -> List[str]`: Suggest optimizations based on grid characteristics.

### H3Cache
 Caching utilities for H3 operations.

**Methods**:
- `get(key: str) -> Optional[Any]`: Get item from cache.
- `put(key: str, value: Any)`: Put item in cache.
- `clear()`: Clear all cached items.
- `size() -> int`: Get current cache size.
- `stats() -> Dict[str, Any]`: Get cache statistics.

### H3MapVisualizer
 Interactive map visualizations for H3 grids using Folium and Plotly.

**Methods**:
- `create_folium_map(value_column: Optional[str], color_scheme: str, **kwargs) -> 'folium.Map'`: Create interactive Folium map with H3 grid overlay.
- `create_heatmap(value_column: str, **kwargs) -> 'folium.Map'`: Create heatmap visualization using cell centroids.

### H3StaticVisualizer
 Static plot visualizations for H3 grids using Matplotlib and Seaborn.

**Methods**:
- `plot_grid_overview(figsize: Tuple[int, int], save_path: Optional[str])`: Create grid overview plot.
- `plot_hexagon_grid(value_column: Optional[str], figsize: Tuple[int, int], save_path: Optional[str])`: Plot actual hexagonal grid with proper hexagon shapes.
- `plot_connectivity_analysis(figsize: Tuple[int, int], save_path: Optional[str])`: Plot connectivity analysis results.

### H3InteractiveVisualizer
 Interactive visualizations using Plotly for H3 grids.

**Methods**:
- `create_plotly_map(value_column: Optional[str], **kwargs) -> 'go.Figure'`: Create interactive Plotly map with H3 hexagons.
- `create_dashboard(**kwargs) -> 'go.Figure'`: Create dashboard with multiple views.

### H3AnimationVisualizer
 Animation visualizations for H3 grids showing temporal changes.

**Methods**:
- `create_temporal_animation(value_column: str, save_path: Optional[str], **kwargs) -> 'go.Figure'`: Create animated visualization showing temporal changes.

### create_sample_datasets
 `create_sample_datasets() -> Dict[str, H3Dataset]` Create sample H3 datasets for testing and demonstration.

### decorator
 `decorator(func)`

### wrapper
 `wrapper(self, *args, **kwargs)`

### get_neighbors_in_set
 `get_neighbors_in_set(cell: str) -> List[str]` Get neighbors of a cell that are in our cell set.

### expand_cluster
 `expand_cluster(cell: str, neighbors: List[str], cluster: List[str])` Expand cluster from seed cell.

### get_resolution_info
 `get_resolution_info(resolution: int) -> Dict[str, Any]` Get information about an H3 resolution level.

### find_optimal_resolution
 `find_optimal_resolution(area_km2: float, target_cells: int) -> Dict[str, Any]` Find the optimal H3 resolution for a given area or target number of cells.

### create_h3_grid_for_bounds
 `create_h3_grid_for_bounds(min_lat: float, max_lat: float, min_lng: float, max_lng: float, resolution: int) -> List[str]` Create an H3 grid covering the specified bounding box.

### coordinate_to_cell
 `coordinate_to_cell(lat: float, lng: float, resolution: int) -> str` Convert latitude/longitude coordinates to H3 cell index.

### cell_to_coordinates
 `cell_to_coordinates(h3_index: str) -> Tuple[float, float]` Convert H3 cell index to latitude/longitude coordinates.

### cell_to_boundary
 `cell_to_boundary(h3_index: str, geo_json: bool) -> List[Tuple[float, float]]` Get the boundary coordinates of an H3 cell.

### cells_to_geojson
 `cells_to_geojson(h3_indices: List[str], properties: Optional[Dict[str, Any]]) -> Dict[str, Any]` Convert H3 cell indices to GeoJSON FeatureCollection.

### grid_disk
 `grid_disk(h3_index: str, k: int) -> List[str]` Get all H3 cells within k rings of the given cell (k-ring).

### grid_ring
 `grid_ring(h3_index: str, k: int) -> List[str]` Get H3 cells at exactly k rings from the given cell.

### grid_distance
 `grid_distance(h3_index1: str, h3_index2: str) -> int` Calculate the grid distance between two H3 cells.

### grid_path
 `grid_path(h3_index1: str, h3_index2: str) -> List[str]` Find a path between two H3 cells.

### cell_to_parent
 `cell_to_parent(h3_index: str, parent_resolution: int) -> str` Get the parent cell at a coarser resolution.

### cell_to_children
 `cell_to_children(h3_index: str, child_resolution: int) -> List[str]` Get the children cells at a finer resolution.

### compact_cells
 `compact_cells(h3_indices: Set[str]) -> List[str]` Compact a set of H3 cells by replacing clusters with their parents.

### uncompact_cells
 `uncompact_cells(h3_indices: Set[str], target_resolution: int) -> List[str]` Uncompact a set of H3 cells to a target resolution.

### polygon_to_cells
 `polygon_to_cells(polygon_coords: List[Tuple[float, float]], resolution: int) -> List[str]` Get H3 cells that cover a polygon.

### cells_to_polygon
 `cells_to_polygon(h3_indices: Set[str]) -> List[Tuple[float, float]]` Create a polygon boundary from a set of H3 cells.

### cell_area
 `cell_area(h3_index: str, unit: str) -> float` Calculate the area of an H3 cell.

### cells_area
 `cells_area(h3_indices: Set[str], unit: str) -> float` Calculate the total area of a set of H3 cells.

### neighbor_cells
 `neighbor_cells(h3_index: str) -> List[str]` Get the immediate neighbors of an H3 cell.

### cell_resolution
 `cell_resolution(h3_index: str) -> int` Get the resolution of an H3 cell.

### is_valid_cell
 `is_valid_cell(h3_index: str) -> bool` Check if an H3 index is valid.

### are_neighbor_cells
 `are_neighbor_cells(h3_index1: str, h3_index2: str) -> bool` Check if two H3 cells are neighbors.

### cells_intersection
 `cells_intersection(cells1: Set[str], cells2: Set[str]) -> List[str]` Find the intersection of two sets of H3 cells.

### cells_union
 `cells_union(cells1: Set[str], cells2: Set[str]) -> List[str]` Find the union of two sets of H3 cells.

### cells_difference
 `cells_difference(cells1: Set[str], cells2: Set[str]) -> List[str]` Find the difference between two sets of H3 cells.

### grid_statistics
 `grid_statistics(h3_indices: Set[str]) -> Dict[str, Any]` Calculate statistics for a set of H3 cells.

### cell_to_boundary
 `cell_to_boundary(h3_index: str, geo_json_format: bool) -> Union[List[Tuple[float, float]], List[List[float]]]` Get boundary coordinates of H3 cell as polygon vertices.

### cells_to_geojson
 `cells_to_geojson(h3_indices: List[str], properties: Optional[Dict[str, Dict[str, Any]]]) -> Dict[str, Any]` Convert list of H3 cell indices to GeoJSON FeatureCollection.

### grid_disk
 `grid_disk(h3_index: str, k: int) -> List[str]` Get all cells within k distance of the given cell (filled disk).

### grid_ring
 `grid_ring(h3_index: str, k: int) -> List[str]` Get all cells at exactly k distance from the given cell (hollow ring).

### grid_distance
 `grid_distance(h3_index1: str, h3_index2: str) -> int` Calculate grid distance between two H3 cells.

### grid_path
 `grid_path(h3_index1: str, h3_index2: str) -> List[str]` Find path of cells between two H3 cells.

### cell_to_parent
 `cell_to_parent(h3_index: str, parent_resolution: int) -> str` Get parent cell at coarser resolution.

### cell_to_children
 `cell_to_children(h3_index: str, child_resolution: int) -> List[str]` Get child cells at finer resolution.

### compact_cells
 `compact_cells(h3_indices: List[str]) -> List[str]` Compact set of cells to mixed resolutions for efficiency.

### uncompact_cells
 `uncompact_cells(h3_indices: List[str], target_resolution: int) -> List[str]` Uncompact cells to uniform resolution.

### polygon_to_cells
 `polygon_to_cells(polygon_coords: Union[List[Tuple[float, float]], Dict[str, Any]], resolution: int, geo_json_format: bool) -> List[str]` Convert polygon to H3 cells that cover the area.

### cells_to_polygon
 `cells_to_polygon(h3_indices: List[str]) -> List[Tuple[float, float]]` Convert H3 cells to polygon boundary (convex hull approximation).

### cell_area
 `cell_area(h3_index: str, unit: str) -> float` Get area of H3 cell.

### cells_area
 `cells_area(h3_indices: List[str], unit: str) -> float` Get total area of multiple H3 cells.

### neighbor_cells
 `neighbor_cells(h3_index: str) -> List[str]` Get immediate neighbor cells (k=1 ring, excluding center).

### cell_resolution
 `cell_resolution(h3_index: str) -> int` Get resolution of H3 cell.

### is_valid_cell
 `is_valid_cell(h3_index: str) -> bool` Check if H3 cell index is valid.

### are_neighbor_cells
 `are_neighbor_cells(h3_index1: str, h3_index2: str) -> bool` Check if two H3 cells are neighbors.

### cells_intersection
 `cells_intersection(cells1: List[str], cells2: List[str]) -> List[str]` Find intersection of two sets of H3 cells.

### cells_union
 `cells_union(cells1: List[str], cells2: List[str]) -> List[str]` Find union of two sets of H3 cells.

### cells_difference
 `cells_difference(cells1: List[str], cells2: List[str]) -> List[str]` Find difference of two sets of H3 cells (cells1 - cells2).

### grid_statistics
 `grid_statistics(h3_indices: List[str]) -> Dict[str, Any]` Calculate statistics for a set of H3 cells.

### cross_product
 `cross_product(o, a, b)`

## Capabilities

- **25 classes** for core functionality
- **56 functions** for utility operations

## Integration

- **Location**: `src/geo_infer_space/backends/h3`
- **Type**: Directory Node
