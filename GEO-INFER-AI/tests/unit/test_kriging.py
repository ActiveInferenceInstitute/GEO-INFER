"""
Unit tests for Ordinary Kriging interpolation.
"""

import numpy as np
import pytest

from geo_infer_ai.models.predictive.spatial_predictor import OrdinaryKriging


class TestOrdinaryKriging:
    """Test OrdinaryKriging class."""

    @pytest.fixture
    def spatial_data(self) -> tuple:
        """Generate spatially correlated data on a grid."""
        np.random.seed(42)
        x = np.linspace(0, 10, 6)
        y = np.linspace(0, 10, 6)
        xx, yy = np.meshgrid(x, y)
        coords = np.column_stack([xx.ravel(), yy.ravel()])
        # Spatially correlated values (smooth surface)
        values = np.sin(coords[:, 0] * 0.3) + np.cos(coords[:, 1] * 0.3)
        return coords, values

    def test_init_defaults(self) -> None:
        ok = OrdinaryKriging()
        assert ok.variogram_model == "spherical"
        assert ok.n_lags == 15

    def test_fit_estimates_variogram(self, spatial_data: tuple) -> None:
        coords, values = spatial_data
        ok = OrdinaryKriging(variogram_model="spherical")
        ok.fit(coords, values)

        assert ok.sill > 0
        assert ok.range_param > 0
        assert ok.nugget >= 0

    def test_predict_returns_predictions_and_variances(self, spatial_data: tuple) -> None:
        coords, values = spatial_data
        ok = OrdinaryKriging(variogram_model="spherical")
        ok.fit(coords, values)

        targets = np.array([[5.0, 5.0], [2.5, 7.5]])
        preds, variances = ok.predict(targets)

        assert preds.shape == (2,)
        assert variances.shape == (2,)
        assert all(v >= 0 for v in variances)

    def test_predict_at_known_point(self, spatial_data: tuple) -> None:
        """Prediction at a known point should be close to the known value."""
        coords, values = spatial_data
        ok = OrdinaryKriging(variogram_model="spherical")
        ok.fit(coords, values)

        # Predict at first known point
        pred, var = ok.predict(coords[:1])
        np.testing.assert_allclose(pred[0], values[0], atol=0.5)

    def test_predict_before_fit_raises(self) -> None:
        ok = OrdinaryKriging()
        with pytest.raises(ValueError, match="Must call fit"):
            ok.predict(np.array([[0.0, 0.0]]))

    def test_fit_too_few_points(self) -> None:
        coords = np.array([[0.0, 0.0], [1.0, 1.0]])
        values = np.array([1.0, 2.0])
        ok = OrdinaryKriging()
        with pytest.raises(ValueError, match="at least 3"):
            ok.fit(coords, values)

    def test_exponential_variogram(self, spatial_data: tuple) -> None:
        coords, values = spatial_data
        ok = OrdinaryKriging(variogram_model="exponential")
        ok.fit(coords, values)

        targets = np.array([[5.0, 5.0]])
        preds, variances = ok.predict(targets)
        assert preds.shape == (1,)

    def test_gaussian_variogram(self, spatial_data: tuple) -> None:
        coords, values = spatial_data
        ok = OrdinaryKriging(variogram_model="gaussian")
        ok.fit(coords, values)

        targets = np.array([[5.0, 5.0]])
        preds, variances = ok.predict(targets)
        assert preds.shape == (1,)
