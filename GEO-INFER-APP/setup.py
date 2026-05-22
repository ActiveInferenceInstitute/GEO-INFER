from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="geo-infer-app",
    version="0.1.0",
    author="GEO-INFER Development Team",
    author_email="geo-infer@activeinference.institute",
    description="User interfaces, accessibility tools, and application development for GEO-INFER",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/geo-infer/geo-infer",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Creative Commons License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: GIS",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    python_requires=">=3.11",
    install_requires=[
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "pydantic>=1.8.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.2.0",
            "pytest-cov>=2.12.0",
            "pytest-asyncio>=0.20.0",
            "black>=21.9.0",
            "flake8>=3.9.0",
            "mypy>=0.910",
            "isort>=5.9.0",
        ],
    },
)
