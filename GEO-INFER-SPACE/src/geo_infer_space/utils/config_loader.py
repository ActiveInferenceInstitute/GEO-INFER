#!/usr/bin/env python3
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
    Configuration loader for place-based analysis.
    
    Handles loading, merging, and validation of configuration from
    multiple sources including YAML, JSON, and defaults.
    """
    
    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize config loader.
        
        Args:
            config_dir: Directory for configuration files
        """
        self.config_dir = Path(config_dir) if config_dir else Path(__file__).parent.parent.parent / 'config'
        self.default_config = self._load_default_config()
        self.loaded_config = {}
        
        logger.info(f"Config loader initialized with directory: {self.config_dir}")
    
    def load_location_config(self, location: str) -> Dict[str, Any]:
        """
        Load configuration for a specific location.
        
        Args:
            location: Location identifier (e.g., 'del_norte_county')
            
        Returns:
            Merged configuration dictionary
        """
        config = self.default_config.copy()
        
        # Load base config
        base_config_path = self.config_dir / 'base.yaml'
        if base_config_path.exists():
            with open(base_config_path, 'r') as f:
                base_config = yaml.safe_load(f)
            config = self._merge_configs(config, base_config)
        
        # Load location-specific config
        location_config_path = self.config_dir / f'{location}.yaml'
        if location_config_path.exists():
            with open(location_config_path, 'r') as f:
                location_config = yaml.safe_load(f)
            config = self._merge_configs(config, location_config)
        else:
            logger.warning(f"Location config not found: {location_config_path}")
        
        self._validate_config(config)
        self.loaded_config[location] = config
        
        return config
    
    def get_location_bounds(self, config: Dict[str, Any]) -> LocationBounds:
        """Extract location bounds from config."""
        bounds = config.get('location', {}).get('bounds', {})
        return LocationBounds(
            north=bounds.get('north', 90.0),
            south=bounds.get('south', -90.0),
            east=bounds.get('east', 180.0),
            west=bounds.get('west', -180.0)
        )
    
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
    
    def _merge_configs(self, base: Dict, update: Dict) -> Dict:
        """Recursively merge two configuration dictionaries."""
        for key, value in update.items():
            if isinstance(value, dict) and key in base:
                base[key] = self._merge_configs(base[key], value)
            else:
                base[key] = value
        return base
    
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