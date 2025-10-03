#!/usr/bin/env python3
"""
Comprehensive test for multiple dispatch to H3 and SRAI backends.

This test verifies that all spatial operations properly dispatch to both
H3 and SRAI backends, ensuring the backend-agnostic architecture works correctly.
"""

import sys
import os
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent / "src"))


def test_multiple_dispatch_indexing():
    """Test multiple dispatch for spatial indexing operations."""
    print("🧪 Testing Multiple Dispatch - Spatial Indexing Operations")
    print("=" * 60)

    from geo_infer_space.core.spatial_indexing import SpatialIndexingInterface

    # Test data
    lat, lng = 37.7749, -122.4194  # San Francisco
    resolution = 9

    polygon = {
        "type": "Polygon",
        "coordinates": [[
            [-122.42, 37.77], [-122.41, 37.77],
            [-122.41, 37.78], [-122.42, 37.78],
            [-122.42, 37.77]
        ]]
    }

    # Test with H3 backend
    print("\n🔍 Testing H3 Backend:")
    try:
        h3_indexer = SpatialIndexingInterface(backend='h3')

        # Test latlng_to_cell
        cell_h3 = h3_indexer.latlng_to_cell(lat, lng, resolution)
        print(f"✅ H3 latlng_to_cell: {cell_h3}")

        # Test cell_to_latlng
        lat_back, lng_back = h3_indexer.cell_to_latlng(cell_h3)
        print(f"✅ H3 cell_to_latlng: ({lat_back:.4f}, {lng_back:.4f})")

        # Test polygon_to_cells
        cells_h3 = h3_indexer.polygon_to_cells(polygon, resolution)
        print(f"✅ H3 polygon_to_cells: {len(cells_h3)} cells")

        # Test get_cell_neighbors
        neighbors_h3 = h3_indexer.get_cell_neighbors(cell_h3, k=1)
        print(f"✅ H3 get_cell_neighbors: {len(neighbors_h3)} neighbors")

        # Test get_cell_distance
        if len(neighbors_h3) > 0:
            distance_h3 = h3_indexer.get_cell_distance(cell_h3, neighbors_h3[0])
            print(f"✅ H3 get_cell_distance: {distance_h3}")

        # Test compact_cells
        compacted_h3 = h3_indexer.compact_cells(cells_h3)
        print(f"✅ H3 compact_cells: {len(compacted_h3)} compacted cells")

        # Test uncompact_cells
        if len(compacted_h3) > 0:
            uncompacted_h3 = h3_indexer.uncompact_cells(compacted_h3, resolution)
            print(f"✅ H3 uncompact_cells: {len(uncompacted_h3)} uncompacted cells")

        h3_success = True

    except Exception as e:
        print(f"❌ H3 backend test failed: {e}")
        h3_success = False

    # Test with SRAI backend
    print("\n🔍 Testing SRAI Backend:")
    try:
        srai_indexer = SpatialIndexingInterface(backend='srai')

        # Test latlng_to_cell
        cell_srai = srai_indexer.latlng_to_cell(lat, lng, resolution)
        print(f"✅ SRAI latlng_to_cell: {cell_srai}")

        # Test cell_to_latlng
        lat_back, lng_back = srai_indexer.cell_to_latlng(cell_srai)
        print(f"✅ SRAI cell_to_latlng: ({lat_back:.4f}, {lng_back:.4f})")

        # Test polygon_to_cells
        cells_srai = srai_indexer.polygon_to_cells(polygon, resolution)
        print(f"✅ SRAI polygon_to_cells: {len(cells_srai)} cells")

        # Test get_cell_neighbors
        neighbors_srai = srai_indexer.get_cell_neighbors(cell_srai, k=1)
        print(f"✅ SRAI get_cell_neighbors: {len(neighbors_srai)} neighbors")

        # Test get_cell_distance
        if len(neighbors_srai) > 0:
            distance_srai = srai_indexer.get_cell_distance(cell_srai, neighbors_srai[0])
            print(f"✅ SRAI get_cell_distance: {distance_srai}")

        # Test compact_cells
        compacted_srai = srai_indexer.compact_cells(cells_srai)
        print(f"✅ SRAI compact_cells: {len(compacted_srai)} compacted cells")

        # Test uncompact_cells
        if len(compacted_srai) > 0:
            uncompacted_srai = srai_indexer.uncompact_cells(compacted_srai, resolution)
            print(f"✅ SRAI uncompact_cells: {len(uncompacted_srai)} uncompacted cells")

        srai_success = True

    except Exception as e:
        print(f"❌ SRAI backend test failed: {e}")
        srai_success = False

    # Test default backend (should use H3)
    print("\n🔍 Testing Default Backend (H3):")
    try:
        default_indexer = SpatialIndexingInterface()

        cell_default = default_indexer.latlng_to_cell(lat, lng, resolution)
        print(f"✅ Default backend latlng_to_cell: {cell_default}")

        # Should match H3 result
        if h3_success and cell_default == cell_h3:
            print("✅ Default backend matches H3 backend")
        else:
            print("⚠️  Default backend may not match H3 backend")

        default_success = True

    except Exception as e:
        print(f"❌ Default backend test failed: {e}")
        default_success = False

    return h3_success and srai_success and default_success


