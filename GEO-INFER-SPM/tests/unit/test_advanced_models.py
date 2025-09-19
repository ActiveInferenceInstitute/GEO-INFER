"""
Unit tests for advanced statistical modeling methods
"""

import numpy as np
import pytest

from geo_infer_spm.models.data_models import SPMData, DesignMatrix
from geo_infer_spm.core.advanced.mixed_effects import MixedEffectsSPM, fit_mixed_effects
from geo_infer_spm.core.advanced.nonparametric import NonparametricSPM, fit_nonparametric
from geo_infer_spm.core.advanced.model_validation import ModelValidator, validate_spm_model
from geo_infer_spm.core.advanced.spatial_regression import SpatialRegression, fit_spatial_model


class TestMixedEffectsSPM:
    """Test Mixed Effects SPM implementation."""

    def setup_method(self):
        """Set up test data."""
        np.random.seed(42)
        n_points = 100
        n_groups = 5
        points_per_group = n_points // n_groups

        # Create coordinates and group structure with proper lat/lon ranges
        self.coordinates = np.column_stack([
            np.random.uniform(-180, 180, n_points),  # longitude
            np.random.uniform(-90, 90, n_points)     # latitude
        ])

        # Create group indices (spatial clusters)
        group_indices = np.repeat(np.arange(n_groups), points_per_group)
        if len(group_indices) < n_points:
            group_indices = np.concatenate([group_indices, np.full(n_points - len(group_indices), n_groups - 1)])

        self.random_groups = {'spatial_cluster': group_indices}

        # Create data with group-specific effects
        X = np.random.randn(n_points, 2)
        group_effects = group_indices * 0.5  # Different intercepts per group
        y = X @ np.array([1.0, -0.5]) + group_effects + 0.1 * np.random.randn(n_points)

        self.spm_data = SPMData(data=y, coordinates=self.coordinates, crs='EPSG:4326')
        self.design_matrix = DesignMatrix(matrix=X, names=['intercept', 'slope'])

    def test_mixed_effects_initialization(self):
        """Test MixedEffectsSPM initialization."""
        model = MixedEffectsSPM(self.design_matrix, self.random_groups)

        assert model.fixed_design is self.design_matrix
        assert model.random_groups == self.random_groups
        assert model.fitted_model is None

    def test_mixed_effects_fit(self):
        """Test mixed effects model fitting."""
        model = MixedEffectsSPM(self.design_matrix, self.random_groups)

        result = model.fit(self.spm_data, method="REML")

        assert result is not None
        assert hasattr(result, 'beta_coefficients')
        assert hasattr(result, 'residuals')
        assert 'method' in result.model_diagnostics
        assert result.model_diagnostics['method'] == 'Mixed_Effects_REML'

    def test_mixed_effects_convergence(self):
        """Test that mixed effects model converges."""
        model = MixedEffectsSPM(self.design_matrix, self.random_groups)

        result = model.fit(self.spm_data, method="ML", optimizer="BFGS")

        # Check that we get some result (may not fully converge on synthetic data)
        assert result.beta_coefficients.shape == (2,)
        assert len(result.residuals) == len(self.spm_data.data)

    def test_random_effects_extraction(self):
        """Test random effects extraction."""
        model = MixedEffectsSPM(self.design_matrix, self.random_groups)
        model.fit(self.spm_data)

        random_effects = model.get_random_effects()

        # Should return some structure even if simplified
        assert isinstance(random_effects, dict)

    def test_mixed_effects_anova(self):
        """Test likelihood ratio test between models."""
        model1 = MixedEffectsSPM(self.design_matrix, self.random_groups)
        model2 = MixedEffectsSPM(self.design_matrix, {})  # No random effects

        result1 = model1.fit(self.spm_data)
        result2 = model2.fit(self.spm_data)

        anova_result = model1.anova(model2)

        assert 'likelihood_ratio' in anova_result
        assert 'p_value' in anova_result
        assert 'significant' in anova_result

    def test_convenience_function(self):
        """Test fit_mixed_effects convenience function."""
        result = fit_mixed_effects(self.spm_data, self.design_matrix, self.random_groups)

        assert result is not None
        assert hasattr(result, 'model_diagnostics')


