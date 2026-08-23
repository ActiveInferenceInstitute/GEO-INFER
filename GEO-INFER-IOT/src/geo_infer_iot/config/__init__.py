"""
Configuration Management Module

This module provides comprehensive configuration management and validation
for the GEO-INFER-IOT module, ensuring all components are properly configured.
"""

import logging
import os
import yaml
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class IoTConfig:
    """Comprehensive configuration for GEO-INFER-IOT module."""

    # Core module settings
    module_name: str = "geo_infer_iot"
    version: str = "1.0.0"
    debug: bool = False

    # Sensor network configuration
    sensor_networks: Dict[str, Dict] = field(default_factory=dict)

    # Spatial configuration
    spatial: Dict[str, Any] = field(default_factory=lambda: {
        'indexing_system': 'h3',
        'default_resolution': 8,
        'max_resolution': 12,
        'min_resolution': 5,
        'coordinate_system': 'WGS84'
    })

    # Temporal configuration
    temporal: Dict[str, Any] = field(default_factory=lambda: {
        'default_timezone': 'UTC',
        'retention_policy': {
            'raw_data_days': 30,
            'aggregated_data_days': 365
        },
        'analysis_windows': {
            'real_time': '5min',
            'short_term': '1h',
            'medium_term': '24h',
            'long_term': '7d'
        }
    })

    # Bayesian inference configuration
    bayesian_inference: Dict[str, Any] = field(default_factory=lambda: {
        'enabled': True,
        'default_prior': 'informative',
        'covariance_function': 'matern_52',
        'inference_engine': 'variational',
        'update_frequency': '15min',
        'convergence_threshold': 0.001,
        'max_iterations': 1000,
        'confidence_levels': [0.68, 0.95, 0.99]
    })

    # Quality control configuration
    quality_control: Dict[str, Any] = field(default_factory=lambda: {
        'enabled': True,
        'outlier_detection': {
            'method': 'isolation_forest',
            'contamination': 0.1,
            'window_size': 100
        },
        'range_validation': {
            'enabled': True,
            'action': 'flag',
            'strict_mode': False
        },
        'temporal_consistency': {
            'enabled': True,
            'max_change_rate': 0.1,
            'window_minutes': 60
        },
        'spatial_consistency': {
            'enabled': True,
            'neighbor_threshold': 2.0,
            'min_neighbors': 3
        }
    })

    # Data storage configuration
    storage: Dict[str, Any] = field(default_factory=lambda: {
        'timeseries': {
            'type': 'influxdb',
            'host': 'localhost',
            'port': 8086,
            'database': 'iot_sensors',
            'retention_days': 30
        },
        'spatial': {
            'type': 'postgis',
            'host': 'localhost',
            'port': 5432,
            'database': 'spatial_iot',
            'schema': 'public'
        },
        'object': {
            'type': 'minio',
            'endpoint': 'localhost:9000',
            'access_key': None,
            'secret_key': None,
            'bucket': 'iot-sensor-data'
        }
    })

    # API configuration
    api: Dict[str, Any] = field(default_factory=lambda: {
        'rest': {
            'enabled': True,
            'host': '0.0.0.0',
            'port': 8000,
            'workers': 4,
            'cors_enabled': True
        },
        'websocket': {
            'enabled': True,
            'port': 8001,
            'max_connections': 1000
        },
        'graphql': {
            'enabled': False,
            'endpoint': '/graphql'
        }
    })

    # Protocol-specific configurations
    protocols: Dict[str, Dict] = field(default_factory=lambda: {
        'mqtt': {
            'enabled': True,
            'broker_host': 'localhost',
            'broker_port': 1883,
            'username': None,
            'password': None,
            'topics': ['sensors/+/data'],
            'qos': 1,
            'keepalive': 60
        },
        'coap': {
            'enabled': False,
            'server_host': 'localhost',
            'server_port': 5683
        },
        'lorawan': {
            'enabled': False,
            'network_server': 'localhost',
            'app_key': None
        },
        'http_polling': {
            'enabled': True,
            'endpoints': [],
            'interval_seconds': 300
        }
    })

    # Performance and optimization
    performance: Dict[str, Any] = field(default_factory=lambda: {
        'cache': {
            'enabled': True,
            'backend': 'redis',
            'ttl_seconds': 300,
            'max_size_mb': 100
        },
        'connection_pooling': {
            'max_connections': 100,
            'pool_timeout_seconds': 30
        },
        'batch_processing': {
            'batch_size': 1000,
            'flush_interval_seconds': 10
        }
    })

    # Security configuration
    security: Dict[str, Any] = field(default_factory=lambda: {
        'authentication': {
            'type': 'jwt',
            'secret_key': None,
            'expiration_hours': 24
        },
        'authorization': {
            'rbac': {
                'enabled': True,
                'roles': ['sensor_admin', 'data_analyst', 'viewer']
            }
        },
        'encryption': {
            'at_rest': True,
            'in_transit': True,
            'algorithm': 'AES-256-GCM'
        }
    })

    # Logging configuration
    logging: Dict[str, Any] = field(default_factory=lambda: {
        'level': 'INFO',
        'format': 'json',
        'handlers': [
            {'type': 'console'},
            {
                'type': 'file',
                'filename': '/var/log/geo-infer-iot/application.log',
                'rotation': 'daily',
                'retention_days': 30
            }
        ]
    })

    # Visualization configuration
    visualization: Dict[str, Any] = field(default_factory=lambda: {
        'dashboard': {
            'enabled': True,
            'update_interval_seconds': 30
        },
        'mapping': {
            'default_zoom': 10,
            'tile_server': 'OpenStreetMap',
            'overlay_types': ['sensor_locations', 'h3_grid', 'interpolated_surface']
        },
        'alerts': {
            'enabled': True,
            'notification_channels': ['email', 'slack', 'webhook']
        }
    })

    # Machine learning integration
    ml_integration: Dict[str, Any] = field(default_factory=lambda: {
        'predictive_maintenance': {
            'enabled': True,
            'model_type': 'random_forest',
            'features': ['battery_level', 'signal_strength', 'data_quality_score'],
            'prediction_horizon_days': 7
        },
        'anomaly_detection': {
            'enabled': True,
            'model_type': 'autoencoder',
            'window_size_hours': 1,
            'threshold': 0.95
        }
    })

