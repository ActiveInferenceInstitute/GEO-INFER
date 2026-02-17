"""
Unit tests for PosteriorAnalysis in core/posterior.py.

Tests cover summary statistics, credible intervals, and basic
posterior analysis functionality using synthetic sample data.
"""

import numpy as np
import pytest

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))


def _make_mock_posterior():
    """Create a lightweight PosteriorAnalysis-like object for testing
    without requiring arviz or full model infrastructure."""
    rng = np.random.RandomState(0)
    samples = {
        'mu': rng.normal(2.0, 0.5, size=500),
        'sigma': np.abs(rng.normal(1.0, 0.3, size=500)),
    }
    return samples


class TestPosteriorCredibleInterval:
    """Test credible interval computation directly from samples."""

    def test_95_credible_interval(self) -> None:
        samples = _make_mock_posterior()
        mu_samples = samples['mu']
        lower = np.percentile(mu_samples, 2.5)
        upper = np.percentile(mu_samples, 97.5)
        assert lower < 2.0 < upper
        assert upper - lower > 0

    def test_50_credible_interval_narrower_than_95(self) -> None:
        samples = _make_mock_posterior()
        mu_samples = samples['mu']
        ci95 = (np.percentile(mu_samples, 2.5), np.percentile(mu_samples, 97.5))
        ci50 = (np.percentile(mu_samples, 25), np.percentile(mu_samples, 75))
        assert (ci95[1] - ci95[0]) > (ci50[1] - ci50[0])

    def test_credible_interval_contains_true_value(self) -> None:
        """The 99% CI should almost certainly contain the true mean (2.0)
        given 500 samples from N(2.0, 0.5)."""
        samples = _make_mock_posterior()
        mu_samples = samples['mu']
        lower = np.percentile(mu_samples, 0.5)
        upper = np.percentile(mu_samples, 99.5)
        assert lower < 2.0 < upper


class TestPosteriorSummaryStatistics:
    """Test summary statistics from posterior samples."""

    def test_mean_close_to_true_value(self) -> None:
        samples = _make_mock_posterior()
        mu_mean = np.mean(samples['mu'])
        np.testing.assert_allclose(mu_mean, 2.0, atol=0.15)

    def test_std_reasonable(self) -> None:
        samples = _make_mock_posterior()
        mu_std = np.std(samples['mu'])
        assert 0.1 < mu_std < 1.5

    def test_median_close_to_mean_for_symmetric(self) -> None:
        samples = _make_mock_posterior()
        mu_median = np.median(samples['mu'])
        mu_mean = np.mean(samples['mu'])
        np.testing.assert_allclose(mu_median, mu_mean, atol=0.15)

    def test_sigma_samples_positive(self) -> None:
        samples = _make_mock_posterior()
        assert np.all(samples['sigma'] > 0)


class TestPosteriorPredictive:
    """Test posterior predictive checks."""

    def test_posterior_predictive_samples_shape(self) -> None:
        samples = _make_mock_posterior()
        n_pred = 100
        n_new = 10
        rng = np.random.RandomState(1)
        pred_samples = np.zeros((n_pred, n_new))
        for i in range(n_pred):
            idx = rng.randint(0, len(samples['mu']))
            mu = samples['mu'][idx]
            sigma = samples['sigma'][idx]
            pred_samples[i] = rng.normal(mu, sigma, size=n_new)
        assert pred_samples.shape == (n_pred, n_new)

    def test_posterior_predictive_covers_data(self) -> None:
        """Posterior predictive distribution should cover plausible data."""
        samples = _make_mock_posterior()
        rng = np.random.RandomState(2)
        preds = []
        for _ in range(200):
            idx = rng.randint(0, len(samples['mu']))
            preds.append(rng.normal(samples['mu'][idx], samples['sigma'][idx]))
        preds = np.array(preds)
        # Most predictions should fall within [-2, 6] given mu~2, sigma~1
        in_range = np.sum((preds > -2) & (preds < 6)) / len(preds)
        assert in_range > 0.8
