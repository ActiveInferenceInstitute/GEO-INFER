"""
Random Field Theory implementation for Statistical Parametric Mapping

This module implements Random Field Theory (RFT) for multiple comparison correction
in SPM analysis. RFT provides rigorous control of family-wise error rates when
analyzing continuous statistical fields, which is essential for geospatial SPM.

The implementation follows the mathematical framework developed by Keith Worsley
and others, adapted for geospatial applications with spatial and temporal fields.

Key Features:
- Euler characteristic calculation for Gaussian random fields
- Spatial smoothness estimation
- Cluster-level inference
- Peak-level correction
- Support for both 2D spatial and 3D spatio-temporal fields

Mathematical Foundation:
For a Gaussian random field with smoothness parameters (FWHM_x, FWHM_y),
the expected number of clusters above threshold u is:
E[K > u] = (4*log(2))^(3/2) * (FWHM_x * FWHM_y)^(-1) * exp(-u²/2) * |Λ|^{1/2}

where Λ is the covariance matrix of the field gradients.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple, Union, Any
from scipy import ndimage
from scipy.stats import norm, t
from scipy.special import gamma
import warnings

from ..models.data_models import SPMResult, ContrastResult


class RandomFieldTheory:
    """
    Random Field Theory for multiple comparison correction in SPM.

    This class implements RFT-based correction for statistical parametric maps,
    providing family-wise error control for continuous data fields.

    Attributes:
        field_shape: Shape of the statistical field
        smoothness: Estimated smoothness parameters (FWHM)
        search_volume: Volume/resolution of the search space
        df: Degrees of freedom for t/F statistics
    """

    def __init__(self, field_shape: Tuple[int, ...], smoothness: Optional[np.ndarray] = None,
                 search_volume: Optional[float] = None, df: Optional[int] = None):
        """
        Initialize RFT calculator.

        Args:
            field_shape: Shape of the statistical field (e.g., (height, width) for 2D)
            smoothness: FWHM smoothness parameters for each dimension
            search_volume: Search volume in resels (resolution elements)
            df: Degrees of freedom for statistical test
        """
        self.field_shape = field_shape
        self.ndim = len(field_shape)
        self.smoothness = smoothness
        self.search_volume = search_volume
        self.df = df

        # RFT constants for different field dimensions
        self._rft_constants = {
            1: 1.0,      # 1D fields
            2: 4*np.log(2),  # 2D fields
            3: (4*np.log(2))**(3/2) * gamma(3/2)  # 3D fields
        }

        self._validate_parameters()

    def _validate_parameters(self):
        """Validate RFT parameters."""
        if self.ndim not in [1, 2, 3]:
            raise ValueError(f"RFT supports 1D, 2D, and 3D fields, got {self.ndim}D")

        if self.smoothness is not None:
            if len(self.smoothness) != self.ndim:
                raise ValueError(f"Smoothness must have {self.ndim} dimensions")

    def estimate_smoothness(self, residuals: np.ndarray,
                          mask: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Estimate field smoothness using residuals.

        Uses the method of moments to estimate FWHM smoothness parameters
        from model residuals, accounting for spatial autocorrelation.

        Args:
            residuals: Model residuals as field
            mask: Optional mask for valid data points

        Returns:
            FWHM smoothness parameters for each dimension
        """
        if mask is None:
            mask = np.ones_like(residuals, dtype=bool)

        # Reshape residuals to field shape
        field_residuals = residuals.reshape(self.field_shape)

        # Estimate smoothness for each dimension
        fwhm = np.zeros(self.ndim)

        for dim in range(self.ndim):
            # Create difference operator for this dimension
            diff_kernel = np.zeros(self.ndim)
            diff_kernel[dim] = 1

            # Compute first differences
            diff_field = ndimage.correlate(field_residuals, diff_kernel[np.newaxis, :],
                                         mode='nearest')

            # Estimate variance of first differences
            var_diff = np.var(diff_field[mask])

            # Convert to FWHM using relationship: FWHM = sqrt(8*ln(2)) / lambda
            # where lambda is the frequency at which power spectrum drops to half
            if var_diff > 0:
                lambda_param = np.sqrt(var_diff / (2 * np.var(field_residuals[mask])))
                fwhm[dim] = np.sqrt(8 * np.log(2)) / lambda_param
            else:
                fwhm[dim] = 1.0  # Default if estimation fails

        self.smoothness = fwhm
        return fwhm

    def compute_search_volume(self, voxel_sizes: Optional[np.ndarray] = None) -> float:
        """
        Compute search volume in resels (resolution elements).

        Args:
            voxel_sizes: Size of voxels/pixels in each dimension

        Returns:
            Search volume in resels
        """
        if voxel_sizes is None:
            voxel_sizes = np.ones(self.ndim)

        if len(voxel_sizes) != self.ndim:
            raise ValueError(f"Voxel sizes must have {self.ndim} dimensions")

        if self.smoothness is None:
            raise ValueError("Smoothness must be estimated before computing search volume")

        # Search volume = product over dimensions of (field_size * smoothness / voxel_size)
        search_vol = 1.0
        for i in range(self.ndim):
            dim_size = self.field_shape[i] * voxel_sizes[i]
            search_vol *= dim_size / self.smoothness[i]

        self.search_volume = search_vol
        return search_vol

    def expected_clusters(self, threshold: float, stat_type: str = 't') -> float:
        """
        Compute expected number of clusters above threshold.

        Args:
            threshold: Statistical threshold (in statistical units)
            stat_type: Type of statistic ('t', 'F', 'Z')

        Returns:
            Expected number of clusters
        """
        if self.search_volume is None:
            raise ValueError("Search volume must be computed first")

        if self.smoothness is None:
            raise ValueError("Smoothness must be estimated first")

        # Convert threshold to Z-score equivalent
        if stat_type == 't':
            if self.df is None:
                raise ValueError("Degrees of freedom required for t-statistic")
            z_threshold = t.ppf(1 - norm.cdf(threshold), self.df)
        elif stat_type == 'F':
            # Simplified F to Z conversion (approximation)
            z_threshold = np.sqrt(threshold)
        elif stat_type == 'Z':
            z_threshold = threshold
        else:
            raise ValueError(f"Unknown statistic type: {stat_type}")

        # RFT formula for expected clusters
        # E[K > u] = R * (4*ln(2))^(D/2) * |Λ|^(1/2) * exp(-u²/2) / (2π)^(D/2)
        # where R is search volume, D is dimensionality, Λ is smoothness product

        smoothness_product = np.prod(self.smoothness)
        rft_const = self._rft_constants[self.ndim]

        # Simplified version for computational efficiency
        if self.ndim == 2:
            expected_k = (self.search_volume * np.sqrt(4 * np.log(2)) /
                         smoothness_product * np.exp(-z_threshold**2 / 2))
        elif self.ndim == 3:
            expected_k = (self.search_volume * (4 * np.log(2))**(3/2) /
                         smoothness_product * np.exp(-z_threshold**2 / 2))
        else:  # 1D
            expected_k = (self.search_volume / smoothness_product *
                         np.exp(-z_threshold**2 / 2))

        return expected_k

    def cluster_threshold(self, alpha: float = 0.05, stat_type: str = 't') -> float:
        """
        Compute cluster-forming threshold for given alpha level.

        Args:
            alpha: Family-wise error rate
            stat_type: Type of statistic

        Returns:
            Cluster-forming threshold
        """
        # Use bisection method to find threshold where E[K] = alpha
        def expected_clusters_func(u):
            return self.expected_clusters(u, stat_type)

        # Initial bounds
        u_min, u_max = 0.0, 5.0

        # Expand bounds if needed
        while expected_clusters_func(u_max) > alpha:
            u_max *= 2

        # Bisection
        for _ in range(50):
            u_mid = (u_min + u_max) / 2
            if expected_clusters_func(u_mid) > alpha:
                u_min = u_mid
            else:
                u_max = u_mid

        return (u_min + u_max) / 2

    def peak_threshold(self, alpha: float = 0.05, stat_type: str = 't') -> float:
        """
        Compute peak-level threshold for given alpha level.

        Args:
            alpha: Family-wise error rate
            stat_type: Type of statistic

        Returns:
            Peak-level threshold
        """
        if self.search_volume is None:
            raise ValueError("Search volume must be computed first")

        # Peak-level correction: p_FWE = 1 - (1 - p_uncorrected)^R
        # Solve for threshold where p_FWE = alpha

        # Approximation for high thresholds
        if stat_type == 'Z':
            # For Z-statistics, threshold ≈ sqrt(2 * log(R / alpha))
            threshold = np.sqrt(2 * np.log(self.search_volume / alpha))
        elif stat_type == 't':
            # Convert Z threshold to t threshold
            if self.df is None:
                raise ValueError("Degrees of freedom required for t-statistic")
            z_thresh = np.sqrt(2 * np.log(self.search_volume / alpha))
            threshold = t.ppf(norm.cdf(z_thresh), self.df)
        else:
            # Simplified approximation
            threshold = np.sqrt(2 * np.log(self.search_volume / alpha))

        return threshold

    def correct_p_values(self, statistical_map: np.ndarray,
                        stat_type: str = 't', method: str = 'cluster') -> np.ndarray:
        """
        Apply RFT-based multiple comparison correction.

        Args:
            statistical_map: Statistical parametric map
            stat_type: Type of statistic ('t', 'F', 'Z')
            method: Correction method ('cluster', 'peak')

        Returns:
            Corrected p-values
        """
        if method == 'cluster':
            threshold = self.cluster_threshold(alpha=0.05, stat_type=stat_type)
        elif method == 'peak':
            threshold = self.peak_threshold(alpha=0.05, stat_type=stat_type)
        else:
            raise ValueError(f"Unknown correction method: {method}")

        # Compute uncorrected p-values
        if stat_type == 't':
            if self.df is None:
                raise ValueError("Degrees of freedom required for t-statistics")
            p_uncorr = 2 * t.sf(np.abs(statistical_map), self.df)
        elif stat_type == 'Z':
            p_uncorr = 2 * norm.sf(np.abs(statistical_map))
        elif stat_type == 'F':
            # Simplified F p-values
            p_uncorr = 1 - np.array([f.cdf(x, 1, self.df or 100) for x in statistical_map.flatten()])
            p_uncorr = p_uncorr.reshape(statistical_map.shape)
        else:
            raise ValueError(f"Unknown statistic type: {stat_type}")

        # Apply cluster-level correction (simplified)
        # In full implementation, this would involve cluster identification
        # For now, use a simplified correction based on cluster extent

        # Identify clusters above threshold
        thresholded = np.abs(statistical_map) > threshold
        labeled_clusters, n_clusters = ndimage.label(thresholded)

        # Compute cluster-level p-values (simplified)
        p_corrected = np.ones_like(p_uncorr)

        for cluster_id in range(1, n_clusters + 1):
            cluster_mask = labeled_clusters == cluster_id
            cluster_size = np.sum(cluster_mask)

            # Simplified cluster p-value based on size and expected clusters
            # This is an approximation; full RFT would use more complex formulas
            expected_clusters_above_size = self.expected_clusters(threshold, stat_type) / cluster_size
            cluster_p = min(1.0, expected_clusters_above_size)

            p_corrected[cluster_mask] = cluster_p

        return p_corrected


