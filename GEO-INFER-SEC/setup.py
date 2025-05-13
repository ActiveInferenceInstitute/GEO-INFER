from setuptools import setup, find_packages

setup(
    name="geo_infer_sec",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    description="Security and privacy frameworks for geospatial information within GEO-INFER",
    author="GEO-INFER Team",
    author_email="info@geo-infer.org",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: GIS",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.8",
    install_requires=[
        "cryptography>=36.0.0",
        "pyjwt>=2.3.0",
        "geopandas>=0.10.0",
        "shapely>=1.8.0",
        "pandas>=1.3.0",
        "numpy>=1.20.0",
        "pyyaml>=6.0",
        "h3>=3.7.0",
        "pyproj>=3.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.12.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.910",
        ],
    },
) 