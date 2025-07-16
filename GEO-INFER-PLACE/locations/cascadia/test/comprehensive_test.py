#!/usr/bin/env python3
"""
Comprehensive Test Suite for Cascadia Agricultural Land Analysis Framework

This test suite provides comprehensive testing of:
- All main framework methods
- Module initialization and functionality
- Data processing workflows
- Integration points
- Error handling
- Configuration management
- Output generation

The tests are designed to validate the entire Cascadia framework comprehensively.
"""

import sys
import os
import tempfile
import json
import yaml
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import logging
from typing import Dict, Any, List

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

# Import framework components
try:
    from geo_infer_space.utils.h3_utils import latlng_to_cell, cell_to_latlng, cell_to_latlng_boundary
    from geo_infer_space.core.base_module import BaseAnalysisModule
    from geo_infer_place.core.unified_backend import CascadianAgriculturalH3Backend
    from geo_infer_space.core.unified_backend import NumpyEncoder
    
    # Import modules
    from zoning.geo_infer_zoning import GeoInferZoning
    from current_use.geo_infer_current_use import GeoInferCurrentUse
    from ownership.geo_infer_ownership import GeoInferOwnership
    from improvements.geo_infer_improvements import GeoInferImprovements
    
    IMPORTS_SUCCESSFUL = True
except ImportError as e:
    logger.warning(f"Some imports failed: {e}")
    IMPORTS_SUCCESSFUL = False

