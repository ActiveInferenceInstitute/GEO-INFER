"""Tests for climate data processing."""

import pytest
from geo_infer_bio.climate import ClimateDataProcessor


class TestClimateDataProcessor:
    """Tests for climate data processing."""

    def test_initialization(self) -> None:
        processor = ClimateDataProcessor()
        assert processor is not None
        assert processor.cache_dir.exists()

    def test_worldclim_variables(self) -> None:
        processor = ClimateDataProcessor()
        variables = processor.worldclim_config["variables"]
        assert "bio1" in variables
        assert "bio12" in variables
        assert len(variables) == 19

    def test_worldclim_resolutions(self) -> None:
        processor = ClimateDataProcessor()
        resolutions = processor.worldclim_config["resolutions"]
        assert "30s" in resolutions
        assert "10m" in resolutions
