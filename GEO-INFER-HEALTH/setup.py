"""
Setup script for GEO-INFER-HEALTH module.

GEO-INFER-HEALTH provides geospatial applications for public health,
epidemiology, and healthcare accessibility analysis within the GEO-INFER framework.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

# Read requirements
def read_requirements(filename):
    """Read requirements from file."""
    with open(filename, 'r') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="geo-infer-health",
    version="1.0.0",
    author="GEO-INFER Framework Team",
    author_email="health@geo-infer.org",
    description="Geospatial Applications for Public Health, Epidemiology, and Healthcare Accessibility",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/geo-infer/geo-infer-health",
    project_urls={
        "Documentation": "https://geo-infer.readthedocs.io/",
        "Source": "https://github.com/geo-infer/geo-infer-health",
        "Tracker": "https://github.com/geo-infer/geo-infer-health/issues",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Healthcare Industry",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Creative Commons Attribution-NoDerivatives-ShareAlike 4.0 International",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: GIS",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    keywords=[
        "geospatial",
        "health",
        "epidemiology",
        "public-health",
        "healthcare-accessibility",
        "disease-surveillance",
        "spatial-epidemiology",
        "environmental-health",
        "active-inference",
        "gis",
        "spatial-analysis"
    ],
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
    install_requires=read_requirements("requirements.txt"),
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "black>=23.12.0",
            "isort>=5.13.0",
            "flake8>=6.1.0",
            "mypy>=1.7.0",
            "pre-commit>=3.6.0",
        ],
        "gpu": [
            "cupy>=13.0.0",
            "tensorflow-gpu>=2.15.0",
        ],
        "database": [
            "sqlalchemy>=2.0.0",
            "psycopg2-binary>=2.9.0",
            "redis>=5.0.0",
        ],
        "docs": [
            "sphinx>=7.2.0",
            "sphinx-rtd-theme>=1.3.0",
            "myst-parser>=2.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "geo-infer-health=geo_infer_health.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "geo_infer_health": [
            "config/*.yaml",
            "config/*.json",
            "docs/*.md",
            "examples/*.py",
        ],
    },
    data_files=[
        ("config", ["config/health_config.yaml", "config/data_sources.yaml"]),
    ],
    zip_safe=False,
)
