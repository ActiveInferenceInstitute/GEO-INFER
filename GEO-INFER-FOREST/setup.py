from setuptools import setup, find_packages

setup(
    name="geo_infer_forest",
    version="0.1.0",
    description="Forest management, carbon sequestration, wildfire risk, and forest ecosystem analysis",
    author="GEO-INFER Team",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "numpy>=1.20.0",
        "pandas>=1.3.0",
        "scipy>=1.7.0",
        "matplotlib>=3.4.0",
        "xarray>=0.19.0",
        "pyyaml>=6.0",
        "scikit-learn>=1.0.0",
    ],
    python_requires=">=3.11",
)

