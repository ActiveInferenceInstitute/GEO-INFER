import pytest
import sys
from pathlib import Path
import subprocess
import shutil
import os

# Optional: OSC integration imports (skip if heavy deps missing)
try:
    from geo_infer_space.osc_geo import create_h3_data_loader  # type: ignore
except Exception as _osc_exc:  # pragma: no cover
    create_h3_data_loader = None  # type: ignore
    print(f"[tests] Warning: OSC integration not available; some tests may be skipped: {_osc_exc}")

# Add cloned repo paths to Python path for test discovery
repo_dir = Path(__file__).parent.parent / "repo"
if repo_dir.exists():
    for repo_path in repo_dir.iterdir():
        if repo_path.is_dir() and not repo_path.name.startswith('.'):
            # Add the repo's src directory to Python path
            src_path = repo_path / "src"
            if src_path.exists():
                sys.path.insert(0, str(src_path))
            # Also add the repo root for packages that install there
            sys.path.insert(0, str(repo_path))

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

# Test execution order - dependencies first, then core, then spatial, then reporting
def pytest_collection_modifyitems(config, items):
    """Reorder tests to run in logical dependency order."""
    
    # Define test order based on dependencies
    test_order = [
        # 1. Setup and repository tests (foundational)
        "test_osc_scripts.py",
        "test_osc_geo.py",
        
        # 2. Core functionality tests (base modules and backend)
        "test_base_module.py", 
        "test_core.py",
        "test_unified_backend.py",
        
        # 3. Spatial analysis tests (data processing and spatial operations)
        "test_data_integrator.py",
        "test_spatial_processor.py",
        "test_place_analyzer.py",
        
        # 4. Reporting and visualization tests (final output)
        "test_enhanced_reporting.py",
        "test_visualization_engine.py"
    ]
    
    # Create mapping of test file to order
    test_order_map = {name: index for index, name in enumerate(test_order)}
    
    # Sort items based on the order
    def get_test_order(item):
        test_file = item.nodeid.split("::")[0].split("/")[-1]
        return test_order_map.get(test_file, len(test_order))
    
    items.sort(key=get_test_order)

@pytest.fixture(scope="session")
def test_data_dir(tmp_path_factory):
    """Create a temporary test data directory for the test session."""
    return tmp_path_factory.mktemp("test_data")

@pytest.fixture(scope="session") 
def sample_geojson():
    """Provide a standard sample GeoJSON for testing."""
    return {
        'type': 'FeatureCollection',
        'features': [{
            'type': 'Feature',
            'properties': {'area': 'TestArea', 'subarea': 'all'},
            'geometry': {
                'type': 'Polygon', 
                'coordinates': [[[0,0], [1,0], [1,1], [0,1], [0,0]]]
            }
        }]
    }

@pytest.fixture(scope="session", autouse=True)
def setup_repo_environment():
    """Set up environment for cloned repo tests and reset virtual environments if needed."""
    # Set OSC_REPOS_DIR environment variable if not already set
    import os
    if 'OSC_REPOS_DIR' not in os.environ:
        os.environ['OSC_REPOS_DIR'] = str(repo_dir)
    
    # Check if virtual environments need resetting (only if they exist and are corrupted)
    if repo_dir.exists():
        needs_reset = False
        for repo_path in repo_dir.iterdir():
            if repo_path.is_dir() and not repo_path.name.startswith('.'):
                if repo_path.name.startswith('osc-') or 'h3' in repo_path.name.lower():
                    venv_path = repo_path / "venv"
                    if venv_path.exists():
                        # Quick check if H3 is working
                        try:
                            if os.name == 'nt':  # Windows
                                python_path = venv_path / "Scripts" / "python"
                            else:  # Unix/Linux/macOS
                                python_path = venv_path / "bin" / "python"
                            
                            result = subprocess.run([
                                str(python_path), "-c", "import h3; print('H3 OK')"
                            ], capture_output=True, text=True, timeout=10)
                            
                            if result.returncode != 0:
                                needs_reset = True
                                print(f"H3 import failed in {repo_path.name}, will reset virtual environment")
                        except:
                            needs_reset = True
                            print(f"Could not test H3 in {repo_path.name}, will reset virtual environment")
        
        if needs_reset:
            print("Resetting virtual environments for corrupted cloned repositories...")
            reset_and_reinstall_venvs(str(repo_dir))
        else:
            print("Virtual environments appear to be working, skipping reset")
    
    yield 