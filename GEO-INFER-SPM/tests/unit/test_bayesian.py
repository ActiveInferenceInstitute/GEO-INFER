"""
Unit tests for Bayesian analysis functionality
"""

import numpy as np
import pytest

from geo_infer_spm.models.data_models import SPMData, DesignMatrix
from geo_infer_spm.core.bayesian import BayesianSPM


class TestBayesianSPM:
    """Test BayesianSPM class functionality."""

    def setup_method(self):
        """Set up test data."""
        np.random.seed(42)
        n_points = 50
        n_regressors = 3

        # Create test data
        self.coordinates = np.column_stack([
            np.random.uniform(-180, 180, n_points),
            np.random.uniform(-90, 90, n_points)
        ])
        self.X = np.random.randn(n_points, n_regressors)
        self.beta_true = np.array([1.0, 2.0, -1.5])
        self.y = self.X @ self.beta_true + 0.1 * np.random.randn(n_points)

        self.spm_data = SPMData(data=self.y, coordinates=self.coordinates, crs='EPSG:4326')
        self.design_matrix = DesignMatrix(matrix=self.X, names=['intercept', 'x1', 'x2'])

        self.bayesian_spm = BayesianSPM()

    def test_initialization(self):
        """Test BayesianSPM initialization."""
        assert self.bayesian_spm.model_type == "hierarchical_glm"
        assert self.bayesian_spm.model_spec is None
        assert isinstance(self.bayesian_spm.priors, dict)

    def test_default_priors(self):
        """Test default prior specification."""
        priors = self.bayesian_spm._default_priors(3)

        required_keys = ['beta', 'sigma', 'beta_intercept']
        for key in required_keys:
            assert key in priors
            assert 'type' in priors[key]

    def test_empirical_bayes_glm(self):
        """Test empirical Bayes GLM fitting."""
        # Force empirical Bayes mode
        self.bayesian_spm.model_type = "empirical_bayes"

        result = self.bayesian_spm.fit_bayesian_glm(
            self.spm_data,
            self.design_matrix.matrix,
            n_samples=100,
            n_tune=50
        )

        assert result.beta_coefficients.shape == (3,)
        assert result.residuals.shape == (50,)
        assert 'method' in result.model_diagnostics
        assert result.model_diagnostics['method'] == 'Empirical_Bayes_GLM'

    def test_pymc3_fallback(self):
        """Test PyMC3 fallback behavior."""
        # This should work even if PyMC3 is not available
        try:
            result = self.bayesian_spm.fit_bayesian_glm(
                self.spm_data,
                self.design_matrix.matrix,
                n_samples=50,
                n_tune=25
            )
            assert result is not None
        except ImportError:
            # Should fallback to empirical Bayes
            pytest.skip("PyMC3 not available, testing fallback")

    def test_posterior_probability_map(self):
        """Test posterior probability map computation."""
        # First fit a model
        self.bayesian_spm.model_type = "empirical_bayes"
        result = self.bayesian_spm.fit_bayesian_glm(
            self.spm_data,
            self.design_matrix.matrix
        )

        # Create mock statistical map
        stat_map = np.random.randn(50)

        # This should work with empirical Bayes
        posterior_prob = self.bayesian_spm.posterior_probability_map(stat_map, threshold=0.95)

        assert posterior_prob.shape == stat_map.shape
        assert np.all((posterior_prob >= 0) & (posterior_prob <= 1))

    def test_bayesian_model_comparison(self):
        """Test Bayesian model comparison."""
        # Create two simple models
        self.bayesian_spm.model_type = "empirical_bayes"

        model1 = self.bayesian_spm.fit_bayesian_glm(
            self.spm_data,
            self.design_matrix.matrix[:, :2]  # Fewer parameters
        )

        model2 = self.bayesian_spm.fit_bayesian_glm(
            self.spm_data,
            self.design_matrix.matrix  # All parameters
        )

        comparison = self.bayesian_spm.bayesian_model_comparison([model1, model2])

        assert 'method' in comparison
        assert 'best_model_index' in comparison
        assert comparison['best_model_index'] in [0, 1]

    def test_spatial_hierarchical_model(self):
        """Test spatial hierarchical model."""
        spatial_structure = {
            'n_basis': 5,
            'scale': 10.0
        }

        result = self.bayesian_spm.spatial_hierarchical_model(
            self.spm_data,
            self.design_matrix.matrix,
            spatial_structure
        )

        assert result.beta_coefficients.shape[0] > 3  # Should include spatial basis
        assert result.model_diagnostics.get('spatial_hierarchical') == True

    def test_variational_inference(self):
        """Test variational inference approximation."""
        result = self.bayesian_spm.variational_inference(
            self.spm_data,
            self.design_matrix.matrix,
            n_iterations=20
        )

        assert result.beta_coefficients.shape == (3,)
        assert 'method' in result.model_diagnostics
        assert result.model_diagnostics['method'] == 'Variational_Inference'


