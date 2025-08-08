#!/usr/bin/env python3
"""
Enhanced Configuration Module for Cascadia Framework

This module provides centralized configuration management:
- Analysis parameters
- Visualization settings
- Data processing options
- Module configurations
- Environment-specific settings

Provides a single source of truth for all framework settings.
"""

import yaml
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class AnalysisConfig:
    """Configuration for analysis parameters."""
    h3_resolution: int = 8
    target_counties: List[str] = None
    active_modules: List[str] = None
    spatial_analysis_enabled: bool = False
    force_refresh: bool = False
    skip_cache: bool = False
    validate_h3: bool = False
    debug_mode: bool = False
    verbose_logging: bool = False

@dataclass
class VisualizationConfig:
    """Configuration for visualization settings."""
    generate_dashboard: bool = False
    lightweight_viz: bool = True
    datashader_viz: bool = False
    deepscatter_viz: bool = False
    interactive_maps: bool = True
    static_plots: bool = True
    export_data: bool = True
    color_schemes: Dict[str, Dict[str, str]] = None
    default_center: List[float] = None
    default_zoom: int = 10
    tile_layer: str = 'OpenStreetMap'

@dataclass
class DataConfig:
    """Configuration for data processing."""
    output_dir: str = 'output'
    export_format: str = 'geojson'
    keep_recent_runs: int = 3
    data_quality_threshold: float = 0.8
    cache_enabled: bool = True
    real_data_priority: bool = True
    fallback_to_synthetic: bool = True

@dataclass
class ModuleConfig:
    """Configuration for individual modules."""
    zoning: Dict[str, Any] = None
    current_use: Dict[str, Any] = None
    ownership: Dict[str, Any] = None
    improvements: Dict[str, Any] = None
    water_rights: Dict[str, Any] = None
    ground_water: Dict[str, Any] = None
    surface_water: Dict[str, Any] = None
    power_source: Dict[str, Any] = None
    mortgage_debt: Dict[str, Any] = None

@dataclass
class CascadiaConfig:
    """Main configuration class for Cascadia framework."""
    analysis: AnalysisConfig
    visualization: VisualizationConfig
    data: DataConfig
    modules: ModuleConfig
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

