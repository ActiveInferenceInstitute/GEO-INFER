"""Tests for COMMS validation utilities."""
import pytest

from geo_infer_comms.utils.validation import (
    validate_coordinates,
    validate_crs,
)


class TestCoordinateValidation:
    def test_valid_coordinates(self):
        assert validate_coordinates(-122.4, 37.7) is True
        assert validate_coordinates(0.0, 0.0) is True
        assert validate_coordinates(180.0, 90.0) is True
        assert validate_coordinates(-180.0, -90.0) is True

    def test_invalid_longitude(self):
        assert validate_coordinates(181.0, 0.0) is False
        assert validate_coordinates(-181.0, 0.0) is False

    def test_invalid_latitude(self):
        assert validate_coordinates(0.0, 91.0) is False
        assert validate_coordinates(0.0, -91.0) is False


class TestCRSValidation:
    def test_valid_crs(self):
        assert validate_crs("EPSG:4326") is True

    def test_invalid_crs_empty(self):
        assert validate_crs("") is False
