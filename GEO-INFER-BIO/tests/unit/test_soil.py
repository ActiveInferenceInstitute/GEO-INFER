"""Tests for soil data integration."""

import pytest
import inspect
from geo_infer_bio.soil import SoilDataIntegrator


class TestSoilDataIntegrator:
    """Tests for soil data integration."""

    def test_initialization(self) -> None:
        integrator = SoilDataIntegrator()
        assert integrator is not None
        assert integrator.cache_dir.exists()

    def test_soilgrids_properties(self) -> None:
        integrator = SoilDataIntegrator()
        props = integrator.soilgrids_config["properties"]
        assert "phh2o" in props
        assert "clay" in props
        assert "sand" in props

    def test_soilgrids_depths(self) -> None:
        integrator = SoilDataIntegrator()
        depths = integrator.soilgrids_config["depths"]
        assert "0-5cm" in depths

    def test_soilgrids_depth_argument_is_not_mutable_default(self) -> None:
        parameter = inspect.signature(
            SoilDataIntegrator.load_soilgrids_data
        ).parameters["depths"]
        assert parameter.default is None
