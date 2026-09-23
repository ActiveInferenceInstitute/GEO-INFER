"""Regression tests for intensity-distribution parameter fidelity in RISK.

``EnhancedCatastropheModel._analyze_intensity_distribution`` picks the
best candidate distribution by AIC. The parameters stored under
``model_parameters["intensity_distribution_params"]`` must be the fit of
the *selected* distribution -- not the parameters of whichever candidate
happened to be fit last (``gumbel_r``, the final candidate).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

from geo_infer_risk.core.catastrophe_models import (
    CatastropheConfig,
    EnhancedEarthquakeModel,
)

# Candidate name -> the scipy distribution the analyzer actually fits.
_CANDIDATES = {
    "exponential": stats.expon,
    "weibull": stats.weibull_min,
    "lognormal": stats.lognorm,
    "gumbel_r": stats.gumbel_r,
}

# Free parameters per candidate after fitting; "weibull" is fit with
# floc=0, so its location is fixed and shape+scale are free (3 total).
_EXPECTED_PARAM_COUNTS = {
    "exponential": 2,
    "weibull": 3,
    "lognormal": 3,
    "gumbel_r": 2,
}


def _fit_earthquake_model(magnitudes: np.ndarray) -> EnhancedEarthquakeModel:
    """Fit an earthquake model to a magnitude column."""
    config = CatastropheConfig(
        simulation_years=10,
        return_periods=[10, 25, 50],
        simulation_method="monte_carlo",
        spatial_correlation=False,
        batch_size=10,
    )
    data = pd.DataFrame(
        {
            "event_id": [f"e{i}" for i in range(len(magnitudes))],
            "magnitude": magnitudes,
        }
    )
    model = EnhancedEarthquakeModel(config=config)
    return model.fit(data)


def test_exponential_wins_aic_stores_exponential_params() -> None:
    """Exponential data -> stored params are exponential's fit (2 params)."""
    magnitudes = np.random.default_rng(42).exponential(scale=5.0, size=300)
    model = _fit_earthquake_model(magnitudes)

    name = model.model_parameters["intensity_distribution"]
    stored = model.model_parameters["intensity_distribution_params"]

    assert name == "exponential"
    assert len(stored) == _EXPECTED_PARAM_COUNTS[name]

    # The stored parameters are the named distribution's fit on the same
    # data -- the fidelity contract the AIC selection promises.
    refit = _CANDIDATES[name].fit(magnitudes)
    np.testing.assert_allclose(stored, refit, rtol=1e-9)


def test_weibull_wins_aic_stores_weibull_params() -> None:
    """Weibull data -> stored params are weibull's floc=0 fit (3 params)."""
    magnitudes = np.random.default_rng(7).weibull(0.6, size=400)
    model = _fit_earthquake_model(magnitudes)

    name = model.model_parameters["intensity_distribution"]
    stored = model.model_parameters["intensity_distribution_params"]

    assert name == "weibull"
    assert len(stored) == 3
    assert stored[1] == 0.0  # floc=0 pins the location

    refit = _CANDIDATES[name].fit(magnitudes, floc=0)
    np.testing.assert_allclose(stored, refit, rtol=1e-9)
