"""
Setup configuration for GEO-INFER-OPS.
"""

from setuptools import setup, find_packages

setup(
    name="geo-infer-ops",
    version="0.1.0",
    description="Operations and infrastructure management for GEO-INFER framework",
    author="GEO-INFER Team",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "fastapi>=0.68.0",
        "pydantic>=1.8.0",
        "pytest>=6.0.0",
        "pytest-cov>=2.12.0",
        "pytest-timeout>=2.0.0",
        "prometheus-client>=0.12.0",
        "prometheus-fastapi-instrumentator>=5.7.0",
        "structlog>=21.1.0",
    ],
    extras_require={
        "dev": [
            "black",
            "flake8",
            "mypy",
            "isort",
        ],
        "test": [
            "pytest",
            "pytest-cov",
            "pytest-timeout",
            "pytest-asyncio",
        ],
    },
) 