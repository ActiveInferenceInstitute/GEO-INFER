from setuptools import setup, find_packages

setup(
    name="geo_infer_act",
    version="0.1.0",
    description="Active Inference modeling module for the GEO-INFER framework",
    author="GEO-INFER Team",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "numpy>=1.20.0",
        "scipy>=1.7.0",
        "pandas>=1.3.0",
        "matplotlib>=3.4.0",
        "torch>=1.9.0",
        "pyro-ppl>=1.7.0",
        "networkx>=2.6.0",
        "pyyaml>=6.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.12.0",
            "black>=21.5b2",
            "isort>=5.9.0",
            "flake8>=3.9.0",
        ],
    },
    python_requires=">=3.8",
) 