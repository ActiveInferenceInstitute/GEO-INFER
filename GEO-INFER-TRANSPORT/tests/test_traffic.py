"""Tests for traffic analysis module."""

import pytest
from geo_infer_transport.core.traffic import TrafficAnalyzer


class TestTrafficAnalyzerInit:
    """Tests for TrafficAnalyzer initialization."""

    def test_import(self) -> None:
        assert TrafficAnalyzer is not None

    def test_initialization(self) -> None:
        analyzer = TrafficAnalyzer()
        assert analyzer is not None
