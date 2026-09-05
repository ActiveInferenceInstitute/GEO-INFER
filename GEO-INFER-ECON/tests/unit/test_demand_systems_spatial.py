"""Regression tests for demand-system estimation (AIDS / SUR) and the
spatial econometrics fixes (real SAC estimation, standardized Getis-Ord G*).
"""

import numpy as np
import pandas as pd
import pytest

from geo_infer_econ.core.econometrics_engine import SpatialEconometricsEngine
from geo_infer_econ.microeconomics.consumer_theory import DemandFunctions


def _demand_frame(n: int = 200, seed: int = 0) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    p1 = np.exp(rng.normal(1.0, 0.3, n))
    p2 = np.exp(rng.normal(1.0, 0.3, n))
    income = np.exp(rng.normal(5.0, 0.3, n))
    q1 = 2.0 * income / p1 + rng.normal(0.0, 0.1, n)
    q2 = 1.5 * income / p2 + 0.5 * p1 / p2 + rng.normal(size=n)
    return pd.DataFrame(
        {
            "quantity_good_1": q1,
            "quantity_good_2": q2,
            "price_good_1": p1,
            "price_good_2": p2,
            "income": income,
        }
    )


class TestAidsEstimation:
    """AIDS demand-system estimation returns real parameters."""

    def test_aids_returns_nonempty_parameters(self) -> None:
        df = _demand_frame()
        result = DemandFunctions().estimate_demand_system(df, method="aids")
        assert result["method"] == "AIDS"
        assert result["goods"] == ["good_1", "good_2"]
        for good in result["goods"]:
            params = result["parameters"][good]
            assert np.isfinite(params["alpha"])
            assert len(params["gamma"]) == 2
            assert 0.0 < params["mean_budget_share"] < 1.0
            assert np.isfinite(result["elasticities"][good]["expenditure"])
            assert result["diagnostics"][good]["r_squared"] > 0.0

    def test_aids_expenditure_elasticity_near_one_for_hicksian_goods(self) -> None:
        """q = income/p implies unit expenditure elasticity."""
        df = _demand_frame()
        result = DemandFunctions().estimate_demand_system(df, method="aids")
        assert result["elasticities"]["good_1"]["expenditure"] == pytest.approx(1.0, abs=0.05)

    def test_aids_rejects_zero_total_expenditure(self) -> None:
        df = _demand_frame(20)
        df.loc[df.index[0], ["quantity_good_1", "quantity_good_2"]] = 0.0
        with pytest.raises(ValueError, match="positive"):
            DemandFunctions().estimate_demand_system(df, method="aids")

    def test_aids_insufficient_data(self) -> None:
        df = pd.DataFrame({"income": [1.0, 2.0], "price_good_1": [1.0, 1.0]})
        result = DemandFunctions().estimate_demand_system(df, method="aids")
        assert result["status"] == "insufficient_data"


class TestSurEstimation:
    """Zellner two-step SUR estimation."""

    def test_sur_recovers_coefficients(self) -> None:
        df = _demand_frame()
        result = DemandFunctions().estimate_demand_system(df, method="sur")
        assert result["method"] == "SUR"
        assert set(result["system_results"]) == {"good_1", "good_2"}
        # DGP q1 = 2*income/p1: linear projection on income is positive
        assert 1.0 < result["system_results"]["good_1"]["coefficients"][0] < 3.0
        assert result["system_results"]["good_1"]["r_squared"] > 0.5

    def test_sur_insufficient_goods(self) -> None:
        df = pd.DataFrame({"quantity_good_1": [1.0], "price_good_1": [1.0], "income": [1.0]})
        result = DemandFunctions().estimate_demand_system(df, method="sur")
        assert result["status"] == "insufficient_goods"

    def test_sur_uses_own_price_regressor(self) -> None:
        """Each equation is estimated on its own price (SUR-informative)."""
        df = _demand_frame()
        result = DemandFunctions().estimate_demand_system(df, method="sur")
        # Own-price coefficient is negative for both goods (q ~ income/price)
        assert result["system_results"]["good_1"]["coefficients"][1] < 0
        assert result["system_results"]["good_2"]["coefficients"][1] < 0


def _contiguity_weights(n: int) -> np.ndarray:
    W = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if abs(i - j) == 1:
                W[i, j] = 1.0
    return W / W.sum(axis=1, keepdims=True)


