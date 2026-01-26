# utils
 ## Overview
 This directory contains utils components. It includes 2 Python modules. ## Components
 ### helper
s
.py Helper utilities for GEO-INFER-COG **Functions**: `load_cognitive_profile`, `save_cognitive_profile`, `load_cognitive_model`, `save_cognitive_model`, `create_default_cognitive_config`, `setup_cognitive_logging`, `calculate_cognitive_load`, `format_spatial_data_for_display`, `_simplify_geometry`, `_extract_key_properties`, `_calculate_display_priority`, `create_performance_report`, `export_cognitive_insights`, `_format_insights_as_markdown`, `validate_file_path`, `create_directory_structure`, `cleanup_temp_files`, `count_coordinates` ### validatio
n
.py Validation utilities for GEO-INFER-COG **Functions**: `validate_spatial_data`, `validate_geometry`, `validate_point_coordinates`, `validate_linestring_coordinates`, `validate_polygon_coordinates`, `validate_multipoint_coordinates`, `validate_multilinestring_coordinates`, `validate_multipolygon_coordinates`, `check_topological_validity`, `do_edges_intersect`, `check_data_completeness`, `validate_cognitive_model`, `validate_perception_model`, `validate_reasoning_model`, `validate_memory_model`, `check_model_consistency`, `validate_user_profile`, `validate_configuration`, `validate_core_config`, `generate_default_config`, `ccw`, `flatten_coords` ## Usage
 See individual component documentation for usage examples. ## Integration
 This directory integrates with other module components and may be used by higher-level modules. 