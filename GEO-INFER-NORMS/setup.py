"""
Setup script for the GEO-INFER-NORMS package.
"""

from setuptools import setup, find_packages

setup(
    name="geo-infer-norms",
    version="0.1.0",
    description="Social-technical compliance modeling with deterministic and probabilistic aspects within the GEO-INFER framework",
    author="GEO-INFER Development Team",
    author_email="blanket@activeinference.institute",
    url="https://github.com/activeinferenceinstitute/geo-infer/geo-infer-norms",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.20.0",
        "pandas>=1.3.0",
        "geopandas>=0.10.0",
        "shapely>=1.8.0",
        "matplotlib>=3.4.0",
        "networkx>=2.6.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.12.0",
            "black>=21.5b2",
            "flake8>=3.9.0",
            "mypy>=0.812",
        ],
        "docs": [
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=0.5.2",
            "nbsphinx>=0.8.0",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering :: GIS",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
) 