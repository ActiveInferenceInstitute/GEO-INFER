"""
Setup configuration for GEO-INFER-DATA.

This module provides comprehensive geospatial data management, ETL pipelines,
and storage optimization for the GEO-INFER framework.
"""

from setuptools import setup, find_packages
import os
from pathlib import Path

# Read README for long description
readme_path = Path(__file__).parent / "README.md"
long_description = ""
if readme_path.exists():
    with open(readme_path, 'r', encoding='utf-8') as f:
        long_description = f.read()

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_path.exists():
    with open(requirements_path, 'r') as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

# Package configuration
setup(
    name="geo-infer-data",
    version="1.0.0",
    author="GEO-INFER Development Team",
    author_email="data@geo-infer.org",
    description="Comprehensive geospatial data management, ETL, and storage optimization",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/GEO-INFER/GEO-INFER-DATA",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Creative Commons Attribution-NoDerivatives-ShareAlike 4.0 International License (CC BY-ND-SA 4.0)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: GIS",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Framework :: AsyncIO",
        "Framework :: FastAPI",
    ],
    keywords=[
        "geospatial", "data-management", "etl", "storage", "gis",
        "spatial-analysis", "data-quality", "active-inference",
        "environmental-monitoring", "urban-planning", "climate-data"
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "pre-commit>=3.0.0",
        ],
        "postgres": [
            "psycopg2-binary>=2.9.0",
            "geoalchemy2>=0.13.0",
        ],
        "h3": [
            "h3>=3.7.0",
        ],
        "spatial": [
            "rtree>=1.0.0",
            "shapely>=2.0.0",
            "geopandas>=0.13.0",
            "rasterio>=1.3.0",
            "fiona>=1.9.0",
        ],
        "timeseries": [
            "timescale-db>=0.1.0",
        ],
        "redis": [
            "redis>=4.5.0",
        ],
        "minio": [
            "minio>=7.1.0",
        ],
        "airflow": [
            "apache-airflow>=2.7.0",
        ],
        "all": [
            "psycopg2-binary>=2.9.0",
            "h3>=3.7.0",
            "rtree>=1.0.0",
            "timescale-db>=0.1.0",
            "redis>=4.5.0",
            "minio>=7.1.0",
            "apache-airflow>=2.7.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "geo-infer-data=geo_infer_data.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "geo_infer_data": [
            "config/*.yaml",
            "docs/*.yaml",
            "examples/*.py",
            "tests/fixtures/*",
        ],
    },
    zip_safe=False,
    project_urls={
        "Documentation": "https://geo-infer.org/modules/data/",
        "Source": "https://github.com/GEO-INFER/GEO-INFER-DATA",
        "Tracker": "https://github.com/GEO-INFER/GEO-INFER-DATA/issues",
        "Framework": "https://geo-infer.org/",
    },
)
