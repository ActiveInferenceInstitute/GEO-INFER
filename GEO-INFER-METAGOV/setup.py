"""Setup script for GEO-INFER-METAGOV module."""

from setuptools import setup, find_packages

setup(
    name="geo-infer-metagov",
    version="4.0.0",
    description="Meta-governance and organizational governance methods for GEO-INFER",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="GEO-INFER Development Team",
    license="CC BY-ND-SA 4.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "pyyaml>=6.0",
        "numpy>=1.20",
        "typing_extensions>=4.0",
    ],
    extras_require={
        "dev": ["pytest>=7.0", "black>=22.0", "mypy>=0.950"],
        "docs": ["sphinx>=4.5", "sphinx-rtd-theme>=1.0"],
    },
    keywords=[
        "governance",
        "meta-governance",
        "institutional-design",
        "multi-level-governance",
        "geospatial",
        "collaboration",
    ],
    project_urls={
        "Documentation": "https://github.com/geo-infer/geo-infer/tree/main/GEO-INFER-METAGOV",
        "Source": "https://github.com/geo-infer/geo-infer",
        "Tracker": "https://github.com/geo-infer/geo-infer/issues",
    },
)
