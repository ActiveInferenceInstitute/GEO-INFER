#!/usr/bin/env python3
"""
Verification script for GEO-INFER-SPACE installation and functionality.

This script tests the core functionality of the SPACE module to ensure
all components are working correctly after installation.
"""

import sys
import traceback
from pathlib import Path

# Add src to path for development testing
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_core_imports():
    """Test that core modules can be imported."""
    print("🧪 Testing core module imports...")
    
    try:
        # Test basic imports
        import geo_infer_space
        print("✅ geo_infer_space package imported")
        
        # Test H3 utilities
        from geo_infer_space.utils.h3_utils import latlng_to_cell, cell_to_latlng
        print("✅ H3 utilities imported")
        
        # Test analytics modules
        from geo_infer_space.analytics.vector import buffer_and_intersect
        print("✅ Vector analytics imported")
        
        from geo_infer_space.analytics.geostatistics import spatial_interpolation
        print("✅ Geostatistics imported")
        
        # Test data models
        from geo_infer_space.models.data_models import SpatialDataset
        print("✅ Data models imported")
        
        # Test API schemas
        from geo_infer_space.api.schemas import SpatialAnalysisRequest
        print("✅ API schemas imported")
        
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        traceback.print_exc()
        return False


def test_h3_functionality():
    """Test H3 hexagonal grid operations."""
    print("\n🧪 Testing H3 functionality...")
    
    try:
        from geo_infer_space.utils.h3_utils import latlng_to_cell, cell_to_latlng, polygon_to_cells
        
        # Test coordinate conversion
        lat, lng = 37.7749, -122.4194  # San Francisco
        cell = latlng_to_cell(lat, lng, 9)
        print(f"✅ Coordinate to H3 cell: {cell}")
        
        # Test reverse conversion
        result_lat, result_lng = cell_to_latlng(cell)
        print(f"✅ H3 cell to coordinate: ({result_lat:.4f}, {result_lng:.4f})")
        
        # Test polygon conversion
        polygon = {
            "type": "Polygon",
            "coordinates": [[
                [-122.42, 37.77], [-122.41, 37.77],
                [-122.41, 37.78], [-122.42, 37.78],
                [-122.42, 37.77]
            ]]
        }
        cells = polygon_to_cells(polygon, 9)
        print(f"✅ Polygon to H3 cells: {len(cells)} cells")
        
        return True
        
    except Exception as e:
        print(f"❌ H3 functionality test failed: {e}")
        traceback.print_exc()
        return False


def test_vector_operations():
    """Test vector spatial operations."""
    print("\n🧪 Testing vector operations...")
    
    try:
        import geopandas as gpd
        from shapely.geometry import Point, Polygon
        from geo_infer_space.analytics.vector import geometric_calculations, proximity_analysis
        
        # Create test data
        points = gpd.GeoDataFrame(
            {'id': [1, 2]},
            geometry=[Point(0, 0), Point(1, 1)],
            crs='EPSG:4326'
        )
        
        polygons = gpd.GeoDataFrame(
            {'id': [1]},
            geometry=[Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])],
            crs='EPSG:4326'
        )
        
        # Test geometric calculations
        result = geometric_calculations(polygons)
        print(f"✅ Geometric calculations: {len(result)} features processed")
        
        # Test proximity analysis
        result = proximity_analysis(points, polygons.centroid.to_frame('geometry'))
        print(f"✅ Proximity analysis: {len(result)} results")
        
        return True
        
    except Exception as e:
        print(f"❌ Vector operations test failed: {e}")
        traceback.print_exc()
        return False


def test_data_models():
    """Test data model validation."""
    print("\n🧪 Testing data models...")
    
    try:
        from geo_infer_space.models.data_models import SpatialBounds, CoordinateReferenceSystem
        
        # Test spatial bounds
        bounds = SpatialBounds(minx=0, miny=0, maxx=1, maxy=1)
        print(f"✅ Spatial bounds created: area = {bounds.area}")
        
        # Test CRS model
        crs = CoordinateReferenceSystem(epsg_code=4326, name="WGS84")
        print(f"✅ CRS model created: {crs.name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Data models test failed: {e}")
        traceback.print_exc()
        return False


def test_api_schemas():
    """Test API schema validation."""
    print("\n🧪 Testing API schemas...")
    
    try:
        from geo_infer_space.api.schemas import BufferAnalysisRequest
        
        # Test buffer request schema
        request_data = {
            "data": {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [0, 0]},
                "properties": {}
            },
            "buffer_distance": 1000.0
        }
        
        request = BufferAnalysisRequest(**request_data)
        print(f"✅ API schema validation: buffer_distance = {request.buffer_distance}")
        
        return True
        
    except Exception as e:
        print(f"❌ API schemas test failed: {e}")
        traceback.print_exc()
        return False


def main():
    """Run all verification tests."""
    print("🚀 GEO-INFER-SPACE Installation Verification")
    print("=" * 50)
    
    tests = [
        test_core_imports,
        test_h3_functionality,
        test_vector_operations,
        test_data_models,
        test_api_schemas
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! GEO-INFER-SPACE is ready for use.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the error messages above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
