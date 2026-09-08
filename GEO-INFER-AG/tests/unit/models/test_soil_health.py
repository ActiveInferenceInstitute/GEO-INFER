"""Tests for soil health model."""

from geo_infer_ag.models.soil_health import SoilHealthModel


class TestSoilHealthModel:
    """Tests for the soil health model."""

    def test_import(self) -> None:
        assert SoilHealthModel is not None

    def test_initialization(self) -> None:
        model = SoilHealthModel()
        assert model is not None
