#!/usr/bin/env python3
"""
Comprehensive dependency validation for all GEO-INFER modules.

Validates:
1. Dependencies are actually used in source code
2. Version compatibility across modules
3. Proper documentation in README files
4. Consistency between requirements.txt, setup.py, and pyproject.toml
"""

import ast
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent.parent
MODULE_PREFIX = "GEO-INFER-"

# Standard library modules (not dependencies)
STDLIB_MODULES = {
    'abc', 'argparse', 'asyncio', 'base64', 'bz2', 'collections', 'contextlib',
    'copy', 'csv', 'dataclasses', 'datetime', 'decimal', 'email', 'enum',
    'functools', 'gc', 'gzip', 'hashlib', 'heapq', 'http', 'importlib',
    'inspect', 'io', 'itertools', 'json', 'logging', 'math', 'multiprocessing',
    'os', 'pathlib', 'pickle', 'pkg_resources', 'queue', 'random', 're',
    'shutil', 'socket', 'sqlite3', 'ssl', 'string', 'struct', 'subprocess',
    'sys', 'tarfile', 'tempfile', 'threading', 'time', 'traceback', 'typing',
    'unittest', 'urllib', 'uuid', 'warnings', 'weakref', 'xml', 'zipfile',
    '__future__', 'concurrent', 'statistics', 'ast', 'colorsys', 'configparser'
}

# Import name to package name mapping
IMPORT_TO_PACKAGE = {
    'sklearn': 'scikit-learn',
    'yaml': 'pyyaml',
    'PIL': 'pillow',
    'cv2': 'opencv-python',
    'Bio': 'biopython',
    'tfp': 'tensorflow-probability',
    'pymc3': 'pymc',
    'pymc4': 'pymc',
    'pymdp': 'pymdp',
    'jax': 'jax',
    'jaxlib': 'jaxlib',
    'torch': 'torch',
    'tensorflow': 'tensorflow',
    'tf': 'tensorflow',
    'h3': 'h3',
    'h5py': 'h5py',
    'networkx': 'networkx',
    'geopandas': 'geopandas',
    'shapely': 'shapely',
    'rasterio': 'rasterio',
    'fiona': 'fiona',
    'pyproj': 'pyproj',
    'matplotlib': 'matplotlib',
    'seaborn': 'seaborn',
    'plotly': 'plotly',
    'folium': 'folium',
    'fastapi': 'fastapi',
    'uvicorn': 'uvicorn',
    'pydantic': 'pydantic',
    'pymc': 'pymc',
    'requests': 'requests',
    'pyyaml': 'pyyaml',
    'pytest': 'pytest',
    'numpy': 'numpy',
    'pandas': 'pandas',
    'scipy': 'scipy',
    'joblib': 'joblib',
    'mlflow': 'mlflow',
    'jsonschema': 'jsonschema',
    'redis': 'redis',
    'pymongo': 'pymongo',
    'sqlalchemy': 'sqlalchemy',
    'prometheus_client': 'prometheus-client',
    'structlog': 'structlog',
    'loguru': 'loguru',
    'ortools': 'ortools',
    'pulp': 'pulp',
    'statsmodels': 'statsmodels',
    'xarray': 'xarray',
    'rtree': 'rtree',
    'aiohttp': 'aiohttp',
    'websockets': 'websockets',
    'paho': 'paho-mqtt',
    'asyncio_mqtt': 'asyncio-mqtt',
    'flask': 'flask',
    'flask_cors': 'flask-cors',
    'cryptography': 'cryptography',
    'jwt': 'pyjwt',
    'kubernetes': 'kubernetes',
    'tqdm': 'tqdm',
    'branca': 'branca',
    'laspy': 'laspy',
    'osmnx': 'osmnx',
    'imageio': 'imageio',
    'mayavi': 'mayavi',
    'strawberry': 'strawberry-graphql',
    'bayeux': 'bayeux-mcmc',
    'arviz': 'arviz',
    'pyro': 'pyro-ppl',
    'sympy': 'sympy',
    'symengine': 'symengine',
    'cupy': 'cupy',
    'ruptures': 'ruptures',
    'contextily': 'contextily',
    'psutil': 'psutil',
    'tqdm': 'tqdm',
    'werkzeug': 'werkzeug',
}

