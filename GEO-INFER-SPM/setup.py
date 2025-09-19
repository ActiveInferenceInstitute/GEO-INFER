"""
Setup script for GEO-INFER-SPM package
"""

from setuptools import setup, find_packages
import os

# Read README
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
def read_requirements(filename):
    with open(filename, "r") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

# Basic requirements
install_requires = [
    "numpy>=1.20.0",
    "scipy>=1.7.0",
    "pandas>=1.3.0",
    "geopandas>=0.10.0",
    "xarray>=0.20.0",
    "scikit-learn>=1.0.0",
    "matplotlib>=3.5.0",
    "plotly>=5.0.0",
    "h5py>=3.6.0",
    "rasterio>=1.2.0",
]

# Optional dependencies
extras_require = {
    "dev": [
        "pytest>=7.0.0",
        "pytest-cov>=4.0.0",
        "black>=22.0.0",
        "flake8>=4.0.0",
        "mypy>=0.950",
        "sphinx>=4.0.0",
    ],
    "bayesian": [
        "pymc3>=3.11.0",
        "arviz>=0.12.0",
    ],
    "spatial": [
        "libpysal>=4.6.0",
        "esda>=2.4.0",
        "spreg>=1.2.0",
    ],
    "time_series": [
        "statsmodels>=0.13.0",
        "ruptures>=1.1.0",
    ],
    "full": [
        "pymc3>=3.11.0",
        "libpysal>=4.6.0",
        "statsmodels>=0.13.0",
        "ruptures>=1.1.0",
        "arviz>=0.12.0",
        "esda>=2.4.0",
        "spreg>=1.2.0",
    ]
}

setup(
    name="geo-infer-spm",
    version="1.0.0",
    author="GEO-INFER Framework",
    author_email="info@geo-infer.org",
    description="Statistical Parametric Mapping for Geospatial Analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/geo-infer/geo-infer-spm",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: GIS",
        "Topic :: Scientific/Engineering :: Mathematics",
    ],
    python_requires=">=3.8",
    install_requires=install_requires,
    extras_require=extras_require,
    entry_points={
        "console_scripts": [
            "geo-infer-spm=geo_infer_spm.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
