"""Integration coverage for emergency sensor fusion and threat assessment."""

from geo_infer_emergency.core.awareness import SituationalAwareness


def test_sensor_fusion_feeds_threat_assessment() -> None:
    """Fuse local sensor input and return a finite, classified threat result."""
    awareness = SituationalAwareness(data_sources=["sensors"], update_interval=1)
    integration = awareness.integrate_sensors(
        {"sensors": [{"id": "s1", "type": "temperature"}]},
        ["temperature"],
    )
    assessment = awareness.assess_threat(
        {"intensity": 0.7, "speed": 10},
        {"region": "test"},
        [{"population": 1000}],
    )

    assert integration["integration_status"] == "active"
    assert assessment["threat_level"]
    assert 0.0 <= assessment["threat_score"] <= 1.0
