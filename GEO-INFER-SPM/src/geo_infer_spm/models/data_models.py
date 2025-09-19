"""
Data models for Statistical Parametric Mapping

This module defines the core data structures used in GEO-INFER-SPM for
representing geospatial data, statistical models, and analysis results.
All models are designed to work with real geospatial data and support
the Active Inference framework's requirements for uncertainty quantification.
"""

from typing import Dict, List, Optional, Tuple, Union, Any
from dataclasses import dataclass, field
import numpy as np
import pandas as pd
from datetime import datetime
import geopandas as gpd


@dataclass
class SPMData:
    """
    Core data structure for SPM analysis containing geospatial observations.

    This class encapsulates all data required for statistical parametric mapping,
    including spatial coordinates, temporal information, and response variables.
    It supports multiple data formats and provides validation for geospatial integrity.

    Attributes:
        data: Response variable(s) as numpy array or pandas DataFrame
        coordinates: Spatial coordinates (longitude, latitude) or (x, y)
        time: Temporal coordinates if applicable
        covariates: Additional predictor variables
        metadata: Dictionary containing data source and processing information
        crs: Coordinate reference system string (e.g., 'EPSG:4326')
    """

    data: Union[np.ndarray, pd.DataFrame, gpd.GeoDataFrame]
    coordinates: np.ndarray  # Shape: (n_points, 2) for (x, y) or (lon, lat)
    time: Optional[np.ndarray] = None
    covariates: Optional[Dict[str, np.ndarray]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    crs: str = "EPSG:4326"

    def __post_init__(self):
        """Validate data integrity and geospatial consistency."""
        self._validate_data()
        self._validate_coordinates()
        if self.time is not None:
            self._validate_temporal_data()

    def _validate_data(self):
        """Validate response data structure and format."""
        if isinstance(self.data, np.ndarray):
            if self.data.ndim not in [1, 2]:
                raise ValueError("Data array must be 1D or 2D")
        elif isinstance(self.data, (pd.DataFrame, gpd.GeoDataFrame)):
            if len(self.data) == 0:
                raise ValueError("Data cannot be empty")
        else:
            raise TypeError("Data must be numpy array, pandas DataFrame, or GeoDataFrame")

    def _validate_coordinates(self):
        """Validate spatial coordinate consistency."""
        n_points = self._get_n_points()
        if self.coordinates.shape != (n_points, 2):
            raise ValueError(f"Coordinates shape {self.coordinates.shape} does not match data size {n_points}")

        # Check coordinate bounds
        if self.crs.upper() == "EPSG:4326":
            lon, lat = self.coordinates[:, 0], self.coordinates[:, 1]
            if not (-180 <= lon.min() <= lon.max() <= 180):
                raise ValueError("Longitude values must be between -180 and 180 degrees")
            if not (-90 <= lat.min() <= lat.max() <= 90):
                raise ValueError("Latitude values must be between -90 and 90 degrees")

    def _validate_temporal_data(self):
        """Validate temporal coordinate consistency."""
        n_points = self._get_n_points()
        if len(self.time) != n_points:
            raise ValueError("Time array length must match number of data points")

    def _get_n_points(self) -> int:
        """Get number of data points across different data formats."""
        if isinstance(self.data, np.ndarray):
            return self.data.shape[0] if self.data.ndim > 1 else len(self.data)
        elif isinstance(self.data, (pd.DataFrame, gpd.GeoDataFrame)):
            return len(self.data)
        else:
            raise TypeError("Unsupported data type")

    @property
    def n_points(self) -> int:
        """Number of spatial/temporal points in the dataset."""
        return self._get_n_points()

    @property
    def has_temporal(self) -> bool:
        """Whether the data includes temporal information."""
        return self.time is not None

    @property
    def spatial_dims(self) -> Tuple[int, int]:
        """Spatial dimensions of the data."""
        return self.coordinates.shape


@dataclass
class DesignMatrix:
    """
    Design matrix for General Linear Model specification.

    Encapsulates the experimental design including factors, covariates,
    and temporal/spatial basis functions for SPM analysis.

    Attributes:
        matrix: Design matrix as numpy array (n_points x n_regressors)
        names: Names of regressors/columns
        factors: Categorical factors and their levels
        covariates: Continuous covariates
        temporal_basis: Temporal basis functions if applicable
        spatial_basis: Spatial basis functions if applicable
    """

    matrix: np.ndarray
    names: List[str]
    factors: Optional[Dict[str, List[str]]] = None
    covariates: Optional[List[str]] = None
    temporal_basis: Optional[np.ndarray] = None
    spatial_basis: Optional[np.ndarray] = None

    def __post_init__(self):
        """Validate design matrix structure."""
        if self.matrix.ndim != 2:
            raise ValueError("Design matrix must be 2D")
        if len(self.names) != self.matrix.shape[1]:
            raise ValueError("Number of names must match number of columns")

    @property
    def n_regressors(self) -> int:
        """Number of regressors in the design matrix."""
        return self.matrix.shape[1]

    @property
    def n_points(self) -> int:
        """Number of data points."""
        return self.matrix.shape[0]


@dataclass
class ContrastResult:
    """
    Results of a statistical contrast in SPM analysis.

    Contains the contrast weights, statistical values, and significance
    information for a specific hypothesis test.

    Attributes:
        contrast_vector: Contrast weights defining the hypothesis
        t_statistic: T-statistic values across space/time
        effect_size: Effect size estimates
        standard_error: Standard errors of the contrast
        p_values: Uncorrected p-values
        corrected_p_values: Multiple comparison corrected p-values
        significance_mask: Boolean mask of significant points
        threshold: Statistical threshold used
        correction_method: Multiple comparison correction method
    """

    contrast_vector: np.ndarray
    t_statistic: np.ndarray
    effect_size: np.ndarray
    standard_error: np.ndarray
    p_values: np.ndarray
    corrected_p_values: Optional[np.ndarray] = None
    significance_mask: Optional[np.ndarray] = None
    threshold: float = 0.05
    correction_method: str = "uncorrected"

    @property
    def n_significant(self) -> int:
        """Number of significant points."""
        if self.significance_mask is not None:
            return np.sum(self.significance_mask)
        return 0


@dataclass
class SPMResult:
    """
    Complete results from a Statistical Parametric Mapping analysis.

    This class encapsulates all outputs from an SPM analysis including
    statistical maps, model parameters, and diagnostic information.

    Attributes:
        spm_data: Original input data
        design_matrix: Design matrix used in analysis
        beta_coefficients: Estimated regression coefficients
        residuals: Model residuals
        contrasts: List of computed contrasts
        statistical_maps: Dictionary of statistical maps (SPM{t}, SPM{F}, etc.)
        rft_parameters: Random Field Theory parameters
        cluster_analysis: Cluster-level analysis results
        model_diagnostics: Model fit diagnostics and validation metrics
        processing_metadata: Information about analysis parameters and timing
    """

    spm_data: SPMData
    design_matrix: DesignMatrix
    beta_coefficients: np.ndarray
    residuals: np.ndarray
    contrasts: List[ContrastResult] = field(default_factory=list)
    statistical_maps: Dict[str, np.ndarray] = field(default_factory=dict)
    rft_parameters: Optional[Dict[str, Any]] = None
    cluster_analysis: Optional[Dict[str, Any]] = None
    model_diagnostics: Dict[str, Any] = field(default_factory=dict)
    processing_metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize processing metadata."""
        self.processing_metadata['timestamp'] = datetime.now().isoformat()
        self.processing_metadata['n_points'] = self.spm_data.n_points
        self.processing_metadata['n_regressors'] = self.design_matrix.n_regressors

    @property
    def r_squared(self) -> float:
        """Coefficient of determination for model fit."""
        if 'r_squared' in self.model_diagnostics:
            return self.model_diagnostics['r_squared']

        # Calculate R²
        ss_res = np.sum(self.residuals ** 2)
        ss_tot = np.sum((self.spm_data.data - np.mean(self.spm_data.data, axis=0)) ** 2)
        r2 = 1 - (ss_res / ss_tot)
        self.model_diagnostics['r_squared'] = r2
        return r2

    @property
    def log_likelihood(self) -> float:
        """Log-likelihood of the fitted model."""
        if 'log_likelihood' in self.model_diagnostics:
            return self.model_diagnostics['log_likelihood']

        # Calculate log-likelihood assuming Gaussian errors
        n = self.spm_data.n_points
        sigma2 = np.var(self.residuals, ddof=self.design_matrix.n_regressors)
        ll = -0.5 * n * np.log(2 * np.pi * sigma2) - (1 / (2 * sigma2)) * np.sum(self.residuals ** 2)
        self.model_diagnostics['log_likelihood'] = ll
        return ll

    def add_contrast(self, contrast: ContrastResult):
        """Add a computed contrast to the results."""
        self.contrasts.append(contrast)

    def get_significant_clusters(self, contrast_idx: int = 0) -> Optional[Dict[str, Any]]:
        """Get cluster analysis for a specific contrast."""
        if self.cluster_analysis and contrast_idx < len(self.cluster_analysis):
            return self.cluster_analysis[contrast_idx]
        return None