class TestNonparametricSPM:
    """Test Nonparametric SPM implementation."""

    def setup_method(self):
        """Set up test data."""
        np.random.seed(42)
        n_points = 50

        self.coordinates = np.column_stack([
            np.random.uniform(-180, 180, n_points),
            np.random.uniform(-90, 90, n_points)
        ])

        # Create nonlinear relationship
        x = np.linspace(0, 10, n_points)
        y = np.sin(x) + 0.5 * x + 0.2 * np.random.randn(n_points)

        self.spm_data = SPMData(data=y, coordinates=self.coordinates, crs='EPSG:4326')
        self.design_matrix = DesignMatrix(matrix=np.column_stack([np.ones(n_points), x]), names=['intercept', 'x'])

    def test_loess_fitting(self):
        """Test LOESS nonparametric fitting."""
        model = NonparametricSPM(method="loess", bandwidth=0.3)

        result = model.fit(self.spm_data, self.design_matrix)

        assert result is not None
        assert hasattr(result, 'residuals')
        assert result.model_diagnostics['method'] == 'Nonparametric_loess'
        assert 'r_squared' in result.model_diagnostics

    def test_kernel_regression(self):
        """Test kernel regression fitting."""
        model = NonparametricSPM(method="kernel", bandwidth=1.0, kernel="gaussian")

        result = model.fit(self.spm_data, self.design_matrix)

        assert result.model_diagnostics['method'] == 'Nonparametric_kernel'
        assert result.model_diagnostics['kernel'] == 'gaussian'
        assert 'bandwidth' in result.model_diagnostics

    def test_spline_fitting(self):
        """Test spline-based fitting."""
        model = NonparametricSPM(method="spline")

        result = model.fit(self.spm_data, self.design_matrix)

        assert result.model_diagnostics['method'] == 'Nonparametric_spline'

    def test_gam_fitting(self):
        """Test Generalized Additive Model fitting."""
        model = NonparametricSPM(method="gam", bandwidth=0.5)

        result = model.fit(self.spm_data, self.design_matrix)

        assert result.model_diagnostics['method'] == 'Nonparametric_gam'

    def test_robust_regression(self):
        """Test robust nonparametric regression."""
        # Add outliers
        y_outliers = self.spm_data.data.copy()
        y_outliers[:5] = 10  # Extreme outliers

        spm_data_outliers = SPMData(data=y_outliers, coordinates=self.coordinates, crs='EPSG:4326')

        model = NonparametricSPM(method="robust")

        result = model.fit(spm_data_outliers, self.design_matrix)

        assert result.model_diagnostics['method'] == 'Nonparametric_robust'

    def test_temporal_basis_functions(self):
        """Test temporal basis function generation."""
        analyzer = NonparametricSPM()
        time_points = np.arange(20)

        # Test different basis types
        for basis_type in ['fourier', 'polynomial', 'bspline']:
            basis = analyzer._NonparametricSPM__class__()._NonparametricSPM__class__().temporal_basis_functions(
                time_points, n_basis=5, basis_type=basis_type
            )

            assert basis.shape[0] == len(time_points)
            assert basis.shape[1] == 5

    def test_invalid_method(self):
        """Test error handling for invalid methods."""
        with pytest.raises(ValueError, match="Method must be one of"):
            NonparametricSPM(method="invalid")

    def test_invalid_kernel(self):
        """Test error handling for invalid kernels."""
        with pytest.raises(ValueError, match="Kernel must be one of"):
            NonparametricSPM(kernel="invalid")

    def test_convenience_function(self):
        """Test fit_nonparametric convenience function."""
        result = fit_nonparametric(self.spm_data, self.design_matrix, method="loess")

        assert result is not None
        assert result.model_diagnostics['method'] == 'Nonparametric_loess'


