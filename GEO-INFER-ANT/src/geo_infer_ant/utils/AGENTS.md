# Agent
: utils ## Scope
 This directory contains utils components for the module. It provides 7 classes and 9 functions. ## Classes
 and Functions ### SwarmConfi
g
 Swarm configuration dataclass. ### AlgorithmConfi
g
 Algorithm configuration dataclass. ### StigmergyConfi
g
 Stigmergy configuration dataclass. ### SpatialConfi
g
 Spatial configuration dataclass. ### PerformanceConfi
g
 Performance configuration dataclass. ### LoggingConfi
g
 Logging configuration dataclass. ### AntModuleConfi
g
 ANT module configuration. ### load_confi
g
 `load_config(config_path: Optional[Union[str, Path]], config_dict: Optional[Dict[str, Any]], validate_schema: bool) -> AntModuleConfig` Load configuration from file or dictionary. ### validate_confi
g
 `validate_config(config: Union[Dict[str, Any], AntModuleConfig]) -> bool` Validate configuration against schema. ### save_confi
g
 `save_config(config: AntModuleConfig, config_path: Union[str, Path], format: str) -> None` Save configuration to file. ### get_default_confi
g
 `get_default_config() -> AntModuleConfig` Get default configuration. ### update_confi
g
 `update_config(config: AntModuleConfig, updates: Dict[str, Any]) -> AntModuleConfig` Update configuration with values. ## Capabilities
 - **7 classes** for core functionality - **9 functions** for utility operations ## Integration
 - **Location**: `GEO-INFER-ANT/src/geo_infer_ant/utils` - **Type**: Directory Node 