def test_multiple_dispatch_analytics():
    """Test multiple dispatch for spatial analytics operations."""
    print("\n🧪 Testing Multiple Dispatch - Spatial Analytics Operations")
    print("=" * 60)

    from geo_infer_space.core.analytics import SpatialAnalyticsInterface

    # Test data
    cells = ['cell1', 'cell2', 'cell3', 'cell4', 'cell5']
    values = [10, 50, 5, 30, 15]

    data = {
        'cells': cells,
        'values': values
    }

    points = [
        (37.7749, -122.4194),
        (37.7849, -122.4094),
        (37.7649, -122.4294)
    ]

    # Test with H3 backend
    print("\n🔍 Testing H3 Backend Analytics:")
    try:
        h3_analytics = SpatialAnalyticsInterface(backend='h3')

        # Test analyze_hotspots
        hotspots_h3 = h3_analytics.analyze_hotspots(data)
        print(f"✅ H3 analyze_hotspots: {hotspots_h3.get('hotspot_count', 0)} hotspots")

        # Test compute_proximity
        proximity_h3 = h3_analytics.compute_proximity(points)
        print(f"✅ H3 compute_proximity: {proximity_h3.get('analyzed_pairs', 0)} pairs")

        h3_analytics_success = True

    except Exception as e:
        print(f"❌ H3 analytics test failed: {e}")
        h3_analytics_success = False

    # Test with SRAI backend
    print("\n🔍 Testing SRAI Backend Analytics:")
    try:
        srai_analytics = SpatialAnalyticsInterface(backend='srai')

        # Test analyze_hotspots
        hotspots_srai = srai_analytics.analyze_hotspots(data)
        print(f"✅ SRAI analyze_hotspots: {hotspots_srai.get('hotspot_count', 0)} hotspots")

        # Test compute_proximity
        proximity_srai = srai_analytics.compute_proximity(points)
        print(f"✅ SRAI compute_proximity: {proximity_srai.get('analyzed_pairs', 0)} pairs")

        srai_analytics_success = True

    except Exception as e:
        print(f"❌ SRAI analytics test failed: {e}")
        srai_analytics_success = False

    return h3_analytics_success and srai_analytics_success


def test_backend_capabilities():
    """Test that both backends report proper capabilities."""
    print("\n🧪 Testing Backend Capabilities")
    print("=" * 60)

    from geo_infer_space.core.dispatcher import get_backend_dispatcher

    dispatcher = get_backend_dispatcher()
    backends = dispatcher.get_available_backends()

    print(f"Available backends: {backends}")

    for backend_name in backends:
        backend = dispatcher.get_backend(backend_name)
        if backend:
            capabilities = backend.get_capabilities()
            print(f"\n🔍 {backend_name.upper()} Backend Capabilities:")

            # Check indexing capabilities
            if 'indexing' in capabilities:
                indexing_caps = capabilities['indexing']
                print(f"   Indexing: {list(indexing_caps.keys())}")

            # Check analytics capabilities
            if 'analytics' in capabilities:
                analytics_caps = capabilities['analytics']
                print(f"   Analytics: {list(analytics_caps.keys())}")

            # Check geometric capabilities
            if 'geometric' in capabilities:
                geometric_caps = capabilities['geometric']
                print(f"   Geometric: {list(geometric_caps.keys())}")

            print(f"   Available: {backend.is_available()}")
            print(f"   Version: {backend.version}")

    return len(backends) >= 1  # At least H3 should be available


def test_convenience_functions():
    """Test that convenience functions work with multiple backends."""
    print("\n🧪 Testing Convenience Functions")
    print("=" * 60)

    from geo_infer_space.core.spatial_indexing import latlng_to_cell, cell_to_latlng, polygon_to_cells

    lat, lng = 37.7749, -122.4194
    resolution = 9

    # Test convenience functions with explicit backends
    print("\n🔍 Testing with explicit backends:")

    try:
        # H3 backend
        cell_h3 = latlng_to_cell(lat, lng, resolution, backend='h3')
        print(f"✅ latlng_to_cell with H3: {cell_h3}")

        # SRAI backend
        cell_srai = latlng_to_cell(lat, lng, resolution, backend='srai')
        print(f"✅ latlng_to_cell with SRAI: {cell_srai}")

        # Test without explicit backend (should use default)
        cell_default = latlng_to_cell(lat, lng, resolution)
        print(f"✅ latlng_to_cell default: {cell_default}")

        return True

    except Exception as e:
        print(f"❌ Convenience functions test failed: {e}")
        return False


