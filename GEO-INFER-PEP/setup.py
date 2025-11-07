from setuptools import setup, find_packages

setup(
    name="geo_infer_pep",
    version="0.1.0",
    description="Comprehensive people operations management including HR, CRM, talent acquisition, performance tracking, and community engagement",
    author="GEO-INFER Development Team",
    author_email="geo-infer@activeinference.institute",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
    install_requires=[
        "fastapi>=0.100.0",
        "uvicorn[standard]>=0.23.2",
        "pydantic>=2.0",
        "pandas>=2.0",
        "matplotlib>=3.7.0",
        "seaborn>=0.13.0",
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
        "docs": [
            "sphinx>=4.2.0",
            "sphinx-rtd-theme>=1.0.0",
            "nbsphinx>=0.8.0",
            "myst-parser>=0.15.0",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.yaml", "*.yml", "*.json", "*.md", "*.txt"],
    },
)