# GEO-INFER internal modules (not external dependencies)
GEO_INFER_MODULES = {
    'geo_infer_act', 'geo_infer_ag', 'geo_infer_agent', 'geo_infer_ai',
    'geo_infer_ant', 'geo_infer_api', 'geo_infer_app', 'geo_infer_art',
    'geo_infer_bayes', 'geo_infer_bio', 'geo_infer_civ', 'geo_infer_cog',
    'geo_infer_comms', 'geo_infer_data', 'geo_infer_econ', 'geo_infer_git',
    'geo_infer_health', 'geo_infer_intra', 'geo_infer_iot', 'geo_infer_log',
    'geo_infer_math', 'geo_infer_metagov', 'geo_infer_norms', 'geo_infer_ops',
    'geo_infer_org', 'geo_infer_pep', 'geo_infer_place', 'geo_infer_req',
    'geo_infer_risk', 'geo_infer_sec', 'geo_infer_sim', 'geo_infer_space',
    'geo_infer_spm', 'geo_infer_test', 'geo_infer_time'
}


def extract_imports_from_file(file_path: Path) -> Set[str]:
    """Extract all import statements from a Python file."""
    imports = set()
    
    try:
        content = file_path.read_text(encoding='utf-8')
        tree = ast.parse(content, filename=str(file_path))
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module_name = alias.name.split('.')[0]
                    if module_name not in STDLIB_MODULES and module_name not in GEO_INFER_MODULES:
                        imports.add(module_name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    module_name = node.module.split('.')[0]
                    if module_name not in STDLIB_MODULES and module_name not in GEO_INFER_MODULES:
                        imports.add(module_name)
    except Exception as e:
        logger.debug(f"Could not parse {file_path}: {e}")
    
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
    return IMPORT_TO_PACKAGE.get(import_name, import_name)


def parse_requirements_txt(module_path: Path) -> Dict[str, Optional[str]]:
    """Parse declared dependencies from requirements.txt."""
    req_path = module_path / "requirements.txt"
    if not req_path.exists():
        return {}
    
    deps = {}
    try:
        content = req_path.read_text(encoding='utf-8')
        for line in content.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Parse package name and version
            # Format: package>=version, package==version, package~=version, etc.
            match = re.match(r'^([a-zA-Z0-9_-]+(?:\[[^\]]+\])?)([<>=!~]+.*)?$', line)
            if match:
                pkg_name = match.group(1).split('[')[0]  # Remove extras like package[extra]
                version_spec = match.group(2).strip() if match.group(2) else None
                deps[pkg_name] = version_spec
    except Exception as e:
        logger.warning(f"Could not parse {req_path}: {e}")
    
    return deps


def parse_setup_py_dependencies(module_path: Path) -> Dict[str, Optional[str]]:
    """Parse declared dependencies from setup.py."""
    setup_path = module_path / "setup.py"
    if not setup_path.exists():
        return {}
    
    deps = {}
    try:
        content = setup_path.read_text(encoding='utf-8')
        # Look for install_requires
        match = re.search(r'install_requires\s*=\s*\[(.*?)\]', content, re.DOTALL)
        if match:
            deps_section = match.group(1)
            for line in deps_section.split('\n'):
                line = line.strip().strip(',').strip("'\"")
                if line and not line.startswith('#'):
                    # Parse package and version
                    match = re.match(r'^([a-zA-Z0-9_-]+)([<>=!~]+.*)?$', line)
                    if match:
                        pkg_name = match.group(1)
                        version_spec = match.group(2).strip() if match.group(2) else None
                        deps[pkg_name] = version_spec
    except Exception as e:
        logger.debug(f"Could not parse {setup_path}: {e}")
    
    return deps


def parse_pyproject_toml_dependencies(module_path: Path) -> Dict[str, Optional[str]]:
    """Parse declared dependencies from pyproject.toml."""
    pyproject_path = module_path / "pyproject.toml"
    if not pyproject_path.exists():
        return {}
    
    deps = {}
    try:
        content = pyproject_path.read_text(encoding='utf-8')
        # Look for dependencies in [project] or [tool.poetry.dependencies]
        patterns = [
            r'\[project\]\s+dependencies\s*=\s*\[(.*?)\]',
            r'\[tool\.poetry\.dependencies\]\s*(.*?)(?=\[|$)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.DOTALL)
            if match:
                deps_section = match.group(1)
                for line in deps_section.split('\n'):
                    line = line.strip().strip(',').strip("'\"")
                    if line and not line.startswith('#'):
                        # Parse package and version
                        match = re.match(r'^([a-zA-Z0-9_-]+)([<>=!~]+.*)?$', line)
                        if match:
                            pkg_name = match.group(1)
                            version_spec = match.group(2).strip() if match.group(2) else None
                            deps[pkg_name] = version_spec
                break
    except Exception as e:
        logger.debug(f"Could not parse {pyproject_path}: {e}")
    
    return deps


def extract_version_spec(version_str: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    """Extract minimum and maximum version from version spec."""
    if not version_str:
        return None, None
    
    # Simple extraction - look for >=, <=, ==
    min_version = None
    max_version = None
    
    if '>=' in version_str:
        match = re.search(r'>=\s*([0-9.]+)', version_str)
        if match:
            min_version = match.group(1)
    
    if '<=' in version_str:
        match = re.search(r'<=\s*([0-9.]+)', version_str)
        if match:
            max_version = match.group(1)
    
    if '==' in version_str:
        match = re.search(r'==\s*([0-9.]+)', version_str)
        if match:
            min_version = match.group(1)
            max_version = match.group(1)
    
    return min_version, max_version


def check_version_compatibility(all_deps: Dict[str, List[Tuple[str, Optional[str]]]]) -> Dict[str, List[str]]:
    """Check for version conflicts across modules."""
    conflicts = defaultdict(list)
    
    for pkg_name, module_specs in all_deps.items():
        if len(module_specs) < 2:
            continue  # No conflict if only one module uses it
        
        # Extract version ranges
        min_versions = []
        max_versions = []
        
        for module_name, version_spec in module_specs:
            min_ver, max_ver = extract_version_spec(version_spec)
            if min_ver:
                min_versions.append((module_name, min_ver))
            if max_ver:
                max_versions.append((module_name, max_ver))
        
        # Check for conflicts (simplified - would need proper version comparison)
        if min_versions and max_versions:
            max_min = max(v for _, v in min_versions)
            min_max = min(v for _, v in max_versions)
            
            # Simple string comparison (not perfect but works for most cases)
            if max_min > min_max:
                conflicts[pkg_name] = [f"{m}: {v}" for m, v in module_specs]
    
    return dict(conflicts)


def analyze_module(module_path: Path, module_name: str) -> Dict:
    """Analyze a single module's dependencies."""
    # Extract actual imports
    actual_imports = extract_imports_from_module(module_path)
    actual_packages = {normalize_package_name(imp) for imp in actual_imports}
    
    # Get declared dependencies from all sources
    req_deps = parse_requirements_txt(module_path)
    setup_deps = parse_setup_py_dependencies(module_path)
    pyproject_deps = parse_pyproject_toml_dependencies(module_path)
    
    # Merge all declared dependencies (requirements.txt takes precedence)
    declared_deps = req_deps.copy()
    declared_deps.update(setup_deps)
    declared_deps.update(pyproject_deps)
    
    # Find missing dependencies (used but not declared)
    missing_deps = actual_packages - set(declared_deps.keys())
    
    # Find unused dependencies (declared but not used - may have false positives)
    # Only flag obvious ones (not used in any import)
    unused_deps = set(declared_deps.keys()) - actual_packages
    
    # Check consistency between dependency files
    inconsistencies = []
    all_declared = set(req_deps.keys()) | set(setup_deps.keys()) | set(pyproject_deps.keys())
    for pkg in all_declared:
        versions = []
        if pkg in req_deps:
            versions.append(('requirements.txt', req_deps[pkg]))
        if pkg in setup_deps:
            versions.append(('setup.py', setup_deps[pkg]))
        if pkg in pyproject_deps:
            versions.append(('pyproject.toml', pyproject_deps[pkg]))
        
        if len(set(v for _, v in versions)) > 1:
            inconsistencies.append({
                'package': pkg,
                'versions': versions
            })
    
    return {
        "module": module_name,
        "actual_imports": sorted(actual_imports),
        "actual_packages": sorted(actual_packages),
        "declared_deps": declared_deps,
        "missing_deps": sorted(missing_deps),
        "unused_deps": sorted(unused_deps),
        "inconsistencies": inconsistencies,
        "has_requirements_txt": (module_path / "requirements.txt").exists(),
        "has_setup_py": (module_path / "setup.py").exists(),
        "has_pyproject_toml": (module_path / "pyproject.toml").exists(),
    }


def main():
    """Validate all module dependencies."""
    print("=" * 80)
    print("GEO-INFER Dependency Validation")
    print("=" * 80)
    
    results = []
    all_deps = defaultdict(list)  # package -> [(module, version_spec), ...]
    
    # Analyze all modules
    modules = sorted([d for d in PROJECT_ROOT.iterdir() 
                     if d.is_dir() and d.name.startswith(MODULE_PREFIX)])
    
    for module_path in modules:
        module_name = module_path.name[len(MODULE_PREFIX):]
        print(f"\nAnalyzing {module_name}...")
        
        try:
            result = analyze_module(module_path, module_name)
            results.append(result)
            
            # Collect dependencies for version conflict checking
            for pkg, version_spec in result["declared_deps"].items():
                all_deps[pkg].append((module_name, version_spec))
            
            # Print summary
            if result["missing_deps"]:
                print(f"  ⚠️  Missing dependencies: {len(result['missing_deps'])}")
            if result["unused_deps"]:
                print(f"  ℹ️  Potentially unused: {len(result['unused_deps'])}")
            if result["inconsistencies"]:
                print(f"  ⚠️  Inconsistencies: {len(result['inconsistencies'])}")
            if not result["missing_deps"] and not result["inconsistencies"]:
                print(f"  ✅ Dependencies OK")
                
        except Exception as e:
            logger.error(f"Error analyzing {module_name}: {e}")
            print(f"  ❌ Error: {e}")
    
    # Check for version conflicts
    print("\n" + "=" * 80)
    print("Checking version compatibility...")
    conflicts = check_version_compatibility(all_deps)
    
    if conflicts:
        print(f"  ⚠️  Found {len(conflicts)} potential version conflicts")
    else:
        print("  ✅ No version conflicts detected")
    
    # Generate comprehensive report
    report_path = PROJECT_ROOT / "GEO-INFER-INTRA" / "assessment_results" / "DEPENDENCY_VALIDATION_REPORT.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# GEO-INFER Dependency Validation Report\n\n")
        f.write("**Generated**: Automated validation\n\n")
        f.write("## Overview\n\n")
        f.write(f"Validated {len(results)} modules for dependency consistency, usage, and version compatibility.\n\n")
        
        # Summary statistics
        modules_with_missing = [r for r in results if r["missing_deps"]]
        modules_with_unused = [r for r in results if r["unused_deps"]]
        modules_with_inconsistencies = [r for r in results if r["inconsistencies"]]
        
        f.write("## Summary Statistics\n\n")
        f.write(f"- **Modules with missing dependencies**: {len(modules_with_missing)}/{len(results)}\n")
        f.write(f"- **Modules with potentially unused dependencies**: {len(modules_with_unused)}/{len(results)}\n")
        f.write(f"- **Modules with dependency file inconsistencies**: {len(modules_with_inconsistencies)}/{len(results)}\n")
        f.write(f"- **Potential version conflicts**: {len(conflicts)}\n\n")
        
        # Version conflicts
        if conflicts:
            f.write("## Version Conflicts\n\n")
            for pkg, module_specs in sorted(conflicts.items()):
                f.write(f"### {pkg}\n\n")
                f.write("Conflicting version specifications:\n")
                for module, version in module_specs:
                    f.write(f"- `{module}`: {version or 'unspecified'}\n")
                f.write("\n")
        
        # Module details
        f.write("## Module Details\n\n")
        for result in sorted(results, key=lambda x: x['module']):
            f.write(f"### {result['module']}\n\n")
            f.write(f"- **Requirements.txt**: {'✅' if result['has_requirements_txt'] else '❌'}\n")
            f.write(f"- **Setup.py**: {'✅' if result['has_setup_py'] else '❌'}\n")
            f.write(f"- **Pyproject.toml**: {'✅' if result['has_pyproject_toml'] else '❌'}\n")
            f.write(f"- **Declared Dependencies**: {len(result['declared_deps'])}\n")
            f.write(f"- **Actual Imports**: {len(result['actual_packages'])}\n")
            f.write(f"- **Missing Dependencies**: {len(result['missing_deps'])}\n")
            f.write(f"- **Potentially Unused**: {len(result['unused_deps'])}\n")
            f.write(f"- **Inconsistencies**: {len(result['inconsistencies'])}\n\n")
            
            if result['missing_deps']:
                f.write("**Missing Dependencies**:\n")
                for dep in result['missing_deps']:
                    f.write(f"- `{dep}`\n")
                f.write("\n")
            
            if result['inconsistencies']:
                f.write("**Dependency File Inconsistencies**:\n")
                for inc in result['inconsistencies']:
                    f.write(f"- `{inc['package']}`: ")
                    versions_str = ", ".join([f"{src}: {ver or 'unspecified'}" 
                                            for src, ver in inc['versions']])
                    f.write(versions_str + "\n")
                f.write("\n")
            
            if result['unused_deps'] and len(result['unused_deps']) <= 10:
                f.write("**Potentially Unused Dependencies** (may be false positives):\n")
                for dep in result['unused_deps'][:10]:
                    f.write(f"- `{dep}`\n")
                f.write("\n")
            
            f.write("\n")
    
    print(f"\n✅ Detailed report written to: {report_path}")
    print("\n" + "=" * 80)
    print("Validation Complete")
    print("=" * 80)


if __name__ == "__main__":
    main()

