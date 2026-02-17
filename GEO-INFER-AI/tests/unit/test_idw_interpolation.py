"""
Unit tests for IDW interpolation.
"""

import numpy as np
import pytest

from geo_infer_ai.models.predictive.spatial_predictor import IDWInterpolator


class TestIDWInterpolator:
    """Test IDWInterpolator class."""

    @pytest.fixture
    def simple_data(self) -> tuple:
        """Known points with a simple spatial pattern."""
        coords = np.array([
            [0.0, 0.0],
            [1.0, 0.0],
            [0.0, 1.0],
            [1.0, 1.0],
        ])
        values = np.array([0.0, 1.0, 1.0, 2.0])
        return coords, values

    def test_init_defaults(self) -> None:
        idw = IDWInterpolator()
        assert idw.power == 2.0
        assert idw.min_points == 3

    def test_init_invalid_power(self) -> None:
        with pytest.raises(ValueError, match="power must be positive"):
            IDWInterpolator(power=-1.0)

    def test_init_invalid_min_points(self) -> None:
        with pytest.raises(ValueError, match="min_points must be at least 1"):
            IDWInterpolator(min_points=0)

    def test_fit_predict_exact_match(self, simple_data: tuple) -> None:
        """Predictions at known points should return known values."""
        coords, values = simple_data
        idw = IDWInterpolator(power=2.0)
        idw.fit(coords, values)

        predictions = idw.predict(coords)
        np.testing.assert_allclose(predictions, values, atol=1e-6)

    def test_predict_interpolation(self, simple_data: tuple) -> None:
        """Prediction at center should be weighted average."""
        coords, values = simple_data
        idw = IDWInterpolator(power=2.0)
        idw.fit(coords, values)

        center = np.array([[0.5, 0.5]])
        pred = idw.predict(center)

        # At the center, all four corners are equidistant
        # so prediction should be the mean of values
        expected = np.mean(values)
        np.testing.assert_allclose(pred[0], expected, atol=0.01)

    def test_predict_closer_to_higher_value(self) -> None:
        """Points closer to higher-value samples get higher predictions."""
        coords = np.array([[0.0, 0.0], [10.0, 0.0]])
        values = np.array([0.0, 10.0])

        idw = IDWInterpolator(power=2.0, min_points=1)
        idw.fit(coords, values)

        # Point close to second sample
        target = np.array([[8.0, 0.0]])
        pred = idw.predict(target)
        assert pred[0] > 5.0  # Should be closer to 10 than to 0

    def test_predict_before_fit_raises(self) -> None:
        idw = IDWInterpolator()
        with pytest.raises(ValueError, match="Must call fit"):
            idw.predict(np.array([[0.0, 0.0]]))

    def test_fit_mismatched_shapes(self) -> None:
        coords = np.array([[0.0, 0.0], [1.0, 1.0]])
        values = np.array([1.0, 2.0, 3.0])
        idw = IDWInterpolator()
        with pytest.raises(ValueError, match="same number of rows"):
            idw.fit(coords, values)

    def test_max_distance(self) -> None:
        coords = np.array([[0.0, 0.0], [1.0, 0.0], [100.0, 0.0]])
        values = np.array([1.0, 2.0, 100.0])

        idw = IDWInterpolator(power=2.0, min_points=1, max_distance=5.0)
        idw.fit(coords, values)

        target = np.array([[0.5, 0.0]])
        pred = idw.predict(target)
        # Should primarily use first two points (within distance 5)
        assert pred[0] < 10.0
