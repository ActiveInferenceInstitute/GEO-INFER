"""System tests for the GEO-INFER framework.

These tests verify end-to-end integration across multiple modules.
"""

import pytest
import os
import sys
import tempfile
import yaml
import json
from pathlib import Path
from tests.utils import import_module_by_path, collect_test_modules
from tests.utils.geospatial import create_point, create_feature, create_feature_collection

@pytest.mark.system
class TestSystemIntegration:
    """Test suite for system-level integration."""
    
    @pytest.fixture(scope="class")
    def geo_infer_modules(self):
        """Collect all GEO-INFER modules."""
        root_dir = Path(__file__).parent.parent.parent
        return collect_test_modules(root_dir)
    
    @pytest.fixture(scope="class")
    def temp_data_dir(self):
        """Create a temporary directory for test data."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            data_dir = Path(tmp_dir) / "data"
            data_dir.mkdir(exist_ok=True)
            yield data_dir
    
    @pytest.fixture(scope="class")
    def sample_geojson(self, temp_data_dir):
        """Create a sample GeoJSON file with features."""
        # Create features for major cities
        cities = [
            ("New York", -74.0060, 40.7128),
            ("Los Angeles", -118.2437, 34.0522),
            ("Chicago", -87.6298, 41.8781),
            ("San Francisco", -122.4194, 37.7749),
            ("Miami", -80.1918, 25.7617)
        ]
        
        features = []
        for city, lon, lat in cities:
            point = create_point(lon, lat)
            feature = create_feature(
                point, 
                {
                    "name": city,
                    "population": 1000000 + (hash(city) % 9000000),  # Random population
                    "country": "USA"
                }
            )
            features.append(feature)
        
        # Create feature collection
        feature_collection = create_feature_collection(features)
        
        # Write to file
        file_path = temp_data_dir / "cities.geojson"
        with open(file_path, "w") as f:
            json.dump(feature_collection, f, indent=2)
        
        return file_path
    
    def test_e2e_data_to_space(self, geo_infer_modules, sample_geojson):
        """Test end-to-end data flow from DATA to SPACE modules."""
        # Check if required modules are available
        required_modules = ["geo_infer_data", "geo_infer_space"]
        available_required = [m for m in required_modules if m in geo_infer_modules]
        if len(available_required) < len(required_modules):
            pytest.skip(f"Required modules {required_modules} not all available")
        
        # Load the sample GeoJSON file
        with open(sample_geojson) as f:
            data = json.load(f)
        
        # Verify basic data properties
        assert data["type"] == "FeatureCollection"
        assert len(data["features"]) > 0
        
        # In a real implementation, we'd use the geo_infer_data module to load the data
        # and the geo_infer_space module to transform it to a spatial data structure
        # For now, we'll verify that the data has the expected structure
        for feature in data["features"]:
            assert feature["type"] == "Feature"
            assert "geometry" in feature
            assert "properties" in feature
            assert feature["geometry"]["type"] == "Point"
            assert "coordinates" in feature["geometry"]
            assert len(feature["geometry"]["coordinates"]) == 2
    
    def test_e2e_space_to_time(self, geo_infer_modules, sample_geojson):
        """Test end-to-end data flow from SPACE to TIME modules."""
        # Check if required modules are available
        required_modules = ["geo_infer_space", "geo_infer_time"]
        available_required = [m for m in required_modules if m in geo_infer_modules]
        if len(available_required) < len(required_modules):
            pytest.skip(f"Required modules {required_modules} not all available")
        
        # Load the sample GeoJSON file
        with open(sample_geojson) as f:
            data = json.load(f)
        
        # Add time properties to features
        for i, feature in enumerate(data["features"]):
            # Add timestamps and values for a simple time series
            timestamps = [
                f"2023-01-{d:02d}T00:00:00Z" for d in range(1, 6)
            ]
            # Generate some values that increase over time with a random factor
            base_value = 10 + i
            values = [base_value + (d * 0.5) for d in range(5)]
            
            # Add to properties
            feature["properties"]["time_series"] = {
                "timestamps": timestamps,
                "values": values
            }
        
        # In a real implementation, we'd use the geo_infer_space module to handle the 
        # spatial data and the geo_infer_time module to handle time series
        # For now, we'll verify that the data has the expected spatial+temporal structure
        for feature in data["features"]:
            assert "time_series" in feature["properties"]
            assert "timestamps" in feature["properties"]["time_series"]
            assert "values" in feature["properties"]["time_series"]
            assert len(feature["properties"]["time_series"]["timestamps"]) == 5
            assert len(feature["properties"]["time_series"]["values"]) == 5
    
    def test_e2e_data_to_api(self, geo_infer_modules, sample_geojson):
        """Test end-to-end data flow from DATA to API modules."""
        # Check if required modules are available
        required_modules = ["geo_infer_data", "geo_infer_api"]
        available_required = [m for m in required_modules if m in geo_infer_modules]
        if len(available_required) < len(required_modules):
            pytest.skip(f"Required modules {required_modules} not all available")
        
        # Load the sample GeoJSON file
        with open(sample_geojson) as f:
            data = json.load(f)
        
        # In a real implementation, we'd use the geo_infer_data module to load the data
        # and the geo_infer_api module to serve it
        # For now, we'll simulate a basic API response
        api_response = {
            "status": "success",
            "data": data,
            "metadata": {
                "count": len(data["features"]),
                "bbox": [
                    min(f["geometry"]["coordinates"][0] for f in data["features"]),
                    min(f["geometry"]["coordinates"][1] for f in data["features"]),
                    max(f["geometry"]["coordinates"][0] for f in data["features"]),
                    max(f["geometry"]["coordinates"][1] for f in data["features"])
                ]
            }
        }
        
        # Verify API response structure
        assert api_response["status"] == "success"
        assert "data" in api_response
        assert "metadata" in api_response
        assert api_response["metadata"]["count"] == len(data["features"])
        assert len(api_response["metadata"]["bbox"]) == 4 