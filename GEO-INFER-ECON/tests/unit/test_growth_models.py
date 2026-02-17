"""Tests for macroeconomic growth models."""

import numpy as np
import pandas as pd
import pytest
from geo_infer_econ.macroeconomics.growth_models import (
    SolowGrowthModel,
    RegionProfile,
    SpatialGrowthModels,
)


class TestSolowGrowthModel:
    """Tests for the Solow growth model."""

    def setup_method(self) -> None:
        self.model = SolowGrowthModel(
            parameters={
                "alpha": 0.33,
                "s": 0.2,
                "n": 0.02,
                "delta": 0.05,
                "g": 0.02,
            }
        )

    def test_production_function_positive(self) -> None:
        output = self.model.production_function(K=100.0, L=50.0, A=1.0)
        assert output > 0

    def test_production_function_cobb_douglas_property(self) -> None:
        """Constant returns to scale: doubling inputs doubles output."""
        y1 = self.model.production_function(K=100.0, L=50.0, A=1.0)
        y2 = self.model.production_function(K=200.0, L=100.0, A=1.0)
        assert abs(y2 / y1 - 2.0) < 0.01

    def test_production_function_technology_increases_output(self) -> None:
        y1 = self.model.production_function(K=100.0, L=50.0, A=1.0)
        y2 = self.model.production_function(K=100.0, L=50.0, A=2.0)
        assert y2 > y1

    def test_capital_dynamics_positive_at_low_capital(self) -> None:
        dk = self.model.capital_dynamics(K=1.0, L=100.0, A=1.0)
        assert dk > 0  # savings > depreciation at low K

    def test_steady_state_values_positive(self) -> None:
        ss = self.model.steady_state_values()
        assert ss["capital_per_worker"] > 0
        assert ss["output_per_worker"] > 0
        assert ss["consumption_per_worker"] > 0

    def test_steady_state_consumption_less_than_output(self) -> None:
        ss = self.model.steady_state_values()
        assert ss["consumption_per_worker"] < ss["output_per_worker"]

    def test_convergence_analysis_positive_rate(self) -> None:
        result = self.model.convergence_analysis(initial_capital_ratio=0.5)
        assert result["convergence_rate"] > 0
        assert result["half_life_years"] > 0

    def test_simulate_growth_path_returns_dataframe(self) -> None:
        initial = {"K": 50.0, "L": 100.0, "A": 1.0}
        result = self.model.simulate_growth_path(initial, time_horizon=20)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 21
        assert "output" in result.columns
        assert "output_per_worker" in result.columns

    def test_simulate_growth_path_output_increases(self) -> None:
        initial = {"K": 50.0, "L": 100.0, "A": 1.0}
        result = self.model.simulate_growth_path(initial, time_horizon=50)
        # Output should generally increase over time
        assert result["output"].iloc[-1] > result["output"].iloc[0]


class TestSpatialGrowthModels:
    """Tests for spatial growth models."""

    def setup_method(self) -> None:
        self.regions = [
            RegionProfile(
                region_id="R1",
                initial_capital=100.0,
                initial_output=50.0,
                population=1000.0,
                technology_level=1.0,
                location=(40.0, -74.0),
                institutions={"governance": 0.8},
                natural_resources={"land": 100.0},
                connectivity={"road": 0.9},
            ),
            RegionProfile(
                region_id="R2",
                initial_capital=80.0,
                initial_output=40.0,
                population=800.0,
                technology_level=0.9,
                location=(41.0, -73.0),
                institutions={"governance": 0.7},
                natural_resources={"land": 80.0},
                connectivity={"road": 0.8},
            ),
            RegionProfile(
                region_id="R3",
                initial_capital=60.0,
                initial_output=30.0,
                population=600.0,
                technology_level=0.8,
                location=(42.0, -75.0),
                institutions={"governance": 0.6},
                natural_resources={"land": 60.0},
                connectivity={"road": 0.7},
            ),
        ]
        self.sgm = SpatialGrowthModels(self.regions)

    def test_spatial_weights_shape(self) -> None:
        weights = self.sgm.calculate_spatial_weights(decay_parameter=0.5)
        assert weights.shape == (3, 3)

    def test_spatial_weights_zero_diagonal(self) -> None:
        weights = self.sgm.calculate_spatial_weights(decay_parameter=0.5)
        for i in range(3):
            assert weights[i, i] == 0.0

    def test_spatial_weights_row_standardized(self) -> None:
        weights = self.sgm.calculate_spatial_weights(decay_parameter=0.5)
        for i in range(3):
            row_sum = np.sum(weights[i])
            assert abs(row_sum - 1.0) < 0.01 or row_sum == 0.0

    def test_spatial_weights_decay_parameter_effect(self) -> None:
        w1 = self.sgm.calculate_spatial_weights(decay_parameter=0.1)
        w2 = self.sgm.calculate_spatial_weights(decay_parameter=10.0)
        # Higher decay = more localized weights (higher nearby, lower far)
        assert not np.allclose(w1, w2)
