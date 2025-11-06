#!/usr/bin/env python3
"""
Comprehensive dependency analysis for all GEO-INFER modules.
Analyzes actual imports vs declared dependencies.
"""

import ast
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict

PROJECT_ROOT = Path(__file__).parent.parent.parent
MODULE_PREFIX = "GEO-INFER-"

# Standard library modules (not dependencies)
STDLIB_MODULES = {
    'abc', 'argparse', 'asyncio', 'collections', 'copy', 'csv', 'datetime',
    'decimal', 'enum', 'functools', 'hashlib', 'io', 'itertools', 'json',
    'logging', 'math', 'multiprocessing', 'os', 'pathlib', 'pickle', 'queue',
    'random', 're', 'shutil', 'sqlite3', 'string', 'subprocess', 'sys',
    'tempfile', 'threading', 'time', 'typing', 'unittest', 'urllib', 'uuid',
    'warnings', 'weakref', 'xml', 'zipfile'
}

# Known third-party packages
KNOWN_PACKAGES = {
    'numpy': 'numpy',
    'pandas': 'pandas',
    'scipy': 'scipy',
    'sklearn': 'scikit-learn',
    'geopandas': 'geopandas',
    'shapely': 'shapely',
    'h3': 'h3',
    'pyproj': 'pyproj',
    'rasterio': 'rasterio',
    'fiona': 'fiona',
    'matplotlib': 'matplotlib',
    'seaborn': 'seaborn',
    'plotly': 'plotly',
    'folium': 'folium',
    'fastapi': 'fastapi',
    'uvicorn': 'uvicorn',
    'pydantic': 'pydantic',
    'torch': 'torch',
    'tensorflow': 'tensorflow',
    'pymc': 'pymc',
    'networkx': 'networkx',
    'requests': 'requests',
    'pyyaml': 'pyyaml',
    'yaml': 'pyyaml',
    'pytest': 'pytest',
}


def extract_imports_from_file(file_path: Path) -> Set[str]:
    """Extract all import statements from a Python file."""
    imports = set()
    
    try:
        content = file_path.read_text()
        tree = ast.parse(content, filename=str(file_path))
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module_name = alias.name.split('.')[0]
                    if module_name not in STDLIB_MODULES:
                        imports.add(module_name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    module_name = node.module.split('.')[0]
                    if module_name not in STDLIB_MODULES:
                        imports.add(module_name)
    except Exception as e:
        # Skip files that can't be parsed
        pass
    
    return imports


def extract_imports_from_module(module_path: Path) -> Set[str]:
    """Extract all imports from a module's source code."""
    src_path = module_path / "src"
    if not src_path.exists():
        return set()
    
    all_imports = set()
    for py_file in src_path.rglob("*.py"):
        imports = extract_imports_from_file(py_file)
        all_imports.update(imports)
    
    return all_imports


def normalize_package_name(import_name: str) -> str:
    """Convert import name to package name."""
    return KNOWN_PACKAGES.get(import_name, import_name)


def parse_pyproject_dependencies(module_path: Path) -> Set[str]:
    """Parse declared dependencies from pyproject.toml."""
    pyproject_path = module_path / "pyproject.toml"
    if not pyproject_path.exists():
        return set()
    
    content = pyproject_path.read_text()
    
    # Extract dependencies section
    deps_match = re.search(r'dependencies\s*=\s*\[(.*?)\]', content, re.DOTALL)
    if not deps_match:
        return set()
    
    deps = set()
    deps_section = deps_match.group(1)
    
    for line in deps_section.split('\n'):
        line = line.strip()
        if line and not line.startswith('#'):
            # Remove quotes and extract package name
            dep = re.sub(r'["\'].*["\']', '', line).strip()
            if dep and '=' in dep:
                pkg_name = dep.split('>=')[0].split('<=')[0].split('==')[0].split('>')[0].split('<')[0].split('!=')[0].strip()
                if pkg_name:
                    deps.add(pkg_name)
    
    return deps


def analyze_module(module_path: Path, module_name: str) -> Dict:
    """Analyze a single module's dependencies."""
    actual_imports = extract_imports_from_module(module_path)
    declared_deps = parse_pyproject_dependencies(module_path)
    
    # Normalize package names
    actual_packages = {normalize_package_name(imp) for imp in actual_imports}
    
    # Find missing dependencies
    missing_deps = actual_packages - declared_deps
    
    # Find unused dependencies (may have false positives)
    # Skip this for now as it's complex
    
    return {
        "module": module_name,
        "actual_imports": sorted(actual_imports),
        "actual_packages": sorted(actual_packages),
        "declared_deps": sorted(declared_deps),
        "missing_deps": sorted(missing_deps),
    }


def main():
    """Analyze all modules."""
    print("=" * 70)
    print("GEO-INFER Module Dependency Analysis")
    print("=" * 70)
    
    results = []
    
    for item in PROJECT_ROOT.iterdir():
        if item.is_dir() and item.name.startswith(MODULE_PREFIX):
            module_name = item.name[len(MODULE_PREFIX):]
            print(f"\nAnalyzing {module_name}...")
            try:
                result = analyze_module(item, module_name)
                results.append(result)
                if result["missing_deps"]:
                    print(f"  ⚠️  Missing dependencies: {', '.join(result['missing_deps'])}")
                else:
                    print(f"  ✅ Dependencies OK")
            except Exception as e:
                print(f"  ❌ Error: {e}")
    
    # Generate report
    print("\n" + "=" * 70)
    print("Summary Report")
    print("=" * 70)
    
    modules_with_missing = [r for r in results if r["missing_deps"]]
    print(f"\nModules with missing dependencies: {len(modules_with_missing)}/{len(results)}")
    
    if modules_with_missing:
        print("\nMissing Dependencies by Module:")
        for result in modules_with_missing:
            print(f"  {result['module']}: {', '.join(result['missing_deps'])}")
    
    # Write detailed report
    report_path = PROJECT_ROOT / "GEO-INFER-INTRA" / "assessment_results" / "DEPENDENCY_ANALYSIS.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, 'w') as f:
        f.write("# GEO-INFER Dependency Analysis Report\n\n")
        f.write("**Generated**: November 5, 2025\n\n")
        f.write("## Overview\n\n")
        f.write(f"Analyzed {len(results)} modules for dependency consistency.\n\n")
        
        f.write("## Module Details\n\n")
        for result in sorted(results, key=lambda x: x['module']):
            f.write(f"### {result['module']}\n\n")
            f.write(f"- **Declared Dependencies**: {len(result['declared_deps'])}\n")
            f.write(f"- **Actual Imports**: {len(result['actual_imports'])}\n")
            f.write(f"- **Missing Dependencies**: {len(result['missing_deps'])}\n")
            
            if result['missing_deps']:
                f.write(f"\n**Missing**: {', '.join(result['missing_deps'])}\n")
            
            f.write("\n")
    
    print(f"\n✅ Detailed report written to: {report_path}")


if __name__ == "__main__":
    main()

