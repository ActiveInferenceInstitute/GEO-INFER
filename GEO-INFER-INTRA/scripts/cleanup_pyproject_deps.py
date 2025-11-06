#!/usr/bin/env python3
"""
Cleanup script to remove duplicate dependencies from pyproject.toml files.
"""

import re
from pathlib import Path
from typing import List, Set

PROJECT_ROOT = Path(__file__).parent.parent.parent
MODULE_PREFIX = "GEO-INFER-"


def normalize_dep_name(dep: str) -> str:
    """Extract package name from dependency string."""
    dep_clean = dep.strip().replace('"', '').replace("'", "")
    return re.split(r'[>=<!=,\s]', dep_clean)[0].strip().lower()


def deduplicate_dependencies(deps: List[str]) -> List[str]:
    """Remove duplicate dependencies, keeping the most specific version."""
    dep_dict = {}
    
    for dep in deps:
        dep_clean = dep.strip().replace('"', '').replace("'", "")
        dep_name = normalize_dep_name(dep)
        
        if dep_name:
            if dep_name not in dep_dict:
                dep_dict[dep_name] = dep_clean
            else:
                # Keep the more specific version constraint
                current = dep_dict[dep_name]
                # Prefer constraints with < or , (more specific)
                if ("," in dep_clean or "<" in dep_clean) and ("," not in current and "<" not in current):
                    dep_dict[dep_name] = dep_clean
                elif ("," not in dep_clean and "<" not in dep_clean) and ("," in current or "<" in current):
                    # Keep current if it's more specific
                    pass
                else:
                    # Both similar, prefer the one with higher minimum version
                    dep_dict[dep_name] = dep_clean
    
    # Sort by package name
    return [dep_dict[name] for name in sorted(dep_dict.keys())]


def cleanup_pyproject(module_path: Path):
    """Clean up duplicate dependencies in pyproject.toml."""
    pyproject_path = module_path / "pyproject.toml"
    if not pyproject_path.exists():
        return
    
    content = pyproject_path.read_text()
    
    # Find dependencies section
    deps_match = re.search(r'dependencies\s*=\s*\[(.*?)\]', content, re.DOTALL)
    if not deps_match:
        return
    
    deps_section = deps_match.group(1)
    
    # Extract individual dependencies
    deps = []
    for line in deps_section.split('\n'):
        line = line.strip()
        if line and not line.startswith('#'):
            # Remove comments
            if '#' in line:
                line = line.split('#')[0].strip()
            if line and (line.startswith('"') or line.startswith("'")):
                # Remove quotes
                dep = line.strip('"').strip("'").strip(',').strip()
                if dep:
                    deps.append(dep)
    
    if not deps:
        return
    
    # Deduplicate
    unique_deps = deduplicate_dependencies(deps)
    
    # Rebuild dependencies section
    deps_text = ",\n    ".join([f'"{dep}"' for dep in unique_deps])
    
    # Replace in content
    new_content = content[:deps_match.start()] + f'dependencies = [\n    {deps_text}\n]' + content[deps_match.end():]
    
    pyproject_path.write_text(new_content)
    print(f"  ✅ Cleaned {module_path.name}: {len(deps)} -> {len(unique_deps)} dependencies")


def main():
    """Clean up all pyproject.toml files."""
    print("Cleaning duplicate dependencies in pyproject.toml files...\n")
    
    for item in PROJECT_ROOT.iterdir():
        if item.is_dir() and item.name.startswith(MODULE_PREFIX):
            try:
                cleanup_pyproject(item)
            except Exception as e:
                print(f"  ❌ Error cleaning {item.name}: {e}")
    
    print("\n✅ Cleanup complete")


if __name__ == "__main__":
    main()

