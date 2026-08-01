"""
DOMAIN-02 Acceptance tests for GEO-INFER-SPM documented features.

These tests exercise real implemented behavior for documented features that
previously lacked focused acceptance tests:

1. SPMData / DesignMatrix — data model validation, geospatial consistency.
2. GeneralLinearModel — OLS fitting, residuals, diagnostics, prediction,
   coefficient significance testing.
3. Contrast — string parsing ("A > B"), t-contrast computation, F-contrast.
4. RandomFieldTheory — smoothness estimation, search volume, cluster threshold.
5. compute_spm — RFT, FDR, and Bonferroni multiple-comparison corrections.

No mocks, stubs, or placeholders: every assertion exercises actual code paths.
"""

import pytest
import numpy as np

from geo_infer_spm.core.glm import GeneralLinearModel, fit_glm
from geo_infer_spm.core.contrasts import (
    Contrast,
    contrast,
    generate_common_contrasts,
)
from geo_infer_spm.core.rft import RandomFieldTheory, compute_spm
from geo_infer_spm.models.data_models import (
    SPMData,
    SPMResult,
    ContrastResult,
    DesignMatrix,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_spm_data(n: int = 20, seed: int = 42) -> tuple:
    """Create synthetic SPMData + DesignMatrix for OLS fitting."""
    rng = np.random.default_rng(seed=seed)
    x = rng.uniform(0, 10, n)
    # True model: y = 2 + 0.5*x + noise
    y = 2.0 + 0.5 * x + rng.normal(0, 0.1, n)
    coords = np.column_stack([
        rng.uniform(-90, 90, n),    # latitudes
        rng.uniform(-180, 180, n),  # longitudes
    ])
    data = SPMData(data=y, coordinates=coords)
    # Design matrix: [intercept, x]
    X = np.column_stack([np.ones(n), x])
    design = DesignMatrix(matrix=X, names=["intercept", "x"])
    return data, design


# ---------------------------------------------------------------------------
# SPMData / DesignMatrix data models
# ---------------------------------------------------------------------------

class TestSPMDataModels:
    """Acceptance: core data model construction and validation."""

    def test_spmdata_valid_construction(self):
        """SPMData accepts a 1D array with matching coordinates."""
        rng = np.random.default_rng(seed=1)
        n = 10
        data = SPMData(
            data=rng.standard_normal(n),
            coordinates=np.column_stack([
                rng.uniform(-90, 90, n),
                rng.uniform(-180, 180, n),
            ]),
        )
        assert data.n_points == n
        assert data.has_temporal is False
        assert data.spatial_dims == (n, 2)

    def test_spmdata_rejects_3d_array(self):
        """SPMData rejects arrays with more than 2 dimensions."""
        with pytest.raises(ValueError, match="Data array must be 1D or 2D"):
            SPMData(
                data=np.zeros((3, 3, 3)),
                coordinates=np.zeros((3, 2)),
            )

    def test_design_matrix_auto_names(self):
        """DesignMatrix auto-generates regressor names when none provided."""
        X = np.ones((5, 3))
        design = DesignMatrix(matrix=X)
        assert design.n_regressors == 3
        assert design.n_points == 5
        assert design.names == ["regressor_0", "regressor_1", "regressor_2"]

    def test_spmdata_copy_preserves_attributes(self):
        """copy() returns a new SPMData with the same metadata and crs."""
        rng = np.random.default_rng(seed=2)
        n = 5
        original = SPMData(
            data=rng.standard_normal(n),
            coordinates=np.column_stack([
                rng.uniform(-90, 90, n),
                rng.uniform(-180, 180, n),
            ]),
            metadata={"source": "test"},
            crs="EPSG:3857",
        )
        clone = original.copy()
        assert clone.crs == original.crs
        assert clone.metadata == original.metadata
        assert clone.n_points == original.n_points
        # Copy is independent
        clone.metadata["new"] = True
        assert "new" not in original.metadata


# ---------------------------------------------------------------------------
# GeneralLinearModel fitting
# ---------------------------------------------------------------------------

class TestGeneralLinearModel:
    """Acceptance: GLM fitting, diagnostics, and prediction."""

    def test_ols_fit_recovers_coefficients(self):
        """OLS fit recovers true coefficients within tolerance."""
        data, design = _make_spm_data(n=50, seed=7)
        glm = GeneralLinearModel(design)
        result = glm.fit(data, method="OLS")
        assert isinstance(result, SPMResult)
        # True model: y = 2 + 0.5*x
        assert result.beta_coefficients.shape == (2,)
        assert abs(result.beta_coefficients[0] - 2.0) < 0.5
        assert abs(result.beta_coefficients[1] - 0.5) < 0.2

    def test_ols_fit_computes_diagnostics(self):
        """OLS fit populates R-squared and residual diagnostics."""
        data, design = _make_spm_data(n=30, seed=3)
        glm = GeneralLinearModel(design)
        result = glm.fit(data, method="OLS")
        diag = result.model_diagnostics
        assert "r_squared" in diag
        assert diag["r_squared"] > 0.9  # strong linear relationship
        assert "residual_mean" in diag
        assert "durbin_watson" in diag
        assert "condition_number" in diag

    def test_robust_fit_returns_results(self):
        """Robust fitting (Huber IRLS) returns valid coefficients."""
        data, design = _make_spm_data(n=30, seed=4)
        glm = GeneralLinearModel(design)
        result = glm.fit(data, method="robust")
        assert result.beta_coefficients.shape == (2,)
        assert result.residuals is not None

    def test_spatial_fit_returns_results(self):
        """Spatial-regularized fit returns valid coefficients."""
        data, design = _make_spm_data(n=30, seed=5)
        glm = GeneralLinearModel(design)
        result = glm.fit(data, method="spatial", spatial_regularization={"lambda": 0.1})
        assert result.beta_coefficients.shape == (2,)
        assert result.processing_metadata["fitting_method"] == "spatial"

    def test_unknown_method_raises(self):
        """An unsupported fitting method raises ValueError."""
        data, design = _make_spm_data(n=20, seed=6)
        glm = GeneralLinearModel(design)
        with pytest.raises(ValueError, match="Unknown fitting method"):
            glm.fit(data, method="nonexistent")

    def test_insufficient_data_raises(self):
        """Too few observations for the number of regressors raises ValueError."""
        data, design = _make_spm_data(n=3, seed=8)
        glm = GeneralLinearModel(design)
        with pytest.raises(ValueError, match="Insufficient data"):
            glm.fit(data, method="OLS")

    def test_predict_on_training_data(self):
        """predict() without new data returns fitted values."""
        data, design = _make_spm_data(n=25, seed=9)
        glm = GeneralLinearModel(design)
        glm.fit(data, method="OLS")
        preds = glm.predict()
        assert preds.shape == (25,)

    def test_predict_before_fit_raises(self):
        """Calling predict() before fit() raises ValueError."""
        data, design = _make_spm_data(n=20, seed=10)
        glm = GeneralLinearModel(design)
        with pytest.raises(ValueError, match="Model must be fitted"):
            glm.predict()

    def test_get_coefficient_test(self):
        """get_coefficient_test returns t-stat, p-value, and significance flag."""
        data, design = _make_spm_data(n=40, seed=11)
        glm = GeneralLinearModel(design)
        glm.fit(data, method="OLS")
        test = glm.get_coefficient_test(1)  # slope coefficient
        assert "coefficient" in test
        assert "standard_error" in test
        assert "t_statistic" in test
        assert "p_value" in test
        assert bool(test["significant"]) is True  # strong signal (np.bool_ → bool)

    def test_fit_glm_convenience_function(self):
        """fit_glm convenience function returns an SPMResult."""
        data, design = _make_spm_data(n=20, seed=12)
        result = fit_glm(data, design, method="OLS")
        assert isinstance(result, SPMResult)
        assert result.processing_metadata["fitting_method"] == "OLS"


# ---------------------------------------------------------------------------
# Contrast specification and testing
# ---------------------------------------------------------------------------

class TestContrast:
    """Acceptance: contrast string parsing and t/F-contrast computation."""

    @pytest.fixture
    def fitted_result(self) -> SPMResult:
        data, design = _make_spm_data(n=30, seed=20)
        glm = GeneralLinearModel(design)
        return glm.fit(data, method="OLS")

    def test_from_string_greater_than(self):
        """Contrast.from_string parses 'A > B' into +1, -1 weights."""
        names = ["intercept", "condition_A", "condition_B"]
        c = Contrast.from_string("condition_A > condition_B", names)
        assert c.vector[1] == 1.0
        assert c.vector[2] == -1.0

    def test_from_string_linear_combination(self):
        """Contrast.from_string parses 'A + B - C' general combinations."""
        names = ["intercept", "A", "B", "C"]
        c = Contrast.from_string("A + B - C", names)
        assert c.vector[1] == 1.0
        assert c.vector[2] == 1.0
        assert c.vector[3] == -1.0

    def test_from_string_no_match_raises(self):
        """A contrast string that matches no columns raises ValueError."""
        names = ["intercept", "x"]
        with pytest.raises(ValueError, match="did not match"):
            Contrast.from_string("nonexistent > other", names)

    def test_t_contrast_returns_statistics(self, fitted_result):
        """A t-contrast returns effect size, t-stat, SE, and p-values."""
        result = contrast(fitted_result, np.array([0, 1]))  # test slope
        assert isinstance(result, ContrastResult)
        assert result.effect_size is not None
        assert result.t_statistic is not None
        assert result.standard_error is not None
        assert result.p_values is not None

    def test_contrast_by_string(self, fitted_result):
        """contrast() accepts a string spec against design matrix names."""
        result = contrast(fitted_result, "x > intercept", contrast_type="t")
        assert isinstance(result, ContrastResult)
        assert len(result.contrast_vector) == 2

    def test_f_contrast_invalid_type_raises(self):
        """A contrast_type other than 't' or 'F' raises ValueError."""
        with pytest.raises(ValueError, match="Contrast type must be"):
            Contrast(np.array([0, 1]), contrast_type="z")

    def test_generate_common_contrasts_categorical(self):
        """generate_common_contrasts produces pairwise comparisons."""
        names = ["intercept", "A", "B", "C"]
        X = np.ones((10, 4))
        design = DesignMatrix(matrix=X, names=names)
        contrasts = generate_common_contrasts(design, "categorical")
        assert len(contrasts) >= 2  # at least A>B, A<C for first pair
        assert all(isinstance(c, Contrast) for c in contrasts)


# ---------------------------------------------------------------------------
# Random Field Theory
# ---------------------------------------------------------------------------

class TestRandomFieldTheory:
    """Acceptance: RFT smoothness estimation and correction."""

    def test_estimate_smoothness_returns_fwhm(self):
        """estimate_smoothness returns positive FWHM for a 2D residual field."""
        rng = np.random.default_rng(seed=30)
        residuals = rng.normal(0, 1, (20, 20))
        rft = RandomFieldTheory(field_shape=(20, 20))
        fwhm = rft.estimate_smoothness(residuals)
        assert fwhm.shape == (2,)
        assert np.all(fwhm > 0)

    def test_compute_search_volume(self):
        """compute_search_volume requires smoothness and returns a float."""
        rng = np.random.default_rng(seed=31)
        residuals = rng.normal(0, 1, (15, 15))
        rft = RandomFieldTheory(field_shape=(15, 15))
        rft.estimate_smoothness(residuals)
        sv = rft.compute_search_volume()
        assert sv > 0
        assert rft.search_volume == sv

    def test_search_volume_without_smoothness_raises(self):
        """compute_search_volume without smoothness raises ValueError."""
        rft = RandomFieldTheory(field_shape=(10, 10))
        with pytest.raises(ValueError, match="Smoothness must be estimated"):
            rft.compute_search_volume()

    def test_expected_clusters_positive(self):
        """expected_clusters returns a non-negative value."""
        rng = np.random.default_rng(seed=32)
        residuals = rng.normal(0, 1, (12, 12))
        rft = RandomFieldTheory(field_shape=(12, 12), df=20)
        rft.estimate_smoothness(residuals)
        rft.compute_search_volume()
        ek = rft.expected_clusters(threshold=2.0, stat_type="Z")
        assert ek >= 0

    def test_invalid_dimensionality_raises(self):
        """RFT rejects 4D fields."""
        with pytest.raises(ValueError, match="RFT supports"):
            RandomFieldTheory(field_shape=(4, 4, 4, 4))


# ---------------------------------------------------------------------------
# compute_spm multiple comparison corrections
# ---------------------------------------------------------------------------

class TestComputeSPM:
    """Acceptance: multiple comparison correction methods."""

    @pytest.fixture
    def fitted_with_contrast(self) -> ContrastResult:
        data, design = _make_spm_data(n=30, seed=40)
        glm = GeneralLinearModel(design)
        result = glm.fit(data, method="OLS")
        return contrast(result, np.array([0, 1]))

    def test_rft_correction_sets_method(self, fitted_with_contrast):
        """compute_spm with RFT sets correction_method and significance mask."""
        corrected = compute_spm(
            _make_contrast_result_spm(fitted_with_contrast),
            fitted_with_contrast,
            correction="RFT",
        )
        assert corrected.correction_method == "RFT"
        assert corrected.significance_mask is not None

    def test_bonferroni_correction_sets_method(self, fitted_with_contrast):
        """compute_spm with Bonferroni sets correction_method and inflates p-values."""
        original_p = fitted_with_contrast.p_values.copy()
        corrected = compute_spm(
            _make_contrast_result_spm(fitted_with_contrast),
            fitted_with_contrast,
            correction="Bonferroni",
        )
        assert corrected.correction_method == "Bonferroni"
        # Bonferroni inflates p-values (or keeps at 1.0)
        assert np.all(corrected.corrected_p_values >= original_p - 1e-12)

    def test_fdr_correction_sets_method(self, fitted_with_contrast):
        """compute_spm with FDR sets correction_method."""
        corrected = compute_spm(
            _make_contrast_result_spm(fitted_with_contrast),
            fitted_with_contrast,
            correction="FDR",
        )
        assert corrected.correction_method == "FDR"
        assert corrected.significance_mask is not None

    def test_uncorrected_passes_through(self, fitted_with_contrast):
        """compute_spm with no correction keeps original p-values."""
        corrected = compute_spm(
            _make_contrast_result_spm(fitted_with_contrast),
            fitted_with_contrast,
            correction="none",
        )
        assert corrected.correction_method == "uncorrected"
        np.testing.assert_array_equal(
            corrected.corrected_p_values, fitted_with_contrast.p_values
        )


def _make_contrast_result_spm(cr: ContrastResult) -> SPMResult:
    """Rebuild a minimal SPMResult so compute_spm can access residuals."""
    n = 30
    rng = np.random.default_rng(seed=40)
    data = SPMData(
        data=rng.standard_normal(n),
        coordinates=np.column_stack([
            rng.uniform(-90, 90, n),
            rng.uniform(-180, 180, n),
        ]),
    )
    X = np.column_stack([np.ones(n), rng.uniform(0, 10, n)])
    design = DesignMatrix(matrix=X, names=["intercept", "x"])
    return SPMResult(
        spm_data=data,
        design_matrix=design,
        beta_coefficients=np.array([2.0, 0.5]),
        residuals=rng.normal(0, 0.1, n),
        cov_beta=np.eye(2) * 0.01,
    )
