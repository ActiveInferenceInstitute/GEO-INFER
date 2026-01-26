# Agent
: analytics ## Scope
 This directory contains analytics components for the module. It provides 3 classes and 51 functions. ## Classes
 and Functions ### PointClou
d
 Point cloud data structure for spatial analysis. **Methods**: - `num_points() -> int`: Number of points in the cloud. - `bounds() -> Tuple[float, float, float, float, float, float]`: Bounding box as (minx, miny, minz, maxx, maxy, maxz). - `to_geoDataFrame(crs: str) -> gpd.GeoDataFrame`: Convert to GeoDataFrame with Point geometries. ### SpatioTemporalAnalyze
r
 analyzer for spatio-temporal patterns. **Methods**: - `analyze_spatial_time_series(data: List[Dict[str, Any]], cell_column: str, timestamp_column: str, value_column: str, temporal_resolution: str) -> Dict[str, Any]`: Analyze time series for each spatial cell. - `detect_spatiotemporal_clusters(data: List[Dict[str, Any]], cell_column: str, timestamp_column: str, spatial_eps: int, temporal_eps_hours: float, min_points: int) -> Dict[str, Any]`: Detect spatio-temporal clusters using ST-DBSCAN algorithm. - `compute_space_time_cube(data: List[Dict[str, Any]], cell_column: str, timestamp_column: str, value_column: str, temporal_bin_size: str, aggregation: str) -> Dict[str, Any]`: Create a space-time cube for 3D analysis (x, y, t). - `detect_emerging_hotspots(data: List[Dict[str, Any]], cell_column: str, timestamp_column: str, value_column: str, time_steps: int, threshold_percentile: float) -> Dict[str, Any]`: Detect emerging, intensifying, and diminishing hotspots. - `compute_spatiotemporal_autocorrelation(data: List[Dict[str, Any]], cell_column: str, timestamp_column: str, value_column: str, spatial_lag: int, temporal_lag_hours: float) -> Dict[str, Any]`: Compute space-time autocorrelation (space-time Moran's I). - `analyze_movement_patterns(trajectories: List[Dict[str, Any]], id_column: str, cell_column: str, timestamp_column: str) -> Dict[str, Any]`: Analyze movement patterns from trajectory data. - `kriging_spatiotemporal(known_data: List[Dict[str, Any]], target_cells: List[str], target_timestamp: datetime, cell_column: str, timestamp_column: str, value_column: str, spatial_range: int, temporal_range_hours: float) -> Dict[str, Any]`: Interpolate values using space-time kriging. ### TemporalAnalyze
r
 Analyzer for temporal patterns in spatial data. **Methods**: - `analyze_temporal_patterns(data: List[Dict[str, Any]], timestamp_column: str, value_column: str, temporal_resolution: str) -> Dict[str, Any]`: Analyze temporal patterns in data. ### spatial_interpolatio
n
 `spatial_interpolation(points_gdf: gpd.GeoDataFrame, value_column: str, grid_bounds: Tuple[float, float, float, float], grid_resolution: float, method: str, **kwargs) -> gpd.GeoDataFrame` Perform spatial interpolation on point data. ### clustering_analysi
s
 `clustering_analysis(points_gdf: gpd.GeoDataFrame, method: str, **kwargs) -> gpd.GeoDataFrame` Perform spatial clustering analysis on point data. ### hotspot_detectio
n
 `hotspot_detection(points_gdf: gpd.GeoDataFrame, value_column: Optional[str], method: str, **kwargs) -> gpd.GeoDataFrame` Detect spatial hotspots and coldspots. ### spatial_autocorrelatio
n
 `spatial_autocorrelation(points_gdf: gpd.GeoDataFrame, value_column: str, method: str) -> Dict[str, float]` Calculate global spatial autocorrelation statistics. ### variogram_analysi
s
 `variogram_analysis(points_gdf: gpd.GeoDataFrame, value_column: str, max_distance: Optional[float], n_lags: int) -> pd.DataFrame` Calculate experimental variogram for spatial data. ### shortest_pat
h
 `shortest_path(network_gdf: gpd.GeoDataFrame, start_point: Point, end_point: Point, weight_column: str, impedance_factor: float) -> Dict[str, Any]` Calculate shortest path between two points on a network. ### service_are
a
 `service_area(network_gdf: gpd.GeoDataFrame, center_point: Point, max_distance: float, weight_column: str) -> gpd.GeoDataFrame` Calculate service area (isochrone) from a center point. ### network_connectivit
y
 `network_connectivity(network_gdf: gpd.GeoDataFrame, weight_column: str) -> Dict[str, Any]` Analyze network connectivity metrics. ### routing_analysi
s
 `routing_analysis(network_gdf: gpd.GeoDataFrame, origins: List[Point], destinations: List[Point], weight_column: str) -> pd.DataFrame` Perform origin-destination routing analysis. ### accessibility_analysi
s
 `accessibility_analysis(network_gdf: gpd.GeoDataFrame, origins: List[Point], destinations: List[Point], max_distance: float, weight_column: str) -> pd.DataFrame` Calculate accessibility metrics from origins to destinations. ### load_point_clou
d
 `load_point_cloud(file_path: str) -> PointCloud` Load point cloud from various file formats. ### point_cloud_filterin
g
 `point_cloud_filtering(point_cloud: PointCloud, filter_type: str, **kwargs) -> PointCloud` Apply filtering operations to point cloud data. ### feature_extractio
n
 `feature_extraction(point_cloud: PointCloud, neighborhood_size: int, search_radius: float) -> pd.DataFrame` Extract geometric features from point cloud neighborhoods. ### classificatio
n
 `classification(point_cloud: PointCloud, features_df: pd.DataFrame, method: str, **kwargs) -> PointCloud` Classify point cloud points into different categories. ### surface_generatio
n
 `surface_generation(point_cloud: PointCloud, method: str, grid_resolution: float, **kwargs) -> Union[gpd.GeoDataFrame, np.ndarray]` Generate surfaces from point cloud data. ### terrain_analysi
s
 `terrain_analysis(dem_path: str, output_dir: str, analyses: List[str]) -> Dict[str, str]` Perform terrain analysis on a Digital Elevation Model. ### map_algebr
a
 `map_algebra(raster_paths: List[str], expression: str, output_path: str, nodata_value: float) -> str` Perform map algebra operations on multiple rasters. ### focal_statistic
s
 `focal_statistics(raster_path: str, output_path: str, statistic: str, window_size: int, circular: bool) -> str` Calculate focal statistics for a raster. ### zonal_statistic
s
 `zonal_statistics(raster_path: str, zones_gdf: gpd.GeoDataFrame, statistics: List[str]) -> gpd.GeoDataFrame` Calculate zonal statistics for raster values within polygon zones. ### raster_overla
y
 `raster_overlay(raster_paths: List[str], output_path: str, method: str, weights: Optional[List[float]]) -> str` Overlay multiple rasters using specified method. ### image_processin
g
 `image_processing(raster_path: str, output_path: str, operation: str, **kwargs) -> str` Perform image processing operations on raster data. ### are_neighbor
s
 `are_neighbors(p1, p2)` Check if two points are ST-neighbors. ### get_neighbor
s
 `get_neighbors(point_idx)` Get all neighbors of a point. ### buffer_and_intersec
t
 `buffer_and_intersect(points_gdf: gpd.GeoDataFrame, polygons_gdf: gpd.GeoDataFrame, buffer_distance_meters: Union[int, float]) -> gpd.GeoDataFrame` Buffer points and intersect with polygons. ### overlay_analysi
s
 `overlay_analysis(gdf1: gpd.GeoDataFrame, gdf2: gpd.GeoDataFrame, operation: str, keep_geom_type: bool) -> gpd.GeoDataFrame` Perform overlay operations between two GeoDataFrames. ### proximity_analysi
s
 `proximity_analysis(gdf1: gpd.GeoDataFrame, gdf2: gpd.GeoDataFrame, max_distance: Optional[float]) -> gpd.GeoDataFrame` Calculate proximity metrics between two sets of geometries. ### spatial_join_analysi
s
 `spatial_join_analysis(left_gdf: gpd.GeoDataFrame, right_gdf: gpd.GeoDataFrame, predicate: str, how: str) -> gpd.GeoDataFrame` Perform spatial join between two GeoDataFrames. ### geometric_calculation
s
 `geometric_calculations(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame` Calculate geometric properties for geometries. ### topology_operation
s
 `topology_operations(gdf: gpd.GeoDataFrame, operation: str, tolerance: float) -> gpd.GeoDataFrame` Perform topology operations on geometries. ## Capabilities
 - **3 classes** for core functionality - **51 functions** for utility operations ## Integration
 - **Location**: `GEO-INFER-SPACE/src/geo_infer_space/analytics` - **Type**: Directory Node 