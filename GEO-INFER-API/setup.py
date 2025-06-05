"""
Setup script for the GEO-INFER-API package.
"""
from setuptools import setup, find_packages

# Read version from the package
with open("src/geo_infer_api/__init__.py", "r") as f:
    for line in f:
        if line.startswith("__version__"):
            version = line.split("=")[1].strip().strip('"\'')
            break
    else:
        version = "0.1.0"

# Read requirements
with open("requirements.txt", "r") as f:
    requirements = [line.strip() for line in f if line.strip()]

# Read long description
with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="geo_infer_api",
    version=version,
    description="Standardized API for geospatial interoperability within the GEO-INFER framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="GEO-INFER Team",
    author_email="info@geo-infer.org",
    url="https://github.com/activeinference/GEO-INFER",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.9",
    install_requires=requirements,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Creative Commons Attribution-NoDerivatives-ShareAlike 4.0 International License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering :: GIS",
    ],
    entry_points={
        "console_scripts": [
            "geo-infer-api=geo_infer_api.app:main",
        ],
    },
) 