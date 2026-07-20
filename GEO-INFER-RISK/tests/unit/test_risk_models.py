"""Tests for risk models."""

import numpy as np
import pytest
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
from geo_infer_risk.core.risk_models import (
    RiskModel,
    RiskParameters,
    HazardModel,
    VulnerabilityModel,
    ExposureModel,
    FloodHazardModel,
    BuildingVulnerabilityModel,
    PopulationExposureModel,
)


class TestRiskModels:
    """Tests for risk model implementations."""

    def test_risk_model_import(self) -> None:
        assert RiskModel is not None

    def test_risk_parameters_import(self) -> None:
        assert RiskParameters is not None

    def test_hazard_model_import(self) -> None:
        assert HazardModel is not None

    def test_vulnerability_model_import(self) -> None:
        assert VulnerabilityModel is not None

    def test_exposure_model_import(self) -> None:
        assert ExposureModel is not None

    def test_risk_parameters_validate_numeric_contract(self) -> None:
        with pytest.raises(ValueError, match="confidence_level"):
            RiskParameters(confidence_level=1.0)
        with pytest.raises(ValueError, match="monte_carlo_iterations"):
            RiskParameters(monte_carlo_iterations=0)

    @staticmethod
    def _configured_model(seed: int = 7) -> RiskModel:
        model = RiskModel(RiskParameters(monte_carlo_iterations=8, random_seed=seed))
        model.set_hazard(FloodHazardModel())
        model.set_vulnerability(BuildingVulnerabilityModel())
        model.set_exposure(PopulationExposureModel())
        return model

    @staticmethod
    def _geometry() -> gpd.GeoDataFrame:
        return gpd.GeoDataFrame(
            geometry=[Point(-122.4, 37.7), Point(-122.3, 37.8)],
            crs="EPSG:4326",
        )

    def test_risk_calculation_reports_point_estimate_when_components_have_no_bounds(
        self,
    ) -> None:
        model = self._configured_model()
        result = model.calculate_risk(self._geometry())

        np.testing.assert_allclose(result["risk_lower_bound"], result["risk_score"])
        np.testing.assert_allclose(result["risk_upper_bound"], result["risk_score"])
        assert set(result["uncertainty_source"]) == {"point_estimate"}

    def test_monte_carlo_is_reproducible_with_a_local_seed(self) -> None:
        geometry = self._geometry()
        first = self._configured_model(seed=19).run_monte_carlo(geometry)
        second = self._configured_model(seed=19).run_monte_carlo(geometry)

        np.testing.assert_allclose(first["mean"], second["mean"])
        assert first["confidence_level"] == pytest.approx(0.95)

    def test_component_bounds_must_contain_point_estimate(self) -> None:
        frame = pd.DataFrame(
            {
                "hazard_probability": [0.2, 0.4],
                "hazard_probability_lower_bound": [0.3, 0.1],
                "hazard_probability_upper_bound": [0.5, 0.6],
            }
        )
        with pytest.raises(ValueError, match="contain the point estimate"):
            RiskModel._component_bounds(
                frame,
                "hazard_probability",
                "hazard",
                np.array([0.2, 0.4]),
            )
