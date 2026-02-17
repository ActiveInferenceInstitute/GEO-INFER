"""Tests for economic indicators utility module."""

import numpy as np
import pandas as pd
import pytest
from geo_infer_econ.utils.indicators import EconomicIndicators


class TestEconomicIndicators:
    """Tests for the EconomicIndicators class."""

    def setup_method(self) -> None:
        self.ind = EconomicIndicators()

    def test_gini_perfect_equality(self) -> None:
        incomes = np.array([100.0, 100.0, 100.0, 100.0])
        gini = self.ind.calculate_gini_coefficient(incomes)
        assert abs(gini) < 0.01

    def test_gini_between_zero_and_one(self) -> None:
        incomes = np.array([10.0, 20.0, 30.0, 40.0, 100.0])
        gini = self.ind.calculate_gini_coefficient(incomes)
        assert 0 <= gini <= 1

    def test_theil_index_equal_values(self) -> None:
        values = np.array([50.0, 50.0, 50.0])
        theil = self.ind.calculate_theil_index(values)
        assert abs(theil) < 0.01

    def test_theil_index_unequal_values(self) -> None:
        values = np.array([10.0, 50.0, 100.0, 500.0])
        theil = self.ind.calculate_theil_index(values)
        assert theil > 0

    def test_unemployment_rate(self) -> None:
        rate = self.ind.calculate_unemployment_rate(50.0, 1000.0)
        assert abs(rate - 5.0) < 0.01

    def test_inflation_rate(self) -> None:
        prices = np.array([100.0, 102.0, 105.0])
        inflation = self.ind.calculate_inflation_rate(prices, base_period=0)
        assert abs(inflation[0]) < 0.01  # base period = 0%
        assert abs(inflation[1] - 2.0) < 0.01

    def test_gdp_per_capita(self) -> None:
        gdp = 1_000_000.0
        population = 50_000.0
        gdp_pc = self.ind.calculate_gdp_per_capita(gdp, population)
        assert abs(gdp_pc - 20.0) < 0.01

    def test_growth_rate_simple(self) -> None:
        values = np.array([100.0, 110.0, 121.0])
        rates = self.ind.calculate_growth_rate(values, periods=1, method="simple")
        assert abs(rates[0] - 0.1) < 0.01

    def test_economic_distance_euclidean(self) -> None:
        r1 = {"gdp": 100.0, "population": 50.0}
        r2 = {"gdp": 200.0, "population": 100.0}
        dist = self.ind.calculate_economic_distance(r1, r2, method="euclidean")
        assert dist >= 0

    def test_economic_distance_no_common_raises(self) -> None:
        r1 = {"a": 1.0}
        r2 = {"b": 2.0}
        with pytest.raises(ValueError, match="No common"):
            self.ind.calculate_economic_distance(r1, r2)

    def test_economic_complexity_index(self) -> None:
        exports = np.array([
            [10.0, 5.0, 0.0],
            [2.0, 8.0, 3.0],
            [0.0, 1.0, 15.0],
        ])
        result = self.ind.calculate_economic_complexity_index(
            exports,
            countries=["C1", "C2", "C3"],
            products=["P1", "P2", "P3"],
        )
        assert "C1" in result
        assert "C2" in result
        assert "C3" in result
