#!/usr/bin/env python3
"""
Add missing dependencies to modules that don't have any.
"""

from pathlib import Path
import re

PROJECT_ROOT = Path(__file__).parent.parent.parent

# Module-specific dependencies based on functionality
MODULE_DEPS = {
    "AG": [
        "numpy>=1.20.0",
        "pandas>=1.3.0",
        "geopandas>=0.10.0",
        "shapely>=1.8.0",
        "scikit-learn>=1.0.0",
        "rasterio>=1.2.0",
    ],
    "AI": [
        "numpy>=1.20.0",
        "pandas>=1.3.0",
        "torch>=1.9.0",
        "tensorflow>=2.6.0",
        "scikit-learn>=1.0.0",
    ],
    "APP": [
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "pydantic>=1.8.0",
    ],
    "CIV": [
        "geopandas>=0.10.0",
        "pandas>=1.3.0",
    ],
    "COG": [
        "numpy>=1.20.0",
        "pandas>=1.3.0",
    ],
    "COMMS": [
        "fastapi>=0.68.0",
        "pydantic>=1.8.0",
    ],
    "ECON": [
        "numpy>=1.20.0",
        "pandas>=1.3.0",
        "scipy>=1.7.0",
    ],
    "LOG": [
        "pandas>=1.3.0",
        "geopandas>=0.10.0",
    ],
    "ORG": [
        "pandas>=1.3.0",
    ],
    "REQ": [
        "pydantic>=1.8.0",
    ],
    "RISK": [
        "numpy>=1.20.0",
        "pandas>=1.3.0",
        "scipy>=1.7.0",
    ],
    "SIM": [
        "numpy>=1.20.0",
        "pandas>=1.3.0",
    ],
    "TIME": [
        "numpy>=1.20.0",
        "pandas>=1.3.0",
        "scipy>=1.7.0",
        "statsmodels>=0.13.0",
    ],
}


def add_dependencies(module_path: Path, module_name: str):
    """Add dependencies to a module's pyproject.toml."""
    pyproject_path = module_path / "pyproject.toml"
    if not pyproject_path.exists():
        return False
    
    content = pyproject_path.read_text()
    
    # Check if dependencies section is empty
    deps_match = re.search(r'dependencies\s*=\s*\[(.*?)\]', content, re.DOTALL)
    if not deps_match:
        return False
    
    deps_content = deps_match.group(1).strip()
    
    # Check if it's empty or just has comments
    if deps_content and not all(line.strip().startswith('#') or not line.strip() for line in deps_content.split('\n')):
        # Has dependencies, skip
        return False
    
    # Get dependencies for this module
    deps = MODULE_DEPS.get(module_name, [])
    if not deps:
        return False
    
    # Build new dependencies section
    deps_text = ",\n    ".join([f'"{dep}"' for dep in deps])
    new_deps_section = f'dependencies = [\n    {deps_text}\n]'
    
    # Replace
    new_content = content[:deps_match.start()] + new_deps_section + content[deps_match.end():]
    pyproject_path.write_text(new_content)
    
    print(f"  ✅ Added {len(deps)} dependencies to {module_name}")
    return True


def main():
    """Add missing dependencies to all modules."""
    print("Adding missing dependencies...\n")
    
    for item in PROJECT_ROOT.iterdir():
        if item.is_dir() and item.name.startswith("GEO-INFER-"):
            module_name = item.name[len("GEO-INFER-"):]
            if module_name in MODULE_DEPS:
                add_dependencies(item, module_name)
    
    print("\n✅ Complete")


if __name__ == "__main__":
    main()

