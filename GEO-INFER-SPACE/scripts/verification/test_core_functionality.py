#!/usr/bin/env python3
"""
Core functionality test for GEO-INFER-SPACE.

This test verifies the basic structure and imports of the module
without requiring external dependencies.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_module_structure():
    """Test that the module structure is correct."""
    print("🧪 Testing module structure...")
    
    src_path = Path(__file__).parent / "src" / "geo_infer_space"
    
    # Check main directories exist
    required_dirs = [
        "analytics",
        "api", 
        "models",
        "io",
        "utils"
    ]
    
    for dir_name in required_dirs:
        dir_path = src_path / dir_name
        if dir_path.exists():
            print(f"✅ {dir_name}/ directory exists")
        else:
            print(f"❌ {dir_name}/ directory missing")
            return False
    
    # Check key files exist
    key_files = [
        "__init__.py",
        "analytics/__init__.py",
        "analytics/vector.py",
        "analytics/raster.py", 
        "analytics/network.py",
        "analytics/geostatistics.py",
        "analytics/point_cloud.py",
        "api/__init__.py",
        "api/schemas.py",
        "api/rest_api.py",
        "models/__init__.py",
        "models/data_models.py",
        "models/config_models.py",
        "io/__init__.py",
        "io/vector_io.py",
        "utils/__init__.py",
        "utils/h3_utils.py"
    ]
    
    for file_path in key_files:
        full_path = src_path / file_path
        if full_path.exists():
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} missing")
            return False
    
    return True


def test_basic_imports():
    """Test basic imports that don't require external dependencies."""
    print("\n🧪 Testing basic imports...")
    
    try:
        # Test main package import
        import geo_infer_space
        print("✅ geo_infer_space package imported")
        
        # Test version
        version = getattr(geo_infer_space, '__version__', None)
        if version:
            print(f"✅ Version: {version}")
        else:
            print("❌ No version found")
            
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False


def test_h3_utils_structure():
    """Test H3 utilities structure (without requiring h3 package)."""
    print("\n🧪 Testing H3 utilities structure...")
    
    try:
        # Import the module (should work even without h3 package)
        from geo_infer_space.utils import h3_utils
        
        # Check that functions are defined
        expected_functions = [
            'latlng_to_cell',
            'cell_to_latlng',
            'cell_to_latlng_boundary', 
            'polygon_to_cells',
            'geo_to_cells',
            'grid_disk',
            'grid_distance',
            'compact_cells',
            'uncompact_cells'
        ]
        
        for func_name in expected_functions:
            if hasattr(h3_utils, func_name):
                print(f"✅ {func_name} function available")
            else:
                print(f"❌ {func_name} function missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ H3 utils test failed: {e}")
        return False


def test_analytics_structure():
    """Test analytics module structure."""
    print("\n🧪 Testing analytics module structure...")
    
    try:
        # Test that analytics modules can be imported (structure-wise)
        import importlib.util
        
        analytics_modules = [
            'geo_infer_space.analytics.vector',
            'geo_infer_space.analytics.raster',
            'geo_infer_space.analytics.network',
            'geo_infer_space.analytics.geostatistics',
            'geo_infer_space.analytics.point_cloud'
        ]
        
        for module_name in analytics_modules:
            try:
                spec = importlib.util.find_spec(module_name)
                if spec is not None:
                    print(f"✅ {module_name} module found")
                else:
                    print(f"❌ {module_name} module not found")
                    return False
            except Exception as e:
                print(f"❌ Error checking {module_name}: {e}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Analytics structure test failed: {e}")
        return False


def test_api_structure():
    """Test API module structure."""
    print("\n🧪 Testing API module structure...")
    
    try:
        import importlib.util
        
        api_modules = [
            'geo_infer_space.api.schemas',
            'geo_infer_space.api.rest_api'
        ]
        
        for module_name in api_modules:
            try:
                spec = importlib.util.find_spec(module_name)
                if spec is not None:
                    print(f"✅ {module_name} module found")
                else:
                    print(f"❌ {module_name} module not found")
                    return False
            except Exception as e:
                print(f"❌ Error checking {module_name}: {e}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ API structure test failed: {e}")
        return False


def test_configuration_files():
    """Test that configuration and documentation files exist."""
    print("\n🧪 Testing configuration and documentation...")
    
    base_path = Path(__file__).parent
    
    required_files = [
        "README.md",
        "requirements.txt", 
        "setup.py",
        "DEVELOPMENT_SUMMARY.md",
        "verify_installation.py"
    ]
    
    for file_name in required_files:
        file_path = base_path / file_name
        if file_path.exists():
            print(f"✅ {file_name} exists")
        else:
            print(f"❌ {file_name} missing")
            return False
    
    # Check README has substantial content
    readme_path = base_path / "README.md"
    if readme_path.stat().st_size > 10000:  # At least 10KB
        print("✅ README.md has substantial content")
    else:
        print("❌ README.md appears incomplete")
        return False
    
    return True


def test_code_quality():
    """Test basic code quality indicators."""
    print("\n🧪 Testing code quality indicators...")
    
    src_path = Path(__file__).parent / "src" / "geo_infer_space"
    
    # Count Python files
    py_files = list(src_path.rglob("*.py"))
    print(f"✅ Found {len(py_files)} Python files")
    
    # Check for docstrings in main modules
    main_modules = [
        src_path / "analytics" / "vector.py",
        src_path / "api" / "rest_api.py",
        src_path / "models" / "data_models.py",
        src_path / "utils" / "h3_utils.py"
    ]
    
    for module_path in main_modules:
        if module_path.exists():
            content = module_path.read_text()
            if '"""' in content and 'def ' in content:
                print(f"✅ {module_path.name} has docstrings and functions")
            else:
                print(f"❌ {module_path.name} missing docstrings or functions")
                return False
    
    return True


def main():
    """Run all core functionality tests."""
    print("🚀 GEO-INFER-SPACE Core Functionality Test")
    print("=" * 60)
    
    tests = [
        test_module_structure,
        test_basic_imports,
        test_h3_utils_structure,
        test_analytics_structure,
        test_api_structure,
        test_configuration_files,
        test_code_quality
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All core functionality tests passed!")
        print("📋 Module structure is complete and ready for development")
        print("\n📝 Next Steps:")
        print("1. Install dependencies: pip install -e '.[all]'")
        print("2. Run full test suite: pytest tests/ -v")
        print("3. Start API server: python -m geo_infer_space.api.rest_api")
        print("4. Access documentation: http://localhost:8000/docs")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
