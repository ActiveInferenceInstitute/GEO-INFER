from setuptools import setup, find_packages
setup(
    name="geo_infer_energy",
    version="0.1.0",
    description="Energy systems analysis, renewable energy optimization, and grid management",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=["numpy>=1.20.0", "pandas>=1.3.0", "scipy>=1.7.0", "matplotlib>=3.4.0", "xarray>=0.19.0", "pyyaml>=6.0", "scikit-learn>=1.0.0"],
    python_requires=">=3.9",
)