class TestBayesianModelTypes:
    """Test different Bayesian model types."""

    def setup_method(self):
        """Set up test data."""
        np.random.seed(42)
        n_points = 30

        coordinates = np.column_stack([
            np.random.uniform(-180, 180, n_points),
            np.random.uniform(-90, 90, n_points)
        ])
        X = np.random.randn(n_points, 2)
        y = X @ np.array([1.5, -0.5]) + 0.2 * np.random.randn(n_points)

        self.spm_data = SPMData(data=y, coordinates=coordinates, crs='EPSG:4326')
        self.design_matrix = DesignMatrix(matrix=X, names=['intercept', 'slope'])

    def test_hierarchical_glm_model(self):
        """Test hierarchical GLM model specification."""
        bayesian_spm = BayesianSPM(model_type="hierarchical_glm")

        # Should initialize with hierarchical model type
        assert bayesian_spm.model_type == "hierarchical_glm"

        # Test fitting (should fallback to empirical Bayes if PyMC3 unavailable)
        result = bayesian_spm.fit_bayesian_glm(
            self.spm_data,
            self.design_matrix.matrix,
            n_samples=50,
            n_tune=25
        )

        assert result is not None

    def test_spatial_hierarchical_model(self):
        """Test spatial hierarchical model."""
        bayesian_spm = BayesianSPM(model_type="spatial_hierarchical")

        spatial_structure = {
            'n_basis': 3,
            'scale': 5.0
        }

        result = bayesian_spm.spatial_hierarchical_model(
            self.spm_data,
            self.design_matrix.matrix,
            spatial_structure
        )

        # Should include spatial basis functions
        assert result.beta_coefficients.shape[0] >= 2  # At least original parameters
        assert result.model_diagnostics.get('spatial_hierarchical') == True


class TestBayesianDiagnostics:
    """Test Bayesian diagnostic and utility functions."""

    def test_r_hat_computation_placeholder(self):
        """Test R-hat computation (placeholder)."""
        bayesian_spm = BayesianSPM()

        # Mock trace object
        class MockTrace:
            def __init__(self):
                self.posterior = type('obj', (object,), {
                    'dims': {'chain': 4, 'draw': 100}
                })()

        mock_trace = MockTrace()
        r_hat = bayesian_spm._compute_r_hat(mock_trace)

        # Should return array of appropriate shape
        assert isinstance(r_hat, np.ndarray)
        assert len(r_hat) == 4  # Number of chains

    def test_ess_computation_placeholder(self):
        """Test ESS computation (placeholder)."""
        bayesian_spm = BayesianSPM()

        # Mock trace object
        class MockTrace:
            def __init__(self):
                self.posterior = type('obj', (object,), {
                    'dims': {'chain': 2, 'draw': 200}
                })()

        mock_trace = MockTrace()
        ess = bayesian_spm._compute_ess(mock_trace)

        assert isinstance(ess, np.ndarray)
        assert len(ess) == 1  # Single ESS value

    def test_spatial_basis_creation(self):
        """Test spatial basis function creation for hierarchical models."""
        bayesian_spm = BayesianSPM()

        coordinates = np.random.rand(20, 2) * 100
        spatial_structure = {'n_basis': 5, 'scale': 10.0}

        basis = bayesian_spm._create_spatial_basis(coordinates, spatial_structure)

        assert basis.shape == (20, 5)
        assert np.all(basis >= 0)  # Gaussian basis should be non-negative


