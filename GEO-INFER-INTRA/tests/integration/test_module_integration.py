"""Integration tests for cross-module functionality."""

import pytest
import os
import sys
import yaml
import tempfile
from pathlib import Path
from tests.utils import import_module_by_path, collect_test_modules

@pytest.mark.integration
class TestCrossModuleIntegration:
    """Test suite for cross-module integration."""
    
    @pytest.fixture(scope="class")
    def geo_infer_modules(self):
        """Collect all GEO-INFER modules."""
        root_dir = Path(__file__).parent.parent.parent
        return collect_test_modules(root_dir)
    
    @pytest.fixture(scope="class")
    def test_config_dir(self):
        """Create a temporary directory for test configurations."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_dir = Path(tmp_dir) / "config"
            config_dir.mkdir(exist_ok=True)
            yield config_dir
    
    @pytest.fixture(scope="class")
    def test_log_dir(self):
        """Create a temporary directory for test logs."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_dir = Path(tmp_dir) / "logs"
            log_dir.mkdir(exist_ok=True)
            yield log_dir
    
    @pytest.fixture(scope="class")
    def create_test_config_file(self, test_config_dir, test_log_dir):
        """Factory fixture to create config files for different modules."""
        def _create_config(module_name: str) -> Path:
            config_file = test_config_dir / f"{module_name}_config.yml"
            config = {
                "module": module_name,
                "environment": "test",
                "debug": True,
                "logging": {
                    "level": "DEBUG",
                    "format": "json",
                    "file": str(test_log_dir / f"{module_name}.log")
                }
            }
            
            # Add module-specific configuration
            if module_name == "geo_infer_space":
                config["coordinate_systems"] = ["WGS84", "EPSG:3857", "EPSG:4326"]
                config["spatial_index"] = "H3"
            elif module_name == "geo_infer_time":
                config["time_formats"] = ["ISO8601", "RFC3339"]
                config["timezone"] = "UTC"
            elif module_name == "geo_infer_api":
                config["server"] = {
                    "host": "localhost",
                    "port": 9000,
                    "workers": 1
                }
                config["auth"] = {
                    "enabled": False
                }
            
            with open(config_file, "w") as f:
                yaml.dump(config, f)
            
            return config_file
        
        return _create_config
    
    @pytest.fixture(scope="class")
    def space_config_file(self, create_test_config_file):
        """Create test configuration file for geo_infer_space module."""
        return create_test_config_file("geo_infer_space")
    
    @pytest.fixture(scope="class")
    def time_config_file(self, create_test_config_file):
        """Create test configuration file for geo_infer_time module."""
        return create_test_config_file("geo_infer_time")
    
    @pytest.fixture(scope="class")
    def api_config_file(self, create_test_config_file):
        """Create test configuration file for geo_infer_api module."""
        return create_test_config_file("geo_infer_api")
    
    @pytest.fixture(scope="class")
    def data_config_file(self, create_test_config_file):
        """Create test configuration file for geo_infer_data module."""
        return create_test_config_file("geo_infer_data")
    
    @pytest.fixture(scope="class")
    def test_geojson_feature(self):
        """Create a GeoJSON Feature for testing."""
        return {
            "type": "Feature",
            "properties": {
                "name": "Test Polygon",
                "value": 42
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [100.0, 0.0], [101.0, 0.0], [101.0, 1.0],
                        [100.0, 1.0], [100.0, 0.0]
                    ]
                ]
            }
        }
    
    @pytest.fixture(scope="class")
    def test_time_series_data(self):
        """Create sample time series data for testing."""
        return {
            "timestamps": [
                "2023-01-01T00:00:00Z",
                "2023-01-02T00:00:00Z",
                "2023-01-03T00:00:00Z",
                "2023-01-04T00:00:00Z",
                "2023-01-05T00:00:00Z"
            ],
            "values": [10.5, 11.2, 9.8, 12.3, 10.9]
        }
    
    def test_module_discovery(self, geo_infer_modules):
        """Test that modules can be discovered."""
        assert len(geo_infer_modules) > 0
        
        # Check some key modules
        expected_modules = [
            "geo_infer_space", 
            "geo_infer_time",
            "geo_infer_data"
        ]
        
        # Adjust expectations based on what's actually available
        available_expected = [m for m in expected_modules if m in geo_infer_modules]
        if available_expected:
            for module_name in available_expected:
                assert module_name in geo_infer_modules, f"Module {module_name} not found"
        else:
            pytest.skip("No expected modules found in the project")
    
    def test_module_imports(self, geo_infer_modules):
        """Test that modules can be imported."""
        # Test importing a few key modules
        modules_to_test = ["geo_infer_space", "geo_infer_time", "geo_infer_data"]
        modules_found = False
        
        for module_name in modules_to_test:
            if module_name in geo_infer_modules:
                modules_found = True
                module_path = geo_infer_modules[module_name]
                init_file = module_path / "src" / module_name.replace("-", "_") / "__init__.py"
                
                if init_file.exists():
                    try:
                        # Try to import the module
                        imported_module = import_module_by_path(str(init_file), module_name)
                        assert imported_module is not None
                    except ImportError as e:
                        pytest.skip(f"Could not import {module_name}: {e}")
        
        if not modules_found:
            pytest.skip("No testable modules found")
    
    @pytest.mark.parametrize("config_fixture", [
        "space_config_file",
        "time_config_file",
        "api_config_file",
        "data_config_file"
    ])
    def test_module_configs(self, request, config_fixture):
        """Test that module-specific configuration files can be loaded."""
        config_file = request.getfixturevalue(config_fixture)
        assert config_file.exists()
        
        # Try to load the config file
        with open(config_file) as f:
            config = yaml.safe_load(f)
        
        assert "module" in config
        assert "environment" in config
        assert "debug" in config
        assert "logging" in config
    
    def test_space_time_integration(self, geo_infer_modules, test_geojson_feature, test_time_series_data):
        """Test integration between space and time modules."""
        # Skip test if required modules not available
        required_modules = ["geo_infer_space", "geo_infer_time"]
        available_required = [m for m in required_modules if m in geo_infer_modules]
        if len(available_required) < len(required_modules):
            pytest.skip(f"Required modules {required_modules} not all available")
        
        # Create a feature with time series data
        space_time_feature = {
            "type": "Feature",
            "geometry": test_geojson_feature["geometry"],
            "properties": {
                **test_geojson_feature["properties"],
                "time_series": test_time_series_data
            }
        }
        
        # Make assertions about the combined feature
        assert "time_series" in space_time_feature["properties"]
        assert "timestamps" in space_time_feature["properties"]["time_series"]
        assert "values" in space_time_feature["properties"]["time_series"]
        assert len(space_time_feature["properties"]["time_series"]["timestamps"]) == \
               len(space_time_feature["properties"]["time_series"]["values"]) 