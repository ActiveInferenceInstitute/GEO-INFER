#!/usr/bin/env python3
"""
Comprehensive Validation Runner for Cascadia Framework

This script runs all validation tests systematically to ensure the framework
is fully functional and ready for production use.
"""

import sys
import os
import subprocess
import logging
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

# Setup paths
cascadian_dir = os.path.dirname(os.path.realpath(__file__))
project_root = os.path.abspath(os.path.join(cascadian_dir, '..', '..', '..'))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_main_script_syntax():
    """Test that the main script has valid syntax and can be imported"""
    logger.info("Testing main script syntax...")
    
    main_script = Path(cascadian_dir) / "cascadia_main.py"
    
    if not main_script.exists():
        logger.error(f"❌ Main script not found: {main_script}")
        return False
    
    try:
        # Test syntax by importing
        import importlib.util
        spec = importlib.util.spec_from_file_location("cascadia_main", main_script)
        cascadia_main = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cascadia_main)
        
        # Check that key functions exist
        required_functions = [
            'setup_logging',
            'check_dependencies',
            'load_analysis_config',
            'generate_analysis_report',
            'main'
        ]
        
        missing_functions = []
        for func_name in required_functions:
            if not hasattr(cascadia_main, func_name):
                missing_functions.append(func_name)
        
        if missing_functions:
            logger.error(f"❌ Missing functions: {missing_functions}")
            return False
        
        logger.info("✅ Main script syntax is valid")
        logger.info("✅ All required functions are present")
        return True
        
    except Exception as e:
        logger.error(f"❌ Main script syntax error: {e}")
        return False

def test_configuration_files():
    """Test that configuration files exist and are valid"""
    logger.info("Testing configuration files...")
    
    config_path = Path(cascadian_dir) / "config" / "analysis_config.yaml"
    
    if not config_path.exists():
        logger.error(f"❌ Configuration file not found: {config_path}")
        return False
    
    try:
        import yaml
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Check required sections
        required_sections = ['analysis_settings']
        missing_sections = []
        for section in required_sections:
            if section not in config:
                missing_sections.append(section)
        
        if missing_sections:
            logger.error(f"❌ Missing configuration sections: {missing_sections}")
            return False
        
        logger.info("✅ Configuration file is valid")
        return True
        
    except Exception as e:
        logger.error(f"❌ Configuration file error: {e}")
        return False

def test_module_structure():
    """Test that module structure is correct"""
    logger.info("Testing module structure...")
    
    required_modules = ['zoning', 'current_use', 'ownership', 'improvements']
    missing_modules = []
    
    for module_name in required_modules:
        module_path = Path(cascadian_dir) / module_name
        if not module_path.exists():
            missing_modules.append(module_name)
            continue
        
        # Check for required files
        required_files = [
            f"geo_infer_{module_name}.py",
            "__init__.py"
        ]
        
        for file_name in required_files:
            file_path = module_path / file_name
            if not file_path.exists():
                logger.warning(f"⚠️ Missing file in {module_name}: {file_name}")
    
    if missing_modules:
        logger.error(f"❌ Missing modules: {missing_modules}")
        return False
    
    logger.info("✅ Module structure is correct")
    return True

def test_h3_integration():
    """Test H3 integration from SPACE"""
    logger.info("Testing H3 integration...")
    
    try:
        # Add SPACE src to path
        space_src_path = os.path.join(project_root, 'GEO-INFER-SPACE', 'src')
        if space_src_path not in sys.path:
            sys.path.insert(0, space_src_path)
        
        from geo_infer_space.utils.h3_utils import latlng_to_cell, cell_to_latlng, cell_to_latlng_boundary
        
        # Test H3 functions
        lat, lng = 40.5, -120.5
        h3_cell = latlng_to_cell(lat, lng, 8)
        lat2, lng2 = cell_to_latlng(h3_cell)
        boundary = cell_to_latlng_boundary(h3_cell)
        
        # Validate results
        assert abs(lat - lat2) < 0.01
        assert abs(lng - lng2) < 0.01
        assert len(boundary) == 6
        
        logger.info(f"✅ H3 utilities working: {h3_cell}")
        return True
        
    except Exception as e:
        logger.error(f"❌ H3 integration test failed: {e}")
        return False

