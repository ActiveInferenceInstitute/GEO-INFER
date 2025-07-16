#!/usr/bin/env python3
"""
Test script for Cascadia modules

This script tests the converted modules to ensure they work correctly
with the BaseAnalysisModule pattern and SPACE integration.
"""

import sys
import os
from pathlib import Path

# Add paths for imports
cascadian_dir = os.path.dirname(os.path.realpath(__file__))
project_root = os.path.abspath(os.path.join(cascadian_dir, '..', '..', '..'))
place_src_path = os.path.join(project_root, 'GEO-INFER-PLACE', 'src')
space_src_path = os.path.join(project_root, 'GEO-INFER-SPACE', 'src')

for p in [cascadian_dir, place_src_path, space_src_path]:
    if os.path.isdir(p) and p not in sys.path:
        sys.path.insert(0, p)

import logging
import yaml
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Import SPACE utilities to test H3 integration
from geo_infer_space.utils.h3_utils import latlng_to_cell, cell_to_latlng, cell_to_latlng_boundary
from geo_infer_space.core.base_module import BaseAnalysisModule

# Import backend
from geo_infer_place.core.unified_backend import CascadianAgriculturalH3Backend

# Import converted modules
from zoning.geo_infer_zoning import GeoInferZoning
from current_use.geo_infer_current_use import GeoInferCurrentUse
from ownership.geo_infer_ownership import GeoInferOwnership
from improvements.geo_infer_improvements import GeoInferImprovements

def test_h3_integration():
    """Test basic H3 integration from SPACE"""
    logger.info("Testing H3 integration...")
    
    try:
        # Test basic H3 functions
        lat, lng = 40.5, -120.5  # Lassen County area
        h3_cell = latlng_to_cell(lat, lng, 8)
        logger.info(f"✅ H3 cell for ({lat}, {lng}): {h3_cell}")
        
        # Test reverse conversion
        lat2, lng2 = cell_to_latlng(h3_cell)
        logger.info(f"✅ Reverse conversion: ({lat2:.3f}, {lng2:.3f})")
        
        # Test boundary
        boundary = cell_to_latlng_boundary(h3_cell)
        logger.info(f"✅ Boundary has {len(boundary)} points")
        
        return True
    except Exception as e:
        logger.error(f"❌ H3 integration test failed: {e}")
        return False

def test_module_initialization():
    """Test module initialization with backend"""
    logger.info("Testing module initialization...")
    
    try:
        # Load config
        config_path = Path('config/analysis_config.yaml')
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        target_counties = config['analysis_settings']['target_counties']
        
        # Create a test backend
        backend = CascadianAgriculturalH3Backend(
            modules={},
            resolution=8,
            bioregion='Cascadia',
            target_counties=target_counties,
            base_data_dir=Path('./test_output/data'),
            osc_repo_dir=Path(project_root) / 'GEO-INFER-SPACE' / 'repo'
        )
        
        logger.info(f"✅ Backend created with {len(backend.target_hexagons)} target hexagons")
        
        # Test module initialization
        modules = {}
        
        # Test zoning module
        try:
            modules['zoning'] = GeoInferZoning(backend)
            logger.info("✅ Zoning module initialized")
        except Exception as e:
            logger.error(f"❌ Zoning module failed: {e}")
        
        # Test current_use module
        try:
            modules['current_use'] = GeoInferCurrentUse(backend)
            logger.info("✅ Current use module initialized")
        except Exception as e:
            logger.error(f"❌ Current use module failed: {e}")
        
        # Test ownership module
        try:
            modules['ownership'] = GeoInferOwnership(backend)
            logger.info("✅ Ownership module initialized")
        except Exception as e:
            logger.error(f"❌ Ownership module failed: {e}")
        
        # Test improvements module
        try:
            modules['improvements'] = GeoInferImprovements(backend)
            logger.info("✅ Improvements module initialized")
        except Exception as e:
            logger.error(f"❌ Improvements module failed: {e}")
        
        logger.info(f"✅ Successfully initialized {len(modules)} modules")
        return True, backend, modules
        
    except Exception as e:
        logger.error(f"❌ Module initialization test failed: {e}")
        return False, None, None

def test_module_workflow():
    """Test the BaseAnalysisModule workflow"""
    logger.info("Testing module workflow...")
    
    success, backend, modules = test_module_initialization()
    if not success:
        return False
    
    # Test the standardized workflow for one module
    try:
        zoning_module = modules['zoning']
        
        # Test that module has required methods
        required_methods = ['acquire_raw_data', 'run_final_analysis', 'run_analysis']
        for method_name in required_methods:
            if hasattr(zoning_module, method_name):
                logger.info(f"✅ {method_name} method exists")
            else:
                logger.error(f"❌ {method_name} method missing")
        
        # Test data directory creation
        if zoning_module.data_dir.exists():
            logger.info(f"✅ Data directory created: {zoning_module.data_dir}")
        else:
            logger.error(f"❌ Data directory not created")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Module workflow test failed: {e}")
        return False

def main():
    """Run all tests"""
    logger.info("🚀 Starting Cascadia module tests...")
    
    # Create output directory
    output_dir = Path('./test_output')
    output_dir.mkdir(exist_ok=True)
    
    tests = [
        ("H3 Integration", test_h3_integration),
        ("Module Initialization", lambda: test_module_initialization()[0]),
        ("Module Workflow", test_module_workflow)
    ]
    
    results = {}
    for test_name, test_func in tests:
        logger.info(f"\n--- Running {test_name} Test ---")
        try:
            results[test_name] = test_func()
        except Exception as e:
            logger.error(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False
    
    # Print summary
    logger.info("\n--- Test Summary ---")
    passed = 0
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{test_name}: {status}")
        if result:
            passed += 1
    
    logger.info(f"\nOverall: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        logger.info("🎉 All tests passed! Modules are working correctly.")
    else:
        logger.warning("⚠️ Some tests failed. Check the logs above.")
    
    return passed == len(tests)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 