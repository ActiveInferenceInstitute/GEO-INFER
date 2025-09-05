#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from setuptools import setup, find_packages, Command
from setuptools.command.build_py import build_py
from setuptools.command.install import install
from setuptools.command.develop import develop
import os

# Ensure the src directory is on the Python path for importing repo_management
sys.path.insert(0, os.path.abspath("src"))

# Custom Commands
class SetupOSCReposCommand(Command):
    """
    Custom setuptools command to clone, set up, and install dependencies for OSC repositories.
    """
    description = "Clone and set up OS-Climate repositories"
    user_options = [
        ('repo=', 'r', 'Specify a single repository to process (e.g., osc-geo-h3loader-cli)'),
        ('force-clone', 'f', 'Force re-clone repositories if they already exist'),
        ('verbose', 'v', 'Enable verbose output'),
    ]

    def initialize_options(self):
        self.repo = None
        self.force_clone = False
        self.verbose = False

    def finalize_options(self):
        pass # No super call, as we are inheriting from Command

    def run(self):
        print("\nRunning custom command: setup_osc_repos")
        from geo_infer_space.osc_geo.utils.repo_management import RepoManager
        manager = RepoManager(force_clone=self.force_clone, verbose=self.verbose)
        manager.run_all(target_repo=self.repo)

class TestOSCReposCommand(Command):
    """
    Custom setuptools command to run tests for OSC repositories.
    """
    description = "Run tests for OS-Climate repositories"
    user_options = [
        ('repo=', 'r', 'Specify a single repository to test (e.g., osc-geo-h3loader-cli)'),
        ('verbose', 'v', 'Enable verbose output'),
    ]

    def initialize_options(self):
        self.repo = None
        self.verbose = False

    def finalize_options(self):
        pass # No super call, as we are inheriting from Command

    def run(self):
        print("\nRunning custom command: test_osc_repos")
        from geo_infer_space.osc_geo.utils.repo_management import RepoManager
        manager = RepoManager(verbose=self.verbose)
        
        repos_to_test = [self.repo] if self.repo else manager.osc_repos.keys()
        overall_success = True
        for repo in repos_to_test:
            if not manager.run_repo_tests(repo_name=repo):
                overall_success = False
        
        if not overall_success:
            sys.exit(1)


setup(
    name="geo-infer-space",
    version="0.1.0",
    description="Advanced spatial methods for the GEO-INFER framework with OS-Climate forks",
    author="GEO-INFER Team",
    author_email="info@geo-infer.org",
    url="https://github.com/geo-infer/geo-infer-space",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    cmdclass={
        'setup_osc_repos': SetupOSCReposCommand,
        'test_osc_repos': TestOSCReposCommand,
    },
    entry_points={
        'console_scripts': [
            'gis-verify-h3-v4=geo_infer_space.tools.verify_h3_v4_compliance:main',
            'gis-fix-h3-v4=geo_infer_space.tools.fix_h3_v4_api:main',
            'gis-fix-h3-calls=geo_infer_space.tools.fix_h3_calls:main',
            'gis-fix-double-h3=geo_infer_space.tools.fix_double_h3:main',
            'gis-fix-imports=geo_infer_space.tools.fix_imports:main',
            'gis-fix-rel-imports=geo_infer_space.tools.fix_relative_imports:main',
            'gis-h3-tests=geo_infer_space.tools.run_h3_tests_simple:main',
        ]
    },
    # scripts=[
    #     "bin/osc_status",
    # ],
    install_requires=[
        # Core geospatial dependencies
        "numpy>=1.20.0,<2.0",
        "pandas>=1.3.0",
        "geopandas>=0.10.0",
        "shapely>=1.8.0",
        "h3>=4.0.0",
        "pyproj>=3.3.0",
        "rasterio>=1.3.0",
        "fiona>=1.8.0",
        
        # Spatial analysis dependencies
        "scipy>=1.7.0",
        "scikit-learn>=1.0.0",
        "networkx>=2.6.0",
        
        # API dependencies
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "python-multipart>=0.0.5",
        "pydantic>=1.8.0",
        "geojson-pydantic>=0.4.0",
        
        # Data validation and serialization
        "pyyaml>=6.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.2.5",
            "pytest-cov>=2.12.1",
            "pytest-asyncio>=0.18.0",
            "black>=23.3.0",
            "flake8>=6.0.0",
            "isort>=5.12.0",
            "mypy>=1.0.0",
        ],
        "optional": [
            # Point cloud processing
            "laspy>=2.0.0",
            
            # Network analysis enhancement
            "osmnx>=1.2.0",
            
            # Raster processing enhancements
            "xarray>=0.20.0",
            "rioxarray>=0.11.0",
            
            # Performance optimization
            "numba>=0.56.0",
            "dask>=2021.10.0",
            "dask[dataframe]>=2021.10.0",
            
            # Caching
            "redis>=4.0.0",
        ],
        "viz": [
            "matplotlib>=3.5.0",
            "seaborn>=0.11.0",
            "plotly>=5.0.0",
            "folium>=0.12.0",
        ],
        "docs": [
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
        "all": [
            # Include all optional dependencies
            "laspy>=2.0.0",
            "osmnx>=1.2.0",
            "xarray>=0.20.0",
            "rioxarray>=0.11.0",
            "numba>=0.56.0",
            "dask>=2021.10.0",
            "dask[dataframe]>=2021.10.0",
            "redis>=4.0.0",
            "matplotlib>=3.5.0",
            "seaborn>=0.11.0",
            "plotly>=5.0.0",
            "folium>=0.12.0",
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering :: GIS",
    ],
    keywords="geospatial, h3, active inference, geoinformatics",
    python_requires=">=3.9",
) 