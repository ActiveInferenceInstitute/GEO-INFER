"""
Tests for the regression models module.
"""

import numpy as np
import pytest
from geo_infer_math.models.regression import (
    OrdinaryLeastSquares, SpatialLagModel, GeographicallyWeightedRegression,
    SpatialErrorModel, SpatialDurbinModel, spatial_regression_analysis
)

class TestOrdinaryLeastSquares:
    """Test Ordinary Least Squares regression."""

    def setup_method(self):
        """Set up test data."""
        np.random.seed(42)
        n_samples, n_features = 100, 3

        # Generate synthetic data
        self.X = np.random.randn(n_samples, n_features)
        true_beta = np.array([1.5, -2.0, 0.5])
        self.y = self.X @ true_beta + 0.1 * np.random.randn(n_samples)

    def test_ols_fit(self):
        """Test OLS model fitting."""
        model = OrdinaryLeastSquares()
        model.fit(self.X, self.y)

        assert model.is_fitted
        assert model.coefficients is not None
        assert model.intercept is not None

        # Coefficients should be close to true values
        np.testing.assert_allclose(model.coefficients, [1.5, -2.0, 0.5], atol=0.2)

    def test_ols_predict(self):
        """Test OLS prediction."""
        model = OrdinaryLeastSquares()
        model.fit(self.X, self.y)

        predictions = model.predict(self.X)

        assert len(predictions) == len(self.y)
        assert predictions.shape == self.y.shape

    def test_ols_score(self):
        """Test OLS R-squared calculation."""
        model = OrdinaryLeastSquares()
        model.fit(self.X, self.y)

        r_squared = model.score(self.X, self.y)

        assert 0 <= r_squared <= 1
        assert r_squared > 0.8  # Should be high for synthetic data

class TestSpatialLagModel:
    """Test Spatial Lag (SAR) regression model."""

    def setup_method(self):
        """Set up test data with spatial structure."""
        np.random.seed(42)
        n_samples = 50

        # Create coordinates
        self.coords = np.random.rand(n_samples, 2) * 10

        # Generate spatial weights matrix
        from geo_infer_math.core.linalg_tensor import MatrixOperations
        self.weights_matrix = MatrixOperations.spatial_weights_matrix(
            self.coords, method='knn', k=5
        )

        # Generate synthetic data with spatial lag
        n_features = 2
        self.X = np.random.randn(n_samples, n_features)
        true_beta = np.array([1.0, -0.5])
        rho = 0.3  # Spatial autoregressive parameter

        # Create spatially autocorrelated errors
        noise = np.random.randn(n_samples)
        Wy = self.weights_matrix @ (self.X @ true_beta + noise)
        self.y = rho * Wy + self.X @ true_beta + 0.1 * noise

    def test_sar_fit(self):
        """Test SAR model fitting."""
        model = SpatialLagModel(self.weights_matrix)
        model.fit(self.X, self.y)

        assert model.is_fitted
        assert model.rho is not None
        assert model.beta is not None

        # Rho should be positive (as defined in test data)
        assert model.rho > 0
        assert len(model.beta) == self.X.shape[1]

    def test_sar_predict(self):
        """Test SAR prediction."""
        model = SpatialLagModel(self.weights_matrix)
        model.fit(self.X, self.y)

        predictions = model.predict(self.X)

        assert len(predictions) == len(self.y)
        assert predictions.shape == self.y.shape

class TestGeographicallyWeightedRegression:
    """Test Geographically Weighted Regression."""

    def setup_method(self):
        """Set up test data."""
        np.random.seed(42)
        n_samples = 100

        # Create coordinates
        self.coords = np.random.rand(n_samples, 2) * 10

        # Generate spatially varying coefficients
        self.X = np.random.randn(n_samples, 2)
        self.y = np.zeros(n_samples)

        for i in range(n_samples):
            # Coefficients vary with location
            beta0 = 1 + 0.1 * self.coords[i, 0]
            beta1 = -1 + 0.05 * self.coords[i, 1]
            self.y[i] = beta0 + beta1 * self.X[i, 1] + 0.1 * np.random.randn()

    def test_gwr_fit(self):
        """Test GWR model fitting."""
        model = GeographicallyWeightedRegression(bandwidth=2.0)
        model.fit(self.X, self.y, self.coords)

        assert model.is_fitted
        assert model.bandwidth > 0

    def test_gwr_predict(self):
        """Test GWR prediction."""
        model = GeographicallyWeightedRegression(bandwidth=2.0)
        model.fit(self.X, self.y, self.coords)

        # Predict at subset of locations
        test_indices = np.arange(0, len(self.coords), 10)
        test_coords = self.coords[test_indices]
        test_X = self.X[test_indices]

        predictions = model.predict(test_X, test_coords)

        assert len(predictions) == len(test_indices)
        assert all(np.isfinite(pred) for pred in predictions)

class TestSpatialErrorModel:
    """Test Spatial Error Model."""

    def setup_method(self):
        """Set up test data."""
        np.random.seed(42)
        n_samples = 50

        # Create coordinates and weights
        self.coords = np.random.rand(n_samples, 2) * 10
        from geo_infer_math.core.linalg_tensor import MatrixOperations
        self.weights_matrix = MatrixOperations.spatial_weights_matrix(
            self.coords, method='knn', k=5
        )

        # Generate data
        self.X = np.random.randn(n_samples, 2)
        true_beta = np.array([1.5, -0.8])
        lambda_param = 0.2

        # Create spatially autocorrelated errors
        epsilon = np.random.randn(n_samples)
        We = self.weights_matrix @ epsilon
        self.y = self.X @ true_beta + lambda_param * We

    def test_sem_fit(self):
        """Test SEM model fitting."""
        model = SpatialErrorModel(self.weights_matrix)
        model.fit(self.X, self.y)

        assert model.is_fitted
        assert model.lambda_param is not None
        assert model.beta is not None

        assert len(model.beta) == self.X.shape[1]

    def test_sem_predict(self):
        """Test SEM prediction."""
        model = SpatialErrorModel(self.weights_matrix)
        model.fit(self.X, self.y)

        predictions = model.predict(self.X)

        assert len(predictions) == len(self.y)

