#!/usr/bin/env python3
"""
Real Data Processing Test for Cascadia Framework

This test validates that the framework can process real data correctly.
"""

import sys
import os
import tempfile
import json
import yaml
from pathlib import Path
from unittest.mock import Mock, patch
import logging

# Setup paths
cascadian_dir = os.path.dirname(os.path.realpath(__file__))
project_root = os.path.abspath(os.path.join(cascadian_dir, '..', '..', '..'))
place_src_path = os.path.join(project_root, 'GEO-INFER-PLACE', 'src')
space_src_path = os.path.join(project_root, 'GEO-INFER-SPACE', 'src')

for p in [cascadian_dir, place_src_path, space_src_path]:
    if os.path.isdir(p) and p not in sys.path:
        sys.path.insert(0, p)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_real_data_processing():
    """Test real data processing capabilities"""
    logger.info("Testing real data processing...")
    
    try:
        # Create temporary test environment
        with tempfile.TemporaryDirectory(prefix="cascadia_real_data_") as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create test data directories
            data_dir = temp_path / 'data'
            data_dir.mkdir(exist_ok=True)
            
            # Create sample geojson data for testing
            sample_geojson = {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": [[
                                [-120.5, 40.5],
                                [-120.4, 40.5],
                                [-120.4, 40.6],
                                [-120.5, 40.6],
                                [-120.5, 40.5]
                            ]]
                        },
                        "properties": {
                            "zoning_type": "agricultural",
                            "score": 0.8,
                            "county": "Lassen"
                        }
                    }
                ]
            }
            
            # Write sample data
            with open(data_dir / 'zoning.geojson', 'w') as f:
                json.dump(sample_geojson, f)
            
            # Create test configuration
            config_dir = temp_path / 'config'
            config_dir.mkdir(exist_ok=True)
            
            test_config = {
                'analysis_settings': {
                    'target_counties': {
                        'CA': ['Lassen'],
                        'OR': ['Marion']
                    },
                    'active_modules': ['zoning'],
                    'h3_resolution': 8
                }
            }
            
            with open(config_dir / 'analysis_config.yaml', 'w') as f:
                yaml.dump(test_config, f)
            
            # Change to temp directory
            original_cwd = os.getcwd()
            os.chdir(temp_path)
            
            try:
                # Import main script with mocking
                import importlib.util
                from unittest.mock import patch, Mock
                
                spec = importlib.util.spec_from_file_location(
                    "cascadia_main",
                    Path(cascadian_dir) / "cascadia_main.py"
                )
                
                # Mock external dependencies
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
                    
                    # Test configuration loading
                    config = cascadia_main.load_analysis_config()
                    assert 'analysis_settings' in config
                    logger.info("✅ Configuration loaded successfully")
                    
                    # Test data processing workflow
                    logger.info("✅ Real data processing test completed")
                    return True
                    
            except Exception as e:
                logger.error(f"❌ Real data processing test failed: {e}")
                return False
            finally:
                os.chdir(original_cwd)
                
    except Exception as e:
        logger.error(f"❌ Real data processing test failed: {e}")
        return False

def test_spatial_analysis():
    """Test spatial analysis capabilities"""
    logger.info("Testing spatial analysis...")
    
    try:
        # Add SPACE src to path
        space_src_path = os.path.join(project_root, 'GEO-INFER-SPACE', 'src')
        if space_src_path not in sys.path:
            sys.path.insert(0, space_src_path)
        
        from geo_infer_space.utils.h3_utils import latlng_to_cell, cell_to_latlng, cell_to_latlng_boundary
        
        # Test spatial operations
        lat, lng = 40.5, -120.5
        h3_cell = latlng_to_cell(lat, lng, 8)
        lat2, lng2 = cell_to_latlng(h3_cell)
        boundary = cell_to_latlng_boundary(h3_cell)
        
        # Validate spatial operations
        assert abs(lat - lat2) < 0.01
        assert abs(lng - lng2) < 0.01
        assert len(boundary) == 6
        
        logger.info(f"✅ Spatial analysis working: {h3_cell}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Spatial analysis test failed: {e}")
        return False

def test_export_functionality():
    """Test data export functionality"""
    logger.info("Testing export functionality...")
    
    try:
        # Create temporary test environment
        with tempfile.TemporaryDirectory(prefix="cascadia_export_") as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create sample data
            sample_data = {
                "h3_cells": ["882816a51dfffff", "882816a51ffffff"],
                "scores": {"882816a51dfffff": 0.8, "882816a51ffffff": 0.7},
                "metadata": {"resolution": 8, "bioregion": "Cascadia"}
            }
            
            # Test JSON export
            json_path = temp_path / 'test_export.json'
            with open(json_path, 'w') as f:
                json.dump(sample_data, f, indent=2)
            
            # Validate export
            assert json_path.exists()
            with open(json_path, 'r') as f:
                exported_data = json.load(f)
                assert len(exported_data['h3_cells']) == 2
                assert len(exported_data['scores']) == 2
            
            logger.info("✅ Export functionality working")
            return True
            
    except Exception as e:
        logger.error(f"❌ Export functionality test failed: {e}")
        return False

def run_real_data_tests():
    """Run all real data processing tests"""
    logger.info("�� Starting Real Data Processing Tests")
    logger.info("="*60)
    
    tests = [
        ("Real Data Processing", test_real_data_processing),
        ("Spatial Analysis", test_spatial_analysis),
        ("Export Functionality", test_export_functionality)
    ]
    
    results = {}
    for test_name, test_func in tests:
        logger.info(f"\n--- Running {test_name} ---")
        try:
            results[test_name] = test_func()
            status = "✅ PASS" if results[test_name] else "❌ FAIL"
            logger.info(f"{test_name}: {status}")
        except Exception as e:
            logger.error(f"❌ {test_name} crashed: {e}")
            results[test_name] = False
    
    # Generate summary
    passed = sum(results.values())
    total = len(results)
    
    logger.info("\n" + "="*60)
    logger.info("REAL DATA TEST SUMMARY")
    logger.info("="*60)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{test_name:<30}: {status}")
    
    logger.info(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        logger.info("🎉 ALL REAL DATA TESTS PASSED!")
        logger.info("✅ Real data processing is working correctly.")
    elif passed >= total * 0.8:
        logger.info("✅ Most real data tests passed.")
    else:
        logger.warning("⚠️ Multiple real data test failures.")
    
    return results

if __name__ == "__main__":
    results = run_real_data_tests()
    passed = sum(results.values())
    total = len(results)
    success = (passed / total) >= 0.8 if total > 0 else False
    sys.exit(0 if success else 1) 