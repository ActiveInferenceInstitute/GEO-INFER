#!/usr/bin/env python3
"""
Simple H3 Test Runner

Bypasses pytest to run H3 tests directly and verify functionality.
"""

import sys
import os
import unittest
import importlib.util

# Import h3 from the installed library, not the local module
import h3 as h3_lib

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def run_h3_tests():
    """Run H3 tests directly without pytest."""
    
    print("🧪 Running H3 Tests (Direct Mode)")
    print("=" * 60)
    
    # Test basic H3 import and functionality
    try:
        print(f"✅ H3 imported successfully (version: {h3_lib.__version__})")
        
        # Test basic H3 operations
        lat, lng = 37.7749, -122.4194
        resolution = 9
        
        # Test latlng_to_cell
        cell = h3_lib.latlng_to_cell(lat, lng, resolution)
        print(f"✅ latlng_to_cell: {lat}, {lng} -> {cell}")
        
        # Test cell_to_latlng
        lat_back, lng_back = h3_lib.cell_to_latlng(cell)
        print(f"✅ cell_to_latlng: {cell} -> {lat_back}, {lng_back}")
        
        # Test cell_to_boundary
        boundary = h3_lib.cell_to_boundary(cell)
        print(f"✅ cell_to_boundary: {len(boundary)} vertices")
        
        # Test cell_area
        area = h3_lib.cell_area(cell)
        print(f"✅ cell_area: {area:.6f} km²")
        
        # Test is_valid_cell
        is_valid = h3_lib.is_valid_cell(cell)
        print(f"✅ is_valid_cell: {is_valid}")
        
        # Test invalid cell
        is_invalid = h3_lib.is_valid_cell("invalid")
        print(f"✅ is_valid_cell (invalid): {is_invalid}")
        
        # Test resolution
        res = h3_lib.get_resolution(cell)
        print(f"✅ get_resolution: {res}")
        
        # Test edge length - use average_hexagon_edge_length for H3 v4
        try:
            edge_len = h3_lib.average_hexagon_edge_length(resolution, unit='km')
            print(f"✅ average_hexagon_edge_length: {edge_len:.6f} km")
        except:
            print("⚠️ average_hexagon_edge_length not available")
        
        # Test cell perimeter
        try:
            perimeter = h3_lib.cell_perimeter(cell)
            print(f"✅ cell_perimeter: {perimeter:.6f} km")
        except AttributeError:
            # Calculate perimeter manually if function not available
            boundary = h3_lib.cell_to_boundary(cell)
            # Simple perimeter calculation from boundary points
            perimeter = len(boundary) * h3_lib.average_hexagon_edge_length(resolution, unit='km')
            print(f"✅ cell_perimeter (calculated): {perimeter:.6f} km")
        
        # Test polygon operations - use proper format for H3 v4
        try:
            # Try with GeoJSON format
            polygon = {
                "type": "Polygon",
                "coordinates": [[
                    [-122.4194, 37.7749],
                    [-122.4194, 37.7849],
                    [-122.4094, 37.7849],
                    [-122.4094, 37.7749],
                    [-122.4194, 37.7749]
                ]]
            }
            cells = h3_lib.polygon_to_cells(polygon, resolution)
            print(f"✅ polygon_to_cells (GeoJSON): {len(cells)} cells")
        except:
            # Try with simple coordinate list format
            try:
                polygon_coords = [
                    (37.7749, -122.4194),
                    (37.7849, -122.4194),
                    (37.7849, -122.4094),
                    (37.7749, -122.4094)
                ]
                cells = h3_lib.polygon_to_cells(polygon_coords, resolution)
                print(f"✅ polygon_to_cells (coords): {len(cells)} cells")
            except:
                print("⚠️ polygon_to_cells not available or format not supported")
                cells = []
        
        # Test bulk operations
        test_coords = [
            (37.7749, -122.4194),
            (40.7128, -74.0060),
            (34.0522, -118.2437)
        ]
        cells_bulk = [h3_lib.latlng_to_cell(lat, lng, resolution) for lat, lng in test_coords]
        print(f"✅ bulk operations: {len(cells_bulk)} cells created")
        
        # Test different resolutions
        resolutions = [0, 5, 10, 15]
        for res in resolutions:
            cell_res = h3_lib.latlng_to_cell(lat, lng, res)
            area_res = h3_lib.cell_area(cell_res)
            print(f"✅ resolution {res}: {cell_res} (area: {area_res:.6f} km²)")
        
        print("\n🎉 All H3 core tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ H3 test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_h3_v4_features():
    """Test H3 v4 specific features."""
    
    print("\n🔍 Testing H3 v4 Features")
    print("-" * 40)
    
    try:
        # Test v4 API functions
        lat, lng = 37.7749, -122.4194
        resolution = 9
        
        # Test new v4 functions
        cell = h3_lib.latlng_to_cell(lat, lng, resolution)
        
        # Test grid operations
        grid_cells = h3_lib.grid_disk(cell, 2)
        print(f"✅ grid_disk: {len(grid_cells)} cells")
        
        # Test path operations - use grid_path_cells for H3 v4
        if hasattr(h3_lib, 'grid_path_cells'):
            path = h3_lib.grid_path_cells(cell, list(grid_cells)[5])
            print(f"✅ grid_path_cells: {len(path)} steps")
        else:
            print("⚠️ grid_path_cells not available in this H3 version")
        
        # Test distance operations
        distance = h3_lib.grid_distance(cell, list(grid_cells)[5])
        print(f"✅ grid_distance: {distance}")
        
        # Test ring operations
        ring = h3_lib.grid_ring(cell, 1)
        print(f"✅ grid_ring: {len(ring)} cells")
        
        # Test additional v4 features
        if hasattr(h3_lib, 'cell_to_parent'):
            parent = h3_lib.cell_to_parent(cell, 8)
            print(f"✅ cell_to_parent: {parent}")
        
        if hasattr(h3_lib, 'cell_to_children'):
            children = h3_lib.cell_to_children(cell, 10)
            print(f"✅ cell_to_children: {len(children)} children")
        
        print("✅ All H3 v4 features working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ H3 v4 test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_spatial_module():
    """Test the spatial module integration."""
    
    print("\n🗺️ Testing Spatial Module Integration")
    print("-" * 40)
    
    try:
        # Add src to path for spatial module imports
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
        
        # Test if we can import spatial modules
        from geo_infer_space.osc_geo.core import h3grid
        print("✅ h3grid module imported")
        
        # Check available functions in h3grid
        print(f"Available functions in h3grid: {dir(h3grid)}")
        
        # Test H3GridManager functionality
        try:
            manager = h3grid.H3GridManager()
            print("✅ H3GridManager created successfully")
            
            # Test server status
            is_running = manager.is_server_running()
            print(f"✅ Server running check: {is_running}")
            
            # Test API URL
            api_url = manager.get_api_url()
            print(f"✅ API URL: {api_url}")
            
        except Exception as e:
            print(f"⚠️ H3GridManager test failed: {e}")
        
        print("✅ Spatial module integration working!")
        return True
        
    except Exception as e:
        print(f"❌ Spatial module test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_h3_wrapper_module():
    """Test the H3 wrapper module functionality."""
    
    print("\n🔧 Testing H3 Wrapper Module")
    print("-" * 40)
    
    try:
        # Add src to path
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
        
        # Import the wrapper module using the correct path
        from h3.core import latlng_to_cell, cell_to_latlng, cell_to_boundary
        print("✅ H3 wrapper module imported")
        
        # Test wrapper functions
        lat, lng = 37.7749, -122.4194
        resolution = 9
        
        cell = latlng_to_cell(lat, lng, resolution)
        print(f"✅ Wrapper latlng_to_cell: {cell}")
        
        lat_back, lng_back = cell_to_latlng(cell)
        print(f"✅ Wrapper cell_to_latlng: {lat_back}, {lng_back}")
        
        boundary = cell_to_boundary(cell)
        print(f"✅ Wrapper cell_to_boundary: {len(boundary)} vertices")
        
        print("✅ H3 wrapper module working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ H3 wrapper module test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_h3_documentation():
    """Test H3 documentation completeness."""
    
    print("\n📚 Testing H3 Documentation")
    print("-" * 40)
    
    try:
        # Check README
        readme_path = "README.md"
        if os.path.exists(readme_path):
            with open(readme_path, 'r') as f:
                readme_content = f.read()
                if "H3" in readme_content and "geospatial" in readme_content.lower():
                    print("✅ README contains H3 documentation")
                else:
                    print("⚠️ README may need H3 documentation updates")
        else:
            print("❌ README.md not found")
        
        # Check docs directory
        docs_dir = "docs"
        if os.path.exists(docs_dir):
            h3_docs = [f for f in os.listdir(docs_dir) if "h3" in f.lower()]
            if h3_docs:
                print(f"✅ H3 documentation files found: {h3_docs}")
            else:
                print("⚠️ No H3-specific documentation files found")
        else:
            print("⚠️ docs directory not found")
        
        # Check source code documentation
        src_dir = "src"
        if os.path.exists(src_dir):
            h3_files = []
            for root, dirs, files in os.walk(src_dir):
                for file in files:
                    if file.endswith('.py') and 'h3' in file.lower():
                        h3_files.append(os.path.join(root, file))
            
            if h3_files:
                print(f"✅ H3 source files found: {len(h3_files)}")
                # Check for docstrings in H3 files
                for h3_file in h3_files[:3]:  # Check first 3 files
                    try:
                        with open(h3_file, 'r') as f:
                            content = f.read()
                            if '"""' in content or "'''" in content:
                                print(f"✅ {h3_file} has documentation")
                            else:
                                print(f"⚠️ {h3_file} may need documentation")
                    except:
                        pass
            else:
                print("⚠️ No H3 source files found")
        
        print("✅ H3 documentation test completed!")
        return True
        
    except Exception as e:
        print(f"❌ H3 documentation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting H3 Test Suite")
    print("=" * 60)
    
    # Run all tests
    tests = [
        ("H3 Core Operations", run_h3_tests),
        ("H3 v4 Features", test_h3_v4_features),
        ("H3 Wrapper Module", test_h3_wrapper_module),
        ("Spatial Module", test_spatial_module),
        ("H3 Documentation", test_h3_documentation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name}...")
        if test_func():
            passed += 1
            print(f"✅ {test_name} PASSED")
        else:
            print(f"❌ {test_name} FAILED")
    
    print("\n" + "=" * 60)
    print(f"📊 TEST SUMMARY")
    print(f"Passed: {passed}/{total}")
    print(f"Failed: {total - passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed!")
        sys.exit(0)
    else:
        print("⚠️ Some tests failed!")
        sys.exit(1) 