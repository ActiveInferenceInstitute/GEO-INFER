"""
API module for OSC-GEO.

This module provides programmatic interfaces for interacting with OSC-GEO functionality.
"""

from .rest import router as rest_router

__all__ = ["rest_router"] 