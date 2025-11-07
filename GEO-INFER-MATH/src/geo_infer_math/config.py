"""
Configuration Management for GEO-INFER-MATH

This module provides configuration management for various
mathematical operations and backends.
"""

from typing import Dict, Any, Optional
import logging
import os

logger = logging.getLogger(__name__)


class MathConfig:
    """
    Configuration manager for GEO-INFER-MATH.
    
    Provides centralized configuration for:
    - Theorem proving backends
    - Information theory parameters
    - Performance settings
    - Numerical precision
    """
    
    def __init__(self):
        """Initialize configuration with defaults."""
        self._config = {
            'theorem_proving': {
                'backend': 'z3',
                'timeout': 10.0,
                'enable_caching': True,
            },
            'information_theory': {
                'base': 2.0,
                'epsilon': 1e-10,
                'default_bins': 20,
            },
            'performance': {
                'enable_caching': True,
                'cache_size': 256,
                'parallel_processing': False,
                'num_workers': 4,
            },
            'numerical': {
                'precision': 'float64',
                'epsilon': 1e-10,
                'max_iterations': 1000,
            },
            'symbolic_math': {
                'backend': 'sympy',
                'enable_proof_generation': True,
            },
        }
        
        # Load from environment variables
        self._load_from_env()
    
    def _load_from_env(self):
        """Load configuration from environment variables."""
        # Theorem proving
        if os.getenv('GEO_INFER_MATH_TP_BACKEND'):
            self._config['theorem_proving']['backend'] = os.getenv('GEO_INFER_MATH_TP_BACKEND')
        
        if os.getenv('GEO_INFER_MATH_TP_TIMEOUT'):
            self._config['theorem_proving']['timeout'] = float(os.getenv('GEO_INFER_MATH_TP_TIMEOUT'))
        
        # Performance
        if os.getenv('GEO_INFER_MATH_ENABLE_CACHING'):
            self._config['performance']['enable_caching'] = (
                os.getenv('GEO_INFER_MATH_ENABLE_CACHING').lower() == 'true'
            )
        
        if os.getenv('GEO_INFER_MATH_PARALLEL'):
            self._config['performance']['parallel_processing'] = (
                os.getenv('GEO_INFER_MATH_PARALLEL').lower() == 'true'
            )
    
    def get(self, section: str, key: Optional[str] = None) -> Any:
        """
        Get configuration value.
        
        Args:
            section: Configuration section
            key: Optional key within section
        
        Returns:
            Configuration value
        """
        if key is None:
            return self._config.get(section, {})
        return self._config.get(section, {}).get(key)
    
    def set(self, section: str, key: str, value: Any):
        """
        Set configuration value.
        
        Args:
            section: Configuration section
            key: Key within section
            value: Value to set
        """
        if section not in self._config:
            self._config[section] = {}
        self._config[section][key] = value
        logger.debug(f"Set config: {section}.{key} = {value}")
    
    def update(self, section: str, values: Dict[str, Any]):
        """
        Update configuration section.
        
        Args:
            section: Configuration section
            values: Dictionary of values to update
        """
        if section not in self._config:
            self._config[section] = {}
        self._config[section].update(values)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Get full configuration as dictionary.
        
        Returns:
            Configuration dictionary
        """
        return self._config.copy()


# Global configuration instance
_config = MathConfig()


def get_config() -> MathConfig:
    """
    Get global configuration instance.
    
    Returns:
        Global MathConfig instance
    """
    return _config


def configure(**kwargs) -> MathConfig:
    """
    Configure GEO-INFER-MATH settings.
    
    Args:
        **kwargs: Configuration options
    
    Returns:
        Configuration instance
    
    Example:
        >>> configure(theorem_proving_backend='z3', enable_caching=True)
    """
    for key, value in kwargs.items():
        if '_' in key:
            section, option = key.split('_', 1)
            _config.set(section, option, value)
        else:
            _config.set('general', key, value)
    
    return _config


