from setuptools import setup, find_packages

setup(
    name="geo_infer_iot",
    version="0.1.0",
    description="Internet of Things sensors and spatial web integration for the GEO-INFER framework",
    author="GEO-INFER Team",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        # Core dependencies
        "numpy>=1.20.0",
        "pandas>=1.3.0",
        "geopandas>=0.10.0",
        "h3>=3.7.0",
        
        # IoT communication protocols
        "paho-mqtt>=1.6.0",
        "confluent-kafka>=1.8.0",
        "aiocoap>=0.4.3",
        "pyserial>=3.5",
        
        # Spatial and Bayesian dependencies
        "pyproj>=3.3.0",
        "scipy>=1.7.0",
        "scikit-learn>=1.0.0",
        
        # Time series and streaming
        "influxdb-client>=1.24.0",
        "asyncio-mqtt>=0.11.0",
        "websockets>=10.0",
        
        # API and web services
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "pydantic>=1.8.0",
        
        # Configuration and utilities
        "pyyaml>=6.0",
        "python-dotenv>=0.19.0",
        "rich>=12.0.0",
        
        # Visualization
        "matplotlib>=3.5.0",
        "plotly>=5.0.0",
        "folium>=0.12.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.12.0",
            "pytest-asyncio>=0.20.0",
            "black>=21.5b2",
            "isort>=5.9.0",
            "flake8>=3.9.0",
            "mypy>=0.910",
        ],
        "lorawan": [
            "lora>=0.2.0",
            "chirpstack-api>=3.12.0",
        ],
        "satellite": [
            "pyorbital>=1.7.0",
            "sgp4>=2.20",
        ],
        "advanced": [
            "gpytorch>=1.6.0",  # Advanced Gaussian processes
            "pymc>=4.0.0",      # Bayesian modeling
            "arviz>=0.12.0",    # Bayesian analysis
        ],
    },
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: GIS",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: System :: Monitoring",
    ],
) 