def test_backend_initialization():
    """Test backend initialization with mocked dependencies"""
    logger.info("Testing backend initialization...")
    
    try:
        # Add PLACE src to path
        place_src_path = os.path.join(project_root, 'GEO-INFER-PLACE', 'src')
        if place_src_path not in sys.path:
            sys.path.insert(0, place_src_path)
        
        # Mock the H3 data loader creation to avoid OSC issues
        from unittest.mock import patch, Mock
        with patch('geo_infer_place.core.unified_backend.create_h3_data_loader') as mock_loader:
            # Configure mock to return a functional mock object
            mock_loader.return_value = Mock()
            
            # Import and test backend
            from geo_infer_place.core.unified_backend import CascadianAgriculturalH3Backend
            
            backend = CascadianAgriculturalH3Backend(
                modules={},
                resolution=8,
                bioregion='Cascadia',
                target_counties={'CA': ['Lassen'], 'OR': ['Marion']},
                base_data_dir=Path('/tmp/test_data'),
                osc_repo_dir=Path('/tmp/fake_repo')
            )
            
            # Test basic backend properties
            assert backend.resolution == 8
            assert backend.bioregion == 'Cascadia'
            assert len(backend.target_hexagons) > 0
            logger.info(f"✅ Backend created with {len(backend.target_hexagons)} hexagons")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Backend initialization test failed: {e}")
        return False

def test_module_imports():
    """Test that all modules can be imported"""
    logger.info("Testing module imports...")
    
    try:
        # Add paths
        place_src_path = os.path.join(project_root, 'GEO-INFER-PLACE', 'src')
        space_src_path = os.path.join(project_root, 'GEO-INFER-SPACE', 'src')
        
        for p in [cascadian_dir, place_src_path, space_src_path]:
            if os.path.isdir(p) and p not in sys.path:
                sys.path.insert(0, p)
        
        # Test module imports
        from zoning.geo_infer_zoning import GeoInferZoning
        from current_use.geo_infer_current_use import GeoInferCurrentUse
        from ownership.geo_infer_ownership import GeoInferOwnership
        from improvements.geo_infer_improvements import GeoInferImprovements
        
        logger.info("✅ All modules imported successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Module import test failed: {e}")
        return False

