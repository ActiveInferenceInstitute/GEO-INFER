"""Regression tests for IoT visualization boundaries."""

from pathlib import Path

from geo_infer_iot.utils.visualization import IoTVisualization


def test_sensor_map_validates_coordinates_and_creates_nested_output(
    tmp_path: Path,
) -> None:
    """Sensor maps accept valid coordinates and create missing parents."""
    output_file = tmp_path / "nested" / "sensor_map.html"
    result = IoTVisualization().create_sensor_map(
        [{"sensor_id": "s1", "latitude": 40.7, "longitude": -74.0}],
        output_file=str(output_file),
    )

    assert result["success"] is True
    assert output_file.exists()


def test_sensor_map_reports_invalid_coordinates() -> None:
    """Invalid geographic coordinates are returned as an explicit error."""
    result = IoTVisualization().create_sensor_map(
        [{"sensor_id": "bad", "latitude": 95, "longitude": 0}]
    )

    assert "error" in result
    assert "geographic bounds" in result["error"]


def test_interpolation_map_rejects_misaligned_values() -> None:
    """Interpolation points and values must have matching lengths."""
    result = IoTVisualization().create_spatial_interpolation_map(
        {
            "target_coordinates": [[40.7, -74.0], [40.8, -74.1]],
            "interpolated_values": [1.0],
        }
    )

    assert "error" in result
    assert "must align" in result["error"]
