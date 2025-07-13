#!/usr/bin/env python3
"""
GEO-INFER Framework Test Script

This script tests the framework installation and verifies that all modules
can be imported and used correctly.
"""

import sys
import logging
from pathlib import Path
from typing import Dict, List, Any
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_path_manager():
    """Test the path manager functionality."""
    logger.info("=== Testing Path Manager ===")
    
    try:
        from .geo_infer_paths import get_path_manager, list_available_modules, is_module_installed
        
        manager = get_path_manager()
        available_modules = list_available_modules()
        
        logger.info(f"Available modules: {len(available_modules)}")
        for module in available_modules:
            installed = is_module_installed(module)
            status = "✓ installed" if installed else "○ development"
            logger.info(f"  {module}: {status}")
        
        return True
    except Exception as e:
        logger.error(f"Path manager test failed: {e}")
        return False

def test_module_imports():
    """Test importing all available modules."""
    logger.info("=== Testing Module Imports ===")
    
    try:
        from .geo_infer_paths import import_module, list_available_modules
        
        available_modules = list_available_modules()
        results = {}
        
        for module_name in available_modules:
            try:
                module = import_module(module_name)
                if module:
                    results[module_name] = {
                        'status': 'success',
                        'version': getattr(module, '__version__', 'unknown'),
                        'file': getattr(module, '__file__', 'unknown')
                    }
                    logger.info(f"✓ {module_name} imported successfully")
                else:
                    results[module_name] = {'status': 'failed', 'error': 'Import returned None'}
                    logger.error(f"✗ {module_name} import returned None")
            except Exception as e:
                results[module_name] = {'status': 'error', 'error': str(e)}
                logger.error(f"✗ {module_name} import failed: {e}")
        
        return results
    except Exception as e:
        logger.error(f"Module import test failed: {e}")
        return {}

def test_cross_module_imports():
    """Test cross-module imports that are commonly used."""
    logger.info("=== Testing Cross-Module Imports ===")
    
    cross_import_tests = [
        ('geo_infer_place', 'PlaceAnalyzer'),
        ('geo_infer_space', 'setup_osc_geo'),
        ('geo_infer_iot', 'IoTDataIngestion'),
        ('geo_infer_bayes', 'GaussianProcess'),
        ('geo_infer_act', 'ActiveInferenceModel'),
        ('geo_infer_agent', 'AgentFramework'),
        ('geo_infer_art', 'ArtisticVisualization'),
        ('geo_infer_sec', 'SecurityFramework'),
        ('geo_infer_test', 'TestRunner'),
        ('geo_infer_api', 'APIManager'),
        ('geo_infer_norms', 'ComplianceFramework'),
        ('geo_infer_ops', 'OperationsManager'),
        ('geo_infer_examples', 'ExampleRunner'),
        ('geo_infer_git', 'GitManager'),
    ]
    
    try:
        from .geo_infer_paths import import_from_module
        
        results = {}
        for module_name, item_name in cross_import_tests:
            try:
                item = import_from_module(module_name, item_name)
                if item:
                    results[f"{module_name}.{item_name}"] = {
                        'status': 'success',
                        'type': type(item).__name__
                    }
                    logger.info(f"✓ {module_name}.{item_name} imported successfully")
                else:
                    results[f"{module_name}.{item_name}"] = {
                        'status': 'not_found',
                        'error': 'Item not found in module'
                    }
                    logger.warning(f"○ {module_name}.{item_name} not found in module")
            except Exception as e:
                results[f"{module_name}.{item_name}"] = {
                    'status': 'error',
                    'error': str(e)
                }
                logger.error(f"✗ {module_name}.{item_name} import failed: {e}")
        
        return results
    except Exception as e:
        logger.error(f"Cross-module import test failed: {e}")
        return {}

def test_framework_entry_point():
    """Test the main framework entry point."""
    logger.info("=== Testing Framework Entry Point ===")
    
    try:
        from . import get_framework, list_modules, run_diagnostics
        
        framework = get_framework()
        modules = list_modules()
        diagnostics = run_diagnostics()
        
        logger.info(f"Framework loaded {len(modules)} modules")
        logger.info(f"Framework version: {diagnostics.get('framework_version', 'unknown')}")
        logger.info(f"Python version: {diagnostics.get('python_version', 'unknown')}")
        
        return {
            'framework_loaded': True,
            'module_count': len(modules),
            'diagnostics': diagnostics
        }
    except Exception as e:
        logger.error(f"Framework entry point test failed: {e}")
        return {'framework_loaded': False, 'error': str(e)}

