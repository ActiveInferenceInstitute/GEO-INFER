# Agent
: utils ## Scope
 This directory contains utils components for the module. It provides 0 classes and 40 functions. ## Classes
 and Functions ### load_cognitive_profil
e
 `load_cognitive_profile(user_id: str, profile_path: str) -> Optional[UserCognitiveProfile]` Load user cognitive profile from file. ### save_cognitive_profil
e
 `save_cognitive_profile(profile: UserCognitiveProfile, profile_path: str) -> bool` Save user cognitive profile to file. ### load_cognitive_mode
l
 `load_cognitive_model(model_path: str, model_type: str) -> Dict[str, Any]` Load cognitive model from file. ### save_cognitive_mode
l
 `save_cognitive_model(model_config: Dict[str, Any], model_path: str, model_type: str) -> bool` Save cognitive model configuration to file. ### create_default_cognitive_confi
g
 `create_default_cognitive_config() -> Dict[str, Any]` Create default cognitive processing configuration. ### setup_cognitive_loggin
g
 `setup_cognitive_logging(config: Dict[str, Any]) -> None` Setup logging configuration for cognitive processing. ### calculate_cognitive_loa
d
 `calculate_cognitive_load(spatial_data: Dict[str, Any], user_profile: Optional[UserCognitiveProfile]) -> float` Calculate cognitive load for processing spatial data. ### format_spatial_data_for_displa
y
 `format_spatial_data_for_display(spatial_data: Dict[str, Any], user_profile: Optional[UserCognitiveProfile]) -> Dict[str, Any]` Format spatial data for user-friendly display. ### create_performance_repor
t
 `create_performance_report(processing_results: List[Dict[str, Any]]) -> Dict[str, Any]` Create performance report from processing results. ### export_cognitive_insight
s
 `export_cognitive_insights(insights: Dict[str, Any], format: str) -> Union[str, Dict[str, Any]]` Export cognitive insights in various formats. ### validate_file_pat
h
 `validate_file_path(file_path: str, required_extension: Optional[str]) -> bool` Validate file path and check if file exists and is readable. ### create_directory_structur
e
 `create_directory_structure(base_path: str) -> None` Create standard directory structure for cognitive processing. ### cleanup_temp_file
s
 `cleanup_temp_files(temp_dir: str, max_age_hours: int) -> int` Clean up temporary files older than specified age. ### count_coordinate
s
 `count_coordinates(c)` ### validate_spatial_dat
a
 `validate_spatial_data(spatial_data: Dict[str, Any]) -> Dict[str, Any]` Validate spatial data for geometric consistency and completeness. ### validate_geometr
y
 `validate_geometry(geometry: Dict[str, Any]) -> Dict[str, Any]` Validate geometry for topological consistency and coordinate validity. ### validate_point_coordinate
s
 `validate_point_coordinates(coords: List[float]) -> Dict[str, Any]` Validate Point coordinates. ### validate_linestring_coordinate
s
 `validate_linestring_coordinates(coords: List[List[float]]) -> Dict[str, Any]` Validate LineString coordinates. ### validate_polygon_coordinate
s
 `validate_polygon_coordinates(coords: List[List[List[float]]]) -> Dict[str, Any]` Validate Polygon coordinates. ### validate_multipoint_coordinate
s
 `validate_multipoint_coordinates(coords: List[List[float]]) -> Dict[str, Any]` Validate MultiPoint coordinates. ### validate_multilinestring_coordinate
s
 `validate_multilinestring_coordinates(coords: List[List[List[float]]]) -> Dict[str, Any]` Validate MultiLineString coordinates. ### validate_multipolygon_coordinate
s
 `validate_multipolygon_coordinates(coords: List[List[List[List[float]]]]) -> Dict[str, Any]` Validate MultiPolygon coordinates. ### check_topological_validit
y
 `check_topological_validity(geometry: Dict[str, Any]) -> Dict[str, Any]` Check topological validity of geometry. ### do_edges_intersec
t
 `do_edges_intersect(p1: List[float], p2: List[float], p3: List[float], p4: List[float]) -> bool` Check if two line segments intersect. ### check_data_completenes
s
 `check_data_completeness(spatial_data: Dict[str, Any]) -> Dict[str, Any]` Check completeness of spatial data. ### validate_cognitive_mode
l
 `validate_cognitive_model(model_config: Dict[str, Any], model_type: str) -> Dict[str, Any]` Validate cognitive model configuration and parameters. ### validate_perception_mode
l
 `validate_perception_model(config: Dict[str, Any]) -> Dict[str, Any]` Validate perception model configuration. ### validate_reasoning_mode
l
 `validate_reasoning_model(config: Dict[str, Any]) -> Dict[str, Any]` Validate reasoning model configuration. ### validate_memory_mode
l
 `validate_memory_model(config: Dict[str, Any]) -> Dict[str, Any]` Validate memory model configuration. ### check_model_consistenc
y
 `check_model_consistency(config: Dict[str, Any], model_type: str) -> Dict[str, Any]` Check consistency of model configuration. ### validate_user_profil
e
 `validate_user_profile(profile_data: Dict[str, Any]) -> Dict[str, Any]` Validate user cognitive profile data. ### validate_configuratio
n
 `validate_configuration(config: Dict[str, Any], module_name: str) -> Dict[str, Any]` Validate module configuration for consistency and completeness. ### validate_core_confi
g
 `validate_core_config(core_config: Dict[str, Any]) -> Dict[str, Any]` Validate core module configuration. ### generate_default_confi
g
 `generate_default_config(module_name: str) -> Dict[str, Any]` Generate default configuration for a module. ### cc
w
 `ccw(A: List[float], B: List[float], C: List[float]) -> bool` ### flatten_coord
s
 `flatten_coords(c)` ## Capabilities
 - **40 functions** for utility operations ## Integration
 - **Location**: `GEO-INFER-COG/src/geo_infer_cog/utils` - **Type**: Directory Node 