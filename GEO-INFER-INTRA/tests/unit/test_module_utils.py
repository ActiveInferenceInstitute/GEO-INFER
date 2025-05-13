"""Unit tests for module discovery utilities."""

import pytest
import sys
import os
import tempfile
from pathlib import Path

# Add parent directory to the path to find our utilities
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from tests.utils import find_modules_by_name, collect_test_modules

@pytest.mark.unit
class TestModuleUtils:
    """Test suite for module discovery utilities."""
    
    @pytest.fixture
    def mock_project_structure(self):
        """Create a mock project structure for testing."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            
            # Create a few mock modules with src/module structure
            modules = ["GEO-INFER-MOCK1", "GEO-INFER-MOCK2", "GEO-INFER-MOCK3"]
            for module in modules:
                module_dir = root / module
                module_dir.mkdir()
                src_dir = module_dir / "src"
                src_dir.mkdir()
                module_name = module.lower().replace("-", "_")
                module_subdir = src_dir / module_name
                module_subdir.mkdir()
                init_file = module_subdir / "__init__.py"
                init_file.touch()
            
            # Create a non-module directory
            non_module = root / "NON-MODULE"
            non_module.mkdir()
            # This directory doesn't have a src directory
            
            # Create another invalid module (has src but not module subdir)
            invalid = root / "GEO-INFER-INVALID"
            invalid.mkdir()
            invalid_src = invalid / "src"
            invalid_src.mkdir()
            # This module has a src directory but not the module subdirectory
            
            yield root
    
    def test_find_modules_by_name(self, mock_project_structure):
        """Test finding modules by name."""
        # Test with exact name
        modules = find_modules_by_name(mock_project_structure, "GEO-INFER-MOCK1")
        assert len(modules) == 1
        assert modules[0].name == "GEO-INFER-MOCK1"
        
        # Test with glob pattern
        modules = find_modules_by_name(mock_project_structure, "GEO-INFER-*")
        assert len(modules) == 3
        module_names = [m.name for m in modules]
        assert "GEO-INFER-MOCK1" in module_names
        assert "GEO-INFER-MOCK2" in module_names
        assert "GEO-INFER-MOCK3" in module_names
        
        # Invalid pattern should return empty list
        modules = find_modules_by_name(mock_project_structure, "NONEXISTENT-*")
        assert len(modules) == 0
    
    def test_collect_test_modules(self, mock_project_structure):
        """Test collecting test modules."""
        modules = collect_test_modules(mock_project_structure)
        
        assert len(modules) == 3
        assert "geo_infer_mock1" in modules
        assert "geo_infer_mock2" in modules
        assert "geo_infer_mock3" in modules
        
        # Check path mapping
        for name, path in modules.items():
            assert path.name.lower().replace("-", "_") == name
            assert (path / "src" / name).exists()
    
    def test_nonexistent_directory(self):
        """Test with nonexistent directory."""
        nonexistent = Path("/nonexistent/path")
        modules = find_modules_by_name(nonexistent, "GEO-INFER-*")
        assert len(modules) == 0
        
        modules = collect_test_modules(nonexistent)
        assert len(modules) == 0 