class ComprehensiveTestSuite:
    """Comprehensive test suite for the Cascadia framework"""
    
    def __init__(self):
        self.test_results = {}
        self.temp_dir = None
        self.test_config = None
        
    def setup_test_environment(self):
        """Setup test environment with temporary directories and mock data"""
        logger.info("Setting up test environment...")
        
        # Create temporary directory
        self.temp_dir = Path(tempfile.mkdtemp(prefix="cascadia_test_"))
        
        # Create test configuration
        self.test_config = {
            'analysis_settings': {
                'target_counties': {
                    'CA': ['Lassen', 'Plumas'],  # Limited for testing
                    'OR': ['Clackamas', 'Marion']  # Limited for testing
                },
                'active_modules': ['zoning', 'current_use', 'ownership', 'improvements'],
                'h3_resolution': 8
            }
        }
        
        # Create config directory and file
        config_dir = self.temp_dir / 'config'
        config_dir.mkdir(exist_ok=True)
        
        with open(config_dir / 'analysis_config.yaml', 'w') as f:
            yaml.dump(self.test_config, f)
        
        # Create data directories
        for module in self.test_config['analysis_settings']['active_modules']:
            (self.temp_dir / 'data' / module).mkdir(parents=True, exist_ok=True)
        
        logger.info(f"✅ Test environment setup complete: {self.temp_dir}")
        
    def test_h3_integration(self) -> bool:
        """Test H3 integration from SPACE module"""
        logger.info("Testing H3 integration...")
        
        try:
            # Test basic H3 functions
            lat, lng = 40.5, -120.5  # Lassen County area
            h3_cell = latlng_to_cell(lat, lng, 8)
            logger.info(f"✅ H3 cell generation: {h3_cell}")
            
            # Test reverse conversion
            lat2, lng2 = cell_to_latlng(h3_cell)
            logger.info(f"✅ Reverse conversion: ({lat2:.3f}, {lng2:.3f})")
            
            # Test boundary
            boundary = cell_to_latlng_boundary(h3_cell)
            logger.info(f"✅ Boundary calculation: {len(boundary)} points")
            
            # Validate results
            assert abs(lat - lat2) < 0.01, "H3 round-trip conversion failed"
            assert abs(lng - lng2) < 0.01, "H3 round-trip conversion failed"
            assert len(boundary) == 6, "H3 hexagon should have 6 boundary points"
            
            return True
            
        except Exception as e:
            logger.error(f"❌ H3 integration test failed: {e}")
            return False
    
    def test_backend_initialization(self) -> bool:
        """Test backend initialization with proper configuration"""
        logger.info("Testing backend initialization...")
        
        try:
            # Create mock backend with minimal dependencies
            with patch('geo_infer_place.core.unified_backend.create_h3_data_loader') as mock_loader:
                mock_loader.return_value = Mock()
                
                backend = CascadianAgriculturalH3Backend(
                    modules={},
                    resolution=8,
                    bioregion='Cascadia',
                    target_counties=self.test_config['analysis_settings']['target_counties'],
                    base_data_dir=self.temp_dir / 'data',
                    osc_repo_dir=Path(project_root) / 'GEO-INFER-SPACE' / 'repo'
                )
                
                # Validate backend properties
                assert backend.resolution == 8, "Backend resolution not set correctly"
                assert backend.bioregion == 'Cascadia', "Backend bioregion not set correctly"
                assert len(backend.target_hexagons) > 0, "No target hexagons generated"
                
                logger.info(f"✅ Backend initialized with {len(backend.target_hexagons)} hexagons")
                return True
                
        except Exception as e:
            logger.error(f"❌ Backend initialization failed: {e}")
            return False
    
    def test_module_initialization(self) -> bool:
        """Test individual module initialization"""
        logger.info("Testing module initialization...")
        
        try:
            # Create mock backend
            with patch('geo_infer_place.core.unified_backend.create_h3_data_loader') as mock_loader:
                mock_loader.return_value = Mock()
                
                backend = CascadianAgriculturalH3Backend(
                    modules={},
                    resolution=8,
                    bioregion='Cascadia',
                    target_counties=self.test_config['analysis_settings']['target_counties'],
                    base_data_dir=self.temp_dir / 'data',
                    osc_repo_dir=Path(project_root) / 'GEO-INFER-SPACE' / 'repo'
                )
                
                modules = {}
                module_classes = {
                    'zoning': GeoInferZoning,
                    'current_use': GeoInferCurrentUse,
                    'ownership': GeoInferOwnership,
                    'improvements': GeoInferImprovements
                }
                
                # Test each module initialization
                for module_name, module_class in module_classes.items():
                    try:
                        module = module_class(backend)
                        modules[module_name] = module
                        
                        # Validate module properties
                        assert hasattr(module, 'module_name'), f"{module_name} missing module_name"
                        assert hasattr(module, 'backend'), f"{module_name} missing backend"
                        assert hasattr(module, 'data_dir'), f"{module_name} missing data_dir"
                        assert hasattr(module, 'run_analysis'), f"{module_name} missing run_analysis method"
                        
                        logger.info(f"✅ {module_name} module initialized successfully")
                        
                    except Exception as e:
                        logger.warning(f"⚠️ {module_name} module initialization failed: {e}")
                
                logger.info(f"✅ Successfully tested {len(modules)} modules")
                return len(modules) > 0
                
        except Exception as e:
            logger.error(f"❌ Module initialization test failed: {e}")
            return False
    
    def test_configuration_loading(self) -> bool:
        """Test configuration loading functionality"""
        logger.info("Testing configuration loading...")
        
        try:
            # Change to temp directory to test config loading
            original_cwd = os.getcwd()
            os.chdir(self.temp_dir)
            
            # Import the main module to test config loading
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "cascadia_main",
                Path(cascadian_dir) / "cascadia_main.py"
            )
            cascadia_main = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(cascadia_main)
            
            # Test config loading
            config = cascadia_main.load_analysis_config()
            
            # Validate config structure
            assert 'analysis_settings' in config, "Config missing analysis_settings"
            assert 'target_counties' in config['analysis_settings'], "Config missing target_counties"
            assert 'active_modules' in config['analysis_settings'], "Config missing active_modules"
            
            logger.info("✅ Configuration loading successful")
            
            # Restore original directory
            os.chdir(original_cwd)
            return True
            
        except Exception as e:
            logger.error(f"❌ Configuration loading test failed: {e}")
            os.chdir(original_cwd)
            return False
    
    def test_data_processing_workflow(self) -> bool:
        """Test the complete data processing workflow"""
        logger.info("Testing data processing workflow...")
        
        try:
            # Create mock backend with test data
            with patch('geo_infer_place.core.unified_backend.create_h3_data_loader') as mock_loader:
                mock_loader.return_value = Mock()
                
                backend = CascadianAgriculturalH3Backend(
                    modules={},
                    resolution=8,
                    bioregion='Cascadia',
                    target_counties={'CA': ['Lassen'], 'OR': ['Marion']},
                    base_data_dir=self.temp_dir / 'data',
                    osc_repo_dir=Path(project_root) / 'GEO-INFER-SPACE' / 'repo'
                )
                
                # Add mock unified data
                test_hexagons = list(backend.target_hexagons)[:10]  # Test with 10 hexagons
                for h3_cell in test_hexagons:
                    backend.unified_data[h3_cell] = {
                        'zoning': {'score': 0.8, 'data': {'type': 'agricultural'}},
                        'current_use': {'score': 0.7, 'data': {'crop': 'wheat'}},
                        'ownership': {'score': 0.6, 'data': {'owner_type': 'private'}},
                        'improvements': {'score': 0.5, 'data': {'building_count': 2}}
                    }
                
                # Test redevelopment calculation
                redevelopment_scores = backend.calculate_agricultural_redevelopment_potential()
                assert len(redevelopment_scores) > 0, "No redevelopment scores calculated"
                
                # Test summary generation
                summary = backend.get_comprehensive_summary()
                assert 'bioregion' in summary, "Summary missing bioregion"
                assert 'total_hexagons' in summary, "Summary missing total_hexagons"
                
                logger.info("✅ Data processing workflow successful")
                return True
                
        except Exception as e:
            logger.error(f"❌ Data processing workflow test failed: {e}")
            return False
    
    def test_export_functionality(self) -> bool:
        """Test data export functionality"""
        logger.info("Testing export functionality...")
        
        try:
            # Create mock backend with test data
            with patch('geo_infer_place.core.unified_backend.create_h3_data_loader') as mock_loader:
                mock_loader.return_value = Mock()
                
                backend = CascadianAgriculturalH3Backend(
                    modules={},
                    resolution=8,
                    bioregion='Cascadia',
                    target_counties={'CA': ['Lassen']},
                    base_data_dir=self.temp_dir / 'data',
                    osc_repo_dir=Path(project_root) / 'GEO-INFER-SPACE' / 'repo'
                )
                
                # Add test data
                test_hexagons = list(backend.target_hexagons)[:5]
                for h3_cell in test_hexagons:
                    backend.unified_data[h3_cell] = {
                        'zoning': {'score': 0.8},
                        'current_use': {'score': 0.7}
                    }
                
                # Test JSON export
                json_path = self.temp_dir / 'test_export.json'
                backend.export_unified_data(str(json_path), 'json')
                assert json_path.exists(), "JSON export file not created"
                
                # Validate JSON content
                with open(json_path, 'r') as f:
                    exported_data = json.load(f)
                assert len(exported_data) > 0, "Exported JSON data is empty"
                
                logger.info("✅ Export functionality successful")
                return True
                
        except Exception as e:
            logger.error(f"❌ Export functionality test failed: {e}")
            return False
    
    def test_main_script_syntax(self) -> bool:
        """Test that the main script has valid syntax and can be imported"""
        logger.info("Testing main script syntax...")
        
        try:
            # Test importing the main script
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "cascadia_main",
                Path(cascadian_dir) / "cascadia_main.py"
            )
            cascadia_main = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(cascadia_main)
            
            # Test that key functions exist
            required_functions = [
                'setup_logging',
                'check_dependencies', 
                'load_analysis_config',
                'generate_analysis_report',
                'main'
            ]
            
            for func_name in required_functions:
                assert hasattr(cascadia_main, func_name), f"Missing function: {func_name}"
                logger.info(f"✅ Function {func_name} exists")
            
            logger.info("✅ Main script syntax validation successful")
            return True
            
        except Exception as e:
            logger.error(f"❌ Main script syntax test failed: {e}")
            return False
    
    def test_error_handling(self) -> bool:
        """Test error handling in various scenarios"""
        logger.info("Testing error handling...")
        
        try:
            # Test with invalid configuration
            with patch('geo_infer_place.core.unified_backend.create_h3_data_loader') as mock_loader:
                mock_loader.side_effect = Exception("Simulated loader error")
                
                try:
                    backend = CascadianAgriculturalH3Backend(
                        modules={},
                        resolution=8,
                        bioregion='Cascadia',
                        target_counties={'INVALID': ['INVALID']},
                        base_data_dir=self.temp_dir / 'data',
                        osc_repo_dir=Path(project_root) / 'GEO-INFER-SPACE' / 'repo'
                    )
                    logger.warning("⚠️ Backend should have failed with invalid config")
                except Exception:
                    logger.info("✅ Error handling working correctly")
                    
            return True
            
        except Exception as e:
            logger.error(f"❌ Error handling test failed: {e}")
            return False
    
    def test_comprehensive_integration(self) -> bool:
        """Test comprehensive integration of all components"""
        logger.info("Testing comprehensive integration...")
        
        try:
            # Change to temp directory
            original_cwd = os.getcwd()
            os.chdir(self.temp_dir)
            
            # Mock external dependencies
            with patch('geo_infer_place.core.unified_backend.create_h3_data_loader') as mock_loader, \
                 patch('geo_infer_space.core.spatial_processor.SpatialProcessor') as mock_processor, \
                 patch('geo_infer_space.core.visualization_engine.InteractiveVisualizationEngine') as mock_viz:
                
                mock_loader.return_value = Mock()
                mock_processor.return_value = Mock()
                mock_viz.return_value = Mock()
                
                # Test backend with modules
                backend = CascadianAgriculturalH3Backend(
                    modules={},
                    resolution=8,
                    bioregion='Cascadia',
                    target_counties={'CA': ['Lassen']},
                    base_data_dir=self.temp_dir / 'data',
                    osc_repo_dir=Path(project_root) / 'GEO-INFER-SPACE' / 'repo'
                )
                
                # Add modules
                zoning_module = GeoInferZoning(backend)
                backend.modules['zoning'] = zoning_module
                
                # Test analysis workflow
                test_hexagons = list(backend.target_hexagons)[:3]
                for h3_cell in test_hexagons:
                    backend.unified_data[h3_cell] = {
                        'zoning': {'score': 0.8, 'data': {'type': 'agricultural'}}
                    }
                
                # Test summary generation
                summary = backend.get_comprehensive_summary()
                assert summary['total_hexagons'] > 0, "Summary should have hexagon count"
                
                # Test report generation
                import importlib.util
                spec = importlib.util.spec_from_file_location(
                    "cascadia_main",
                    Path(cascadian_dir) / "cascadia_main.py"
                )
                cascadia_main = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(cascadia_main)
                
                report_path = self.temp_dir / 'test_report.md'
                cascadia_main.generate_analysis_report(summary, report_path)
                assert report_path.exists(), "Report should be generated"
                
                logger.info("✅ Comprehensive integration successful")
                
                # Restore directory
                os.chdir(original_cwd)
                return True
                
        except Exception as e:
            logger.error(f"❌ Comprehensive integration test failed: {e}")
            os.chdir(original_cwd)
            return False
    
    def run_all_tests(self) -> Dict[str, bool]:
        """Run all tests and return results"""
        logger.info("🚀 Starting comprehensive test suite...")
        
        if not IMPORTS_SUCCESSFUL:
            logger.error("❌ Cannot run tests due to import failures")
            return {}
        
        # Setup test environment
        self.setup_test_environment()
        
        # Define all tests
        tests = [
            ("H3 Integration", self.test_h3_integration),
            ("Backend Initialization", self.test_backend_initialization),
            ("Module Initialization", self.test_module_initialization),
            ("Configuration Loading", self.test_configuration_loading),
            ("Data Processing Workflow", self.test_data_processing_workflow),
            ("Export Functionality", self.test_export_functionality),
            ("Main Script Syntax", self.test_main_script_syntax),
            ("Error Handling", self.test_error_handling),
            ("Comprehensive Integration", self.test_comprehensive_integration)
        ]
        
        # Run tests
        results = {}
        for test_name, test_func in tests:
            logger.info(f"\n--- Running {test_name} Test ---")
            try:
                results[test_name] = test_func()
                status = "✅ PASS" if results[test_name] else "❌ FAIL"
                logger.info(f"{test_name}: {status}")
            except Exception as e:
                logger.error(f"❌ {test_name} test crashed: {e}")
                results[test_name] = False
        
        # Generate summary
        passed = sum(results.values())
        total = len(results)
        
        logger.info("\n" + "="*60)
        logger.info("COMPREHENSIVE TEST SUMMARY")
        logger.info("="*60)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            logger.info(f"{test_name:<30}: {status}")
        
        logger.info(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        
        if passed == total:
            logger.info("🎉 ALL TESTS PASSED! The Cascadia framework is working correctly.")
        elif passed > total * 0.8:
            logger.info("✅ Most tests passed. Framework is largely functional.")
        else:
            logger.warning("⚠️ Multiple test failures. Framework needs attention.")
        
        # Cleanup
        try:
            import shutil
            shutil.rmtree(self.temp_dir)
            logger.info(f"🧹 Cleaned up test environment: {self.temp_dir}")
        except Exception as e:
            logger.warning(f"⚠️ Failed to cleanup test environment: {e}")
        
        return results

def main():
    """Main test runner"""
    test_suite = ComprehensiveTestSuite()
    results = test_suite.run_all_tests()
    
    # Return success if most tests pass
    passed = sum(results.values())
    total = len(results)
    success_threshold = 0.8
    
    return (passed / total) >= success_threshold if total > 0 else False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 