#!/usr/bin/env python3
"""
Test script to verify OSC repository path detection fix
"""

import sys
import os
from pathlib import Path

# Add paths
cascadian_dir = os.path.dirname(os.path.realpath(__file__))
project_root = os.path.abspath(os.path.join(cascadian_dir, '..', '..', '..'))
place_src_path = os.path.join(project_root, 'GEO-INFER-PLACE', 'src')
space_src_path = os.path.join(project_root, 'GEO-INFER-SPACE', 'src')

for p in [cascadian_dir, place_src_path, space_src_path]:
    if os.path.isdir(p) and p not in sys.path:
        sys.path.insert(0, p)

import logging
from unittest.mock import patch
import yaml

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_fixed_backend_initialization():
    """Test backend initialization with properly passed repo path"""
    logger.info("Testing fixed backend initialization...")
    
    try:
        # Load config
        config_path = Path('config/analysis_config.yaml')
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        target_counties = config['analysis_settings']['target_counties']
        
        # Set environment variable for OSC repos
        correct_repo_path = str(Path(project_root) / 'GEO-INFER-SPACE' / 'repo')
        os.environ['OSC_REPOS_DIR'] = correct_repo_path
        logger.info(f"Set OSC_REPOS_DIR to: {correct_repo_path}")
        
        # Verify the path exists
        if os.path.exists(correct_repo_path):
            logger.info(f"✅ OSC repo directory exists: {correct_repo_path}")
            for item in os.listdir(correct_repo_path):
                logger.info(f"  📁 {item}")
        else:
            logger.error(f"❌ OSC repo directory does not exist: {correct_repo_path}")
            return False
        
        # Test path detection with environment variable
        from geo_infer_space.osc_geo.core.repos import get_repo_path
        
        for repo_key in ['h3loader-cli', 'h3grid-srv']:
            result = get_repo_path(repo_key, None)  # None should use env var
            logger.info(f"  {repo_key}: {result}")
            if result and os.path.exists(result):
                logger.info(f"    ✅ Found and verified")
            else:
                logger.error(f"    ❌ Not found")
                return False
        
        # Test module imports
        from zoning.geo_infer_zoning import GeoInferZoning
        from current_use.geo_infer_current_use import GeoInferCurrentUse
        logger.info("✅ Module imports successful")
        
        # Test backend initialization with environment variable approach
        from geo_infer_place.core.unified_backend import CascadianAgriculturalH3Backend
        
        backend = CascadianAgriculturalH3Backend(
            modules={},
            resolution=8,
            bioregion='Cascadia',
            target_counties=target_counties,
            base_data_dir=Path('./test_output/data'),
            osc_repo_dir=correct_repo_path  # Explicit path
        )
        
        logger.info(f"✅ Backend initialized with {len(backend.target_hexagons)} hexagons")
        
        # Test module initialization
        zoning_module = GeoInferZoning(backend)
        logger.info("✅ Zoning module initialized successfully")
        
        current_use_module = GeoInferCurrentUse(backend)
        logger.info("✅ Current use module initialized successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Clean up environment variable
        if 'OSC_REPOS_DIR' in os.environ:
            del os.environ['OSC_REPOS_DIR']

def test_main_script_integration():
    """Test integration with main script approach"""
    logger.info("Testing main script integration...")
    
    try:
        # Set the environment variable before any imports
        correct_repo_path = str(Path(project_root) / 'GEO-INFER-SPACE' / 'repo')
        os.environ['OSC_REPOS_DIR'] = correct_repo_path
        
        # Import main script components
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "cascadia_main",
            Path(cascadian_dir) / "cascadia_main.py"
        )
        cascadia_main = importlib.util.module_from_spec(spec)
        
        # Mock the problematic imports to avoid full execution
        with patch('geo_infer_space.osc_geo.check_integration_status') as mock_status:
            mock_status.return_value = type('MockStatus', (), {'is_ready': lambda: True})()
            
            spec.loader.exec_module(cascadia_main)
            logger.info("✅ Main script loaded successfully")
        
        # Test configuration loading
        config = cascadia_main.load_analysis_config()
        logger.info("✅ Configuration loaded successfully")
        
        # Test dependency checking
        deps_ok = cascadia_main.check_dependencies()
        logger.info(f"✅ Dependency check: {deps_ok}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Main script integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Clean up environment variable
        if 'OSC_REPOS_DIR' in os.environ:
            del os.environ['OSC_REPOS_DIR']

def main():
    """Run all tests"""
    logger.info("🚀 Starting repository path fix tests...")
    
    tests = [
        ("Fixed Backend Initialization", test_fixed_backend_initialization),
        ("Main Script Integration", test_main_script_integration)
    ]
    
    results = {}
    for test_name, test_func in tests:
        logger.info(f"\n--- Running {test_name} ---")
        results[test_name] = test_func()
        status = "✅ PASS" if results[test_name] else "❌ FAIL"
        logger.info(f"{test_name}: {status}")
    
    # Summary
    passed = sum(results.values())
    total = len(results)
    
    logger.info(f"\n=== TEST SUMMARY ===")
    logger.info(f"Passed: {passed}/{total}")
    
    if passed == total:
        logger.info("🎉 All tests passed! The fix works correctly.")
    else:
        logger.warning("⚠️ Some tests failed. Fix needs refinement.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 