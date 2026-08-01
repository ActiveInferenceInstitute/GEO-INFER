"""PSIS-LOO contract tests (STATS-02).

The model-comparison LOO path must use Pareto-smoothed importance sampling
(PSIS-LOO, Vehtari et al. 2017) when arviz is available, and must report the
method and Pareto-k diagnostics rather than silently presenting naive LOO as
PSIS-LOO.

arviz is imported at module level deliberately: the strict test contract
requires optional-dependency absence to be a loud ImportError, not a skip.
"""

import arviz  # noqa: F401  (top-level import: loud failure if absent)
import numpy as np
import pytest

from geo_infer_bayes.core.model_comparison import ModelComparison


@pytest.fixture
def comparison():
    return ModelComparison()


@pytest.fixture
def ll_data():
    """Well-behaved posterior log-likelihood: 500 samples x 8 observations."""
    rng = np.random.default_rng(42)
    matrix = rng.normal(-1.0, 0.5, size=(500, 8))
    return {"log_likelihood_matrix": matrix}


def test_loo_uses_psis_method(comparison, ll_data):
    """LOO reports method='psis-loo' with a finite Pareto-k."""
    result = comparison._loo_comparison(None, ll_data)
    assert result["method"] == "psis-loo"
    assert "pareto_k_max" in result
    assert np.isfinite(result["pareto_k_max"])


def test_loo_elpd_finite_and_reasonable(comparison, ll_data):
    """ELPD is finite and on the same scale as the raw log-likelihoods."""
    result = comparison._loo_comparison(None, ll_data)
    assert np.isfinite(result["elpd_loo"])
    assert np.isfinite(result["se"])
    assert np.isfinite(result["p_loo"])
    # Log-likelihoods ~ N(-1, 0.5) → elpd per obs ~ -1; total over 8 obs < 0.
    assert result["elpd_loo"] < 0.0


def test_loo_close_to_naive_on_well_behaved_posterior(comparison, ll_data):
    """PSIS-LOO stays within a few elpd units of naive LOO on this posterior.

    PSIS smoothing legitimately shifts the estimate (heavy-tailed pointwise
    likelihoods); the exact agreement is pinned against arviz.loo in
    ``test_loo_matches_arviz_reference``. This test only guards against gross
    errors (e.g. sign/scale mistakes), with an absolute bound of 3.0 elpd
    units on a ~-7 to -9 elpd total.
    """
    result = comparison._loo_comparison(None, ll_data)
    ll = ll_data["log_likelihood_matrix"]
    max_ll = np.max(ll, axis=0)
    naive_i = np.log(np.mean(np.exp(ll - max_ll), axis=0)) + max_ll
    naive_loo = float(np.sum(naive_i))
    assert abs(result["elpd_loo"] - naive_loo) < 3.0


def test_loo_matches_arviz_reference(comparison, ll_data):
    """PSIS-LOO equals arviz.loo on the same matrix (verified formula)."""
    ll = ll_data["log_likelihood_matrix"]
    n_samples, n_obs = ll.shape

    import xarray as xr

    obs_coords = xr.Coordinates({"observation": np.arange(n_obs)})
    da_ll = xr.DataArray(
        ll[None, :, :],
        dims=("chain", "draw", "observation"),
        coords=obs_coords,
        name="y",
    )
    da_p = xr.DataArray(np.zeros((1, n_samples)), dims=("chain", "draw"), name="dummy")
    idata = arviz.InferenceData(
        posterior=xr.Dataset({"dummy": da_p}),
        log_likelihood=xr.Dataset({"y": da_ll}),
    )
    ref = arviz.loo(idata, pointwise=True)

    result = comparison._loo_comparison(None, ll_data)
    assert result["elpd_loo"] == pytest.approx(float(ref["elpd_loo"]), rel=1e-6)
    assert result["p_loo"] == pytest.approx(float(ref["p_loo"]), rel=1e-6)
    assert result["se"] == pytest.approx(float(ref["se"]), rel=1e-6)
    assert result["pareto_k_max"] == pytest.approx(
        float(np.max(ref["pareto_k"])), rel=1e-6
    )