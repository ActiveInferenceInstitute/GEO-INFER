"""Setup shim for GEO-INFER-INTRA.

All packaging metadata is canonical in pyproject.toml; this shim only
exists to support legacy tooling that invokes ``setup.py`` directly.
"""

from setuptools import setup

setup()
