# Agent
: utils

## Scope
 This directory contains utils components for the module. It provides 7 classes and 9 functions.

## Classes
 and Functions

### SwarmConfig
 Swarm configuration dataclass.

### AlgorithmConfig
 Algorithm configuration dataclass.

### StigmergyConfig
 Stigmergy configuration dataclass.

### SpatialConfig
 Spatial configuration dataclass.

### PerformanceConfig
 Performance configuration dataclass.

### LoggingConfig
 Logging configuration dataclass.

### AntModuleConfig
 ANT module configuration.

### load_config
 `load_config(config_path: Optional[Union[str, Path]], config_dict: Optional[Dict[str, Any]], validate_schema: bool) -> AntModuleConfig` Load configuration from file or dictionary.

### validate_config
 `validate_config(config: Union[Dict[str, Any], AntModuleConfig]) -> bool` Validate configuration against schema.

### save_config
 `save_config(config: AntModuleConfig, config_path: Union[str, Path], format: str) -> None` Save configuration to file.

### get_default_config
 `get_default_config() -> AntModuleConfig` Get default configuration.

### update_config
 `update_config(config: AntModuleConfig, updates: Dict[str, Any]) -> AntModuleConfig` Update configuration with values.

## Capabilities

- **7 classes** for core functionality
- **9 functions** for utility operations

## Integration

- **Location**: `GEO-INFER-ANT/src/geo_infer_ant/utils`
- **Type**: Directory Node
