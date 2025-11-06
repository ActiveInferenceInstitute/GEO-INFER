from setuptools import setup, find_packages

setup(
    name="geo_infer_sim",
    version="0.1.0",
    description="Advanced simulation environments for geospatial hypothesis testing, policy evaluation, and scenario analysis using agent-based modeling and system dynamics",
    author="GEO-INFER Team",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "numpy>=1.20.0",
        "pandas>=1.3.0",
        "scipy>=1.7.0",
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

