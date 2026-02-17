"""Tests for IoT sensor registry module."""
import pytest

from geo_infer_iot.core.registry import (
    SensorRegistry,
    SensorMetadata,
    SensorNetwork,
)


class TestSensorMetadata:
    def test_create_sensor(self):
        sensor = SensorMetadata(
            sensor_id="s-001",
            network_id="net-1",
            sensor_type="temperature",
            latitude=37.7749,
            longitude=-122.4194,
        )
        assert sensor.sensor_id == "s-001"
        assert sensor.h3_index != ""  # Should be auto-computed

    def test_h3_index_auto_computed(self):
        sensor = SensorMetadata(
            sensor_id="s-002",
            network_id="net-1",
            sensor_type="humidity",
            latitude=40.7128,
            longitude=-74.006,
        )
        assert sensor.h3_index is not None
        assert len(sensor.h3_index) > 0

    def test_custom_h3_resolution(self):
        sensor = SensorMetadata(
            sensor_id="s-003",
            network_id="net-1",
            sensor_type="pressure",
            latitude=51.5074,
            longitude=-0.1278,
            h3_resolution=6,
        )
        assert sensor.h3_resolution == 6


class TestSensorNetwork:
    def test_create_network(self):
        network = SensorNetwork(
            network_id="net-1",
            name="Test Network",
            protocol="mqtt",
            spatial_bounds={"lat_min": 30, "lat_max": 50, "lon_min": -130, "lon_max": -70},
            sensor_types=["temperature", "humidity"],
        )
        assert network.name == "Test Network"
        assert network.protocol == "mqtt"
        assert network.sensor_count == 0


class TestSensorRegistry:
    def test_init(self):
        registry = SensorRegistry()
        assert len(registry.networks) == 0
        assert len(registry.sensors) == 0

    def test_register_network(self):
        registry = SensorRegistry()
        network = registry.register_network(
            name="Weather Network",
            protocol="mqtt",
            spatial_bounds={"lat_min": 30, "lat_max": 50, "lon_min": -130, "lon_max": -70},
            sensor_types=["temperature", "humidity"],
        )
        assert network.name == "Weather Network"
        assert len(registry.networks) == 1

    def test_register_sensor(self):
        registry = SensorRegistry()
        registry.register_network(
            network_id="net-1",
            name="Test",
            protocol="mqtt",
            spatial_bounds={},
            sensor_types=["temperature"],
        )
        sensor = registry.register_sensor({
            "sensor_id": "s-001",
            "network_id": "net-1",
            "sensor_type": "temperature",
            "latitude": 37.7749,
            "longitude": -122.4194,
        })
        assert sensor.sensor_id == "s-001"
        assert len(registry.sensors) == 1
        assert registry.networks["net-1"].sensor_count == 1

    def test_get_sensors_by_type(self):
        registry = SensorRegistry()
        registry.register_sensor({
            "sensor_id": "s-001",
            "network_id": "net-1",
            "sensor_type": "temperature",
            "latitude": 37.7, "longitude": -122.4,
        })
        registry.register_sensor({
            "sensor_id": "s-002",
            "network_id": "net-1",
            "sensor_type": "humidity",
            "latitude": 37.8, "longitude": -122.3,
        })
        temp_sensors = registry.get_sensors_by_type("temperature")
        assert len(temp_sensors) == 1
        assert temp_sensors[0].sensor_id == "s-001"

    def test_get_sensors_in_area(self):
        registry = SensorRegistry()
        registry.register_sensor({
            "sensor_id": "s-001",
            "network_id": "net-1",
            "sensor_type": "temperature",
            "latitude": 37.7, "longitude": -122.4,
        })
        registry.register_sensor({
            "sensor_id": "s-002",
            "network_id": "net-1",
            "sensor_type": "temperature",
            "latitude": 50.0, "longitude": 10.0,
        })
        sensors = registry.get_sensors_in_area({
            "lat_min": 37.0, "lat_max": 38.0,
            "lon_min": -123.0, "lon_max": -122.0,
        })
        assert len(sensors) == 1
        assert sensors[0].sensor_id == "s-001"

    def test_get_sensors_in_h3_cell(self):
        registry = SensorRegistry()
        sensor = registry.register_sensor({
            "sensor_id": "s-001",
            "network_id": "net-1",
            "sensor_type": "temperature",
            "latitude": 37.7749, "longitude": -122.4194,
        })
        cell_sensors = registry.get_sensors_in_h3_cell(sensor.h3_index)
        assert len(cell_sensors) == 1