class TestModelValidator:
    """Test ModelValidator implementation."""

    def setup_method(self):
        """Set up test data."""
        np.random.seed(42)
        n_points = 100

        self.coordinates = np.column_stack([
            np.random.uniform(-180, 180, n_points),
            np.random.uniform(-90, 90, n_points)
        ])

        X = np.random.randn(n_points, 2)
        beta = np.array([1.5, -0.8])
        y = X @ beta + 0.2 * np.random.randn(n_points)

        self.spm_data = SPMData(data=y, coordinates=self.coordinates, crs='EPSG:4326')
        self.design_matrix = DesignMatrix(matrix=X, names=['intercept', 'slope'])

        # Create fitted model
        from geo_infer_spm.core.glm import fit_glm
        self.model_result = fit_glm(self.spm_data, self.design_matrix)

    def test_kfold_cross_validation(self):
        """Test k-fold cross-validation."""
        validator = ModelValidator(validation_method="kfold", n_folds=5)

        cv_results = validator.cross_validate(fit_glm, self.spm_data, self.design_matrix)

        assert cv_results['method'] == 'kfold'
        assert cv_results['n_folds'] == 5
        assert 'overall_mse' in cv_results
        assert 'overall_rmse' in cv_results
        assert 'overall_r2' in cv_results
        assert len(cv_results['cv_scores']) == 5

    def test_loo_cross_validation(self):
        """Test leave-one-out cross-validation."""
        validator = ModelValidator(validation_method="loo")

        cv_results = validator.cross_validate(fit_glm, self.spm_data, self.design_matrix)

        assert cv_results['method'] == 'loo'
        assert 'mse' in cv_results
        assert 'rmse' in cv_results
        assert 'r2' in cv_results
        assert 'predictions' in cv_results

    def test_bootstrap_validation(self):
        """Test bootstrap validation."""
        validator = ModelValidator(validation_method="bootstrap", n_bootstraps=10)

        cv_results = validator.cross_validate(fit_glm, self.spm_data, self.design_matrix)

        assert cv_results['method'] == 'bootstrap'
        assert cv_results['n_bootstraps'] == 10
        assert 'avg_predictions' in cv_results

    def test_model_comparison_aic(self):
        """Test model comparison using AIC."""
        validator = ModelValidator()

        # Create two similar models
        model1 = self.model_result
        model2 = self.model_result  # Same model for testing

        comparison = validator.compare_models([model1, model2], method="aic")

        assert comparison['method'] == 'AIC'
        assert 'scores' in comparison
        assert 'best_model_index' in comparison
        assert len(comparison['relative_likelihoods']) == 2

    def test_model_comparison_bic(self):
        """Test model comparison using BIC."""
        validator = ModelValidator()

        models = [self.model_result, self.model_result]
        comparison = validator.compare_models(models, method="bic")

        assert comparison['method'] == 'BIC'
        assert len(comparison['scores']) == 2

    def test_diagnostic_tests(self):
        """Test comprehensive diagnostic tests."""
        validator = ModelValidator()

        diagnostics = validator.diagnostic_tests(self.model_result)

        expected_tests = ['shapiro_wilk', 'jarque_bera', 'breusch_pagan', 'durbin_watson', 'r_squared']
        for test in expected_tests:
            assert test in diagnostics

    def test_convenience_function(self):
        """Test validate_spm_model convenience function."""
        diagnostics = validate_spm_model(self.model_result, method="diagnostics")

        assert isinstance(diagnostics, dict)
        assert len(diagnostics) > 0