class EnhancedConfigManager:
    """
    Enhanced configuration manager for Cascadia framework.
    
    Provides:
    - Centralized configuration management
    - Environment-specific settings
    - Validation and defaults
    - Configuration persistence
    """
    
    def __init__(self, config_dir: Path = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_dir: Directory containing configuration files
        """
        if config_dir is None:
            config_dir = Path(__file__).parent.parent / "config"
        
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Default configuration
        self.default_config = self._create_default_config()
        
        # Load configuration
        self.config = self.load_configuration()
        
        logger.info("Enhanced Configuration Manager initialized")
    
    def _create_default_config(self) -> CascadiaConfig:
        """Create default configuration."""
        return CascadiaConfig(
            analysis=AnalysisConfig(
                h3_resolution=8,
                target_counties=["CA:Del Norte"],
                active_modules=["zoning", "current_use", "ownership", "improvements"],
                spatial_analysis_enabled=False,
                force_refresh=False,
                skip_cache=False,
                validate_h3=False,
                debug_mode=False,
                verbose_logging=False
            ),
            visualization=VisualizationConfig(
                generate_dashboard=False,
                lightweight_viz=True,
                datashader_viz=False,
                deepscatter_viz=False,
                interactive_maps=True,
                static_plots=True,
                export_data=True,
                color_schemes={
                    'zoning': {
                        'Agricultural': '#90EE90',
                        'Residential': '#FFB6C1',
                        'Commercial': '#FFD700',
                        'Industrial': '#A0522D',
                        'Conservation': '#228B22'
                    },
                    'current_use': {
                        'Agriculture': '#90EE90',
                        'Forest': '#228B22',
                        'Residential': '#FFB6C1',
                        'Commercial': '#FFD700',
                        'Industrial': '#A0522D',
                        'Open Space': '#98FB98'
                    },
                    'ownership': {
                        'Private': '#FF6B6B',
                        'Public': '#4ECDC4',
                        'Corporate': '#45B7D1',
                        'Trust': '#96CEB4'
                    },
                    'improvements': {
                        'High': '#FF0000',
                        'Medium': '#FFA500',
                        'Low': '#FFFF00',
                        'None': '#808080'
                    }
                },
                default_center=[41.7558, -124.2016],
                default_zoom=10,
                tile_layer='OpenStreetMap'
            ),
            data=DataConfig(
                output_dir='output',
                export_format='geojson',
                keep_recent_runs=3,
                data_quality_threshold=0.8,
                cache_enabled=True,
                real_data_priority=True,
                fallback_to_synthetic=True
            ),
            modules=ModuleConfig(
                zoning={'enabled': True, 'data_sources': ['county', 'state']},
                current_use={'enabled': True, 'data_sources': ['usda', 'state']},
                ownership={'enabled': True, 'data_sources': ['assessor', 'state']},
                improvements={'enabled': True, 'data_sources': ['permit', 'state']},
                water_rights={'enabled': False, 'data_sources': ['state']},
                ground_water={'enabled': False, 'data_sources': ['usgs', 'state']},
                surface_water={'enabled': False, 'data_sources': ['usgs', 'state']},
                power_source={'enabled': False, 'data_sources': ['utility', 'state']},
                mortgage_debt={'enabled': False, 'data_sources': ['federal', 'state']}
            )
        )
    
    def load_configuration(self) -> CascadiaConfig:
        """
        Load configuration from files or create default.
        
        Returns:
            Loaded configuration
        """
        config_file = self.config_dir / "cascadia_config.yaml"
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config_data = yaml.safe_load(f)
                
                # Merge with default configuration
                config = self._merge_configs(self.default_config, config_data)
                logger.info(f"Configuration loaded from {config_file}")
                return config
                
            except Exception as e:
                logger.warning(f"Failed to load configuration from {config_file}: {e}")
                logger.info("Using default configuration")
                return self.default_config
        else:
            # Create default configuration file
            self.save_configuration(self.default_config)
            logger.info(f"Created default configuration at {config_file}")
            return self.default_config
    
    def save_configuration(self, config: CascadiaConfig):
        """
        Save configuration to file.
        
        Args:
            config: Configuration to save
        """
        config_file = self.config_dir / "cascadia_config.yaml"
        
        try:
            # Convert to dictionary
            config_dict = self._config_to_dict(config)
            
            with open(config_file, 'w') as f:
                yaml.dump(config_dict, f, default_flow_style=False, indent=2)
            
            logger.info(f"Configuration saved to {config_file}")
            
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
    
    def update_configuration(self, updates: Dict[str, Any]):
        """
        Update configuration with new values.
        
        Args:
            updates: Dictionary of configuration updates
        """
        try:
            # Convert current config to dict
            current_dict = self._config_to_dict(self.config)
            
            # Apply updates
            self._deep_update(current_dict, updates)
            
            # Convert back to config object
            self.config = self._dict_to_config(current_dict)
            
            # Save updated configuration
            self.save_configuration(self.config)
            
            logger.info("Configuration updated successfully")
            
        except Exception as e:
            logger.error(f"Failed to update configuration: {e}")
    
    def get_analysis_config(self) -> AnalysisConfig:
        """Get analysis configuration."""
        return self.config.analysis
    
    def get_visualization_config(self) -> VisualizationConfig:
        """Get visualization configuration."""
        return self.config.visualization
    
    def get_data_config(self) -> DataConfig:
        """Get data configuration."""
        return self.config.data
    
    def get_module_config(self) -> ModuleConfig:
        """Get module configuration."""
        return self.config.modules
    
    def get_active_modules(self) -> List[str]:
        """Get list of active modules."""
        return self.config.analysis.active_modules
    
    def is_module_enabled(self, module_name: str) -> bool:
        """Check if a module is enabled."""
        if module_name in self.config.analysis.active_modules:
            module_config = getattr(self.config.modules, module_name, {})
            return module_config.get('enabled', True) if module_config else True
        return False
    
    def get_module_config(self, module_name: str) -> Dict[str, Any]:
        """Get configuration for a specific module."""
        module_config = getattr(self.config.modules, module_name, {})
        return module_config if module_config else {}
    
    def validate_configuration(self) -> Dict[str, Any]:
        """
        Validate configuration and return validation results.
        
        Returns:
            Dictionary with validation results
        """
        validation_results = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Validate H3 resolution
        if not (0 <= self.config.analysis.h3_resolution <= 15):
            validation_results['errors'].append("H3 resolution must be between 0 and 15")
            validation_results['valid'] = False
        
        # Validate target counties
        if not self.config.analysis.target_counties:
            validation_results['warnings'].append("No target counties specified")
        
        # Validate active modules
        if not self.config.analysis.active_modules:
            validation_results['errors'].append("No active modules specified")
            validation_results['valid'] = False
        
        # Validate output directory
        output_dir = Path(self.config.data.output_dir)
        if not output_dir.parent.exists():
            validation_results['warnings'].append(f"Output directory parent does not exist: {output_dir.parent}")
        
        # Validate data quality threshold
        if not (0.0 <= self.config.data.data_quality_threshold <= 1.0):
            validation_results['errors'].append("Data quality threshold must be between 0.0 and 1.0")
            validation_results['valid'] = False
        
        return validation_results
    
    def _merge_configs(self, default_config: CascadiaConfig, updates: Dict[str, Any]) -> CascadiaConfig:
        """Merge default configuration with updates."""
        default_dict = self._config_to_dict(default_config)
        self._deep_update(default_dict, updates)
        return self._dict_to_config(default_dict)
    
    def _config_to_dict(self, config: CascadiaConfig) -> Dict[str, Any]:
        """Convert configuration object to dictionary."""
        config_dict = asdict(config)
        
        # Convert dataclass objects to dictionaries
        for key, value in config_dict.items():
            if hasattr(value, '__dataclass_fields__'):
                config_dict[key] = asdict(value)
        
        return config_dict
    
    def _dict_to_config(self, config_dict: Dict[str, Any]) -> CascadiaConfig:
        """Convert dictionary to configuration object."""
        # Reconstruct nested dataclass objects
        if 'analysis' in config_dict:
            config_dict['analysis'] = AnalysisConfig(**config_dict['analysis'])
        
        if 'visualization' in config_dict:
            config_dict['visualization'] = VisualizationConfig(**config_dict['visualization'])
        
        if 'data' in config_dict:
            config_dict['data'] = DataConfig(**config_dict['data'])
        
        if 'modules' in config_dict:
            config_dict['modules'] = ModuleConfig(**config_dict['modules'])
        
        return CascadiaConfig(**config_dict)
    
    def _deep_update(self, base_dict: Dict[str, Any], updates: Dict[str, Any]):
        """Recursively update dictionary with new values."""
        for key, value in updates.items():
            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                self._deep_update(base_dict[key], value)
            else:
                base_dict[key] = value

def create_enhanced_config_manager(config_dir: Path = None) -> EnhancedConfigManager:
    """
    Create an enhanced configuration manager instance.
    
    Args:
        config_dir: Directory containing configuration files
        
    Returns:
        EnhancedConfigManager instance
    """
    return EnhancedConfigManager(config_dir)
