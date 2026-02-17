"""Tests for market structure analysis module."""

import numpy as np
import pandas as pd
import pytest
from geo_infer_econ.microeconomics.market_structure import (
    CompetitionAnalysis,
    SpatialMarketAnalysis,
    MarketDefinition,
)


class TestCompetitionAnalysis:
    """Tests for competition analysis."""

    def setup_method(self) -> None:
        self.ca = CompetitionAnalysis()

    def test_price_correlation_matrix_shape(self) -> None:
        np.random.seed(42)
        data = pd.DataFrame({
            "product_A": np.random.randn(50) + 10,
            "product_B": np.random.randn(50) + 10,
            "product_C": np.random.randn(50) + 5,
        })
        corr = self.ca.calculate_price_correlation_matrix(data)
        assert corr.shape == (3, 3)
        assert np.allclose(np.diag(corr), 1.0)

    def test_market_definition_test_correlated(self) -> None:
        np.random.seed(42)
        base = np.random.randn(100)
        data = pd.DataFrame({
            "A": base + np.random.randn(100) * 0.1,
            "B": base + np.random.randn(100) * 0.1,
            "C": np.random.randn(100) * 5,
        })
        result = self.ca.test_market_definition(data, ["A", "B"])
        assert result["internal_correlation"] > 0.5
        assert "is_relevant_market" in result

    def test_analyze_entry_barriers(self) -> None:
        data = pd.DataFrame({
            "capital_intensity": [0.7, 0.8],
            "minimum_efficient_scale": [0.4, 0.5],
            "advertising_intensity": [0.2, 0.3],
            "regulatory_burden": [0.6, 0.7],
        })
        barriers = self.ca.analyze_entry_barriers(data)
        assert barriers["capital_requirements"] == "high"
        assert barriers["regulatory_barriers"] == "high"

    def test_analyze_entry_barriers_low(self) -> None:
        data = pd.DataFrame({
            "capital_intensity": [0.1, 0.2],
            "minimum_efficient_scale": [0.1, 0.1],
        })
        barriers = self.ca.analyze_entry_barriers(data)
        assert barriers["capital_requirements"] == "low"


class TestSpatialMarketAnalysis:
    """Tests for spatial market analysis."""

    def setup_method(self) -> None:
        self.sma = SpatialMarketAnalysis()

    def test_delineate_geographic_markets(self) -> None:
        np.random.seed(42)
        base = np.random.randn(100)
        data = pd.DataFrame({
            "loc_A": base + np.random.randn(100) * 0.05,
            "loc_B": base + np.random.randn(100) * 0.05,
            "loc_C": np.random.randn(100) * 3,
        })
        result = self.sma.delineate_geographic_markets(
            data, ["loc_A", "loc_B", "loc_C"]
        )
        assert "geographic_markets" in result
        assert "price_correlations" in result

    def test_market_accessibility(self) -> None:
        locations = np.array([[0.0, 0.0], [1.0, 0.0], [0.0, 1.0]])
        market_centers = np.array([[0.5, 0.5]])
        access = self.sma.calculate_market_accessibility(locations, market_centers)
        assert len(access) == 3


class TestMarketDefinition:
    """Tests for market definition data class."""

    def test_market_definition_creation(self) -> None:
        md = MarketDefinition(
            market_id="m1",
            product_market="widgets",
            geographic_market="northeast",
            time_period="2024",
            participants=["firm_A", "firm_B"],
            boundaries={"type": "region", "bounds": [-80, 35, -70, 45]},
        )
        assert md.market_id == "m1"
        assert len(md.participants) == 2
