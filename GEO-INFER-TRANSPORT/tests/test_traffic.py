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


class TestAnalyzeFlowResolution:
    """Hourly volume must derive from the configured time_resolution."""

    @pytest.mark.parametrize(
        "resolution,expected_multiplier",
        [("15min", 4), ("5min", 12), ("30min", 2), ("1h", 1), ("60s", 60)],
    )
    def test_hourly_volume_uses_resolution(self, resolution, expected_multiplier) -> None:
        analyzer = TrafficAnalyzer(time_resolution=resolution)
        result = analyzer.analyze_flow(
            segment={"id": "seg1", "capacity": 2000, "speed_limit": 50},
            counts=[{"count": 10}],
        )
        assert result.volume == 10 * expected_multiplier

    def test_unsupported_resolution_raises(self) -> None:
        analyzer = TrafficAnalyzer(time_resolution="banana")
        with pytest.raises(ValueError, match="time_resolution"):
            analyzer.analyze_flow(segment={"id": "seg1"}, counts=[{"count": 10}])
