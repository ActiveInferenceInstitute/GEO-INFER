from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="geo-infer-art",
    version="0.1.0",
    author="GEO-INFER Team",
    author_email="info@geo-infer.org",
    description="Art production and aesthetics with geospatial dimensions for the GEO-INFER framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/activeinference/GEO-INFER",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: Creative Commons License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: GIS",
        "Topic :: Artistic Software",
    ],
    python_requires=">=3.9",
    install_requires=[
        "numpy>=1.21.0",
        "matplotlib>=3.4.0",
        "geopandas>=0.10.0",
        "rasterio>=1.2.0",
        "pillow>=8.3.0",
        "scipy>=1.7.0",
        "colour>=0.1.5",
        "scikit-image>=0.18.0",
        "tensorflow>=2.6.0",
        "opencv-python>=4.5.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.2.5",
            "pytest-cov>=2.12.1",
            "black>=21.6b0",
            "flake8>=3.9.2",
            "isort>=5.9.2",
        ],
    },
) 