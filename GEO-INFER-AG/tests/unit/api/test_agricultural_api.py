"""Unit tests for the AgriculturalAPI module."""

import pytest

from geo_infer_ag.api.agricultural_api import AgriculturalAPI


class TestAgriculturalAPI:
    """Test suite for AgriculturalAPI yield analysis validation."""

    def setup_method(self):
        """Create a fresh API client for each test."""
        self.api = AgriculturalAPI()

    def test_analyze_crop_yield_with_valid_weather(self):
        """Yield analysis succeeds with well-formed weather data."""
        weather = [
            {"temperature_high": 25.0, "precipitation": 10.0},
            {"temperature_high": 27.0, "precipitation": 15.0},
        ]
        result = self.api.analyze_crop_yield(
            crop_type="corn",
            location={"lat": 40.0, "lon": -95.0},
            weather_data=weather,
            soil_data={"ph_level": 6.8, "organic_matter": 3.0},
        )

        assert result["crop_type"] == "corn"
        assert result["predicted_yield"] > 0

    def test_analyze_crop_yield_empty_weather_raises(self):
        """Empty weather_data must raise ValueError, not ZeroDivisionError."""
        with pytest.raises(ValueError, match="at least one daily record"):
            self.api.analyze_crop_yield(
                crop_type="corn",
                location={"lat": 40.0, "lon": -95.0},
                weather_data=[],
                soil_data={},
            )

    def test_analyze_crop_yield_missing_key_raises(self):
        """A record missing 'temperature_high' must raise a clear ValueError."""
        with pytest.raises(ValueError, match="temperature_high"):
            self.api.analyze_crop_yield(
                crop_type="corn",
                location={"lat": 40.0, "lon": -95.0},
                weather_data=[{"precipitation": 10.0}],
                soil_data={},
            )

    def test_analyze_crop_yield_missing_precipitation_raises(self):
        """A record missing 'precipitation' must raise a clear ValueError."""
        with pytest.raises(ValueError, match="precipitation"):
            self.api.analyze_crop_yield(
                crop_type="corn",
                location={"lat": 40.0, "lon": -95.0},
                weather_data=[{"temperature_high": 25.0}],
                soil_data={},
            )
