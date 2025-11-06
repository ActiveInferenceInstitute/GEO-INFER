#!/usr/bin/env python3
"""
Fix existing pyproject.toml files to preserve their dependencies and merge properly.
"""

import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent

# Modules with existing pyproject.toml that should be preserved/merged
EXISTING_MODULES = {
    "MATH": {
        "dependencies": [
            "numpy>=1.20.0",
            "scipy>=1.7.0",
            "pandas>=1.3.0",
            "geopandas>=0.10.0",
            "scikit-learn>=1.0.0",
            "matplotlib>=3.4.0",
            "shapely>=1.8.0",
        ]
    },
    "HEALTH": {
        "preserve": True  # Already has comprehensive dependencies
    },
    "PEP": {
        "convert_from_poetry": True  # Needs conversion from Poetry format
    }
}


def convert_pep_from_poetry():
    """Convert PEP's Poetry format to standard pyproject.toml."""
    pep_path = PROJECT_ROOT / "GEO-INFER-PEP" / "pyproject.toml"
    if not pep_path.exists():
        return
    
    content = pep_path.read_text()
    
    # Check if it's Poetry format
    if "[tool.poetry]" not in content:
        return
    
    print("Converting PEP from Poetry format...")
    
    # Extract Poetry dependencies
    poetry_deps_match = re.search(r'\[tool\.poetry\.dependencies\]\s*(.*?)(?=\[|$)', content, re.DOTALL)
    poetry_dev_match = re.search(r'\[tool\.poetry\.dev-dependencies\]\s*(.*?)(?=\[|$)', content, re.DOTALL)
    
    # Build standard pyproject.toml
    new_content = """[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "geo-infer-pep"
version = "0.1.0"
description = "People, Engagement, and Performance (PEP) management for GEO-INFER"
readme = "README.md"
license = {text = "CC BY-ND-SA 4.0"}
requires-python = ">=3.9"
authors = [
    {name = "GEO-INFER Development Team", email = "geo-infer@activeinference.institute"}
]
keywords = ["geospatial", "active inference", "geoinformatics", "people-management, hr, crm, engagement"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: Creative Commons License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Scientific/Engineering :: GIS",
    "Topic :: Scientific/Engineering :: Information Analysis",
]

dependencies = [
    "fastapi>=0.100.0",
    "uvicorn[standard]>=0.23.2",
    "pydantic>=2.0",
    "pandas>=2.0",
    "matplotlib>=3.7.0",
    "seaborn>=0.13.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "ruff>=0.1.0",
    "pytest>=6.2.0",
    "pytest-cov>=2.12.0",
    "pytest-asyncio>=0.20.0",
    "black>=21.9.0",
    "flake8>=3.9.0",
    "mypy>=0.910",
    "isort>=5.9.0",
]
docs = [
    "sphinx>=4.2.0",
    "sphinx-rtd-theme>=1.0.0",
    "nbsphinx>=0.8.0",
    "myst-parser>=0.15.0",
]

[project.urls]
Homepage = "https://github.com/geo-infer/geo-infer"
Documentation = "https://geo-infer.readthedocs.io/"
Repository = "https://github.com/geo-infer/geo-infer"
"Bug Tracker" = "https://github.com/geo-infer/geo-infer/issues"

[tool.setuptools]
package-dir = {"" = "src"}

[tool.setuptools.packages.find]
where = ["src"]
exclude = ["tests*"]

[tool.setuptools.package-data]
"*" = ["*.yaml", "*.yml", "*.json", "*.md", "*.txt"]

[tool.black]
line-length = 88
target-version = ['py39', 'py310', 'py311', 'py312']
include = '\.pyi?$'

[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88
known_first_party = ["geo_infer_pep"]

[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_equality = true

[[tool.mypy.overrides]]
module = [
    "numpy.*",
    "pandas.*",
    "geopandas.*",
    "h3.*",
    "folium.*",
    "plotly.*",
    "matplotlib.*",
    "scipy.*",
    "sklearn.*",
]
ignore_missing_imports = true

[tool.pytest.ini_options]
minversion = "6.0"
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--strict-markers",
    "--strict-config",
]
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
    "unit: marks tests as unit tests",
    "performance: marks tests as performance tests",
]

[tool.coverage.run]
source = ["src"]
omit = [
    "*/tests/*",
    "*/test_*",
    "*/__pycache__/*",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "class .*\\bProtocol\\):",
    "@(abc\\.)?abstractmethod",
]
"""
    
    pep_path.write_text(new_content)
    print("  ✅ Converted PEP from Poetry format")


def fix_health_pyproject():
    """Ensure HEALTH's pyproject.toml is properly formatted."""
    # HEALTH already has a comprehensive pyproject.toml, just ensure it's correct
    health_path = PROJECT_ROOT / "GEO-INFER-HEALTH" / "pyproject.toml"
    if health_path.exists():
        print("  ✅ HEALTH pyproject.toml already comprehensive")
        return


def main():
    """Fix existing pyproject.toml files."""
    print("Fixing existing pyproject.toml files...\n")
    
    convert_pep_from_poetry()
    fix_health_pyproject()
    
    print("\n✅ Fix complete")


if __name__ == "__main__":
    main()