class TestSacModel:
    """SAC estimation combines spatial lag and spatial error processes."""

    def _sac_dgp(self, n: int = 30, seed: int = 42):
        rng = np.random.default_rng(seed)
        W = _contiguity_weights(n)
        X = np.column_stack([np.ones(n), rng.normal(size=n)])
        rho, lam, beta = 0.5, 0.4, np.array([1.0, 2.0])
        u = np.linalg.solve(np.eye(n) - 0.4 * W, rng.normal(size=n))
        y = np.linalg.solve(np.eye(n) - rho * W, X @ beta) + u
        return X, y, W, rho

    def test_sac_returns_rho_and_lambda(self) -> None:
        X, y, W, _ = self._sac_dgp()
        engine = SpatialEconometricsEngine({})
        engine.fit(X, y, W, model_type="sac")
        assert engine.model_type == "sac"
        assert len(engine.coefficients_) == 4  # rho, beta1, beta2, lambda
        assert 0.0 < engine.coefficients_[0] < 1.0

    def test_sac_diagnostics_include_both_parameters(self) -> None:
        X, y, W, _ = self._sac_dgp()
        engine = SpatialEconometricsEngine({})
        results = engine._fit_sac_model(y, X, W)
        assert abs(results.spatial_diagnostics["spatial_lambda"]) < 1.0
        assert "covariance" in results.convergence_info

    def test_sac_prediction_matches_reduced_form(self) -> None:
        X, y, W, _ = self._sac_dgp()
        engine = SpatialEconometricsEngine({})
        engine.fit(X, y, W, model_type="sac")
        pred = engine.predict(X, W)
        expected = np.linalg.solve(np.eye(len(X)) - engine.coefficients_[0] * W,
                                   X @ engine.coefficients_[1:-1])
        assert np.allclose(pred, expected)

    def test_sac_prediction_requires_weights(self) -> None:
        X, y, W, _ = self._sac_dgp()
        engine = SpatialEconometricsEngine({})
        engine.fit(X, y, W, model_type="sac")
        with pytest.raises(ValueError, match="weights"):
            engine.predict(X, None)

    def test_hotspot_produces_positive_z(self) -> None:
        n = 25
        engine = SpatialEconometricsEngine({})
        residuals = np.concatenate([np.full(5, 3.0), np.full(20, -0.5)])
        z = engine.spatial_diagnostics(residuals, np.eye(n))["getis_ord_g_star_z"]
        assert z > 1.5

    def test_zero_residuals_give_zero_z(self) -> None:
        engine = SpatialEconometricsEngine({})
        z = engine.spatial_diagnostics(np.zeros(10), np.eye(10))["getis_ord_g_star_z"]
        assert z == 0.0

    def test_white_noise_gives_moderate_z(self) -> None:
        rng = np.random.default_rng(1)
        engine = SpatialEconometricsEngine({})
        W = _contiguity_weights(25)
        z = engine.spatial_diagnostics(rng.normal(size=25), W)["getis_ord_g_star_z"]
        assert 0.0 < z < 6.0

    def test_result_contains_documented_keys(self) -> None:
        engine = SpatialEconometricsEngine({})
        result = engine.spatial_diagnostics(np.random.default_rng(0).normal(size=20), np.eye(20))
        for key in ("morans_i", "expected_morans_i", "z_morans", "p_value_morans",
                    "significant_autocorr", "geary_c", "getis_ord_g_star_z"):
            assert key in result


class TestSpatialCovarianceDocumentation:
    """SAR/SEM results document their simplified covariance."""

    def test_sar_convergence_info_documents_covariance(self) -> None:
        n = 20
        rng = np.random.default_rng(0)
        W = _contiguity_weights(n)
        X = np.column_stack([np.ones(n), rng.normal(size=n)])
        y = np.linalg.solve(np.eye(n) - 0.5 * W, X @ np.array([1.0, 2.0])) + rng.normal(size=n) * 0.1
        engine = SpatialEconometricsEngine({})
        results = engine._fit_sar_model(y, X, W)
        assert "covariance" in results.convergence_info
        assert "ignores spatial dependence" in results.convergence_info["covariance"]

    def test_sem_convergence_info_documents_covariance(self) -> None:
        n = 20
        rng = np.random.default_rng(0)
        W = _contiguity_weights(n)
        X = np.column_stack([np.ones(n), rng.normal(size=n)])
        y = X @ np.array([1.0, 2.0]) + rng.normal(size=n) * 0.1
        engine = SpatialEconometricsEngine({})
        results = engine._fit_sem_model(y, X, W)
        assert "covariance" in results.convergence_info
        assert "ignores spatial dependence" in results.convergence_info["covariance"]