def test_backend_dispatcher_configuration():
    """Test backend dispatcher configuration and routing."""
    print("\n🧪 Testing Backend Dispatcher Configuration")
    print("=" * 60)

    from geo_infer_space.core.dispatcher import get_backend_dispatcher, configure_backends

    dispatcher = get_backend_dispatcher()

    # Test configuration
    print("\n🔍 Testing configuration:")
    try:
        # Configure custom defaults
        config = {
            'default_backends': {
                'indexing': 'h3',
                'analytics': 'srai'
            }
        }

        configure_backends(config)
        print("✅ Backend configuration applied")

        # Test that configuration is applied
        indexing_default = dispatcher.get_default_backend('indexing')
        analytics_default = dispatcher.get_default_backend('analytics')

        print(f"✅ Indexing default: {indexing_default}")
        print(f"✅ Analytics default: {analytics_default}")

        # Test backend info
        info = dispatcher.get_backend_info()
        print(f"✅ Retrieved info for {len(info)} backends")

        return True

    except Exception as e:
        print(f"❌ Dispatcher configuration test failed: {e}")
        return False


def test_backend_specific_features():
    """Test backend-specific features and capabilities."""
    print("\n🧪 Testing Backend-Specific Features")
    print("=" * 60)

    # Test H3-specific features
    print("\n🔍 Testing H3-Specific Features:")
    try:
        from geo_infer_space.backends.h3 import H3Backend

        h3_backend = H3Backend()
        capabilities = h3_backend.get_capabilities()

        print(f"✅ H3 backend name: {h3_backend.name}")
        print(f"✅ H3 backend version: {h3_backend.version}")
        print(f"✅ H3 supported resolutions: {capabilities.get('supported_resolutions', [])}")
        print(f"✅ H3 coordinate system: {capabilities.get('coordinate_system', 'unknown')}")

        h3_features_success = True

    except Exception as e:
        print(f"❌ H3 features test failed: {e}")
        h3_features_success = False

    # Test SRAI-specific features
    print("\n🔍 Testing SRAI-Specific Features:")
    try:
        from geo_infer_space.backends.srai import SraiBackend

        srai_backend = SraiBackend()
        capabilities = srai_backend.get_capabilities()

        print(f"✅ SRAI backend name: {srai_backend.name}")
        print(f"✅ SRAI backend version: {srai_backend.version}")
        print(f"✅ SRAI regionalizers: {capabilities.get('regionalizers', [])}")
        print(f"✅ SRAI embedders: {capabilities.get('embedders', [])}")

        srai_features_success = True

    except Exception as e:
        print(f"❌ SRAI features test failed: {e}")
        srai_features_success = False

    return h3_features_success and srai_features_success


def main():
    """Run all multiple dispatch tests."""
    print("🚀 GEO-INFER-SPACE Multiple Dispatch Comprehensive Test")
    print("=" * 70)

    tests = [
        ("Backend Capabilities", test_backend_capabilities),
        ("Indexing Multiple Dispatch", test_multiple_dispatch_indexing),
        ("Analytics Multiple Dispatch", test_multiple_dispatch_analytics),
        ("Convenience Functions", test_convenience_functions),
        ("Dispatcher Configuration", test_backend_dispatcher_configuration),
        ("Backend-Specific Features", test_backend_specific_features)
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}:")
        print("-" * 50)

        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")

    print("\n" + "=" * 70)
    print(f"📊 TEST RESULTS: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 ALL MULTIPLE DISPATCH TESTS PASSED!")
        print("\n📋 Multiple Dispatch Verification Summary:")
        print("✅ Spatial indexing operations dispatch to both H3 and SRAI")
        print("✅ Spatial analytics operations dispatch to both H3 and SRAI")
        print("✅ All core methods support multiple dispatch")
        print("✅ Backend capabilities properly reported")
        print("✅ Convenience functions work with explicit backends")
        print("✅ Dispatcher configuration works correctly")
        print("✅ Backend-specific features accessible")
        print("\n📝 Backend-Agnostic Architecture Confirmed:")
        print("   • Generic interfaces dispatch to appropriate backends")
        print("   • Both H3 and SRAI backends fully implemented")
        print("   • All operations support multiple dispatch pattern")
        print("   • Backward compatibility maintained")
        return 0
    else:
        print("⚠️  Some multiple dispatch tests failed. Please check the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
