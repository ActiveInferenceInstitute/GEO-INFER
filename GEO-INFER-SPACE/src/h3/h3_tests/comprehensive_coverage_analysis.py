#!/usr/bin/env python3
"""
Comprehensive H3 Method Coverage Analysis

This script analyzes all H3 methods from the modules and checks
which ones are covered by our test suite.

Author: GEO-INFER Framework
Version: 4.3.0
License: Apache-2.0
"""

import h3
import re
from pathlib import Path
from typing import Dict, List, Set, Any

def extract_methods_from_modules():
    """Extract all H3 methods from the module files."""
    
    # Define module files to analyze
    module_files = [
        '../__init__.py',
        '../analysis.py', 
        '../constants.py',
        '../conversion.py',
        '../core.py',
        '../hierarchy.py',
        '../indexing.py',
        '../unidirectional.py',
        '../traversal.py',
        '../validation.py',
        '../utilities.py'
    ]
    
    all_methods = set()
    module_methods = {}
    
    for file_path in module_files:
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Extract function definitions
            function_pattern = r'def\s+(\w+)\s*\('
            functions = re.findall(function_pattern, content)
            
            # Extract from __all__ lists
            all_pattern = r"__all__\s*=\s*\[(.*?)\]"
            all_matches = re.findall(all_pattern, content, re.DOTALL)
            
            module_name = Path(file_path).stem
            module_methods[module_name] = set()
            
            for func in functions:
                if not func.startswith('_'):
                    all_methods.add(func)
                    module_methods[module_name].add(func)
            
            # Also extract from __all__ lists
            for all_match in all_matches:
                # Parse the __all__ list
                items = re.findall(r"'([^']+)'", all_match)
                for item in items:
                    all_methods.add(item)
                    module_methods[module_name].add(item)
                    
        except FileNotFoundError:
            print(f"Warning: {file_path} not found")
            continue
    
    return all_methods, module_methods

def analyze_test_coverage():
    """Analyze which H3 methods are covered by tests."""
    
    # Get all available H3 library functions
    h3_library_functions = [f for f in dir(h3) if not f.startswith('_') and callable(getattr(h3, f))]
    
    # Define test files
    test_files = [
        'visual/test_visual_analysis.py',
        'performance/test_performance_benchmarks.py',
        'integration/test_integration_scenarios.py',
        'interactive/test_interactive_features.py',
        'animations/test_animation_generation.py'
    ]
    
    # Track method usage by test category
    coverage_by_category = {}
    all_used_methods = set()
    
    for test_file in test_files:
        try:
            with open(test_file, 'r') as f:
                content = f.read()
                
            # Find all h3. method calls
            h3_calls = re.findall(r'h3\.(\w+)', content)
            category_name = Path(test_file).parent.name
            coverage_by_category[category_name] = set(h3_calls)
            all_used_methods.update(h3_calls)
                
        except FileNotFoundError:
            print(f"Warning: {test_file} not found")
            continue
    
    return h3_library_functions, all_used_methods, coverage_by_category

