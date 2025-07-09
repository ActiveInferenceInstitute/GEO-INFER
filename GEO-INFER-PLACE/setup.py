#!/usr/bin/env python3
"""
Setup script for GEO-INFER-PLACE: Deep Place-Based Geospatial Analysis Framework

This module provides comprehensive, location-specific geospatial analysis capabilities
within the GEO-INFER framework.
"""

from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    """Read README file for long description."""
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Deep place-based geospatial analysis framework"

# Define version
__version__ = "0.1.0"

# Core dependencies required for the framework
CORE_REQUIREMENTS = [
    # Geospatial and scientific computing
    "numpy>=1.21.0",
    "pandas>=1.3.0",
    "geopandas>=0.10.0",
    "shapely>=1.8.0",
    "rasterio>=1.2.0",
    "xarray>=0.19.0",
    "dask>=2021.9.0",
    
    # Spatial analysis and indexing
    "h3>=3.7.0",
    "pyproj>=3.2.0",
    "rtree>=0.9.0",
    
    # Time series and temporal analysis
    "cftime>=1.5.0",
    "netCDF4>=1.5.7",
    
    # Data access and APIs
    "requests>=2.26.0",
    "urllib3>=1.26.0",
    
    # Configuration and serialization
    "pyyaml>=5.4.0",
    "toml>=0.10.0",
    "jsonschema>=3.2.0",
    
    # Visualization and plotting
    "matplotlib>=3.4.0",
    "seaborn>=0.11.0",
    "plotly>=5.3.0",
    "folium>=0.12.0",
    
    # Utilities
    "click>=8.0.0",
    "tqdm>=4.62.0",
    "python-dateutil>=2.8.0",
    "pytz>=2021.1",
]

# Optional dependencies for enhanced functionality
OPTIONAL_REQUIREMENTS = {
    "ai": [
        "scikit-learn>=1.0.0",
        "tensorflow>=2.6.0",
        "torch>=1.9.0",
        "xgboost>=1.4.0",
    ],
    "bayesian": [
        "pymc>=4.0.0",
        "arviz>=0.11.0",
        "stan>=3.3.0",
    ],
    "simulation": [
        "mesa>=0.8.9",
        "networkx>=2.6.0",
        "scipy>=1.7.0",
    ],
    "bio": [
        "biopython>=1.79",
        "scikit-bio>=0.5.6",
    ],
    "health": [
        "lifelines>=0.26.0",
        "epidemics>=0.1.0",
    ],
    "climate": [
        "climtas>=0.4.0",
        "cf-units>=3.0.0",
        "cdo>=1.5.0",
    ],
    "performance": [
        "numba>=0.54.0",
        "cupy>=9.4.0",  # GPU acceleration
        "dask[complete]>=2021.9.0",
    ],
    "quality": [
        "pytest>=6.2.0",
        "pytest-cov>=2.12.0",
        "black>=21.9.0",
        "flake8>=3.9.0",
        "mypy>=0.910",
    ],
    "docs": [
        "sphinx>=4.2.0",
        "sphinx-rtd-theme>=1.0.0",
        "nbsphinx>=0.8.0",
    ],
}

# Location-specific dependencies
LOCATION_REQUIREMENTS = {
    "del_norte_county": [
        "calfire-api>=0.1.0",  # Custom package for CalFire data
        "usgs-water>=0.3.0",   # USGS water data access
        "noaa-coops>=1.1.0",   # NOAA CO-OPS tide data
    ],
    "australia": [
        "bom-data>=0.2.0",     # Bureau of Meteorology data access
        "ala-python>=0.1.0",   # Atlas of Living Australia
        "austopo>=0.1.0",      # Australian topographic data
    ],
    "siberia": [
        "roshydromet>=0.1.0",  # Russian meteorological data
        "arctic-data>=0.2.0",  # Arctic research data access
        "permafrost>=0.1.0",   # Permafrost monitoring tools
    ],
}

# All optional dependencies combined
ALL_OPTIONAL = []
for deps in OPTIONAL_REQUIREMENTS.values():
    ALL_OPTIONAL.extend(deps)
for deps in LOCATION_REQUIREMENTS.values():
    ALL_OPTIONAL.extend(deps)

OPTIONAL_REQUIREMENTS["all"] = ALL_OPTIONAL

setup(
    name="geo-infer-place",
    version=__version__,
    author="GEO-INFER Team",
    author_email="place@geo-infer.org",
    description="Deep place-based geospatial analysis framework",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/activeinference/GEO-INFER",
    project_urls={
        "Documentation": "https://geo-infer-place.readthedocs.io/",
        "Source": "https://github.com/activeinference/GEO-INFER/tree/main/GEO-INFER-PLACE",
        "Tracker": "https://github.com/activeinference/GEO-INFER/issues",
        "Community": "https://discord.activeinference.institute/",
    },
    
    # Package configuration
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    
    # Python version requirement
    python_requires=">=3.9",
    
    # Dependencies
    install_requires=CORE_REQUIREMENTS,
    extras_require=OPTIONAL_REQUIREMENTS,
    
    # Package metadata
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Creative Commons License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: GIS",
        "Topic :: Scientific/Engineering :: Atmospheric Science",
        "Topic :: Scientific/Engineering :: Hydrology",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    
    # Keywords for discovery
    keywords=[
        "geospatial", "place-based", "active-inference", "climate", 
        "ecosystems", "arctic", "permafrost", "biodiversity", 
        "forest-management", "coastal-resilience", "gis", "remote-sensing"
    ],
    
    # Entry points for command-line tools
    entry_points={
        "console_scripts": [
            "geo-place=geo_infer_place.cli:main",
            "geo-place-del-norte=geo_infer_place.locations.del_norte_county.cli:main",
            "geo-place-australia=geo_infer_place.locations.australia.cli:main",
            "geo-place-siberia=geo_infer_place.locations.siberia.cli:main",
        ],
        "geo_infer.modules": [
            "place=geo_infer_place",
        ],
    },
    
    # Data files to include
    package_data={
        "geo_infer_place": [
            "config/*.yaml",
            "config/*.json",
            "data/*.json",
            "data/*.geojson",
            "templates/*.html",
            "templates/*.jinja2",
        ],
    },
    
    # Additional files to include in source distribution
    data_files=[
        ("config", ["config/module_config.yaml"]),
    ],
    
    # Testing configuration
    test_suite="tests",
    tests_require=OPTIONAL_REQUIREMENTS["quality"],
    
    # Zip safe configuration
    zip_safe=False,
)

# Post-installation message
def print_post_install_message():
    """Print helpful information after installation."""
    print("\n" + "="*60)
    print("🌍 GEO-INFER-PLACE Installation Complete!")
    print("="*60)
    print("\nAvailable study locations:")
    print("  🌲 Del Norte County, California, USA")
    print("  🦘 Australia (continental analysis)")
    print("  ❄️  Siberia, Russia (Arctic/sub-Arctic)")
    print("\nQuick start:")
    print("  >>> from geo_infer_place import PlaceAnalyzer")
    print("  >>> analyzer = PlaceAnalyzer()")
    print("  >>> locations = analyzer.get_available_locations()")
    print("\nFor location-specific analysis:")
    print("  >>> from geo_infer_place import DelNorteCounty, Australia, Siberia")
    print("\nDocumentation: https://geo-infer-place.readthedocs.io/")
    print("Community: https://discord.activeinference.institute/")
    print("="*60 + "\n")

if __name__ == "__main__":
    print_post_install_message() 