def test_specific_functionality():
    """Test specific functionality that users commonly need."""
    logger.info("=== Testing Specific Functionality ===")
    
    tests = {}
    
    # Test SPACE module H3 functionality
    try:
        from geo_infer_space import setup_osc_geo
        tests['space_h3'] = {'status': 'success', 'description': 'H3 spatial indexing'}
        logger.info("✓ SPACE H3 functionality available")
    except Exception as e:
        tests['space_h3'] = {'status': 'error', 'error': str(e)}
        logger.error(f"✗ SPACE H3 functionality failed: {e}")
    
    # Test PLACE module functionality
    try:
        from geo_infer_place import PlaceAnalyzer
        tests['place_analyzer'] = {'status': 'success', 'description': 'Place-based analysis'}
        logger.info("✓ PLACE analyzer available")
    except Exception as e:
        tests['place_analyzer'] = {'status': 'error', 'error': str(e)}
        logger.error(f"✗ PLACE analyzer failed: {e}")
    
    # Test IOT module functionality
    try:
        from geo_infer_iot import IoTDataIngestion
        tests['iot_ingestion'] = {'status': 'success', 'description': 'IoT data ingestion'}
        logger.info("✓ IOT data ingestion available")
    except Exception as e:
        tests['iot_ingestion'] = {'status': 'error', 'error': str(e)}
        logger.error(f"✗ IOT data ingestion failed: {e}")
    
    # Test BAYES module functionality
    try:
        from geo_infer_bayes import GaussianProcess
        tests['bayes_gp'] = {'status': 'success', 'description': 'Bayesian Gaussian processes'}
        logger.info("✓ BAYES Gaussian processes available")
    except Exception as e:
        tests['bayes_gp'] = {'status': 'error', 'error': str(e)}
        logger.error(f"✗ BAYES Gaussian processes failed: {e}")
    
    return tests

def generate_report(results: Dict[str, Any]) -> str:
    """Generate a comprehensive test report."""
    report = {
        'timestamp': str(Path.cwd()),
        'python_version': sys.version,
        'results': results
    }
    
    # Calculate summary statistics
    total_tests = 0
    passed_tests = 0
    
    for test_name, test_results in results.items():
        if isinstance(test_results, dict):
            if 'status' in test_results:
                total_tests += 1
                if test_results['status'] == 'success':
                    passed_tests += 1
            elif isinstance(test_results, dict):
                # Handle nested results
                for sub_test, sub_result in test_results.items():
                    if isinstance(sub_result, dict) and 'status' in sub_result:
                        total_tests += 1
                        if sub_result['status'] == 'success':
                            passed_tests += 1
    
    report['summary'] = {
        'total_tests': total_tests,
        'passed_tests': passed_tests,
        'failed_tests': total_tests - passed_tests,
        'success_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0
    }
    
    return json.dumps(report, indent=2)

def main():
    """Run all tests and generate a report."""
    logger.info("=== GEO-INFER Framework Test Suite ===")
    
    results = {}
    
    # Run all tests
    results['path_manager'] = test_path_manager()
    results['module_imports'] = test_module_imports()
    results['cross_module_imports'] = test_cross_module_imports()
    results['framework_entry_point'] = test_framework_entry_point()
    results['specific_functionality'] = test_specific_functionality()
    
    # Generate and save report
    report = generate_report(results)
    
    report_path = Path('framework_test_report.json')
    with open(report_path, 'w') as f:
        f.write(report)
    
    logger.info(f"=== Test Report Generated ===")
    logger.info(f"Report saved to: {report_path}")
    
    # Print summary
    summary = results.get('framework_entry_point', {}).get('diagnostics', {}).get('summary', {})
    if summary:
        logger.info(f"Framework Summary:")
        logger.info(f"  - Total modules: {summary.get('total_modules', 'unknown')}")
        logger.info(f"  - Loaded modules: {summary.get('loaded_modules', 'unknown')}")
        logger.info(f"  - Success rate: {summary.get('success_rate', 'unknown')}%")
    
    return results

if __name__ == "__main__":
    main() 