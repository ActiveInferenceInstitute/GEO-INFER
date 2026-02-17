import importlib.util
import sys
from pathlib import Path
from typing import Dict, List

def collect_test_modules(root_dir: Path) -> Dict[str, Path]:
    """Collect all GEO-INFER modules in the given root directory."""
    modules = {}
    if not root_dir.exists():
        return modules
        
    for item in root_dir.iterdir():
        if item.is_dir() and item.name.startswith("GEO-INFER-"):
             module_name_snake = item.name.lower().replace("-", "_")
             if (item / "src" / module_name_snake).is_dir():
                modules[module_name_snake] = item
    return modules

def import_module_by_path(path: str, name: str):
    """Import a module from a file path."""
    spec = importlib.util.spec_from_file_location(name, path)
    if spec and spec.loader:
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        return module
    return None

def find_modules_by_name(root_dir: Path, pattern: str) -> List[Path]:
    """Find modules matching a name pattern. Returns a list of paths."""
    modules = []
    import fnmatch
    
    if not root_dir.exists():
        return []
        
    for item in root_dir.iterdir():
        if item.is_dir() and fnmatch.fnmatch(item.name, pattern):
             module_name_snake = item.name.lower().replace("-", "_")
             if (item / "src" / module_name_snake).is_dir():
                 modules.append(item)
             
    return sorted(modules)
