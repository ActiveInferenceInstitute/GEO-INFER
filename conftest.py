"""
Root conftest.py for the GEO-INFER ecosystem.

Registers ecosystem-wide markers so modules with custom markers
don't trigger PytestUnknownMarkWarning during collection.
"""

import pytest


def pytest_configure(config):
    """Register ecosystem-wide markers."""
    config.addinivalue_line("markers", "module: auto-applied module marker")
