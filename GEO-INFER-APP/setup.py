"""Compatibility shim.

All package metadata lives in pyproject.toml; this shim exists so that
legacy setuptools entry points (``python setup.py``) keep working.
"""

from setuptools import setup

setup()