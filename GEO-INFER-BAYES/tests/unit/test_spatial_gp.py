"""
Unit tests for the SpatialGP model.
"""

import numpy as np
import pytest
from numpy.testing import assert_allclose, assert_array_equal, assert_array_almost_equal

from geo_infer_bayes.models import SpatialGP


class TestSpatialGP:
    """Tests for the SpatialGP model."""
    
    @pytest.fixture
    def sample_data(self):
        """Generate sample data for testing."""
        # Generate 2D grid of points
        x = np.linspace(0, 1, 5)
        y = np.linspace(0, 1, 5)
        X1, X2 = np.meshgrid(x, y)
        X = np.column_stack((X1.flatten(), X2.flatten()))
        
        # Generate target values from a known function
        y = np.sin(X[:, 0] * 3) * np.cos(X[:, 1] * 3)
        
        return X, y
    
    @pytest.fixture
    def sample_model(self):
        """Create a sample model for testing."""
        return SpatialGP(
            kernel='rbf',
            lengthscale=0.5,
            variance=1.0,
            noise=0.1
        )
    
    def test_init(self, sample_model):
        """Test model initialization."""
        assert sample_model.kernel_type == 'rbf'
        assert sample_model.lengthscale == 0.5
        assert sample_model.variance == 1.0
        assert sample_model.noise == 0.1
        assert sample_model.jitter > 0
    
    def test_kernel_types(self):
        """Test different kernel types."""
        for kernel in ['rbf', 'matern', 'exponential']:
            model = SpatialGP(kernel=kernel)
            assert model.kernel_type == kernel
            assert callable(model.kernel_fn)
    
    def test_rbf_kernel(self, sample_model):
        """Test RBF kernel computation."""
        X1 = np.array([[0, 0], [1, 1]])
        X2 = np.array([[0, 0], [1, 0]])
        
        K = sample_model._rbf_kernel(X1, X2)
        
        # Check shape
        assert K.shape == (2, 2)
        
        # Check diagonal elements
        assert K[0, 0] == sample_model.variance
        
        # Check symmetry for square matrices
        K_square = sample_model._rbf_kernel(X1, X1)
        assert_allclose(K_square, K_square.T)
    
    def test_fit_predict(self, sample_data, sample_model):
        """Test fitting and prediction."""
        X, y = sample_data
        
        # Fit model
        model = sample_model.fit(X, y)
        
        # Should return self
        assert model is sample_model
        
        # Check that training data is stored
        assert_array_equal(model.X_train, X)
        assert_array_equal(model.y_train, y)
        
        # Test prediction
        y_pred = model.predict(X)
        
        # Shape should match
        assert y_pred.shape == y.shape
        
        # Predictions at training points should be close to observed values
        assert_allclose(y_pred, y, rtol=0.1, atol=0.1)
        
        # Test prediction with standard deviation
        y_pred, y_std = model.predict(X, return_std=True)
        
        # Shapes should match
        assert y_pred.shape == y.shape
        assert y_std.shape == y.shape
        
        # Standard deviations should be positive
        assert np.all(y_std > 0)
    
    def test_log_likelihood(self, sample_data, sample_model):
        """Test log likelihood computation."""
        X, y = sample_data
        
        # Fit model
        model = sample_model.fit(X, y)
        
        # Compute log likelihood with current parameters
        theta = {
            'lengthscale': model.lengthscale,
            'variance': model.variance,
            'noise': model.noise
        }
        data = {'X': X, 'y': y}
        
        ll = model.log_likelihood(theta, data)
        
        # Should be a scalar
        assert np.isscalar(ll)
        
        # Should be finite
        assert np.isfinite(ll)
        
        # Compare with worse parameters
        worse_theta = {
            'lengthscale': 0.01,  # Too small
            'variance': model.variance,
            'noise': model.noise
        }
        
        worse_ll = model.log_likelihood(worse_theta, data)
        
        # Better parameters should have higher likelihood
        assert ll > worse_ll
    
    def test_log_prior(self, sample_model):
        """Test log prior computation."""
        # Parameters within prior range
        theta = {
            'lengthscale': 1.0,
            'variance': 1.0,
            'noise': 0.1
        }
        
        lp = sample_model.log_prior(theta)
        
        # Should be a scalar
        assert np.isscalar(lp)
        
        # Should be finite
        assert np.isfinite(lp)
        
        # Test with Matern kernel
        matern_model = SpatialGP(kernel='matern', degree=1.5)
        theta['degree'] = 1.5
        
        lp_matern = matern_model.log_prior(theta)
        
        # Should be a scalar
        assert np.isscalar(lp_matern)
        
        # Should be finite
        assert np.isfinite(lp_matern)
        
        # Test with degree outside range
        theta['degree'] = 5.0  # Outside default range
        lp_bad = matern_model.log_prior(theta)
        
        # Should be -inf
        assert lp_bad == -np.inf 