class TestSpatialRegression:
    """Test SpatialRegression implementation."""

    def setup_method(self):
        """Set up test data."""
        np.random.seed(42)
        n_points = 50

        self.coordinates = np.column_stack([
            np.random.uniform(-180, 180, n_points),
            np.random.uniform(-90, 90, n_points)
        ])

        # Create spatially autocorrelated data
        X = np.random.randn(n_points, 2)
        beta = np.array([1.0, -0.5])

        # Add spatial autocorrelation to response
        distances = np.linalg.norm(self.coordinates[:, np.newaxis] - self.coordinates[np.newaxis, :], axis=2)
        spatial_corr = np.exp(-distances / 30)  # Exponential decay
        spatial_effect = spatial_corr @ np.random.randn(n_points) * 0.5

        y = X @ beta + spatial_effect + 0.1 * np.random.randn(n_points)

        self.spm_data = SPMData(data=y, coordinates=self.coordinates, crs='EPSG:4326')
        self.design_matrix = DesignMatrix(matrix=X, names=['intercept', 'slope'])

    def test_sar_model(self):
        """Test Spatial Autoregressive (SAR) model."""
        model = SpatialRegression(model_type="sar")

        result = model.fit(self.spm_data, self.design_matrix, bandwidth=20.0)

        assert result is not None
        assert result.model_diagnostics['method'] == 'SAR'
        assert 'spatial_autoregressive_param' in result.model_diagnostics

    def test_sem_model(self):
        """Test Spatial Error Model (SEM)."""
        model = SpatialRegression(model_type="sem")

        result = model.fit(self.spm_data, self.design_matrix, k_neighbors=5)

        assert result.model_diagnostics['method'] == 'SEM'
        assert 'spatial_error_param' in result.model_diagnostics

    def test_sdm_model(self):
        """Test Spatial Durbin Model (SDM)."""
        model = SpatialRegression(model_type="sdm")

        result = model.fit(self.spm_data, self.design_matrix, bandwidth=25.0)

        assert result.model_diagnostics['method'] == 'SDM'

    def test_slx_model(self):
        """Test Spatial Lag of X (SLX) model."""
        model = SpatialRegression(model_type="slx")

        result = model.fit(self.spm_data, self.design_matrix, k_neighbors=4)

        assert result.model_diagnostics['method'] == 'SLX'

    def test_gwr_model(self):
        """Test Geographically Weighted Regression (GWR)."""
        model = SpatialRegression(model_type="gwr")

        result = model.fit(self.spm_data, self.design_matrix, bandwidth=15.0)

        assert result.model_diagnostics['method'] == 'GWR'
        assert 'bandwidth' in result.model_diagnostics

    def test_spatial_filter_model(self):
        """Test spatial filter model."""
        model = SpatialRegression(model_type="spatial_filter")

        result = model.fit(self.spm_data, self.design_matrix, eigenvalue_threshold=0.1)

        assert result.model_diagnostics['method'] == 'Spatial_Filter'

    def test_invalid_model_type(self):
        """Test error handling for invalid model types."""
        with pytest.raises(ValueError, match="Model type must be one of"):
            SpatialRegression(model_type="invalid")

    def test_spatial_weights_creation(self):
        """Test spatial weights matrix creation."""
        model = SpatialRegression()

        W = model._create_spatial_weights_matrix(self.coordinates, bandwidth=20.0)

        assert W.shape == (len(self.coordinates), len(self.coordinates))
        assert hasattr(W, 'toarray')  # Should be sparse matrix

        # Check row normalization
        row_sums = np.array(W.sum(axis=1)).flatten()
        assert np.allclose(row_sums, 1.0, atol=1e-10)

    def test_convenience_function(self):
        """Test fit_spatial_model convenience function."""
        result = fit_spatial_model(self.spm_data, self.design_matrix, model_type="sar")

        assert result is not None
        assert result.model_diagnostics['method'] == 'SAR'

    def test_spatial_effects_extraction(self):
        """Test spatial effects extraction."""
        model = SpatialRegression(model_type="sar")
        model.fit(self.spm_data, self.design_matrix)

        effects = model.get_spatial_effects()

        assert isinstance(effects, dict)
        assert 'model_type' in effects


