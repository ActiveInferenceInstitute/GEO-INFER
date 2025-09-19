"""
Unit tests for General Linear Model implementation
"""

import numpy as np
import pytest
from scipy import stats

from geo_infer_spm.models.data_models import SPMData, DesignMatrix
from geo_infer_spm.core.glm import GeneralLinearModel, fit_glm


class TestGeneralLinearModel:
    """Test GLM implementation."""

    def setup_method(self):
        """Set up test data."""
        np.random.seed(42)
        n_points = 100
        n_regressors = 3

        # Generate synthetic data with proper coordinate ranges
        self.coordinates = np.column_stack([
            np.random.uniform(-180, 180, n_points),  # longitude
            np.random.uniform(-90, 90, n_points)     # latitude
        ])
        self.X = np.random.randn(n_points, n_regressors)
        self.beta_true = np.array([1.0, 2.0, -1.5])
        self.y = self.X @ self.beta_true + 0.1 * np.random.randn(n_points)

        # Create SPMData and DesignMatrix
        self.spm_data = SPMData(
            data=self.y,
            coordinates=self.coordinates,
            crs='EPSG:4326'
        )

        self.design_matrix = DesignMatrix(
            matrix=self.X,
            names=[f'regressor_{i}' for i in range(n_regressors)]
        )

    def test_glm_initialization(self):
        """Test GLM initialization."""
        glm = GeneralLinearModel(self.design_matrix)
        assert glm.design_matrix is self.design_matrix
        assert glm.beta is None
        assert glm.residuals is None

    def test_ols_fitting(self):
        """Test OLS fitting."""
        glm = GeneralLinearModel(self.design_matrix)
        result = glm.fit(self.spm_data, method="OLS")

        # Check that beta estimates are close to true values
        np.testing.assert_allclose(result.beta_coefficients, self.beta_true, atol=0.1)

        # Check residuals
        assert result.residuals.shape == (len(self.y),)
        assert np.mean(result.residuals) < 0.1  # Should be approximately zero

        # Check diagnostics
        assert 'r_squared' in result.model_diagnostics
        assert 'f_statistic' in result.model_diagnostics
        assert result.model_diagnostics['r_squared'] > 0.9  # High R² for synthetic data

    def test_robust_fitting(self):
        """Test robust fitting with outliers."""
        # Add outliers to data
        y_outliers = self.y.copy()
        outlier_indices = np.random.choice(len(y_outliers), size=5, replace=False)
        y_outliers[outlier_indices] += 10  # Add large outliers

        spm_data_outliers = SPMData(
            data=y_outliers,
            coordinates=self.coordinates
        )

        glm_ols = GeneralLinearModel(self.design_matrix)
        glm_robust = GeneralLinearModel(self.design_matrix)

        result_ols = glm_ols.fit(spm_data_outliers, method="OLS")
        result_robust = glm_robust.fit(spm_data_outliers, method="robust")

        # Robust estimates should be closer to true values
        ols_error = np.mean((result_ols.beta_coefficients - self.beta_true)**2)
        robust_error = np.mean((result_robust.beta_coefficients - self.beta_true)**2)

        assert robust_error < ols_error

    def test_spatial_regularization(self):
        """Test spatial regularization."""
        glm = GeneralLinearModel(self.design_matrix)

        # Fit with spatial regularization
        spatial_params = {'lambda': 0.1, 'spatial_weights': None}
        result = glm.fit(self.spm_data, method="spatial", spatial_regularization=spatial_params)

        # Should still produce valid results
        assert result.beta_coefficients.shape == (self.design_matrix.n_regressors,)
        assert 'r_squared' in result.model_diagnostics

    def test_prediction(self):
        """Test prediction functionality."""
        glm = GeneralLinearModel(self.design_matrix)
        result = glm.fit(self.spm_data, method="OLS")

        # Predict on training data
        predictions = glm.predict()

        # Predictions should be close to original data
        np.testing.assert_allclose(predictions, self.y, atol=0.1)

    def test_coefficient_testing(self):
        """Test coefficient significance testing."""
        glm = GeneralLinearModel(self.design_matrix)
        result = glm.fit(self.spm_data, method="OLS")

        # Test first coefficient (should be significant)
        test_result = glm.get_coefficient_test(0)

        assert 't_statistic' in test_result
        assert 'p_value' in test_result
        assert 'standard_error' in test_result
        assert test_result['p_value'] < 0.05  # Should be significant

    def test_fit_glm_convenience_function(self):
        """Test the fit_glm convenience function."""
        result = fit_glm(self.spm_data, self.design_matrix)

        assert result.beta_coefficients.shape == (self.design_matrix.n_regressors,)
        assert result.residuals.shape == (len(self.y),)
        assert result.model_diagnostics['r_squared'] > 0.9


class TestGLMEdgeCases:
    """Test GLM edge cases and error conditions."""

    def test_rank_deficient_design(self):
        """Test handling of rank deficient design matrices."""
        np.random.seed(42)
        n_points = 50

        # Create rank deficient design (last column is linear combination)
        X = np.random.randn(n_points, 3)
        X[:, 2] = X[:, 0] + X[:, 1]  # Rank deficient

        y = np.random.randn(n_points)

        spm_data = SPMData(data=y, coordinates=np.random.rand(n_points, 2))
        design_matrix = DesignMatrix(matrix=X, names=['x1', 'x2', 'x1_plus_x2'])

        glm = GeneralLinearModel(design_matrix)

        # Should handle rank deficiency gracefully
        result = glm.fit(spm_data, method="OLS")

        # Should still produce results (though with warnings)
        assert result.beta_coefficients.shape == (3,)
        assert result.residuals.shape == (n_points,)

    def test_insufficient_data(self):
        """Test error handling for insufficient data."""
        X = np.random.randn(3, 2)  # Only 3 observations, 2 regressors
        y = np.random.randn(3)

        spm_data = SPMData(data=y, coordinates=np.random.rand(3, 2))
        design_matrix = DesignMatrix(matrix=X, names=['x1', 'x2'])

        glm = GeneralLinearModel(design_matrix)

        # Should raise error for insufficient degrees of freedom
        with pytest.raises(ValueError):
            glm.fit(spm_data, method="OLS")

    def test_mismatched_dimensions(self):
        """Test error handling for mismatched dimensions."""
        X = np.random.randn(100, 2)
        y = np.random.randn(50)  # Different size

        spm_data = SPMData(data=y, coordinates=np.random.rand(50, 2))
        design_matrix = DesignMatrix(matrix=X, names=['x1', 'x2'])

        glm = GeneralLinearModel(design_matrix)

        with pytest.raises(ValueError, match="incompatible dimensions"):
            glm.fit(spm_data, method="OLS")
