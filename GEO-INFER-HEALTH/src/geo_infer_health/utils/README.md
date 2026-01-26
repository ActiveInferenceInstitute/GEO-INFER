# utils
 ## Overview
 This directory contains utils components. It includes 4 Python modules. ## Components
 ### advanced_geospatia
l
.py geospatial utilities for GEO-INFER-HEALTH. **Functions**: `project_to_utm`, `buffer_point`, `spatial_clustering`, `calculate_spatial_statistics`, `validate_geographic_bounds`, `interpolate_points`, `find_centroid`, `calculate_voronoi_regions`, `calculate_spatial_autocorrelation`, `_normal_cdf`, `calculate_hotspot_statistics`, `region_query`, `expand_cluster` ### confi
g
.py Configuration utilities for GEO-INFER-HEALTH module. **Classes**: `HealthConfig` **Functions**: `load_yaml_config`, `load_json_config`, `validate_config`, `merge_configs`, `resolve_environment_variables`, `get_default_config_path`, `load_config`, `save_config`, `get_config_value`, `create_default_config`, `get_global_config`, `reload_global_config`, `resolve_value`, `replace_var` ### geospatial_util
s
.py Module containing 2 functions. **Functions**: `haversine_distance`, `create_bounding_box` ### loggin
g
.py Logging utilities for GEO-INFER-HEALTH module. **Classes**: `PerformanceLogger` **Functions**: `setup_logging`, `get_logger`, `log_function_call`, `log_performance`, `create_log_context`, `setup_structured_logging`, `decorator`, `wrapper` ## Usage
 See individual component documentation for usage examples. ## Integration
 This directory integrates with other module components and may be used by higher-level modules. 