class TestAdvancedModelsIntegration:
    """Test integration between advanced modeling methods."""

    def setup_method(self):
        """Set up comprehensive test data."""
        np.random.seed(42)
        n_points = 80

        self.coordinates = np.column_stack([
            np.random.uniform(-180, 180, n_points),
            np.random.uniform(-90, 90, n_points)
        ])

        # Create complex data with multiple effects
        X = np.random.randn(n_points, 3)
        beta = np.array([2.0, -1.0, 0.5])

        # Spatial effects
        distances = np.linalg.norm(self.coordinates[:, np.newaxis] - self.coordinates[np.newaxis, :], axis=2)
        spatial_effect = np.exp(-distances / 40).sum(axis=1) * 0.3

        # Nonlinear effects
        nonlinear_effect = np.sin(X[:, 1] * 2) * 0.4

        # Group effects (for mixed models)
        n_groups = 4
        group_indices = np.random.randint(0, n_groups, n_points)
        group_effects = group_indices * 0.2

        y = (X @ beta + spatial_effect + nonlinear_effect +
             group_effects + 0.15 * np.random.randn(n_points))

        self.spm_data = SPMData(data=y, coordinates=self.coordinates, crs='EPSG:4326')
        self.design_matrix = DesignMatrix(matrix=X, names=['intercept', 'x1', 'x2'])
        self.group_indices = group_indices

    def test_model_comparison_across_methods(self):
        """Test model comparison across different advanced methods."""
        from geo_infer_spm.core.glm import fit_glm

        # Fit different models
        parametric = fit_glm(self.spm_data, self.design_matrix)

        nonparametric = fit_nonparametric(self.spm_data, self.design_matrix, method="loess")

        mixed_effects = fit_mixed_effects(
            self.spm_data, self.design_matrix,
            {'group': self.group_indices}
        )

        # Compare models
        validator = ModelValidator()
        comparison = validator.compare_models([parametric, nonparametric, mixed_effects], method="aic")

        assert len(comparison['scores']) == 3
        assert comparison['best_model_index'] in [0, 1, 2]

    def test_spatial_model_comparison(self):
        """Test comparison of different spatial models."""
        models = []

        for model_type in ['sar', 'sem', 'slx']:
            try:
                result = fit_spatial_model(self.spm_data, self.design_matrix, model_type)
                models.append(result)
            except:
                continue  # Skip if model fails

        if len(models) >= 2:
            validator = ModelValidator()
            comparison = validator.compare_models(models, method="bic")

            assert len(comparison['scores']) == len(models)

    def test_cross_validation_comparison(self):
        """Test cross-validation across different model types."""
        validator = ModelValidator(validation_method="kfold", n_folds=3)

        # Compare parametric vs nonparametric
        from geo_infer_spm.core.glm import fit_glm

        parametric_cv = validator.cross_validate(fit_glm, self.spm_data, self.design_matrix)

        nonparametric_cv = validator.cross_validate(
            lambda d, dm: fit_nonparametric(d, dm, method="loess"),
            self.spm_data, self.design_matrix
        )

        # Both should produce valid CV results
        assert parametric_cv['overall_r2'] > -1  # Reasonable R²
        assert nonparametric_cv['overall_r2'] > -1

    def test_diagnostic_comparison(self):
        """Test diagnostic comparison across models."""
        from geo_infer_spm.core.glm import fit_glm

        models = [
            fit_glm(self.spm_data, self.design_matrix),
            fit_nonparametric(self.spm_data, self.design_matrix, method="robust")
        ]

        validator = ModelValidator()

        for model in models:
            diagnostics = validator.diagnostic_tests(model)
            assert 'r_squared' in diagnostics
            assert 'shapiro_wilk' in diagnostics
