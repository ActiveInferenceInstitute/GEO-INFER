from setuptools import setup, find_packages

setup(
    name="geo_infer_bayes",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "numpy",
        "scipy",
        "pandas",
        "matplotlib",
        "pymc",
        "arviz",
        "cmdstanpy",
        "tensorflow-probability",
        "xarray",
        "geopandas",
        "rasterio",
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest-cov",
            "black",
            "flake8",
            "mypy",
        ],
    },
    description="Bayesian inference for geospatial applications",
    author="GEO-INFER Team",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
) 