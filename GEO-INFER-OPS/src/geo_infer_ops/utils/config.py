"""
Configuration utilities for GEO-INFER-OPS.

This module provides functionality for loading and validating configuration
from YAML files, environment variables, and command-line arguments.
"""

import os
import yaml
from typing import Any, Dict, Optional
from pathlib import Path

def find_config_file(config_path: Optional[str] = None) -> str:
    """
    Find the configuration file to use.
    
    Order of precedence:
    1. Explicitly provided path
    2. Environment variable GEO_INFER_OPS_CONFIG
    3. ./config/local.yaml
    4. ./config/example.yaml
    
    Args:
        config_path: Optional explicit path to configuration file
        
    Returns:
        Path to the configuration file to use
        
    Raises:
        FileNotFoundError: If no configuration file could be found
    """
    if config_path and os.path.exists(config_path):
        return config_path
        
    if env_path := os.environ.get("GEO_INFER_OPS_CONFIG"):
        if os.path.exists(env_path):
            return env_path
    
    # Try to find config relative to the current working directory
    local_config = os.path.join("config", "local.yaml")
    if os.path.exists(local_config):
        return local_config
    
    example_config = os.path.join("config", "example.yaml")
    if os.path.exists(example_config):
        return example_config
    
    # Try to find config relative to the module directory
    module_dir = Path(__file__).parent.parent.parent.parent
    local_module_config = os.path.join(module_dir, "config", "local.yaml")
    if os.path.exists(local_module_config):
        return local_module_config
    
    example_module_config = os.path.join(module_dir, "config", "example.yaml")
    if os.path.exists(example_module_config):
        return example_module_config
    
    raise FileNotFoundError("No configuration file found")

def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from a YAML file.
    
    Args:
        config_path: Optional explicit path to configuration file
        
    Returns:
        Dictionary containing the configuration
    """
    config_file = find_config_file(config_path)
    
    with open(config_file, "r") as f:
        config = yaml.safe_load(f)
    
    # Override with environment variables
    # Format: GEO_INFER_OPS_SECTION_KEY
    # Example: GEO_INFER_OPS_LOGGING_LEVEL=DEBUG
    for env_var, value in os.environ.items():
        if env_var.startswith("GEO_INFER_OPS_"):
            parts = env_var.lower().split("_")[3:]
            
            if len(parts) < 1:
                continue
                
            section = config
            for part in parts[:-1]:
                if part not in section:
                    section[part] = {}
                section = section[part]
            
            # Convert to appropriate type if possible
            if value.lower() == "true":
                value = True
            elif value.lower() == "false":
                value = False
            elif value.isdigit():
                value = int(value)
            elif value.replace(".", "", 1).isdigit() and value.count(".") == 1:
                value = float(value)
                
            section[parts[-1]] = value
    
    return config 