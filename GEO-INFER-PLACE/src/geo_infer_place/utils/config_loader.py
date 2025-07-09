"""
LocationConfigLoader: Configuration management for place-based analysis.

This module provides comprehensive configuration loading and validation
for location-specific geospatial analysis parameters, including spatial
bounds, analysis settings, data source configurations, and integration
parameters for different GEO-INFER modules.
"""

import logging
import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
import os

logger = logging.getLogger(__name__)

@dataclass
class LocationBounds:
    """Geographic bounds for a location."""
    north: float
    south: float
    east: float
    west: float
    
    def to_bbox(self) -> tuple:
        """Convert to (west, south, east, north) bbox tuple."""
        return (self.west, self.south, self.east, self.north)
    
    def center(self) -> tuple:
        """Get center point as (lat, lon)."""
        lat = (self.north + self.south) / 2
        lon = (self.east + self.west) / 2
        return (lat, lon)

class LocationConfigLoader:
    """
    Configuration loader for location-specific analysis parameters.
    
    This class handles loading, validation, and processing of location-specific
    configuration files that define analysis parameters, data sources, spatial
    bounds, and integration settings for place-based geospatial analysis.
    
    Features:
    - YAML/JSON configuration file loading
    - Configuration validation and type checking
    - Environment variable interpolation
    - Default value management
    - Multi-location configuration support
    - API key and credential management
    
    Example Usage:
        >>> loader = LocationConfigLoader()
        >>> config = loader.load_location_config('del_norte_county')
        >>> bounds = loader.get_location_bounds(config)
        >>> analysis_params = loader.get_analysis_parameters(config, 'forest_health')
    """
    
    def __init__(self, 
                 base_config_dir: Optional[str] = None,
                 default_config_file: Optional[str] = None):
        """
        Initialize configuration loader.
        
        Args:
            base_config_dir: Base directory for configuration files
            default_config_file: Default configuration file for fallback values
        """
        # Determine base configuration directory
        if base_config_dir is None:
            # Default to locations directory in the package
            package_dir = Path(__file__).parent.parent
            base_config_dir = package_dir.parent.parent / "locations"
            
        self.base_config_dir = Path(base_config_dir)
        self.default_config_file = default_config_file
        
        # Cache for loaded configurations
        self.config_cache = {}
        
        # Default configuration values
        self.defaults = self._load_default_config()
        
        logger.info(f"LocationConfigLoader initialized with base directory: {self.base_config_dir}")
        
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration values."""
        defaults = {
            'location': {
                'timezone': 'UTC',
                'coordinate_systems': {
                    'local_crs': 'EPSG:4326',
                    'analysis_crs': 'EPSG:3857',
                    'utm_zone': None
                }
            },
            'spatial': {
                'h3_resolution': 8,
                'buffer_distance_meters': 1000
            },
            'temporal': {
                'default_frequency': 'daily',
                'lookback_days': 30
            },
            'data_management': {
                'cache_enabled': True,
                'retention_policy': '1_year',
                'quality_control': {
                    'automated_checks': True,
                    'validation_rules': 'standard'
                }
            },
            'reporting': {
                'automated_reports': {
                    'frequency': 'monthly',
                    'formats': ['html', 'pdf']
                },
                'dashboard': {
                    'refresh_interval': 'hourly',
                    'public_access_level': 'summary_only'
                }
            }
        }
        
        return defaults
        
    def load_location_config(self, 
                           location_code: str,
                           config_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Load configuration for a specific location.
        
        Args:
            location_code: Identifier for the location (e.g., 'del_norte_county')
            config_path: Optional custom path to configuration file
            
        Returns:
            Dictionary containing complete location configuration
        """
        # Check cache first
        cache_key = f"{location_code}:{config_path}"
        if cache_key in self.config_cache:
            logger.debug(f"Returning cached config for {location_code}")
            return self.config_cache[cache_key]
            
        logger.info(f"Loading configuration for location: {location_code}")
        
        # Determine config file path
        if config_path is None:
            config_path = self.base_config_dir / location_code / "config" / "analysis_config.yaml"
        else:
            config_path = Path(config_path)
            
        if not config_path.exists():
            logger.error(f"Configuration file not found: {config_path}")
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
            
        # Load configuration file
        try:
            with open(config_path, 'r') as f:
                if config_path.suffix.lower() in ['.yaml', '.yml']:
                    raw_config = yaml.safe_load(f)
                elif config_path.suffix.lower() == '.json':
                    raw_config = json.load(f)
                else:
                    raise ValueError(f"Unsupported config file format: {config_path.suffix}")
                    
        except Exception as e:
            logger.error(f"Error loading configuration file {config_path}: {e}")
            raise
            
        # Process and validate configuration
        config = self._process_config(raw_config, location_code)
        
        # Cache processed configuration
        self.config_cache[cache_key] = config
        
        logger.info(f"Successfully loaded configuration for {location_code}")
        return config
        
    def _process_config(self, raw_config: Dict[str, Any], location_code: str) -> Dict[str, Any]:
        """
        Process raw configuration with defaults, validation, and environment substitution.
        
        Args:
            raw_config: Raw configuration from file
            location_code: Location identifier for context
            
        Returns:
            Processed configuration dictionary
        """
        # Start with defaults and merge with raw config
        config = self._deep_merge(self.defaults.copy(), raw_config)
        
        # Add location metadata
        config['location_code'] = location_code
        config['config_loaded_at'] = logger.info.__module__
        
        # Process environment variable substitution
        config = self._substitute_env_vars(config)
        
        # Validate configuration
        self._validate_config(config)
        
        # Process special fields
        config = self._process_special_fields(config)
        
        return config
        
    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries, with override taking precedence."""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
                
        return result
        
    def _substitute_env_vars(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Substitute environment variables in configuration values."""
        def substitute_value(value):
            if isinstance(value, str) and value.startswith('${') and value.endswith('}'):
                env_var = value[2:-1]
                default_value = None
                
                # Handle default values: ${VAR:default}
                if ':' in env_var:
                    env_var, default_value = env_var.split(':', 1)
                    
                return os.getenv(env_var, default_value)
            elif isinstance(value, dict):
                return {k: substitute_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [substitute_value(item) for item in value]
            else:
                return value
                
        return substitute_value(config)
        
    def _validate_config(self, config: Dict[str, Any]) -> None:
        """Validate configuration parameters."""
        # Validate location bounds
        if 'location' in config and 'bounds' in config['location']:
            bounds = config['location']['bounds']
            required_bounds = ['north', 'south', 'east', 'west']
            
            for bound in required_bounds:
                if bound not in bounds:
                    raise ValueError(f"Missing required location bound: {bound}")
                    
                if not isinstance(bounds[bound], (int, float)):
                    raise ValueError(f"Location bound {bound} must be numeric")
                    
            # Validate bounds make sense
            if bounds['north'] <= bounds['south']:
                raise ValueError("North bound must be greater than south bound")
            if bounds['east'] <= bounds['west']:
                raise ValueError("East bound must be greater than west bound")
                
        # Validate H3 resolution
        if 'spatial' in config and 'h3_resolution' in config['spatial']:
            h3_res = config['spatial']['h3_resolution']
            if not isinstance(h3_res, int) or h3_res < 0 or h3_res > 15:
                raise ValueError("H3 resolution must be an integer between 0 and 15")
                
        logger.debug("Configuration validation passed")
        
    def _process_special_fields(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Process special configuration fields that need additional processing."""
        # Create LocationBounds object if bounds exist
        if 'location' in config and 'bounds' in config['location']:
            bounds_dict = config['location']['bounds']
            config['location']['bounds_obj'] = LocationBounds(
                north=bounds_dict['north'],
                south=bounds_dict['south'],
                east=bounds_dict['east'],
                west=bounds_dict['west']
            )
            
        return config
        
    def get_location_bounds(self, config: Dict[str, Any]) -> LocationBounds:
        """
        Extract location bounds from configuration.
        
        Args:
            config: Location configuration dictionary
            
        Returns:
            LocationBounds object
        """
        if 'bounds_obj' in config.get('location', {}):
            return config['location']['bounds_obj']
            
        bounds = config.get('location', {}).get('bounds', {})
        if not bounds:
            raise ValueError("No location bounds found in configuration")
            
        return LocationBounds(
            north=bounds['north'],
            south=bounds['south'],
            east=bounds['east'],
            west=bounds['west']
        )
        
    def get_analysis_parameters(self, 
                              config: Dict[str, Any], 
                              analysis_type: str) -> Dict[str, Any]:
        """
        Get analysis-specific parameters from configuration.
        
        Args:
            config: Location configuration dictionary
            analysis_type: Type of analysis (e.g., 'forest_health', 'coastal_resilience')
            
        Returns:
            Analysis-specific parameters
        """
        analyses = config.get('analyses', {})
        if analysis_type not in analyses:
            logger.warning(f"Analysis type '{analysis_type}' not found in configuration")
            return {}
            
        return analyses[analysis_type]
        
    def get_data_source_config(self, 
                             config: Dict[str, Any], 
                             source_name: str) -> Dict[str, Any]:
        """
        Get data source configuration.
        
        Args:
            config: Location configuration dictionary
            source_name: Name of data source
            
        Returns:
            Data source configuration
        """
        data_sources = config.get('data_sources', {})
        if source_name not in data_sources:
            logger.warning(f"Data source '{source_name}' not found in configuration")
            return {}
            
        return data_sources[source_name]
        
    def get_api_keys(self, config: Dict[str, Any]) -> Dict[str, str]:
        """
        Get API keys from configuration or environment variables.
        
        Args:
            config: Location configuration dictionary
            
        Returns:
            Dictionary of API keys
        """
        api_keys = {}
        
        # Common API key environment variables
        env_api_keys = {
            'noaa': 'NOAA_API_KEY',
            'calfire': 'CALFIRE_API_KEY',
            'usgs': 'USGS_API_KEY',
            'weather': 'WEATHER_API_KEY',
            'google_earth_engine': 'GEE_API_KEY'
        }
        
        for service, env_var in env_api_keys.items():
            api_key = os.getenv(env_var)
            if api_key:
                api_keys[service] = api_key
                
        # Override with config-specified keys
        config_keys = config.get('api_keys', {})
        api_keys.update(config_keys)
        
        return api_keys
        
    def list_available_locations(self) -> List[str]:
        """
        List all available location configurations.
        
        Returns:
            List of location codes with available configurations
        """
        locations = []
        
        if not self.base_config_dir.exists():
            logger.warning(f"Base config directory does not exist: {self.base_config_dir}")
            return locations
            
        for location_dir in self.base_config_dir.iterdir():
            if location_dir.is_dir():
                config_file = location_dir / "config" / "analysis_config.yaml"
                if config_file.exists():
                    locations.append(location_dir.name)
                    
        return sorted(locations)
        
    def validate_location_config(self, location_code: str) -> Dict[str, Any]:
        """
        Validate a location configuration and return validation results.
        
        Args:
            location_code: Location identifier to validate
            
        Returns:
            Validation results with status and any errors
        """
        validation_result = {
            'location_code': location_code,
            'valid': False,
            'errors': [],
            'warnings': [],
            'config_path': None
        }
        
        try:
            config = self.load_location_config(location_code)
            validation_result['valid'] = True
            validation_result['config_path'] = str(self.base_config_dir / location_code)
            
            # Additional validation checks
            bounds = self.get_location_bounds(config)
            if abs(bounds.north - bounds.south) < 0.001:
                validation_result['warnings'].append("Very small latitude range in bounds")
                
            if abs(bounds.east - bounds.west) < 0.001:
                validation_result['warnings'].append("Very small longitude range in bounds")
                
            # Check for enabled analyses
            analyses = config.get('analyses', {})
            enabled_analyses = [name for name, params in analyses.items() 
                              if params.get('enabled', False)]
            
            if not enabled_analyses:
                validation_result['warnings'].append("No analyses are enabled")
            else:
                validation_result['enabled_analyses'] = enabled_analyses
                
        except Exception as e:
            validation_result['errors'].append(str(e))
            
        return validation_result 