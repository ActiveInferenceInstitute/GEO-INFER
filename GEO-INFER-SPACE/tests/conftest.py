import pytest
import sys
from pathlib import Path
from geo_infer_space.osc_geo import create_h3_data_loader

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
    """Set up environment for cloned repo tests."""
    # Set OSC_REPOS_DIR environment variable if not already set
    import os
    if 'OSC_REPOS_DIR' not in os.environ:
        os.environ['OSC_REPOS_DIR'] = str(repo_dir)
    
    # Install dependencies for cloned repos if needed
    for repo_path in repo_dir.iterdir():
        if repo_path.is_dir() and not repo_path.name.startswith('.'):
            requirements_file = repo_path / "requirements.txt"
            if requirements_file.exists():
                # Note: In a real setup, you might want to install these in a separate venv
                # For now, we'll just ensure the Python path is set correctly
                print(f"Found requirements for {repo_path.name}: {requirements_file}")
    
    yield 