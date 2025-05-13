"""Test utilities for the GEO-INFER framework."""

from pathlib import Path
import importlib.util
import sys
from typing import List, Optional, Dict, Any, Callable, Type

def import_module_by_path(module_path: str, module_name: Optional[str] = None) -> Any:
    """
    Dynamically import a module by its file path.
    
    Args:
        module_path: Path to the module file
        module_name: Optional name to give the module
        
    Returns:
        The imported module
    """
    if module_name is None:
        module_name = Path(module_path).stem
    
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load spec for module at {module_path}")
    
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

def find_modules_by_name(parent_dir: Path, name_pattern: str) -> List[Path]:
    """
    Find all modules matching a name pattern.
    
    Args:
        parent_dir: Directory to search in
        name_pattern: Pattern to match (e.g., 'geo_infer_*')
        
    Returns:
        List of paths to matching modules
    """
    if not parent_dir.exists():
        return []
    
    import glob
    matching_dirs = []
    
    # Handle glob pattern
    if '*' in name_pattern:
        # Look for matching directories that have src/<module>/
        module_paths = list(parent_dir.glob(name_pattern))
        for path in module_paths:
            src_path = path / 'src'
            if src_path.exists() and src_path.is_dir():
                matching_dirs.append(path)
    else:
        # Exact name
        module_path = parent_dir / name_pattern
        if module_path.exists() and module_path.is_dir():
            src_path = module_path / 'src'
            if src_path.exists() and src_path.is_dir():
                matching_dirs.append(module_path)
    
    return matching_dirs

def collect_test_modules(root_dir: Path) -> Dict[str, Path]:
    """
    Collect all GEO-INFER modules for testing.
    
    Args:
        root_dir: Root directory of the GEO-INFER project
        
    Returns:
        Dictionary mapping module names to their paths
    """
    modules = {}
    module_paths = find_modules_by_name(root_dir, "GEO-INFER-*")
    
    for module_path in module_paths:
        # Convert module name from kebab-case to snake_case
        module_name = module_path.name.lower().replace('-', '_')
        modules[module_name] = module_path
    
    return modules 