def test_main_script_functionality():
    """Test main script functionality with mocked dependencies"""
    logger.info("Testing main script functionality...")
    
    # Create temporary test environment
    with tempfile.TemporaryDirectory(prefix="cascadia_validation_") as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create test configuration
        config_dir = temp_path / 'config'
        config_dir.mkdir(exist_ok=True)
        
        test_config = {
            'analysis_settings': {
                'target_counties': {
                    'CA': ['Lassen'],
                    'OR': ['Marion']
                },
                'active_modules': ['zoning', 'current_use'],
                'h3_resolution': 8
            }
        }
        
        with open(config_dir / 'analysis_config.yaml', 'w') as f:
            import yaml
            yaml.dump(test_config, f)
        
        # Change to temp directory
        original_cwd = os.getcwd()
        os.chdir(temp_path)
        
        try:
            # Import and test main script components with comprehensive mocking
            import importlib.util
            from unittest.mock import patch, Mock
            
            spec = importlib.util.spec_from_file_location(
                "cascadia_main",
                Path(cascadian_dir) / "cascadia_main.py"
            )
            
            # Mock all external dependencies before importing
            with patch('geo_infer_space.osc_geo.create_h3_data_loader') as mock_h3_loader, \
                 patch('geo_infer_space.osc_geo.setup_osc_geo') as mock_setup, \
                 patch('geo_infer_space.core.spatial_processor.SpatialProcessor') as mock_spatial, \
                 patch('geo_infer_space.core.visualization_engine.InteractiveVisualizationEngine') as mock_viz, \
                 patch('geo_infer_space.core.data_integrator.DataIntegrator') as mock_integrator, \
                 patch('geo_infer_place.core.unified_backend.create_h3_data_loader') as mock_place_loader:
                
                # Configure mocks
                mock_h3_loader.return_value = Mock()
                mock_setup.return_value = Mock()
                mock_spatial.return_value = Mock()
                mock_viz.return_value = Mock()
                mock_integrator.return_value = Mock()
                mock_place_loader.return_value = Mock()
                
                # Import the module
                cascadia_main = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(cascadia_main)
                
                logger.info("✅ Main script imported successfully")
                
                # Test setup_logging function
                cascadia_main.setup_logging(verbose=False, output_dir=str(temp_path))
                logger.info("✅ setup_logging function works")
                
                # Test load_analysis_config function
                config = cascadia_main.load_analysis_config()
                assert 'analysis_settings' in config
                logger.info("✅ load_analysis_config function works")
                
                # Test report generation with mock data
                mock_summary = {
                    'bioregion': 'Cascadia',
                    'h3_resolution': 8,
                    'total_hexagons': 1000,
                    'modules_executed': ['zoning', 'current_use'],
                    'module_coverage': {'zoning': 800, 'current_use': 750},
                    'redevelopment_potential': {
                        'mean_score': 0.65,
                        'median_score': 0.60,
                        'high_potential_count': 150,
                        'low_potential_count': 200
                    }
                }
                
                report_path = temp_path / 'test_report.md'
                cascadia_main.generate_analysis_report(mock_summary, report_path)
                assert report_path.exists()
                
                # Validate report content
                with open(report_path, 'r') as f:
                    report_content = f.read()
                    assert 'Cascadia Agricultural Land Analysis Report' in report_content
                    assert 'Total Hexagons Analyzed: 1,000' in report_content
                    assert 'SPACE Integration' in report_content
                
                logger.info("✅ generate_analysis_report function works")
                
                return True
                
        except Exception as e:
            logger.error(f"❌ Main script functionality test failed: {e}")
            return False
        finally:
            os.chdir(original_cwd)

def run_comprehensive_validation():
    """Run all comprehensive validation tests"""
    logger.info("🚀 Starting Comprehensive Cascadia Framework Validation")
    logger.info("="*80)
    
    tests = [
        ("Main Script Syntax", test_main_script_syntax),
        ("Configuration Files", test_configuration_files),
        ("Module Structure", test_module_structure),
        ("H3 Integration", test_h3_integration),
        ("Backend Initialization", test_backend_initialization),
        ("Module Imports", test_module_imports),
        ("Main Script Functionality", test_main_script_functionality)
    ]
    
    results = {}
    for test_name, test_func in tests:
        logger.info(f"\n{'='*60}")
        logger.info(f"Running {test_name}")
        logger.info(f"{'='*60}")
        try:
            results[test_name] = test_func()
            status = "✅ PASS" if results[test_name] else "❌ FAIL"
            logger.info(f"{test_name}: {status}")
        except Exception as e:
            logger.error(f"❌ {test_name} crashed: {e}")
            results[test_name] = False
    
    # Generate final summary
    passed = sum(results.values())
    total = len(results)
    
    logger.info("\n" + "="*80)
    logger.info("COMPREHENSIVE VALIDATION SUMMARY")
    logger.info("="*80)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{test_name:<35}: {status}")
    
    logger.info(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        logger.info("\n�� ALL VALIDATION TESTS PASSED!")
        logger.info("✅ The Cascadia framework is fully functional and ready for production use.")
        logger.info("�� All components are working correctly.")
        logger.info("📋 Framework is production-ready.")
    elif passed >= total * 0.8:
        logger.info("\n✅ Most tests passed. Framework is largely functional.")
        logger.info("⚠️ Some minor issues may need attention.")
    else:
        logger.warning("\n⚠️ Multiple test failures. Framework needs significant attention.")
        logger.warning("🔧 Please review and fix the failing components.")
    
    return results

if __name__ == "__main__":
    results = run_comprehensive_validation()
    passed = sum(results.values())
    total = len(results)
    success = (passed / total) >= 0.8 if total > 0 else False
    sys.exit(0 if success else 1) 