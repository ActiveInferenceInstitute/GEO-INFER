from setuptools import setup, find_packages

setup(
    name="geo_infer_ai",
    version="0.1.0",
    description="Advanced machine learning and artificial intelligence capabilities specifically designed for geospatial analysis and decision-making",
    author="GEO-INFER Team",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "numpy>=1.20.0",
        "pandas>=1.3.0",
        "torch>=1.9.0",
        "tensorflow>=2.6.0",
        "scikit-learn>=1.0.0",
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