class TestSpatialDurbinModel:
    """Test Spatial Durbin Model."""

    def setup_method(self):
        """Set up test data."""
        np.random.seed(42)
        n_samples = 50

        # Create coordinates and weights
        self.coords = np.random.rand(n_samples, 2) * 10
        from geo_infer_math.core.linalg_tensor import MatrixOperations
        self.weights_matrix = MatrixOperations.spatial_weights_matrix(
            self.coords, method='knn', k=5
        )

        # Generate data
        self.X = np.random.randn(n_samples, 2)
        rho = 0.1
        theta = np.array([0.5, -0.3])

        # Create spatial Durbin structure
        WX = self.weights_matrix @ self.X
        beta = np.array([1.0, 0.5])
        Wy = self.weights_matrix @ (self.X @ beta + WX @ theta)

        self.y = rho * Wy + self.X @ beta + WX @ theta + 0.1 * np.random.randn(n_samples)

    def test_sdm_fit(self):
        """Test SDM model fitting."""
        model = SpatialDurbinModel(self.weights_matrix)
        model.fit(self.X, self.y)

        assert model.is_fitted
        assert model.rho is not None
        assert model.beta is not None
        assert model.theta is not None

        assert len(model.beta) == self.X.shape[1]
        assert len(model.theta) == self.X.shape[1]

    def test_sdm_predict(self):
        """Test SDM prediction."""
        model = SpatialDurbinModel(self.weights_matrix)
        model.fit(self.X, self.y)

        predictions = model.predict(self.X)

        assert len(predictions) == len(self.y)

class TestSpatialRegressionAnalysis:
    """Test comprehensive spatial regression analysis."""

    def setup_method(self):
        """Set up test data."""
        np.random.seed(42)
        n_samples = 100

        # Create coordinates
        self.coords = np.random.rand(n_samples, 2) * 10

        # Generate synthetic data
        self.X = np.random.randn(n_samples, 2)
        self.y = self.X @ np.array([1.5, -0.8]) + 0.1 * np.random.randn(n_samples)

    def test_ols_analysis(self):
        """Test OLS regression analysis."""
        result = spatial_regression_analysis(self.X, self.y, self.coords, model_type='ols')

        assert 'model' in result
        assert 'coefficients' in result
        assert 'intercept' in result
        assert 'r_squared' in result

        assert len(result['coefficients']) == self.X.shape[1]
        assert 0 <= result['r_squared'] <= 1

    def test_sar_analysis(self):
        """Test SAR regression analysis."""
        result = spatial_regression_analysis(self.X, self.y, self.coords, model_type='sar')

        assert 'model' in result
        assert 'rho' in result
        assert 'coefficients' in result

        assert isinstance(result['rho'], (int, float))
        assert len(result['coefficients']) == self.X.shape[1]

    def test_gwr_analysis(self):
        """Test GWR regression analysis."""
        result = spatial_regression_analysis(self.X, self.y, self.coords, model_type='gwr')

        assert 'model' in result
        assert 'bandwidth' in result

        assert result['bandwidth'] > 0

    def test_sem_analysis(self):
        """Test SEM regression analysis."""
        result = spatial_regression_analysis(self.X, self.y, self.coords, model_type='sem')

        assert 'model' in result
        assert 'lambda' in result
        assert 'coefficients' in result

        assert isinstance(result['lambda'], (int, float))
        assert len(result['coefficients']) == self.X.shape[1]

    def test_sdm_analysis(self):
        """Test SDM regression analysis."""
        result = spatial_regression_analysis(self.X, self.y, self.coords, model_type='sdm')

        assert 'model' in result
        assert 'rho' in result
        assert 'direct_effects' in result
        assert 'indirect_effects' in result

        assert len(result['direct_effects']) == self.X.shape[1]
        assert len(result['indirect_effects']) == self.X.shape[1]

    def test_invalid_model_type(self):
        """Test handling of invalid model type."""
        with pytest.raises(ValueError):
            spatial_regression_analysis(self.X, self.y, self.coords, model_type='invalid')

class TestRegressionRobustness:
    """Test regression model robustness."""

    def test_small_dataset(self):
        """Test models with small datasets."""
        X = np.random.randn(5, 2)
        y = X @ np.array([1, -1]) + 0.1 * np.random.randn(5)
        coords = np.random.rand(5, 2)

        # OLS should work with small data
        model = OrdinaryLeastSquares()
        model.fit(X, y)

        assert model.is_fitted

    def test_perfect_fit(self):
        """Test models with perfect fit."""
        X = np.random.randn(50, 2)
        beta_true = np.array([2.0, -1.5])
        y = X @ beta_true  # Perfect fit, no noise

        model = OrdinaryLeastSquares()
        model.fit(X, y)

        # Should achieve perfect R-squared
        r_squared = model.score(X, y)
        assert abs(r_squared - 1.0) < 1e-10

        # Coefficients should be exact
        np.testing.assert_allclose(model.coefficients, beta_true, atol=1e-10)
