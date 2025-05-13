"""Setup script for GEO-INFER-INTRA package."""

from setuptools import setup, find_packages

# Read version from package __init__.py
with open("src/geo_infer_intra/__init__.py", "r") as f:
    for line in f:
        if line.startswith("__version__"):
            version = line.split("=")[1].strip().strip('"').strip("'")
            break
    else:
        version = "0.1.0"

# Read README for long description
with open("GEO-INFER-INTRA-README.md", "r") as f:
    long_description = f.read()

setup(
    name="geo-infer-intra",
    version=version,
    description="Knowledge management backbone for the GEO-INFER framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="GEO-INFER Team",
    author_email="info@geo-infer.org",
    url="https://github.com/geo-infer/geo-infer-intra",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    include_package_data=True,
    python_requires=">=3.9",
    install_requires=[
        "fastapi>=0.95.0",
        "pydantic>=2.0.0",
        "sqlalchemy>=2.0.0",
        "elasticsearch>=8.0.0",
        "rdflib>=6.0.0",
        "mkdocs>=1.4.0",
        "celery>=5.2.0",
        "pyyaml>=6.0",
        "jsonschema>=4.0.0",
        "typer>=0.7.0",
        "rich>=12.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.0.0",
            "mypy>=1.0.0",
            "flake8>=6.0.0",
            "sphinx>=6.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "geo-infer-intra=geo_infer_intra.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: GIS",
    ],
) 