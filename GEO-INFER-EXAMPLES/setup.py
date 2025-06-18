#!/usr/bin/env python3
"""
Setup script for GEO-INFER-EXAMPLES: Comprehensive demonstration framework.

This module serves as the primary entry point for exploring the GEO-INFER ecosystem
through real-world, cross-module integration examples.
"""

from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "Comprehensive demonstration framework for the GEO-INFER ecosystem"

# Read version from __init__.py
def read_version():
    init_path = os.path.join(os.path.dirname(__file__), 'src', 'geo_infer_examples', '__init__.py')
    try:
        with open(init_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('__version__'):
                    return line.split('=')[1].strip().strip('"\'')
    except FileNotFoundError:
        pass
    return "0.1.0"

setup(
    name="geo-infer-examples",
    version=read_version(),
    author="GEO-INFER Team",
    author_email="info@geo-infer.org",
    description="Comprehensive demonstration framework showcasing cross-module integration for the GEO-INFER ecosystem",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/activeinference/GEO-INFER",
    project_urls={
        "Bug Reports": "https://github.com/activeinference/GEO-INFER/issues",
        "Source": "https://github.com/activeinference/GEO-INFER/tree/main/GEO-INFER-EXAMPLES",
        "Documentation": "https://github.com/activeinference/GEO-INFER/tree/main/GEO-INFER-EXAMPLES/docs",
        "Examples": "https://github.com/activeinference/GEO-INFER/tree/main/GEO-INFER-EXAMPLES/examples",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Education",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: GIS",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Education",
        "Topic :: Documentation",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords=[
        "geospatial", "examples", "demonstrations", "tutorials", "integration",
        "gis", "spatial analysis", "active inference", "machine learning",
        "agriculture", "health", "urban planning", "climate", "education"
    ],
    python_requires=">=3.9",
    
    # Minimal core dependencies - most functionality comes from other GEO-INFER modules
    install_requires=[
        "pyyaml>=6.0",           # Configuration management
        "requests>=2.28.0",      # API interactions
        "rich>=12.0.0",          # Beautiful console output for examples
        "typer>=0.7.0",          # CLI for running examples
        "jupyterlab>=3.4.0",     # Interactive notebook examples
        "matplotlib>=3.5.0",     # Basic plotting for demonstrations
        "pandas>=1.4.0",         # Data manipulation for examples
    ],
    
    # Optional dependencies organized by example categories
    extras_require={
        # Development and testing
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=0.991",
            "pre-commit>=2.20.0",
        ],
        
        # Documentation generation
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
            "myst-parser>=0.18.0",
            "sphinx-autodoc-typehints>=1.19.0",
        ],
        
        # Health integration examples
        "health": [
            "scikit-learn>=1.1.0",
            "scipy>=1.9.0",
            "networkx>=2.8",
        ],
        
        # Agriculture examples
        "agriculture": [
            "rasterio>=1.3.0",
            "shapely>=1.8.0",
            "folium>=0.12.0",
        ],
        
        # Urban planning examples
        "urban": [
            "geopandas>=0.11.0",
            "contextily>=1.2.0",
            "plotly>=5.10.0",
        ],
        
        # Climate and environmental examples
        "climate": [
            "xarray>=2022.6.0",
            "netcdf4>=1.6.0",
            "cartopy>=0.21.0",
        ],
        
        # Research and advanced analytics
        "research": [
            "sympy>=1.11.0",
            "networkx>=2.8",
            "seaborn>=0.11.0",
        ],
        
        # All optional dependencies
        "all": [
            "scikit-learn>=1.1.0", "scipy>=1.9.0", "networkx>=2.8",
            "rasterio>=1.3.0", "shapely>=1.8.0", "folium>=0.12.0",
            "geopandas>=0.11.0", "contextily>=1.2.0", "plotly>=5.10.0",
            "xarray>=2022.6.0", "netcdf4>=1.6.0", "cartopy>=0.21.0",
            "sympy>=1.11.0", "seaborn>=0.11.0",
        ],
    },
    
    # Entry points for CLI tools
    entry_points={
        "console_scripts": [
            "geo-examples=geo_infer_examples.cli:main",
            "geo-validate=geo_infer_examples.cli:validate_environment",
            "geo-discover=geo_infer_examples.cli:discover_examples",
        ],
    },
    
    # Include additional files
    include_package_data=True,
    package_data={
        "geo_infer_examples": [
            "config/*.yaml",
            "templates/*.md",
            "templates/*.py",
            "templates/notebooks/*.ipynb",
        ],
    },
    
    # Zip safety
    zip_safe=False,
    
    # Additional metadata for PyPI
    license="MIT",
    platforms=["any"],
    
    # Long description for PyPI
    project_description="""
    GEO-INFER-EXAMPLES is the comprehensive demonstration framework for the GEO-INFER 
    geospatial inference ecosystem. It serves as the primary entry point for users to 
    explore and understand how multiple GEO-INFER modules work together to solve 
    real-world geospatial problems.
    
    Key Features:
    - Cross-module integration examples across health, agriculture, urban planning, 
      climate, and research domains
    - Comprehensive documentation and step-by-step tutorials
    - Interactive Jupyter notebooks for hands-on learning
    - Standardized example structure and best practices
    - Minimal utilities focused on orchestration, not novel functionality
    
    This module demonstrates the synergistic power of combining GEO-INFER modules 
    and provides clear learning pathways for users of all experience levels.
    """,
) 