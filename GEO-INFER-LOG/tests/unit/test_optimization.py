"""Tests for optimization utilities."""

import numpy as np
import pytest
from geo_infer_log.utils.geo import haversine_distance


class TestOptimizationUtils:
    """Tests for optimization utility functions."""

    def test_haversine_distance_same_point(self) -> None:
        d = haversine_distance((-74.0, 40.0), (-74.0, 40.0))
        assert abs(d) < 0.01

    def test_haversine_distance_positive(self) -> None:
        d = haversine_distance((-74.0, 40.0), (-73.0, 41.0))
        assert d > 0

    def test_haversine_distance_symmetric(self) -> None:
        d1 = haversine_distance((-74.0, 40.0), (-73.0, 41.0))
        d2 = haversine_distance((-73.0, 41.0), (-74.0, 40.0))
        assert abs(d1 - d2) < 0.01
