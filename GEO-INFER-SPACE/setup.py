#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name="geo-infer-space",
    version="0.1.0",
    description="Advanced spatial methods for the GEO-INFER framework",
    author="GEO-INFER Team",
    author_email="info@geo-infer.org",
    url="https://github.com/geo-infer/geo-infer-space",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    scripts=[
        "bin/osc_status",
    ],
    install_requires=[
        "numpy>=1.20.0",
        "pandas>=1.3.0",
        "geopandas>=0.10.0",
        "shapely>=1.8.0",
        "h3>=3.7.0",
        "pyproj>=3.3.0",
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "python-multipart>=0.0.5",
    ],
    extras_require={
        "dev": [
            "pytest>=6.2.5",
            "pytest-cov>=2.12.1",
            "black>=23.3.0",
            "flake8>=6.0.0",
            "isort>=5.12.0",
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