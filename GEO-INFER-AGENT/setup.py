#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Setup script for GEO-INFER-AGENT.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="geo-infer-agent",
    version="0.1.0",
    author="GEO-INFER Team",
    author_email="contact@geo-infer.org",
    description="Autonomous agent framework for geospatial applications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/geo-infer/geo-infer-agent",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: GIS",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "geo-infer-agent=geo_infer_agent.cli:main",
        ],
    },
) 