class ConfigurationManager:
    """
    Configuration management system for GEO-INFER-IOT.

    Handles configuration loading, validation, and environment variable
    substitution for all module components.
    """

    def __init__(self, config_paths: Optional[List[str]] = None):
        self.config_paths = config_paths or [
            os.path.join(os.path.dirname(__file__), 'example.yaml'),
            os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'iot_config.yaml'),
            os.path.join(os.path.dirname(__file__), '..', '..', '..', 'config', 'iot_config.yaml')
        ]
        self.config = IoTConfig()
        self.validation_errors: List[str] = []

        # Load configuration
        self._load_configuration()

        logger.info("ConfigurationManager initialized")

    def _load_configuration(self) -> None:
        """Load configuration from files and environment variables."""
        # Try to load from config files
        for config_path in self.config_paths:
            if os.path.exists(config_path):
                try:
                    with open(config_path, 'r') as f:
                        file_config = yaml.safe_load(f)
                    if file_config:
                        self._merge_config(file_config)
                        logger.info(f"Loaded configuration from {config_path}")
                        break
                except Exception as e:
                    logger.warning(f"Failed to load config from {config_path}: {e}")

        # Apply environment variable overrides
        self._apply_environment_overrides()

        # Validate configuration
        self._validate_configuration()

    def _merge_config(self, new_config: Dict[str, Any]) -> None:
        """Merge new configuration into existing config."""
        def merge_dicts(base: Dict[str, Any], update: Dict[str, Any]) -> None:
            for key, value in update.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    merge_dicts(base[key], value)
                else:
                    base[key] = value

        merge_dicts(self.config.__dict__, new_config)

    def _apply_environment_overrides(self) -> None:
        """Apply environment variable overrides to configuration."""
        # MQTT configuration
        if os.getenv('MQTT_BROKER_HOST'):
            self.config.protocols['mqtt']['broker_host'] = os.getenv('MQTT_BROKER_HOST')
        mqtt_port = os.getenv('MQTT_BROKER_PORT')
        if mqtt_port is not None:
            self.config.protocols['mqtt']['broker_port'] = int(mqtt_port)
        if os.getenv('MQTT_USERNAME'):
            self.config.protocols['mqtt']['username'] = os.getenv('MQTT_USERNAME')
        if os.getenv('MQTT_PASSWORD'):
            self.config.protocols['mqtt']['password'] = os.getenv('MQTT_PASSWORD')

        # Database configuration
        if os.getenv('INFLUXDB_HOST'):
            self.config.storage['timeseries']['host'] = os.getenv('INFLUXDB_HOST')
        if os.getenv('POSTGIS_HOST'):
            self.config.storage['spatial']['host'] = os.getenv('POSTGIS_HOST')
        if os.getenv('MINIO_ENDPOINT'):
            self.config.storage['object']['endpoint'] = os.getenv('MINIO_ENDPOINT')

        # Security configuration
        if os.getenv('JWT_SECRET'):
            self.config.security['authentication']['secret_key'] = os.getenv('JWT_SECRET')

    def _validate_configuration(self) -> bool:
        """Validate configuration for consistency and completeness."""
        self.validation_errors = []

        # Validate spatial configuration
        if self.config.spatial['default_resolution'] not in range(0, 16):
            self.validation_errors.append("Invalid H3 resolution level")

        # Validate temporal configuration
        if not isinstance(self.config.temporal['retention_policy']['raw_data_days'], int):
            self.validation_errors.append("Retention policy must specify integer days")

        # Validate API configuration
        if not isinstance(self.config.api['rest']['port'], int):
            self.validation_errors.append("API port must be an integer")

        # Validate protocol configurations
        for protocol, config in self.config.protocols.items():
            if config.get('enabled', False):
                if protocol == 'mqtt' and not config.get('broker_host'):
                    self.validation_errors.append("MQTT broker host required when MQTT enabled")

        # Validate storage configurations
        if self.config.storage['timeseries']['type'] not in ['influxdb', 'timescaledb']:
            self.validation_errors.append("Invalid timeseries database type")

        if self.config.storage['spatial']['type'] not in ['postgis', 'mongodb']:
            self.validation_errors.append("Invalid spatial database type")

        if len(self.validation_errors) > 0:
            logger.error(f"Configuration validation failed: {self.validation_errors}")
            return False

        logger.info("Configuration validation passed")
        return True

    def get_config(self) -> IoTConfig:
        """Get the current configuration."""
        return self.config

    def update_config(self, updates: Dict[str, Any]) -> None:
        """Update configuration with new values."""
        self._merge_config(updates)
        if self._validate_configuration():
            logger.info("Configuration updated successfully")
        else:
            logger.error("Configuration update failed validation")

    def get_sensor_network_config(self, network_id: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific sensor network."""
        return self.config.sensor_networks.get(network_id)

    def add_sensor_network(self, network_id: str, network_config: Dict[str, Any]) -> None:
        """Add configuration for a new sensor network."""
        self.config.sensor_networks[network_id] = network_config
        logger.info(f"Added sensor network configuration: {network_id}")

    def remove_sensor_network(self, network_id: str) -> None:
        """Remove configuration for a sensor network."""
        if network_id in self.config.sensor_networks:
            del self.config.sensor_networks[network_id]
            logger.info(f"Removed sensor network configuration: {network_id}")

    def get_validation_errors(self) -> List[str]:
        """Get list of configuration validation errors."""
        return self.validation_errors.copy()

    def is_valid(self) -> bool:
        """Check if configuration is valid."""
        return len(self.validation_errors) == 0

    def save_config(self, output_path: str) -> None:
        """Save current configuration to file."""
        try:
            # Convert config to dictionary
            config_dict = {}
            for key, value in self.config.__dict__.items():
                if not key.startswith('_'):
                    config_dict[key] = value

            with open(output_path, 'w') as f:
                yaml.dump(config_dict, f, default_flow_style=False, indent=2)

            logger.info(f"Configuration saved to {output_path}")

        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            raise

    def get_config_summary(self) -> Dict[str, Any]:
        """Get a summary of the current configuration."""
        return {
            'module_name': self.config.module_name,
            'version': self.config.version,
            'debug': self.config.debug,
            'sensor_networks_count': len(self.config.sensor_networks),
            'spatial_resolution': self.config.spatial['default_resolution'],
            'api_enabled': self.config.api['rest']['enabled'],
            'websocket_enabled': self.config.api['websocket']['enabled'],
            'validation_errors': len(self.validation_errors),
            'config_sources': [p for p in self.config_paths if os.path.exists(p)],
            'generated_at': datetime.now().isoformat()
        }


# Global configuration manager instance
_config_manager = None

def get_config_manager() -> ConfigurationManager:
    """Get the global configuration manager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigurationManager()
    return _config_manager

def get_config() -> IoTConfig:
    """Get the current configuration."""
    return get_config_manager().get_config()

def update_config(updates: Dict[str, Any]) -> None:
    """Update the global configuration."""
    get_config_manager().update_config(updates)

def validate_config() -> bool:
    """Validate the current configuration."""
    return get_config_manager().is_valid()

def get_config_summary() -> Dict[str, Any]:
    """Get a summary of the current configuration."""
    return get_config_manager().get_config_summary()
