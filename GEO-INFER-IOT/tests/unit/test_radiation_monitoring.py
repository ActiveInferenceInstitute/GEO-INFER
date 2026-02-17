"""Tests for the RadiationMonitoringSystem."""
import pytest
import asyncio

from geo_infer_iot.core.ingestion import RadiationMonitoringSystem


@pytest.fixture
def rad_config():
    return {
        "simulation": {
            "sensor_count": 20,
            "background_radiation": 0.1,
            "noise_level": 0.02,
            "anomalies": {"locations": [{"lat": 37.0, "lon": 140.0, "intensity": 50.0}]},
        },
        "quality_control": {
            "sensor_validation": {
                "min_radiation": 0.0,
                "max_radiation": 100.0,
            }
        },
        "anomaly_detection": {
            "statistical": {"threshold_mild": 2.0}
        },
        "spatial": {"h3_resolution": 5},
        "bayesian_inference": {
            "covariance": {"function": "matern_52", "length_scale": 50000, "noise_variance": 0.01},
            "confidence_levels": [0.68, 0.95],
        },
    }


class TestRadiationMonitoringSystem:
    def test_init(self, rad_config):
        system = RadiationMonitoringSystem(rad_config)
        assert system.metrics["measurements_processed"] == 0

    def test_generate_simulated_data(self, rad_config):
        system = RadiationMonitoringSystem(rad_config)
        data = system.generate_simulated_data(sensor_count=10)
        assert len(data) == 10
        for m in data:
            assert "sensor_id" in m
            assert "latitude" in m
            assert "longitude" in m
            assert "value" in m

    def test_quality_control_valid(self, rad_config):
        system = RadiationMonitoringSystem(rad_config)
        from geo_infer_iot.core.ingestion import SensorMeasurement
        from datetime import datetime, timezone

        m = SensorMeasurement(
            sensor_id="s-001",
            timestamp=datetime.now(timezone.utc),
            variable="gamma_radiation",
            value=0.1,
            unit="uSv/h",
            latitude=37.7,
            longitude=-122.4,
        )
        result = system._quality_control(m)
        assert result["passed"] is True

    def test_quality_control_out_of_range(self, rad_config):
        system = RadiationMonitoringSystem(rad_config)
        from geo_infer_iot.core.ingestion import SensorMeasurement
        from datetime import datetime, timezone

        m = SensorMeasurement(
            sensor_id="s-001",
            timestamp=datetime.now(timezone.utc),
            variable="gamma_radiation",
            value=150.0,  # Above max_radiation=100
            unit="uSv/h",
            latitude=37.7,
            longitude=-122.4,
        )
        result = system._quality_control(m)
        assert result["passed"] is False

    def test_anomaly_detection(self, rad_config):
        system = RadiationMonitoringSystem(rad_config)
        from geo_infer_iot.core.ingestion import SensorMeasurement
        from datetime import datetime, timezone

        normal = SensorMeasurement(
            sensor_id="s-001",
            timestamp=datetime.now(timezone.utc),
            variable="gamma_radiation",
            value=0.1,  # Normal background
            unit="uSv/h",
            latitude=37.7,
            longitude=-122.4,
        )
        assert system._is_anomaly(normal) is False

        anomalous = SensorMeasurement(
            sensor_id="s-002",
            timestamp=datetime.now(timezone.utc),
            variable="gamma_radiation",
            value=5.0,  # Way above background
            unit="uSv/h",
            latitude=37.7,
            longitude=-122.4,
        )
        assert system._is_anomaly(anomalous) is True

    def test_get_system_metrics(self, rad_config):
        system = RadiationMonitoringSystem(rad_config)
        metrics = system.get_system_metrics()
        assert "runtime_seconds" in metrics
        assert "measurements_per_second" in metrics
        assert "error_rate" in metrics