def analyze_module_methods():
    """Analyze methods from our H3 modules."""
    
    all_methods, module_methods = extract_methods_from_modules()
    
    # Get test coverage
    h3_library_functions, all_used_methods, coverage_by_category = analyze_test_coverage()
    
    print("=" * 100)
    print("COMPREHENSIVE H3 METHOD COVERAGE ANALYSIS")
    print("=" * 100)
    
    print(f"\n📊 OVERALL STATISTICS:")
    print(f"  H3 Library Functions Available: {len(h3_library_functions)}")
    print(f"  Module Methods Defined: {len(all_methods)}")
    print(f"  Methods Tested: {len(all_used_methods)}")
    print(f"  Test Coverage: {(len(all_used_methods) / len(h3_library_functions)) * 100:.1f}%")
    
    print(f"\n📁 MODULE ANALYSIS:")
    for module_name, methods in module_methods.items():
        tested_in_module = methods.intersection(all_used_methods)
        coverage = len(tested_in_module) / len(methods) * 100 if methods else 0
        print(f"  {module_name}: {len(tested_in_module)}/{len(methods)} methods ({coverage:.1f}%)")
        
        if tested_in_module:
            print(f"    Tested: {', '.join(sorted(tested_in_module))}")
        untested = methods - all_used_methods
        if untested:
            print(f"    Untested: {', '.join(sorted(untested))}")
    
    print(f"\n🧪 TEST CATEGORY ANALYSIS:")
    for category, methods in coverage_by_category.items():
        print(f"  {category}: {len(methods)} methods")
        print(f"    Methods: {', '.join(sorted(methods))}")
    
    print(f"\n✅ FULLY TESTED METHODS:")
    for method in sorted(all_used_methods):
        print(f"  ✓ {method}")
    
    print(f"\n❌ UNTESTED H3 LIBRARY METHODS:")
    untested_library = set(h3_library_functions) - all_used_methods
    for method in sorted(untested_library):
        print(f"  ✗ {method}")
    
    print(f"\n🔍 METHOD CATEGORIES:")
    
    # Categorize methods by functionality
    method_categories = {
        'Coordinate Conversion': ['latlng_to_cell', 'cell_to_latlng'],
        'Boundary Operations': ['cell_to_boundary'],
        'Grid Operations': ['grid_disk', 'grid_ring', 'grid_path_cells', 'grid_distance'],
        'Hierarchy Operations': ['cell_to_parent', 'cell_to_children', 'get_resolution'],
        'Geometric Properties': ['cell_area', 'average_hexagon_edge_length'],
        'Validation': ['is_valid_cell', 'is_pentagon'],
        'Compact Operations': ['compact_cells', 'uncompact_cells'],
        'Distance Calculations': ['great_circle_distance'],
        'Utility Functions': ['is_res_class_III', 'get_base_cell_number', 'get_icosahedron_faces'],
        'Edge Operations': ['edge_length', 'edge_boundary'],
        'Vertex Operations': ['cell_to_vertexes', 'vertex_to_latlng'],
        'Local Coordinates': ['cell_to_local_ij', 'local_ij_to_cell'],
        'Polygon Operations': ['polygon_to_cells', 'polyfill'],
        'Conversion Functions': ['cell_to_geojson', 'geojson_to_cells'],
        'Analysis Functions': ['analyze_cell_distribution', 'calculate_spatial_statistics']
    }
    
    for category, methods in method_categories.items():
        tested_in_category = [m for m in methods if m in all_used_methods]
        coverage = len(tested_in_category) / len(methods) * 100
        print(f"  {category}: {len(tested_in_category)}/{len(methods)} methods ({coverage:.1f}%)")
        if tested_in_category:
            print(f"    Tested: {', '.join(tested_in_category)}")
        untested = [m for m in methods if m not in all_used_methods]
        if untested:
            print(f"    Untested: {', '.join(untested)}")
    
    return all_methods, all_used_methods, h3_library_functions

def run_all_tests():
    """Run all test files and report results."""
    
    test_files = [
        'visual/test_visual_analysis.py',
        'performance/test_performance_benchmarks.py',
        'integration/test_integration_scenarios.py',
        'interactive/test_interactive_features.py',
        'animations/test_animation_generation.py'
    ]
    
    print(f"\n" + "=" * 100)
    print("TEST EXECUTION RESULTS")
    print("=" * 100)
    
    import subprocess
    import sys
    
    total_tests = 0
    passed_tests = 0
    
    for test_file in test_files:
        try:
            result = subprocess.run([sys.executable, test_file], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                # Extract test count from output
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'Ran' in line and 'tests' in line:
                        test_count = int(line.split('Ran')[1].split('tests')[0].strip())
                        total_tests += test_count
                        passed_tests += test_count
                        print(f"✓ {test_file}: {test_count} tests passed")
                        break
            else:
                print(f"✗ {test_file}: FAILED")
                print(f"  Error: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print(f"✗ {test_file}: TIMEOUT")
        except Exception as e:
            print(f"✗ {test_file}: ERROR - {e}")
    
    print(f"\n📈 TEST SUMMARY:")
    print(f"  Total tests executed: {total_tests}")
    print(f"  Tests passed: {passed_tests}")
    print(f"  Success rate: {(passed_tests / total_tests * 100) if total_tests > 0 else 0:.1f}%")

if __name__ == '__main__':
    all_methods, all_used_methods, h3_library_functions = analyze_module_methods()
    run_all_tests() 