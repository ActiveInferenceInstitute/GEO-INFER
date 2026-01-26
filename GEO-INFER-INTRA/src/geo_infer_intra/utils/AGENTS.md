# Agent
: utils ## Scope
 This directory contains utils components for the module. It provides 0 classes and 7 functions. ## Classes
 and Functions ### load_confi
g
 `load_config(config_path: Union[str, Path]) -> Dict[str, Any]` Load configuration from a file. ### get_schema_pat
h
 `get_schema_path() -> Path` Get the path to the JSON schema file for configuration validation. ### validate_confi
g
 `validate_config(config: Dict[str, Any]) -> Tuple[bool, Optional[str]]` Validate a configuration against the JSON schema. ### get_config_valu
e
 `get_config_value(config: Dict[str, Any], key_path: str, default: Any) -> Any` Get a value from a nested configuration dictionary using dot notation. ### merge_config
s
 `merge_configs(base_config: Dict[str, Any], override_config: Dict[str, Any]) -> Dict[str, Any]` Merge two configuration dictionaries, with override_config taking precedence. ### get_default_config_pat
h
 `get_default_config_path() -> Path` Get the default path for the configuration file. ### load_default_confi
g
 `load_default_config() -> Dict[str, Any]` Load the default configuration. ## Capabilities
 - **7 functions** for utility operations ## Integration
 - **Location**: `GEO-INFER-INTRA/src/geo_infer_intra/utils` - **Type**: Directory Node 