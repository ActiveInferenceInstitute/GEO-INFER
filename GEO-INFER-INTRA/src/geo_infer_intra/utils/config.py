"""Configuration utility functions for GEO-INFER-INTRA."""

import os
import yaml
import json
import jsonschema
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union


def load_config(config_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Load configuration from a file.

    Args:
        config_path: Path to the configuration file.

    Returns:
        Dict containing the configuration.

    Raises:
        FileNotFoundError: If the configuration file does not exist.
        ValueError: If the file format is not supported.
    """
    config_path = Path(config_path)
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    suffix = config_path.suffix.lower()
    if suffix in ['.yaml', '.yml']:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    elif suffix == '.json':
        with open(config_path, 'r') as f:
            return json.load(f)
    else:
        raise ValueError(f"Unsupported configuration file format: {suffix}")


def get_schema_path() -> Path:
    """
    Get the path to the JSON schema file for configuration validation.

    Returns:
        Path to the JSON schema file.
    """
    # First try the package directory
    package_dir = Path(__file__).parent.parent.parent.parent
    schema_path = package_dir / "config" / "schema.json"
    
    if schema_path.exists():
        return schema_path
    
    # Fallback to the installed package location
    import geo_infer_intra
    package_location = Path(geo_infer_intra.__file__).parent.parent
    schema_path = package_location / "config" / "schema.json"
    
    if schema_path.exists():
        return schema_path
    
    raise FileNotFoundError("JSON schema file not found")


def validate_config(config: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Validate a configuration against the JSON schema.

    Args:
        config: Configuration dictionary to validate.

    Returns:
        Tuple of (is_valid, errors).
    """
    try:
        schema_path = get_schema_path()
        with open(schema_path, 'r') as f:
            schema = json.load(f)
        
        jsonschema.validate(config, schema)
        return True, None
    except FileNotFoundError as e:
        return False, str(e)
    except jsonschema.exceptions.ValidationError as e:
        return False, str(e)


def get_config_value(config: Dict[str, Any], key_path: str, default: Any = None) -> Any:
    """
    Get a value from a nested configuration dictionary using dot notation.

    Args:
        config: Configuration dictionary.
        key_path: Path to the value using dot notation (e.g., "section.subsection.key").
        default: Default value to return if the key is not found (optional).

    Returns:
        The value at the specified path, or the default value if not found.

    Raises:
        KeyError: If the key is not found and no default is provided.
    """
    keys = key_path.split('.')
    value = config
    
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            if default is not None:
                return default
            raise KeyError(f"Key not found: {key_path}")
    
    return value


def merge_configs(base_config: Dict[str, Any], override_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge two configuration dictionaries, with override_config taking precedence.

    Args:
        base_config: Base configuration dictionary.
        override_config: Override configuration dictionary.

    Returns:
        Merged configuration dictionary.
    """
    result = base_config.copy()
    
    for key, value in override_config.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_configs(result[key], value)
        else:
            result[key] = value
    
    return result


def get_default_config_path() -> Path:
    """
    Get the default path for the configuration file.

    Returns:
        Path to the default configuration file.
    """
    # Check for config in user home directory
    user_config = Path.home() / ".geo-infer" / "config.yaml"
    if user_config.exists():
        return user_config
    
    # Check for config in current directory
    local_config = Path.cwd() / "config" / "local.yaml"
    if local_config.exists():
        return local_config
    
    # Fall back to example config in package
    package_dir = Path(__file__).parent.parent.parent.parent
    example_config = package_dir / "config" / "example.yaml"
    if example_config.exists():
        return example_config
    
    raise FileNotFoundError("No configuration file found")


def load_default_config() -> Dict[str, Any]:
    """
    Load the default configuration.

    Returns:
        Default configuration dictionary.
    """
    try:
        config_path = get_default_config_path()
        return load_config(config_path)
    except FileNotFoundError:
        # Return a minimal default configuration
        return {
            "general": {
                "debug_mode": False,
                "log_level": "INFO",
                "log_file": str(Path.home() / ".geo-infer" / "logs" / "intra.log")
            },
            "documentation": {
                "server": {
                    "host": "localhost",
                    "port": 8000
                },
                "content_dir": str(Path.home() / ".geo-infer" / "docs")
            },
            "ontology": {
                "base_dir": str(Path.home() / ".geo-infer" / "ontologies"),
                "default_format": "turtle"
            },
            "knowledge_base": {
                "storage_type": "file",
                "file": {
                    "directory": str(Path.home() / ".geo-infer" / "knowledge_base"),
                    "format": "json"
                }
            },
            "workflow": {
                "storage_dir": str(Path.home() / ".geo-infer" / "workflows"),
                "execution": {
                    "parallel": True,
                    "max_workers": 4
                }
            },
            "api": {
                "server": {
                    "host": "localhost",
                    "port": 8080
                },
                "auth": {
                    "enabled": False
                }
            },
            "database": {
                "type": "sqlite",
                "sqlite": {
                    "path": str(Path.home() / ".geo-infer" / "data" / "geo_infer_intra.db")
                }
            },
            "integration": {}
        } 