class TestBayesianEdgeCases:
    """Test edge cases in Bayesian analysis."""

    def test_insufficient_data(self):
        """Test behavior with very small datasets."""
        coordinates = np.array([[0.0, 0.0], [1.0, 1.0]])
        X = np.array([[1.0, 0.5], [1.0, 1.5]])
        y = np.array([1.0, 2.0])

        spm_data = SPMData(data=y, coordinates=coordinates, crs='EPSG:4326')
        design_matrix = DesignMatrix(matrix=X, names=['intercept', 'slope'])

        bayesian_spm = BayesianSPM()

        # Should handle small datasets gracefully
        result = bayesian_spm.fit_bayesian_glm(spm_data, design_matrix.matrix)

        assert result.beta_coefficients.shape == (2,)

    def test_rank_deficient_design(self):
        """Test with rank deficient design matrix."""
        coordinates = np.random.rand(10, 2) * 100
        X = np.ones((10, 3))  # Rank deficient
        X[:, 1] = np.random.randn(10) * 0.01  # Nearly constant
        y = np.random.randn(10)

        spm_data = SPMData(data=y, coordinates=coordinates, crs='EPSG:4326')
        design_matrix = DesignMatrix(matrix=X, names=['int', 'x1', 'x2'])

        bayesian_spm = BayesianSPM()

        # Should handle rank deficiency
        result = bayesian_spm.fit_bayesian_glm(spm_data, design_matrix.matrix)

        assert result.beta_coefficients.shape == (3,)

    def test_extreme_parameter_values(self):
        """Test with extreme parameter values."""
        coordinates = np.random.rand(20, 2) * 100
        X = np.random.randn(20, 2) * 1000  # Very large values
        y = X @ np.array([0.001, -0.002]) + 0.0001 * np.random.randn(20)  # Very small coefficients

        spm_data = SPMData(data=y, coordinates=coordinates, crs='EPSG:4326')
        design_matrix = DesignMatrix(matrix=X, names=['x1', 'x2'])

        bayesian_spm = BayesianSPM()

        result = bayesian_spm.fit_bayesian_glm(spm_data, design_matrix.matrix)

        # Should still produce reasonable results
        assert result.beta_coefficients.shape == (2,)
        assert np.all(np.isfinite(result.beta_coefficients))

    def test_posterior_probability_edge_cases(self):
        """Test posterior probability computation edge cases."""
        bayesian_spm = BayesianSPM()

        # Test with no posterior samples
        stat_map = np.array([1.0, 2.0, 3.0])

        with pytest.raises(ValueError, match="Model must be fitted"):
            bayesian_spm.posterior_probability_map(stat_map)

    def test_model_comparison_single_model(self):
        """Test model comparison with single model."""
        bayesian_spm = BayesianSPM()

        # Create a simple model
        coordinates = np.random.rand(10, 2) * 100
        X = np.random.randn(10, 2)
        y = X @ np.array([1.0, -0.5]) + 0.1 * np.random.randn(10)

        spm_data = SPMData(data=y, coordinates=coordinates, crs='EPSG:4326')
        design_matrix = DesignMatrix(matrix=X, names=['int', 'slope'])

        model = bayesian_spm.fit_bayesian_glm(spm_data, design_matrix.matrix)

        # Single model comparison should work
        comparison = bayesian_spm.bayesian_model_comparison([model])

        assert 'method' in comparison
        assert comparison['best_model_index'] == 0
