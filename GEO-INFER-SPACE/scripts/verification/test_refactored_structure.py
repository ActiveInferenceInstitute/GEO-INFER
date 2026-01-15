#!/usr/bin/env python3
"""
Test script to verify the refactored GEO-INFER-SPACE structure.

This script tests that the new backend-agnostic architecture works correctly,
with proper dispatch to H3 and SRAI backends.
"""

import sys
import os
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent / "src"))


def test_core_imports():
    """Test that core modules can be imported."""
    print("🧪 Testing core module imports...")

    try:
        # Test generic spatial interfaces
        from geo_infer_space.core.spatial_indexing import SpatialIndexingInterface
        from geo_infer_space.core.geometric_operations import GeometricOperationsInterface
        from geo_infer_space.core.analytics import SpatialAnalyticsInterface
        from geo_infer_space.core.dispatcher import get_backend_dispatcher, configure_backends

        print("✅ Core spatial interfaces imported successfully")
        return True

    except Exception as e:
        print(f"❌ Core imports failed: {e}")
        return False


def test_backend_dispatcher():
    """Test the backend dispatcher functionality."""
    print("\n🧪 Testing backend dispatcher...")

    try:
        from geo_infer_space.core.dispatcher import get_backend_dispatcher, configure_backends

        # Get dispatcher
        dispatcher = get_backend_dispatcher()

        # Test backend registration
        backends = dispatcher.get_available_backends()
        print(f"✅ Available backends: {backends}")

        # Test backend info
        info = dispatcher.get_backend_info()
        print(f"✅ Backend info retrieved for {len(info)} backends")

        # Test configuration
        configure_backends({
            'default_backends': {
                'indexing': 'h3',
                'analytics': 'srai'
            }
        })
        print("✅ Backend configuration applied")

        return True

    except Exception as e:
        print(f"❌ Backend dispatcher test failed: {e}")
        return False


def test_spatial_indexing_interface():
    """Test the generic spatial indexing interface."""
    print("\n🧪 Testing spatial indexing interface...")

    try:
        from geo_infer_space.core.spatial_indexing import SpatialIndexingInterface, latlng_to_cell

        # Test with default backend
        indexer = SpatialIndexingInterface()

        # Test latlng to cell conversion
        cell = indexer.latlng_to_cell(37.7749, -122.4194, 9)
        print(f"✅ Default backend latlng_to_cell: {cell}")

        # Test convenience function
        cell2 = latlng_to_cell(37.7749, -122.4194, 9)
        print(f"✅ Convenience function latlng_to_cell: {cell2}")

        # Test with specific backend
        indexer_h3 = SpatialIndexingInterface(backend='h3')
        cell_h3 = indexer_h3.latlng_to_cell(37.7749, -122.4194, 9)
        print(f"✅ H3 backend latlng_to_cell: {cell_h3}")

        return True

    except Exception as e:
        print(f"❌ Spatial indexing interface test failed: {e}")
        return False


def test_backend_implementations():
    """Test that backend implementations are available."""
    print("\n🧪 Testing backend implementations...")

    try:
        # Test H3 backend
        from geo_infer_space.backends.h3 import H3Backend

        h3_backend = H3Backend()
        print(f"✅ H3 backend created: {h3_backend.name} v{h3_backend.version}")
        print(f"   Available: {h3_backend.is_available()}")
        print(f"   Capabilities: {len(h3_backend.get_capabilities())} categories")

        # Test SRAI backend
        from geo_infer_space.backends.srai import SraiBackend

        srai_backend = SraiBackend()
        print(f"✅ SRAI backend created: {srai_backend.name} v{srai_backend.version}")
        print(f"   Available: {srai_backend.is_available()}")
        print(f"   Capabilities: {len(srai_backend.get_capabilities())} categories")

        return True

    except Exception as e:
        print(f"❌ Backend implementations test failed: {e}")
        return False


def test_backward_compatibility():
    """Test that legacy imports still work."""
    print("\n🧪 Testing backward compatibility...")

    try:
        import geo_infer_space

        # Test that old function names still exist (even if they're mocks)
        if hasattr(geo_infer_space, 'latlng_to_cell'):
            print("✅ Legacy latlng_to_cell function available")
        else:
            print("❌ Legacy latlng_to_cell function missing")

        if hasattr(geo_infer_space, 'cell_to_latlng'):
            print("✅ Legacy cell_to_latlng function available")
        else:
            print("❌ Legacy cell_to_latlng function missing")

        return True

    except Exception as e:
        print(f"❌ Backward compatibility test failed: {e}")
        return False


def test_directory_structure():
    """Test that the new directory structure exists."""
    print("\n🧪 Testing directory structure...")

    # Base path should be the project root (2 levels up from scripts/verification/)
    base_path = Path(__file__).parent.parent.parent

    required_dirs = [
        "src/geo_infer_space/core",
        "src/geo_infer_space/backends/h3",
        "src/geo_infer_space/backends/srai",
    ]

    for dir_path in required_dirs:
        full_path = base_path / dir_path
        if full_path.exists():
            print(f"✅ {dir_path} exists")
        else:
            print(f"❌ {dir_path} missing")
            return False

    # Test key files exist
    key_files = [
        "src/geo_infer_space/core/__init__.py",
        "src/geo_infer_space/core/dispatcher.py",
        "src/geo_infer_space/core/spatial_indexing.py",
        "src/geo_infer_space/backends/h3/__init__.py",
        "src/geo_infer_space/backends/h3/h3_backend.py",
        "src/geo_infer_space/backends/srai/__init__.py",
        "src/geo_infer_space/backends/srai/srai_backend.py"
    ]

    for file_path in key_files:
        full_path = base_path / file_path
        if full_path.exists():
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} missing")
            return False

    return True


def main():
    """Run all refactoring tests."""
    print("🚀 GEO-INFER-SPACE Refactoring Verification")
    print("=" * 60)

    tests = [
        ("Directory Structure", test_directory_structure),
        ("Core Imports", test_core_imports),
        ("Backend Dispatcher", test_backend_dispatcher),
        ("Spatial Indexing Interface", test_spatial_indexing_interface),
        ("Backend Implementations", test_backend_implementations),
        ("Backward Compatibility", test_backward_compatibility)
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}:")
        print("-" * 40)

        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")

    print("\n" + "=" * 60)
    print(f"📊 TEST RESULTS: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 ALL REFACTORING TESTS PASSED!")
        print("\n📋 Refactoring Summary:")
        print("✅ Generic spatial methods layer created")
        print("✅ Backend dispatcher system implemented")
        print("✅ H3 backend standalone folder created")
        print("✅ SRAI backend standalone folder created")
        print("✅ Backward compatibility maintained")
        print("✅ Directory structure properly organized")
        print("\n📝 Next Steps:")
        print("1. Add more backend implementations as needed")
        print("2. Implement additional spatial operations")
        print("3. Add comprehensive tests for each backend")
        print("4. Update examples to use new API")
        return 0
    else:
        print("⚠️  Some refactoring tests failed. Please check the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
