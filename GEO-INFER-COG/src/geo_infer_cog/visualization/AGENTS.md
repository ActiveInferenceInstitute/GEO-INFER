# Agent
: visualization ## Scope
 This directory contains visualization components for the module. It provides 3 classes and 2 functions. ## Classes
 and Functions ### VisualizationElemen
t
 Represents a visual element in a cognitive visualization. **Methods**: - `get_visual_complexity() -> float`: Calculate visual complexity of this element. ### ColorSchem
e
 Manages color schemes optimized for human perception and accessibility. **Methods**: - `get_perceptually_uniform_colors(n_colors: int) -> List[str]`: Generate perceptually uniform colors for data visualization. - `get_cognitive_load_colors(load_level: str, n_colors: int) -> List[str]`: Get colors optimized for specific cognitive load levels. ### HumanCenteredVisualize
r
 Human-centered visualization adapter for geospatial data. **Methods**: - `create_optimized_map(spatial_data: Dict[str, Any], user_cognitive_profile: Optional[UserCognitiveProfile], task_context: str, display_constraints: Optional[Dict[str, Any]]) -> Dict[str, Any]`: Create a cognitively optimized map visualization. - `communicate_uncertainty(spatial_predictions: Dict[str, Any], uncertainty_quantification: Dict[str, Any], user_risk_tolerance: str) -> Dict[str, Any]`: Communicate spatial uncertainty in a user-appropriate manner. - `apply_perceptual_grouping(spatial_data: Dict[str, Any], grouping_principles: List[str]) -> Dict[str, Any]`: Apply perceptual grouping principles to spatial data. - `get_status() -> Dict[str, Any]`: Get current status of the visualizer. ### extract_coord
s
 `extract_coords(c)` ### extract_coord
s
 `extract_coords(c)` ## Capabilities
 - **3 classes** for core functionality - **2 functions** for utility operations ## Integration
 - **Location**: `GEO-INFER-COG/src/geo_infer_cog/visualization` - **Type**: Directory Node 