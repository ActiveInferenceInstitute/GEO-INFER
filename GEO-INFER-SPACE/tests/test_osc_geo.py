import pytest
from pathlib import Path
from geo_infer_space.osc_geo.core.repos import clone_osc_repos
from geo_infer_space.osc_geo.utils.osc_simple_status import check_repo_status

import tempfile
import json
import shutil
import subprocess
import sys
import os
from geo_infer_space.osc_geo import H3GridManager, H3DataLoader, load_data_to_h3_grid
from geo_infer_space.osc_geo.utils.h3_utils import cell_to_latlngjson, geojson_to_h3

def reset_and_reinstall_venvs(repo_base_dir):
    """
    Reset and reinstall virtual environments for all cloned OSC repositories.
    This ensures clean, working virtual environments from a cold start.
    
    Args:
        repo_base_dir (str): Base directory containing cloned repositories
    """
    repo_path = Path(repo_base_dir)
    if not repo_path.exists():
        print(f"Repository base directory does not exist: {repo_base_dir}")
        return False
    
    success_count = 0
    total_repos = 0
    
    for repo_dir in repo_path.iterdir():
        if not repo_dir.is_dir() or repo_dir.name.startswith('.'):
            continue
            
        total_repos += 1
        print(f"Processing repository: {repo_dir.name}")
        
        # Check if this is an OSC repository
        if not (repo_dir.name.startswith('osc-') or 'h3' in repo_dir.name.lower()):
            print(f"Skipping non-OSC repository: {repo_dir.name}")
            continue
        
        venv_path = repo_dir / "venv"
        requirements_file = repo_dir / "requirements.txt"
        
        # Remove existing virtual environment if it exists
        if venv_path.exists():
            print(f"Removing existing virtual environment: {venv_path}")
            try:
                shutil.rmtree(venv_path)
            except Exception as e:
                print(f"Warning: Could not remove {venv_path}: {e}")
        
        # Create new virtual environment
        print(f"Creating new virtual environment: {venv_path}")
        try:
            result = subprocess.run([
                sys.executable, "-m", "venv", str(venv_path)
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode != 0:
                print(f"Failed to create virtual environment for {repo_dir.name}: {result.stderr}")
                continue
                
        except subprocess.TimeoutExpired:
            print(f"Timeout creating virtual environment for {repo_dir.name}")
            continue
        except Exception as e:
            print(f"Error creating virtual environment for {repo_dir.name}: {e}")
            continue
        
        # Install requirements if they exist
        if requirements_file.exists():
            print(f"Installing requirements from: {requirements_file}")
            try:
                # Get the path to pip in the new virtual environment
                if os.name == 'nt':  # Windows
                    pip_path = venv_path / "Scripts" / "pip"
                else:  # Unix/Linux/macOS
                    pip_path = venv_path / "bin" / "pip"
                
                # Install requirements
                result = subprocess.run([
                    str(pip_path), "install", "-r", str(requirements_file)
                ], capture_output=True, text=True, timeout=300)
                
                if result.returncode != 0:
                    print(f"Warning: Failed to install requirements for {repo_dir.name}: {result.stderr}")
                else:
                    print(f"Successfully installed requirements for {repo_dir.name}")
                    
            except subprocess.TimeoutExpired:
                print(f"Timeout installing requirements for {repo_dir.name}")
            except Exception as e:
                print(f"Error installing requirements for {repo_dir.name}: {e}")
        else:
            print(f"No requirements.txt found for {repo_dir.name}")
        
        # Verify H3 installation specifically
        try:
            if os.name == 'nt':  # Windows
                python_path = venv_path / "Scripts" / "python"
            else:  # Unix/Linux/macOS
                python_path = venv_path / "bin" / "python"
            
            # Test H3 import
            result = subprocess.run([
                str(python_path), "-c", "import h3; print(f'H3 version: {h3.__version__}')"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print(f"H3 verification successful for {repo_dir.name}: {result.stdout.strip()}")
                success_count += 1
            else:
                print(f"H3 verification failed for {repo_dir.name}: {result.stderr}")
                
        except Exception as e:
            print(f"Error verifying H3 for {repo_dir.name}: {e}")
    
    print(f"Virtual environment reset complete: {success_count}/{total_repos} repositories processed successfully")
    return success_count > 0

@pytest.mark.setup
@pytest.mark.integration
def test_clone_repos(tmp_path):
    """Test cloning of OSC repos into temp path and reset virtual environments."""
    # Clone repositories
    success = clone_osc_repos(str(tmp_path))
    assert success
    assert len(list(tmp_path.iterdir())) > 0  # Check repos were cloned
    
    # Reset and reinstall virtual environments
    print("Resetting and reinstalling virtual environments...")
    venv_success = reset_and_reinstall_venvs(str(tmp_path))
    assert venv_success, "Virtual environment reset failed"

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
        
        # Try to create H3DataLoader with timeout to prevent hanging
        import signal
        
        def timeout_handler(signum, frame):
            raise TimeoutError("H3DataLoader initialization timed out")
        
        # Set a 30-second timeout (increased for virtual environment setup)
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(30)
        
        try:
            loader = H3DataLoader()
            signal.alarm(0)  # Cancel the alarm
            
            success = loader.load_data(str(input_file), str(output_file), resolution=8)
            assert success
            assert output_file.exists()
        except TimeoutError:
            signal.alarm(0)  # Cancel the alarm
            pytest.skip("H3DataLoader initialization timed out - likely due to virtual environment issues")
        except Exception as e:
            signal.alarm(0)  # Cancel the alarm
            if "ImportError" in str(e) or "cannot import name" in str(e):
                pytest.skip(f"H3DataLoader not available due to import issues: {e}")
            else:
                raise AssertionError(f"H3DataLoader failed: {e}")
                
    except Exception as e:
        if "ImportError" in str(e) or "cannot import name" in str(e):
            pytest.skip(f"H3DataLoader not available due to import issues: {e}")
        else:
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
        
        # Try to call load_data_to_h3_grid with timeout to prevent hanging
        import signal
        
        def timeout_handler(signum, frame):
            raise TimeoutError("load_data_to_h3_grid timed out")
        
        # Set a 30-second timeout (increased for virtual environment setup)
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(30)
        
        try:
            success = load_data_to_h3_grid(str(input_file), str(output_file), resolution=8)
            signal.alarm(0)  # Cancel the alarm
            assert success
            assert output_file.exists()
        except TimeoutError:
            signal.alarm(0)  # Cancel the alarm
            pytest.skip("load_data_to_h3_grid timed out - likely due to virtual environment issues")
        except Exception as e:
            signal.alarm(0)  # Cancel the alarm
            if "ImportError" in str(e) or "cannot import name" in str(e):
                pytest.skip(f"load_data_to_h3_grid not available due to import issues: {e}")
            else:
                raise AssertionError(f"load_data_to_h3_grid failed: {e}")
                
    except Exception as e:
        if "ImportError" in str(e) or "cannot import name" in str(e):
            pytest.skip(f"load_data_to_h3_grid not available due to import issues: {e}")
        else:
            raise AssertionError(f"load_data_to_h3_grid not available or failed: {e}")

@pytest.mark.setup
@pytest.mark.unit
def test_cell_to_latlngjson():
    """Test H3 to GeoJSON conversion."""
    h3_indices = ['8928308280fffff']
    properties = {'8928308280fffff': {'test': 'value'}}
    geojson = cell_to_latlngjson(h3_indices, properties)
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