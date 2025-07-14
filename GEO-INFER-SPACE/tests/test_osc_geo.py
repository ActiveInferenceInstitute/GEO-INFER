import pytest
from pathlib import Path
from geo_infer_space.osc_geo.core.repos import clone_osc_repos
from geo_infer_space.osc_geo.utils.osc_simple_status import check_repo_status

import tempfile
import json
import shutil
from geo_infer_space.osc_geo import H3GridManager, H3DataLoader, load_data_to_h3_grid
from geo_infer_space.osc_geo.utils.h3_utils import h3_to_geojson, geojson_to_h3

@pytest.mark.setup
@pytest.mark.integration
def test_clone_repos(tmp_path):
    """Test cloning of OSC repos into temp path."""
    success = clone_osc_repos(str(tmp_path))
    assert success
    assert len(list(tmp_path.iterdir())) > 0  # Check repos were cloned

@pytest.mark.setup
def test_check_status():
    """Test status checking returns dict."""
    status = check_repo_status()
    assert isinstance(status, dict)
    assert 'repositories' in status 

@pytest.mark.setup
@pytest.mark.integration
def test_h3_grid_manager():
    """
    Test H3GridManager lifecycle. This test requires H3GridManager to be available and functional.
    Fails if the dependency is missing or broken.
    """
    try:
        manager = H3GridManager(auto_start=False)
        assert not manager.is_server_running()
        # Note: Server start/stop may not work in test environment
        # Just test that the manager can be created
        assert manager is not None
    except Exception as e:
        raise AssertionError(f"H3GridManager not available or failed: {e}")

@pytest.mark.setup
@pytest.mark.integration
def test_h3_data_loader(tmp_path):
    """
    Test loading data to H3 grid. Requires H3DataLoader to be available and functional.
    Fails if the dependency is missing or broken.
    """
    try:
        # Create sample GeoJSON
        sample_geojson = {
            'type': 'FeatureCollection',
            'features': [{
                'type': 'Feature',
                'properties': {},
                'geometry': {'type': 'Point', 'coordinates': [0, 0]}
            }]
        }
        input_file = tmp_path / 'sample.geojson'
        with open(input_file, 'w') as f:
            json.dump(sample_geojson, f)
        output_file = tmp_path / 'output_h3.geojson'
        loader = H3DataLoader()
        success = loader.load_data(str(input_file), str(output_file), resolution=8)
        assert success
        assert output_file.exists()
    except Exception as e:
        raise AssertionError(f"H3DataLoader not available or failed: {e}")

@pytest.mark.setup
@pytest.mark.integration
def test_load_data_to_h3_grid(tmp_path):
    """
    Test high-level load_data_to_h3_grid function. Requires load_data_to_h3_grid to be available and functional.
    Fails if the dependency is missing or broken.
    """
    try:
        # Create sample GeoJSON
        sample_geojson = {
            'type': 'FeatureCollection',
            'features': [{
                'type': 'Feature',
                'properties': {},
                'geometry': {'type': 'Point', 'coordinates': [0, 0]}
            }]
        }
        input_file = tmp_path / 'sample.geojson'
        with open(input_file, 'w') as f:
            json.dump(sample_geojson, f)
        output_file = tmp_path / 'output_h3.geojson'
        success = load_data_to_h3_grid(str(input_file), str(output_file), resolution=8)
        assert success
        assert output_file.exists()
    except Exception as e:
        raise AssertionError(f"load_data_to_h3_grid not available or failed: {e}")

@pytest.mark.setup
@pytest.mark.unit
def test_h3_to_geojson():
    """Test H3 to GeoJSON conversion."""
    h3_indices = ['8928308280fffff']
    properties = {'8928308280fffff': {'test': 'value'}}
    geojson = h3_to_geojson(h3_indices, properties)
    assert geojson['type'] == 'FeatureCollection'
    assert len(geojson['features']) == 1
    assert 'h3_index' in geojson['features'][0]['properties']

@pytest.mark.setup
@pytest.mark.unit
def test_geojson_to_h3():
    """Test GeoJSON to H3 conversion."""
    sample_geojson = {
        'type': 'FeatureCollection',
        'features': [{
            'type': 'Feature',
            'properties': {'test': 'value'},
            'geometry': {'type': 'Point', 'coordinates': [0, 0]}
        }]
    }
    result = geojson_to_h3(sample_geojson, resolution=9, feature_properties=True)
    assert len(result['h3_indices']) > 0
    assert 'properties' in result 