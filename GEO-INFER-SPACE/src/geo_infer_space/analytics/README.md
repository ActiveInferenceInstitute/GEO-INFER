# analytics
 ## Overview
 This directory contains analytics components. It includes 7 Python modules. ## Components
 ### geostatistic
s
.py Geostatistics module for spatial analysis. **Functions**: `spatial_interpolation`, `clustering_analysis`, `hotspot_detection`, `spatial_autocorrelation`, `variogram_analysis`, `_getis_ord_gi_star`, `_local_morans_i`, `_kernel_density_hotspots`, `_idw_interpolation`, `_kriging_interpolation` ### networ
k
.py Network analysis module for spatial analysis. **Functions**: `shortest_path`, `service_area`, `network_connectivity`, `routing_analysis`, `accessibility_analysis`, `_create_graph_from_gdf`, `_find_nearest_node` ### point_clou
d
.py Point cloud processing module for spatial analysis. **Classes**: `PointCloud` **Functions**: `load_point_cloud`, `point_cloud_filtering`, `feature_extraction`, `classification`, `surface_generation`, `_load_las_file`, `_load_text_file`, `_statistical_outlier_filter`, `_radius_outlier_filter`, `_voxel_grid_filter`, `_ground_filter`, `_filter_point_cloud`, `_calculate_point_features`, `_ground_vegetation_classification`, `_building_detection`, `_clustering_classification`, `_delaunay_triangulation`, `_grid_interpolation`, `_contour_generation` ### raste
r
.py Raster operations module for spatial analysis. **Functions**: `terrain_analysis`, `map_algebra`, `focal_statistics`, `zonal_statistics`, `raster_overlay`, `image_processing`, `_write_raster` ### spatiotempora
l
.py Spatio-Temporal Analysis Module for GEO-INFER-SPACE. **Classes**: `SpatioTemporalAnalyzer` **Functions**: `are_neighbors`, `get_neighbors` ### tempora
l
.py Temporal Analytics Module for GEO-INFER-SPACE. **Classes**: `TemporalAnalyzer` ### vecto
r
.py Vector operations module for spatial analysis. **Functions**: `buffer_and_intersect`, `overlay_analysis`, `proximity_analysis`, `spatial_join_analysis`, `geometric_calculations`, `topology_operations` ## Usage
 See individual component documentation for usage examples. ## Integration
 This directory integrates with other module components and may be used by higher-level modules. 