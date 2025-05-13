"""Unit tests for configuration utilities."""

import pytest
import os
import tempfile
import yaml
import json

# Assuming the module structure we've defined
from geo_infer_intra.utils import config


class TestConfig:
    """Tests for configuration utilities."""

    def test_load_yaml_config(self, tmp_path):
        """Test loading configuration from YAML file."""
        # Create test config file
        config_path = tmp_path / "test_config.yaml"
        test_config = {
            "general": {
                "debug_mode": True,
                "log_level": "DEBUG"
            },
            "documentation": {
                "server": {
                    "host": "localhost",
                    "port": 8000
                }
            }
        }
        
        with open(config_path, "w") as f:
            yaml.dump(test_config, f)
        
        # Test loading config
        loaded_config = config.load_config(config_path)
        assert loaded_config == test_config
        assert loaded_config["general"]["debug_mode"] is True
        assert loaded_config["general"]["log_level"] == "DEBUG"
        assert loaded_config["documentation"]["server"]["port"] == 8000

    def test_validate_config(self, test_config):
        """Test validating configuration against schema."""
        # Test successful validation
        is_valid, errors = config.validate_config(test_config)
        assert is_valid
        assert not errors
        
        # Test invalid configuration
        invalid_config = dict(test_config)
        invalid_config["general"]["log_level"] = "INVALID_LEVEL"
        is_valid, errors = config.validate_config(invalid_config)
        assert not is_valid
        assert errors
        assert "log_level" in str(errors)

    def test_get_config_value(self, test_config):
        """Test getting values from configuration with dot notation."""
        # Test getting simple values
        debug_mode = config.get_config_value(test_config, "general.debug_mode")
        assert debug_mode is True
        
        # Test getting nested values
        port = config.get_config_value(test_config, "documentation.server.port")
        assert port == 8000
        
        # Test default value for missing keys
        missing = config.get_config_value(test_config, "missing.key", default="default")
        assert missing == "default"
        
        # Test handling missing keys without default
        with pytest.raises(KeyError):
            config.get_config_value(test_config, "missing.key")

    def test_merge_configs(self):
        """Test merging configurations."""
        base_config = {
            "general": {
                "debug_mode": False,
                "log_level": "INFO"
            },
            "documentation": {
                "server": {
                    "host": "localhost",
                    "port": 8000
                }
            }
        }
        
        override_config = {
            "general": {
                "debug_mode": True
            },
            "documentation": {
                "server": {
                    "port": 9000
                }
            }
        }
        
        merged_config = config.merge_configs(base_config, override_config)
        assert merged_config["general"]["debug_mode"] is True  # Overridden
        assert merged_config["general"]["log_level"] == "INFO"  # Not overridden
        assert merged_config["documentation"]["server"]["port"] == 9000  # Overridden
        assert merged_config["documentation"]["server"]["host"] == "localhost"  # Not overridden 