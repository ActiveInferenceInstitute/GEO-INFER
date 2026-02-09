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
cascadian_test_dir = os.path.dirname(os.path.realpath(__file__))
cascadian_root = os.path.abspath(os.path.join(cascadian_test_dir, '..', '..'))
project_root = os.path.abspath(os.path.join(cascadian_root, '..', '..', '..'))
place_src_path = os.path.join(project_root, 'GEO-INFER-PLACE', 'src')
space_src_path = os.path.join(project_root, 'GEO-INFER-SPACE', 'src')

for p in [cascadian_root, place_src_path, space_src_path]:
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
from src.data_modules.zoning.geo_infer_zoning import GeoInferZoning
from src.data_modules.current_use.geo_infer_current_use import GeoInferCurrentUse
from src.data_modules.ownership.geo_infer_ownership import GeoInferOwnership
from src.data_modules.improvements.geo_infer_improvements import GeoInferImprovements

def test_h3_integration():
    """Test basic H3 integration from SPACE"""
    logger.info("Testing H3 integration...")
    
    # Test basic H3 functions
    lat, lng = 40.5, -120.5  # Lassen County area
    h3_cell = latlng_to_cell(lat, lng, 8)
    assert h3_cell, "H3 cell creation failed"
    logger.info(f"✅ H3 cell for ({lat}, {lng}): {h3_cell}")
    
    # Test reverse conversion
    lat2, lng2 = cell_to_latlng(h3_cell)
    assert abs(lat - lat2) < 0.1, "Reverse lat conversion inaccurate"
    assert abs(lng - lng2) < 0.1, "Reverse lng conversion inaccurate"
    logger.info(f"✅ Reverse conversion: ({lat2:.3f}, {lng2:.3f})")
    
    # Test boundary
    boundary = cell_to_latlng_boundary(h3_cell)
    assert len(boundary) > 0, "Boundary has no points"
    logger.info(f"✅ Boundary has {len(boundary)} points")

def _init_backend_and_modules():
    """Helper: create backend and initialize modules. Returns (backend, modules)."""
    config_path = Path('config/analysis_config.yaml')
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    output_dir = Path('./test_output')
    output_dir.mkdir(exist_ok=True)
    osc_repo_dir = Path(os.environ.get(
        'OSC_REPOS_DIR',
        str(Path(__file__).resolve().parents[4] / "GEO-INFER-SPACE" / "repo")
    ))
    backend = CascadianAgriculturalH3Backend(
        modules={},
        resolution=8,
        bioregion='Cascadia',
        target_counties={'CA': ['Lassen']},
        base_data_dir=output_dir / 'data',
        osc_repo_dir=osc_repo_dir
    )
    logger.info(f"✅ Backend created with {len(backend.target_hexagons)} target hexagons")

    modules = {}
    modules['zoning'] = GeoInferZoning(backend)
    logger.info("✅ Zoning module initialized")
    modules['current_use'] = GeoInferCurrentUse(backend)
    logger.info("✅ Current use module initialized")
    modules['ownership'] = GeoInferOwnership(backend)
    logger.info("✅ Ownership module initialized")
    modules['improvements'] = GeoInferImprovements(backend)
    logger.info("✅ Improvements module initialized")

    return backend, modules


def test_module_initialization():
    """Test module initialization with backend"""
    logger.info("Testing module initialization...")
    backend, modules = _init_backend_and_modules()
    assert backend is not None, "Backend creation failed"
    assert len(modules) == 4, f"Expected 4 modules, got {len(modules)}"
    logger.info(f"✅ Successfully initialized {len(modules)} modules")

def test_module_workflow():
    """Test the BaseAnalysisModule workflow"""
    logger.info("Testing module workflow...")
    backend, modules = _init_backend_and_modules()
    
    zoning_module = modules['zoning']
    
    # Test that module has required methods
    required_methods = ['acquire_raw_data', 'run_final_analysis', 'run_analysis']
    for method_name in required_methods:
        assert hasattr(zoning_module, method_name), f"{method_name} method missing"
        logger.info(f"✅ {method_name} method exists")
    
    # Test data directory creation
    assert zoning_module.data_dir.exists(), "Data directory not created"
    logger.info(f"✅ Data directory created: {zoning_module.data_dir}")

def main():
    """Run all tests (CLI entry point)."""
    logger.info("🚀 Starting Cascadia module tests...")
    output_dir = Path('./test_output')
    output_dir.mkdir(exist_ok=True)

    tests = [
        ("H3 Integration", test_h3_integration),
        ("Module Initialization", test_module_initialization),
        ("Module Workflow", test_module_workflow),
    ]

    passed = 0
    for test_name, test_func in tests:
        logger.info(f"\n--- Running {test_name} Test ---")
        try:
            test_func()
            passed += 1
            logger.info(f"{test_name}: ✅ PASS")
        except Exception as e:
            logger.error(f"{test_name}: ❌ FAIL — {e}")

    logger.info(f"\nOverall: {passed}/{len(tests)} tests passed")
    return passed == len(tests)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)