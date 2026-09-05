"""Tests for situational awareness module."""

import pytest
from geo_infer_emergency.core.awareness import (
    SituationalAwareness,
    ThreatLevel,
    DataSource,
    SensoryInput,
    LayerConfig,
)


class TestAwarenessDataclasses:
    """Tests for awareness dataclass and enum creation."""

    def test_threat_level_values(self) -> None:
        assert ThreatLevel.LOW.value == "low"
        assert ThreatLevel.EXTREME.value == "extreme"
        assert ThreatLevel.CATASTROPHIC.value == "catastrophic"

    def test_data_source_values(self) -> None:
        assert DataSource.SENSOR.value == "sensor"
        assert DataSource.SATELLITE.value == "satellite"
        assert DataSource.WEATHER.value == "weather"

    def test_layer_config_creation(self) -> None:
        layer = LayerConfig(
            layer_id="l1", name="Hazard", source="wms",
        )
        assert layer.visible is True
        assert layer.refresh_rate_seconds == 60


class TestSituationalAwarenessInit:
    """Tests for SituationalAwareness initialization."""

    def test_default_initialization(self) -> None:
        sa = SituationalAwareness()
        assert sa is not None
        assert "sensors" in sa.data_sources
        assert "kalman" in sa.fusion_algorithms
        assert sa.update_interval == 60

    def test_custom_initialization(self) -> None:
        sa = SituationalAwareness(
            data_sources=["satellite"],
            fusion_algorithms=["particle_filter"],
            update_interval=30,
        )
        assert sa.data_sources == ["satellite"]
        assert sa.update_interval == 30

    def test_initial_threat_level(self) -> None:
        sa = SituationalAwareness()
        assert sa.get_current_threat_level() == "low"


class TestSensorIntegration:
    """Tests for sensor integration."""

    def test_integrate_sensors(self) -> None:
        sa = SituationalAwareness()
        result = sa.integrate_sensors(
            sensor_network={
                "sensors": [
                    {"id": "s1", "type": "temperature", "location": {"lat": 34.0, "lon": -118.0},
                     "readings": {"temperature": 45.0}, "confidence": 0.9},
                    {"id": "s2", "type": "wind", "location": {"lat": 34.1, "lon": -118.1},
                     "readings": {"wind_speed": 25.0}},
                ]
            },
            data_types=["temperature", "wind"],
            sampling_rate="continuous",
        )
        assert result["sensor_count"] == 2
        assert result["integration_status"] == "active"
        assert len(result["sensors"]) == 2
        assert result["sensors"][0]["status"] == "connected"


class TestBuildCOP:
    """Tests for common operating picture."""

    def test_build_cop(self) -> None:
        sa = SituationalAwareness()
        cop = sa.build_cop(
            layers=[
                {"id": "l1", "name": "Hazard", "source": "wms", "type": "hazard", "visible": True},
                {"id": "l2", "name": "Resources", "source": "api", "type": "resource"},
            ],
            extent={"min_lat": 33.0, "max_lat": 35.0, "min_lon": -119.0, "max_lon": -117.0},
            symbology={"hazard": {"color": "red"}, "resource": {"color": "blue"}},
            refresh_rate=15,
        )
        assert "cop_id" in cop
        assert cop["status"] == "active"
        assert len(cop["layers"]) == 2
        assert cop["refresh_rate_seconds"] == 15


class TestThreatAssessment:
    """Tests for threat assessment."""

    def test_low_threat(self) -> None:
        sa = SituationalAwareness()
        result = sa.assess_threat(
            hazard={"type": "flood", "intensity": 0.1, "speed": 0},
            affected_area={"area_sq_km": 5},
            assets_at_risk=[{"name": "park", "population": 100}],
        )
        assert result["threat_level"] == "low"
        assert result["threat_score"] < 0.2

    def test_high_threat(self) -> None:
        sa = SituationalAwareness()
        result = sa.assess_threat(
            hazard={"type": "wildfire", "intensity": 0.7, "speed": 30},
            affected_area={"area_sq_km": 100},
            assets_at_risk=[
                {"name": "town", "population": 50000},
                {"name": "hospital", "population": 500, "critical": True},
            ],
        )
        assert result["threat_level"] in ["high", "extreme", "catastrophic"]
        assert result["threat_score"] > 0.4
        assert len(result["recommendations"]) > 0

    def test_catastrophic_threat(self) -> None:
        sa = SituationalAwareness()
        result = sa.assess_threat(
            hazard={"type": "earthquake", "intensity": 0.95, "speed": 100},
            affected_area={"area_sq_km": 500},
            assets_at_risk=[{"name": "city", "population": 500000}],
        )
        assert result["threat_level"] == "catastrophic"
        assert sa.get_current_threat_level() == "catastrophic"


class TestDataFusion:
    """Tests for data fusion."""

    def test_fuse_data(self) -> None:
        sa = SituationalAwareness()
        result = sa.fuse_data(
            sources=[
                {"data": {"temperature": 30.0, "wind_speed": 20.0}, "confidence": 0.9},
                {"data": {"temperature": 32.0, "wind_speed": 22.0}, "confidence": 0.7},
            ],
            fusion_method="weighted_average",
            confidence_weighting=True,
        )
        assert "fused_data" in result
        assert "temperature" in result["fused_data"]
        # Weighted avg: (30*0.9 + 32*0.7) / (0.9+0.7) = 49.4/1.6 = 30.88
        assert 30.0 < result["fused_data"]["temperature"] < 32.0

    def test_fuse_data_confidence_is_mean_and_bounded(self) -> None:
        sa = SituationalAwareness()
        result = sa.fuse_data(
            sources=[
                {"data": {"temperature": 30.0}, "confidence": 0.9},
                {"data": {"temperature": 32.0}, "confidence": 0.7},
            ],
            confidence_weighting=True,
        )
        # Confidence is the mean of contributing source confidences.
        assert result["confidence"] == pytest.approx(0.8)

    def test_fuse_data_confidence_clamped(self) -> None:
        """Out-of-range source confidences cannot push confidence above 1.0."""
        sa = SituationalAwareness()
        result = sa.fuse_data(
            sources=[
                {"data": {"wind_speed": 20.0}, "confidence": 5.0},
                {"data": {"wind_speed": 22.0}, "confidence": 2.0},
            ],
            confidence_weighting=True,
        )
        assert result["confidence"] == pytest.approx(1.0)

    def test_fuse_empty_sources(self) -> None:
        sa = SituationalAwareness()
        result = sa.fuse_data(sources=[])
        assert "error" in result


class TestDashboard:
    """Tests for dashboard generation."""

    def test_generate_dashboard(self) -> None:
        sa = SituationalAwareness()
        dashboard = sa.generate_dashboard(
            widgets=[
                {"id": "w1", "type": "map", "title": "Incident Map", "data_source": "cop"},
                {"id": "w2", "type": "chart", "title": "Resources", "data_source": "resources"},
            ],
            layout="standard",
            update_frequency=15,
        )
        assert "dashboard_id" in dashboard
        assert dashboard["status"] == "active"
        assert len(dashboard["widgets"]) == 2
        assert dashboard["update_frequency_seconds"] == 15
