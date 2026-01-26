# Agent
: core ## Scope
 This directory contains core components for the module. It provides 11 classes and 0 functions. ## Classes
 and Functions ### CognitiveStat
e
 Represents the current cognitive state of the processing engine. **Methods**: - `update_attention(focus_areas: Dict[str, float]) -> None`: Update attention focus areas with normalized weights. - `add_to_working_memory(key: str, value: Any, importance: float) -> None`: Add item to working memory with importance weighting. - `retrieve_from_memory(key: str) -> Optional[Any]`: Retrieve item from working memory and update access patterns. - `get_memory_utilization() -> Dict[str, float]`: Get memory utilization statistics. ### CognitiveProcessingEngin
e
 Core cognitive processing engine for spatial cognition modeling. **Methods**: - `process_spatial_input(spatial_data: Dict[str, Any], context: Optional[Dict[str, Any]], user_profile: Optional[UserCognitiveProfile]) -> Dict[str, Any]`: Process spatial input through the cognitive pipeline. - `update_cognitive_models(training_data: Dict[str, Any], learning_rate: float) -> Dict[str, Any]`: Update cognitive models based on training data. - `get_performance_summary() -> Dict[str, Any]`: Get performance summary of the cognitive engine. - `save_cognitive_state(filepath: str) -> None`: Save current cognitive state to file. - `load_cognitive_state(filepath: str) -> None`: Load cognitive state from file. ### SpatialMemoryIte
m
 Represents an item stored in spatial memory. **Methods**: - `calculate_retrieval_probability() -> float`: Calculate probability of successful retrieval. - `update_access() -> None`: Update access statistics when item is retrieved. - `decay_memory() -> None`: Apply memory decay over time. ### MemoryConsolidatio
n
 Handles memory consolidation from working to long-term memory. **Methods**: - `check_for_consolidation(working_memory_items: List[SpatialMemoryItem]) -> List[SpatialMemoryItem]`: Check which working memory items are ready for consolidation. ### SpatialMemoryMode
l
 spatial memory model for geospatial knowledge management. **Methods**: - `store_spatial_memory(content: Dict[str, Any], memory_type: str, importance: float, spatial_context: Optional[Dict[str, Any]], metadata: Optional[Dict[str, Any]]) -> str`: Store spatial information in memory. - `retrieve_spatial_memory(item_id: str, context: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]`: Retrieve spatial information from memory. - `update_memory(perception_result: Dict[str, Any], reasoning_result: Dict[str, Any], cognitive_state: Any) -> Dict[str, Any]`: Update memory based on perception and reasoning results. - `search_memory(query: Dict[str, Any], memory_types: Optional[List[str]], limit: int) -> List[Dict[str, Any]]`: Search memory using spatial, temporal, or conceptual criteria. - `get_memory_statistics() -> Dict[str, Any]`: Get memory system statistics. - `export_memory_knowledge_graph() -> Dict[str, Any]`: Export memory contents as a knowledge graph for analysis. - `update_model(training_data: Dict[str, Any], learning_rate: float) -> Dict[str, Any]`: Update memory model based on training data. - `get_status() -> Dict[str, Any]`: Get current status of the memory model. ### SpatialPercep
t
 Represents a perceived spatial element with cognitive properties. **Methods**: - `calculate_attention_priority(task_context: str) -> float`: Calculate attention priority based on task context. ### AttentionMode
l
 Models spatial attention allocation in human perception. **Methods**: - `allocate_attention(spatial_elements: List[SpatialPercept], task_priority: str) -> Dict[str, float]`: Allocate attention across spatial elements. ### SpatialPerceptionMode
l
 spatial perception model for human-like spatial understanding. **Methods**: - `process_spatial_input(spatial_data: Dict[str, Any], context: Optional[Dict[str, Any]], user_profile: Optional[UserCognitiveProfile]) -> Dict[str, Any]`: Process spatial input through perceptual modeling pipeline. - `update_model(training_data: Dict[str, Any], learning_rate: float) -> Dict[str, Any]`: Update perception model based on training data. - `get_status() -> Dict[str, Any]`: Get current status of the perception model. ### SpatialRelatio
n
 Represents a qualitative spatial relationship between regions. **Methods**: - `is_consistent_with(other_relation: 'SpatialRelation') -> bool`: Check if this relation is consistent with another relation. ### ReasoningSte
p
 Represents a single step in a spatial reasoning chain. ### SpatialReasoningEngin
e
 spatial reasoning engine for human-like geospatial inference. **Methods**: - `reason_about_space(spatial_data: Dict[str, Any], perception_result: Dict[str, Any], cognitive_state: Any) -> Dict[str, Any]`: Perform spatial reasoning on input data. - `update_model(training_data: Dict[str, Any], learning_rate: float) -> Dict[str, Any]`: Update reasoning model based on training data. - `get_status() -> Dict[str, Any]`: Get current status of the reasoning engine. ## Capabilities
 - **11 classes** for core functionality ## Integration
 - **Location**: `GEO-INFER-COG/src/geo_infer_cog/core` - **Type**: Directory Node 