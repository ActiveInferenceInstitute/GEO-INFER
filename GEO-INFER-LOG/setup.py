from setuptools import setup, find_packages

setup(
    name="geo_infer_log",
    version="0.1.0",
    description="Geospatial intelligence for logistics optimization, supply chain management, route optimization, and transportation planning",
    author="GEO-INFER Team",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "pandas>=1.3.0",
        "geopandas>=0.10.0",
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