def compute_spm(model_result: SPMResult, contrast: ContrastResult,
               correction: str = "RFT", alpha: float = 0.05) -> ContrastResult:
    """
    Compute Statistical Parametric Map with multiple comparison correction.

    Args:
        model_result: Fitted GLM results
        contrast: Contrast specification
        correction: Multiple comparison correction method ('RFT', 'FDR', 'Bonferroni')
        alpha: Significance level

    Returns:
        ContrastResult with corrected statistics

    Example:
        >>> result = fit_glm(data, design)
        >>> contrast_def = contrast(result, "condition_A > condition_B")
        >>> spm_result = compute_spm(result, contrast_def, correction="RFT")
    """
    # Initialize RFT if needed
    if correction.upper() == "RFT":
        field_shape = model_result.spm_data.spatial_dims

        # Estimate smoothness from residuals
        rft = RandomFieldTheory(field_shape, df=model_result.design_matrix.n_regressors)
        smoothness = rft.estimate_smoothness(model_result.residuals)

        # Compute search volume (assuming unit voxel size)
        search_vol = rft.compute_search_volume()

        # Apply RFT correction
        corrected_p = rft.correct_p_values(contrast.t_statistic, stat_type='t')

        # Update contrast result
        contrast.corrected_p_values = corrected_p
        contrast.correction_method = "RFT"
        contrast.significance_mask = corrected_p < alpha
        contrast.threshold = alpha

    elif correction.upper() == "FDR":
        # False Discovery Rate correction using Benjamini-Hochberg
        p_sorted = np.sort(contrast.p_values.flatten())
        n_tests = len(p_sorted)
        bh_thresholds = alpha * np.arange(1, n_tests + 1) / n_tests
        significant_idx = np.where(p_sorted <= bh_thresholds)[0]

        if len(significant_idx) > 0:
            fdr_threshold = p_sorted[significant_idx[-1]]
            contrast.corrected_p_values = np.where(contrast.p_values <= fdr_threshold,
                                                 contrast.p_values, 1.0)
        else:
            contrast.corrected_p_values = np.ones_like(contrast.p_values)

        contrast.correction_method = "FDR"
        contrast.significance_mask = contrast.corrected_p_values < alpha

    elif correction.upper() == "BONFERRONI":
        # Bonferroni correction
        n_tests = np.prod(contrast.p_values.shape)
        contrast.corrected_p_values = np.minimum(contrast.p_values * n_tests, 1.0)
        contrast.correction_method = "Bonferroni"
        contrast.significance_mask = contrast.corrected_p_values < alpha

    else:
        # No correction
        contrast.corrected_p_values = contrast.p_values
        contrast.correction_method = "uncorrected"
        contrast.significance_mask = contrast.p_values < alpha

    return contrast
