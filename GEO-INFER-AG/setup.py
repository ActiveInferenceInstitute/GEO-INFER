from setuptools import setup, find_packages

setup(
    name="geo_infer_ag",
    version="0.1.0",
    description="Advanced agricultural analysis and precision farming applications using geospatial intelligence and active inference principles",
    author="GEO-INFER Team",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "numpy>=1.20.0",
        "pandas>=1.3.0",
        "geopandas>=0.10.0",
        "shapely>=1.8.0",
        "scikit-learn>=1.0.0",
        "rasterio>=1.2.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.2.0",
            "pytest-cov>=2.12.0",
            "black>=21.9.0",
            "isort>=5.9.0",
            "flake8>=3.9.0",
        ],
    },
    python_requires=">=3.9",
)

