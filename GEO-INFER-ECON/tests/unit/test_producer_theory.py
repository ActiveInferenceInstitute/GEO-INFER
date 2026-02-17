"""Tests for producer theory module."""

import numpy as np
import pytest
from geo_infer_econ.microeconomics.producer_theory import (
    ProductionFunctions,
    FirmProfile,
)


class TestProductionFunctions:
    """Tests for production function implementations."""

    def test_cobb_douglas_basic(self) -> None:
        inputs = np.array([4.0, 9.0])
        alpha = np.array([0.5, 0.5])
        result = ProductionFunctions.cobb_douglas(inputs, alpha)
        expected = np.sqrt(4.0) * np.sqrt(9.0)
        assert abs(result - expected) < 1e-6

    def test_cobb_douglas_zero_input(self) -> None:
        inputs = np.array([0.0, 5.0])
        alpha = np.array([0.5, 0.5])
        result = ProductionFunctions.cobb_douglas(inputs, alpha)
        assert result == 0

    def test_cobb_douglas_constant_returns(self) -> None:
        """Sum of alpha = 1 gives constant returns to scale."""
        alpha = np.array([0.3, 0.7])
        y1 = ProductionFunctions.cobb_douglas(np.array([10.0, 20.0]), alpha)
        y2 = ProductionFunctions.cobb_douglas(np.array([20.0, 40.0]), alpha)
        assert abs(y2 / y1 - 2.0) < 0.01

    def test_ces_production_rho_zero(self) -> None:
        inputs = np.array([4.0, 9.0])
        alpha = np.array([0.5, 0.5])
        result = ProductionFunctions.ces_production(inputs, alpha, rho=0)
        cd = ProductionFunctions.cobb_douglas(inputs, alpha)
        assert abs(result - cd) < 1e-6

    def test_ces_production_positive_rho(self) -> None:
        inputs = np.array([3.0, 5.0])
        alpha = np.array([0.4, 0.6])
        result = ProductionFunctions.ces_production(inputs, alpha, rho=0.5, A=2.0)
        assert result > 0

    def test_translog_production(self) -> None:
        inputs = np.array([1.0, 2.0])
        # beta: constant + 2 linear + 3 quadratic (2+1 cross terms) = 6
        beta = np.array([0.5, 0.3, 0.4, 0.1, 0.05, 0.02])
        result = ProductionFunctions.translog_production(inputs, beta)
        assert isinstance(result, float)


class TestFirmProfile:
    """Tests for firm profile data structure."""

    def test_firm_profile_creation(self) -> None:
        firm = FirmProfile(
            firm_id="f1",
            location=(40.0, -74.0),
            inputs={"labor": 100.0, "capital": 50.0},
            outputs={"product": 200.0},
            input_prices={"labor": 20.0, "capital": 10.0},
            output_prices={"product": 5.0},
            technology_level=1.0,
            scale="medium",
            industry="manufacturing",
        )
        assert firm.firm_id == "f1"
        assert firm.inputs["labor"] == 100.0
        assert firm.scale == "medium"
