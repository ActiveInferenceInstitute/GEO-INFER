"""
Helper functions for GEO-INFER-SPM

This module provides utility functions for creating design matrices,
generating coordinates, and other common SPM analysis tasks.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple, Union, Any
from scipy import stats
import warnings

from ..models.data_models import SPMData, DesignMatrix


def create_design_matrix(data: SPMData, formula: Optional[str] = None,
                        factors: Optional[Dict[str, List[str]]] = None,
                        covariates: Optional[List[str]] = None,
                        intercept: bool = True) -> DesignMatrix:
    """
    Create design matrix from SPMData and specification.

    Args:
        data: SPMData containing covariates
        formula: Formula string for design matrix (e.g., "y ~ x1 + x2 + factor1")
        factors: Dictionary of categorical factors and their levels
        covariates: List of continuous covariate names
        intercept: Whether to include intercept term

    Returns:
        DesignMatrix object

    Example:
        >>> # Simple design with intercept and one covariate
        >>> design = create_design_matrix(data, covariates=['elevation'])

        >>> # Design with categorical factor
        >>> design = create_design_matrix(data, factors={'season': ['winter', 'spring', 'summer']})
    """
    n_points = data.n_points

    if formula is not None:
        # Parse formula (simplified implementation)
        design_matrix, names = _parse_formula(formula, data, intercept)
    else:
        # Build from factors and covariates
        design_components = []
        names = []

        # Intercept
        if intercept:
            design_components.append(np.ones(n_points))
            names.append('intercept')

        # Covariates
        if covariates:
            for cov_name in covariates:
                if cov_name not in data.covariates:
                    raise ValueError(f"Covariate '{cov_name}' not found in data")
                design_components.append(data.covariates[cov_name])
                names.append(cov_name)

        # Factors (categorical variables)
        if factors:
            for factor_name, levels in factors.items():
                if factor_name in data.covariates:
                    # Convert categorical covariate to dummy variables
                    factor_values = data.covariates[factor_name]
                    dummy_matrix = _create_dummy_variables(factor_values, levels)
                    for i, level in enumerate(levels[:-1]):  # n-1 dummies
                        design_components.append(dummy_matrix[:, i])
                        names.append(f"{factor_name}_{level}")
                else:
                    # Create default factor coding
                    warnings.warn(f"Factor '{factor_name}' not found in covariates, using equal groups")
                    factor_values = np.random.choice(levels, n_points)
                    dummy_matrix = _create_dummy_variables(factor_values, levels)
                    for i, level in enumerate(levels[:-1]):
                        design_components.append(dummy_matrix[:, i])
                        names.append(f"{factor_name}_{level}")

        design_matrix = np.column_stack(design_components)

    return DesignMatrix(
        matrix=design_matrix,
        names=names,
        factors=factors,
        covariates=covariates
    )


def _parse_formula(formula: str, data: SPMData, intercept: bool) -> Tuple[np.ndarray, List[str]]:
    """Parse formula string to create design matrix (simplified implementation)."""
    # This is a basic parser - full implementation would be more comprehensive
    if '~' not in formula:
        raise ValueError("Formula must contain '~' separator")

    response, predictors = formula.split('~', 1)

    # Parse predictors
    terms = [term.strip() for term in predictors.split('+')]

    design_components = []
    names = []

    # Intercept
    if intercept and '0' not in terms:
        design_components.append(np.ones(data.n_points))
        names.append('intercept')

    for term in terms:
        term = term.strip()
        if term == '0':
            continue  # No intercept
        elif term in data.covariates:
            design_components.append(data.covariates[term])
            names.append(term)
        elif '*' in term:
            # Interaction term (simplified)
            var1, var2 = term.split('*', 1)
            var1, var2 = var1.strip(), var2.strip()
            if var1 in data.covariates and var2 in data.covariates:
                interaction = data.covariates[var1] * data.covariates[var2]
                design_components.append(interaction)
                names.append(f"{var1}:{var2}")
        else:
            raise ValueError(f"Unknown term in formula: {term}")

    return np.column_stack(design_components), names


def _create_dummy_variables(values: np.ndarray, levels: List[str]) -> np.ndarray:
    """Create dummy variables for categorical factor."""
    n_points = len(values)
    n_levels = len(levels)

    # Map string levels to indices
    level_to_idx = {level: i for i, level in enumerate(levels)}

    # Create dummy matrix (n-1 columns for n levels)
    dummy_matrix = np.zeros((n_points, n_levels - 1))

    for i, value in enumerate(values):
        if value in level_to_idx:
            level_idx = level_to_idx[value]
            if level_idx < n_levels - 1:  # Don't create dummy for last level
                dummy_matrix[i, level_idx] = 1

    return dummy_matrix


def generate_coordinates(grid_type: str = 'regular', n_points: int = 100,
                        bounds: Optional[Tuple[float, float, float, float]] = None,
                        **kwargs) -> np.ndarray:
    """
    Generate synthetic coordinate arrays for testing and examples.

    Args:
        grid_type: Type of coordinate grid ('regular', 'random', 'clustered')
        n_points: Number of coordinate points to generate
        bounds: Spatial bounds (min_lon, max_lon, min_lat, max_lat)
        **kwargs: Additional parameters for grid generation

    Returns:
        Coordinate array of shape (n_points, 2)

    Example:
        >>> # Generate regular grid
        >>> coords = generate_coordinates('regular', n_points=100, bounds=(-180, 180, -90, 90))

        >>> # Generate random coordinates
        >>> coords = generate_coordinates('random', n_points=50)
    """
    if bounds is None:
        bounds = (-180, 180, -90, 90)  # Global bounds

    min_lon, max_lon, min_lat, max_lat = bounds

    if grid_type == 'regular':
        # Create regular grid
        n_cols = int(np.sqrt(n_points))
        n_rows = (n_points + n_cols - 1) // n_cols  # Ceiling division

        lon_vals = np.linspace(min_lon, max_lon, n_cols)
        lat_vals = np.linspace(min_lat, max_lat, n_rows)

        lon_grid, lat_grid = np.meshgrid(lon_vals, lat_vals)
        coordinates = np.column_stack([lon_grid.ravel(), lat_grid.ravel()])[:n_points]

    elif grid_type == 'random':
        # Random coordinates within bounds
        lon_vals = np.random.uniform(min_lon, max_lon, n_points)
        lat_vals = np.random.uniform(min_lat, max_lat, n_points)
        coordinates = np.column_stack([lon_vals, lat_vals])

    elif grid_type == 'clustered':
        # Generate clustered coordinates
        n_clusters = kwargs.get('n_clusters', 3)
        cluster_std = kwargs.get('cluster_std', 5.0)

        coordinates = np.zeros((n_points, 2))

        # Generate cluster centers
        cluster_centers_lon = np.random.uniform(min_lon, max_lon, n_clusters)
        cluster_centers_lat = np.random.uniform(min_lat, max_lat, n_clusters)

        points_per_cluster = n_points // n_clusters
        remaining_points = n_points % n_clusters

        idx = 0
        for cluster in range(n_clusters):
            cluster_size = points_per_cluster + (1 if cluster < remaining_points else 0)

            # Generate points around cluster center
            lon_points = np.random.normal(cluster_centers_lon[cluster], cluster_std, cluster_size)
            lat_points = np.random.normal(cluster_centers_lat[cluster], cluster_std, cluster_size)

            # Clip to bounds
            lon_points = np.clip(lon_points, min_lon, max_lon)
            lat_points = np.clip(lat_points, min_lat, max_lat)

            coordinates[idx:idx + cluster_size] = np.column_stack([lon_points, lat_points])
            idx += cluster_size

    else:
        raise ValueError(f"Unknown grid type: {grid_type}")

    return coordinates


def generate_synthetic_data(coordinates: np.ndarray, effects: Optional[Dict[str, Any]] = None,
                          noise_level: float = 0.1, temporal: bool = False,
                          n_timepoints: int = 10) -> SPMData:
    """
    Generate synthetic SPM data for testing and examples.

    Args:
        coordinates: Spatial coordinates
        effects: Dictionary specifying spatial effects to include
        noise_level: Standard deviation of noise
        temporal: Whether to include temporal dimension
        n_timepoints: Number of time points if temporal

    Returns:
        SPMData with synthetic data

    Example:
        >>> coords = generate_coordinates('regular', 100)
        >>> data = generate_synthetic_data(coords, effects={'trend': 'north_south'})
    """
    n_points = len(coordinates)

    if effects is None:
        effects = {'intercept': 10, 'trend': 'east_west'}

    # Generate base signal
    signal = np.zeros(n_points)

    # Intercept
    if 'intercept' in effects:
        signal += effects['intercept']

    # Spatial trends
    if 'trend' in effects:
        trend_type = effects['trend']

        if trend_type == 'east_west':
            # Linear trend from west to east
            lon_norm = (coordinates[:, 0] - np.min(coordinates[:, 0])) / \
                      (np.max(coordinates[:, 0]) - np.min(coordinates[:, 0]))
            signal += 5 * lon_norm

        elif trend_type == 'north_south':
            # Linear trend from south to north
            lat_norm = (coordinates[:, 1] - np.min(coordinates[:, 1])) / \
                      (np.max(coordinates[:, 1]) - np.min(coordinates[:, 1]))
            signal += 5 * lat_norm

        elif trend_type == 'radial':
            # Radial pattern from center
            center = np.mean(coordinates, axis=0)
            distances = np.linalg.norm(coordinates - center, axis=1)
            dist_norm = distances / np.max(distances)
            signal += 5 * (1 - dist_norm)  # Higher values near center

    # Spatial clusters
    if 'clusters' in effects:
        n_clusters = effects['clusters'].get('n_clusters', 3)
        cluster_effect = effects['clusters'].get('effect_size', 3.0)

        # Simple cluster generation
        for i in range(n_clusters):
            # Random cluster center
            center_idx = np.random.randint(0, n_points)
            center = coordinates[center_idx]

            # Points within cluster radius
            distances = np.linalg.norm(coordinates - center, axis=1)
            cluster_radius = np.percentile(distances, 10)  # 10th percentile distance

            cluster_mask = distances < cluster_radius
            signal[cluster_mask] += cluster_effect

    # Temporal component
    time_coords = None
    if temporal:
        time_coords = np.arange(n_timepoints)
        temporal_signal = np.zeros((n_timepoints, n_points))

        for t in range(n_timepoints):
            # Temporal evolution (e.g., linear trend over time)
            time_effect = 1 + 0.1 * t  # Increasing over time
            temporal_signal[t] = signal * time_effect

        # Add temporal noise
        temporal_noise = np.random.normal(0, noise_level, (n_timepoints, n_points))
        data = temporal_signal + temporal_noise

        # Flatten for SPMData format
        data_flat = data.T  # (n_points, n_timepoints)

    else:
        # Spatial only
        noise = np.random.normal(0, noise_level, n_points)
        data = signal + noise
        data_flat = data

    # Generate covariates
    covariates = {
        'elevation': np.random.normal(500, 100, n_points),  # Simulated elevation
        'temperature': data_flat.mean(axis=-1) + np.random.normal(0, 2, n_points) if temporal
                      else data_flat + np.random.normal(0, 2, n_points)
    }

    # Create metadata
    metadata = {
        'synthetic': True,
        'effects': effects,
        'noise_level': noise_level,
        'temporal': temporal,
        'n_timepoints': n_timepoints if temporal else None,
        'generation_timestamp': str(np.datetime64('now'))
    }

    return SPMData(
        data=data_flat,
        coordinates=coordinates,
        time=time_coords,
        covariates=covariates,
        metadata=metadata,
        crs='EPSG:4326'
    )


def create_spatial_basis_functions(coordinates: np.ndarray, n_basis: int = 10,
                                 method: str = 'gaussian') -> np.ndarray:
    """
    Create spatial basis functions for modeling spatial variation.

    Args:
        coordinates: Spatial coordinates (n_points, 2)
        n_basis: Number of basis functions
        method: Basis function method ('gaussian', 'polynomial', 'fourier')

    Returns:
        Basis function matrix (n_points, n_basis)
    """
    n_points = len(coordinates)

    if method == 'gaussian':
        # Gaussian radial basis functions
        # Random centers
        np.random.seed(42)  # For reproducibility
        center_indices = np.random.choice(n_points, size=min(n_basis, n_points),
                                        replace=False)
        centers = coordinates[center_indices]

        # Width based on median distance
        distances = np.linalg.norm(coordinates[:, np.newaxis] - centers[np.newaxis, :], axis=2)
        median_dist = np.median(distances)
        width = median_dist / np.sqrt(n_basis)

        basis = np.zeros((n_points, n_basis))
        for i in range(n_basis):
            distances_to_center = np.linalg.norm(coordinates - centers[i % len(centers)], axis=1)
            basis[:, i] = np.exp(-distances_to_center**2 / (2 * width**2))

    elif method == 'polynomial':
        # Polynomial basis functions
        lon, lat = coordinates[:, 0], coordinates[:, 1]

        # Normalize coordinates
        lon_norm = (lon - np.mean(lon)) / np.std(lon)
        lat_norm = (lat - np.mean(lat)) / np.std(lat)

        basis_list = [np.ones(n_points)]  # Constant

        degree = 1
        while len(basis_list) < n_basis:
            for i in range(degree + 1):
                j = degree - i
                if i <= 2 and j <= 2:  # Limit to degree 2 to avoid overfitting
                    basis_list.append(lon_norm**i * lat_norm**j)

            degree += 1

        basis = np.column_stack(basis_list[:n_basis])

    elif method == 'fourier':
        # Fourier basis functions
        lon_rad = np.radians(coordinates[:, 0])
        lat_rad = np.radians(coordinates[:, 1])

        basis_list = [np.ones(n_points)]  # Constant

        max_freq = int(np.sqrt(n_basis)) + 1
        for freq_lon in range(max_freq):
            for freq_lat in range(max_freq):
                if len(basis_list) >= n_basis:
                    break
                if freq_lon == 0 and freq_lat == 0:
                    continue  # Already added constant

                basis_list.extend([
                    np.cos(freq_lon * lon_rad) * np.cos(freq_lat * lat_rad),
                    np.sin(freq_lon * lon_rad) * np.cos(freq_lat * lat_rad)
                ])

            if len(basis_list) >= n_basis:
                break

        basis = np.column_stack(basis_list[:n_basis])

    else:
        raise ValueError(f"Unknown basis method: {method}")

    return basis


def compute_power_analysis(effect_size: float, n_points: int, alpha: float = 0.05,
                          n_simulations: int = 1000) -> Dict[str, Any]:
    """
    Perform power analysis for SPM statistical tests.

    Args:
        effect_size: Expected effect size
        n_points: Number of spatial/temporal points
        alpha: Significance level
        n_simulations: Number of simulation runs

    Returns:
        Dictionary with power analysis results
    """
    # Simplified power analysis for t-tests
    # In practice, this would account for spatial autocorrelation

    # Degrees of freedom
    df = n_points - 2  # Assuming simple regression

    # Critical t-value
    t_critical = stats.t.ppf(1 - alpha/2, df)

    # Power calculation using non-central t-distribution
    power_values = []

    for _ in range(n_simulations):
        # Simulate data with effect
        noise = np.random.normal(0, 1, n_points)
        data_with_effect = effect_size + noise

        # Simple regression
        x = np.random.normal(0, 1, n_points)
        slope = np.sum(x * data_with_effect) / np.sum(x**2)
        se = np.sqrt(np.sum((data_with_effect - slope * x)**2) / (n_points - 2)) / np.sqrt(np.sum(x**2))

        t_stat = slope / se
        power_values.append(abs(t_stat) > t_critical)

    power = np.mean(power_values)

    return {
        'power': power,
        'effect_size': effect_size,
        'n_points': n_points,
        'alpha': alpha,
        't_critical': t_critical,
        'n_simulations': n_simulations
    }
