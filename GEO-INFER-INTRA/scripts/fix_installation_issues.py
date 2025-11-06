#!/usr/bin/env python3
"""
Fix common installation issues in pyproject.toml files.
"""

import re
from pathlib import Path
from typing import List

PROJECT_ROOT = Path(__file__).parent.parent.parent

# Known issues and fixes
KNOWN_ISSUES = {
    "API": {
        "relax_versions": True,  # Relax strict version constraints
    },
    "CIV": {
        "add": ["numpy>=1.20.0"],  # Missing numpy for geopandas
    },
    "SIM": {
        "add": ["scipy>=1.7.0"],  # Missing scipy
    },
}


def relax_version_constraints(module_path: Path):
    """Relax overly strict version constraints."""
    pyproject_path = module_path / "pyproject.toml"
    if not pyproject_path.exists():
        return False
    
    content = pyproject_path.read_text()
    modified = False
    
    # Replace strict version constraints with more flexible ones
    replacements = {
        r'fastapi>=0\.95\.0,<0\.96\.0': 'fastapi>=0.95.0',
        r'httpx>=0\.24\.0,<0\.25\.0': 'httpx>=0.24.0',
        r'pydantic>=1\.10\.7,<2\.0\.0': 'pydantic>=1.10.7',
        r'pydantic-settings>=2\.0\.0,<3\.0\.0': 'pydantic-settings>=2.0.0',
        r'pytest>=7\.3\.1,<7\.4\.0': 'pytest>=7.3.1',
        r'pytest-cov>=4\.1\.0,<4\.2\.0': 'pytest-cov>=4.1.0',
        r'python-dotenv>=1\.0\.0,<2\.0\.0': 'python-dotenv>=1.0.0',
        r'python-multipart>=0\.0\.6,<0\.1\.0': 'python-multipart>=0.0.6',
        r'requests>=2\.28\.2,<2\.29\.0': 'requests>=2.28.2',
        r'uvicorn>=0\.21\.0,<0\.22\.0': 'uvicorn>=0.21.0',
    }
    
    for pattern, replacement in replacements.items():
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            modified = True
    
    if modified:
        pyproject_path.write_text(content)
        return True
    
    return False


def add_dependencies(module_path: Path, deps_to_add: List[str]):
    """Add missing dependencies to pyproject.toml."""
    pyproject_path = module_path / "pyproject.toml"
    if not pyproject_path.exists():
        return False
    
    content = pyproject_path.read_text()
    
    # Find dependencies section
    deps_match = re.search(r'dependencies\s*=\s*\[(.*?)\]', content, re.DOTALL)
    if not deps_match:
        return False
    
    deps_section = deps_match.group(1)
    existing_deps = []
    
    # Extract existing dependencies
    for line in deps_section.split('\n'):
        line = line.strip()
        if line and not line.startswith('#'):
            if '=' in line or '>' in line or '<' in line:
                # Extract package name
                dep = re.search(r'["\']([^"\']+)["\']', line)
                if dep:
                    existing_deps.append(dep.group(1))
    
    # Add new dependencies
    for dep in deps_to_add:
        pkg_name = dep.split('>=')[0].split('<=')[0].split('==')[0].strip()
        if pkg_name not in existing_deps:
            existing_deps.append(dep)
    
    # Rebuild dependencies section
    deps_text = ",\n    ".join([f'"{dep}"' for dep in sorted(existing_deps)])
    new_deps_section = f'dependencies = [\n    {deps_text}\n]'
    
    # Replace in content
    new_content = content[:deps_match.start()] + new_deps_section + content[deps_match.end():]
    pyproject_path.write_text(new_content)
    
    return True


def main():
    """Fix installation issues."""
    print("Fixing installation issues...\n")
    
    fixed_count = 0
    
    for module_name, fixes in KNOWN_ISSUES.items():
        module_path = PROJECT_ROOT / f"GEO-INFER-{module_name}"
        if not module_path.exists():
            continue
        
        print(f"Fixing {module_name}...")
        
        if "relax_versions" in fixes and fixes["relax_versions"]:
            if relax_version_constraints(module_path):
                print(f"  ✅ Relaxed version constraints")
                fixed_count += 1
        
        if "add" in fixes:
            if add_dependencies(module_path, fixes["add"]):
                print(f"  ✅ Added missing dependencies: {', '.join(fixes['add'])}")
                fixed_count += 1
    
    print(f"\n✅ Fixed {fixed_count} issues")


if __name__ == "__main__":
    main()

