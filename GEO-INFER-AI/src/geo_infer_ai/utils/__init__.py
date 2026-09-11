"""Utility functions for geospatial AI workflows."""

from .rng import SeedLike, resolve_rng

__all__: list[str] = ["SeedLike", "resolve_rng"]
