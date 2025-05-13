"""
Spatial Analysis API

Provides a clean, consistent interface for spatial analysis operations.
This module serves as a facade over the more complex spatial statistics
and geometric operations provided by the core modules.
"""

import numpy as np
from typing import Union, List, Tuple, Dict, Optional, Any, Callable
from dataclasses import dataclass

from geo_infer_math.core.spatial_statistics import (
    MoranI, getis_ord_g, local_indicators_spatial_association,
    ripley_k, semivariogram, spatial_descriptive_statistics
)
from geo_infer_math.core.geometry import (
    haversine_distance, vincenty_distance, Point, LineString, Polygon,
    point_in_polygon, buffer_point
)

class SpatialAnalysisAPI:
    """
    Provides high-level methods for spatial analysis by encapsulating
    and combining multiple lower-level operations from the core modules.
    """
    
    def __init__(self, verbose: bool = False):
        """
        Initialize the SpatialAnalysisAPI.
        
        Args:
            verbose: Whether to print detailed information during operations
        """
        self.verbose = verbose
    
    def autocorrelation_analysis(
        self, 
        values: np.ndarray, 
        coordinates: np.ndarray, 
        method: str = 'moran',
        **kwargs
    ) -> Dict[str, Any]:
        """
        Perform spatial autocorrelation analysis using the specified method.
        
        Args:
            values: Array of values at each location
            coordinates: Array of coordinates (n x 2)
            method: Method to use ('moran', 'getis', 'lisa')
            **kwargs: Additional parameters to pass to the specific method
            
        Returns:
            Dictionary of results from the analysis
        """
        if self.verbose:
            print(f"Performing {method} spatial autocorrelation analysis...")
        
        # Create a weights matrix from coordinates if not provided
        weights_matrix = kwargs.get('weights_matrix', None)
        
        if method.lower() == 'moran':
            # Perform Moran's I analysis
            moran = MoranI(weights_matrix)
            results = moran.compute(values, coordinates if weights_matrix is None else None)
            
            # Add interpretation
            interpretation = "No significant spatial autocorrelation (random pattern)"
            if results['p_value'] < 0.05:
                if results['I'] > 0:
                    interpretation = "Significant positive spatial autocorrelation (clustered pattern)"
                else:
                    interpretation = "Significant negative spatial autocorrelation (dispersed pattern)"
            
            results['interpretation'] = interpretation
            return results
            
        elif method.lower() == 'getis':
            # Ensure we have a weights matrix
            if weights_matrix is None:
                moran = MoranI()
                weights_matrix = moran._generate_weights(coordinates)
            
            # Perform Getis-Ord G* analysis
            results = getis_ord_g(values, weights_matrix)
            
            # Add hot and cold spot counts
            results['hot_spots'] = np.sum(results['z_scores'] > 1.96)
            results['cold_spots'] = np.sum(results['z_scores'] < -1.96)
            
            return results
            
        elif method.lower() == 'lisa':
            # Ensure we have a weights matrix
            if weights_matrix is None:
                moran = MoranI()
                weights_matrix = moran._generate_weights(coordinates)
            
            # Perform LISA analysis
            results = local_indicators_spatial_association(values, weights_matrix)
            
            # Count each type of cluster/outlier
            results['high_high_count'] = np.sum(results['classifications'] == 1)
            results['low_low_count'] = np.sum(results['classifications'] == 2)
            results['high_low_count'] = np.sum(results['classifications'] == 3)
            results['low_high_count'] = np.sum(results['classifications'] == 4)
            
            return results
        
        else:
            raise ValueError(f"Unknown method: {method}. Choose from 'moran', 'getis', or 'lisa'.")
    
    def point_pattern_analysis(
        self,
        points: np.ndarray,
        method: str = 'ripley',
        **kwargs
    ) -> Dict[str, Any]:
        """
        Perform point pattern analysis using the specified method.
        
        Args:
            points: Array of point coordinates (n x 2)
            method: Method to use ('ripley', 'nearest_neighbor', 'quadrat')
            **kwargs: Additional parameters to pass to the specific method
            
        Returns:
            Dictionary of results from the analysis
        """
        if self.verbose:
            print(f"Performing {method} point pattern analysis...")
        
        if method.lower() == 'ripley':
            # Get or create distances
            distances = kwargs.get('distances', None)
            if distances is None:
                # Auto-generate distances based on study area
                min_x, min_y = np.min(points, axis=0)
                max_x, max_y = np.max(points, axis=0)
                width = max_x - min_x
                height = max_y - min_y
                max_distance = min(width, height) / 2
                distances = np.linspace(0, max_distance, 20)[1:]  # Exclude 0
            
            # Get or calculate area
            area = kwargs.get('area', None)
            if area is None:
                # Calculate area of minimum bounding rectangle
                min_x, min_y = np.min(points, axis=0)
                max_x, max_y = np.max(points, axis=0)
                area = (max_x - min_x) * (max_y - min_y)
            
            # Perform Ripley's K analysis
            results = ripley_k(points, distances, area, 
                              boundary_correction=kwargs.get('boundary_correction', True))
            
            # Add interpretation
            l_function = results['l_function']
            interpretation = []
            
            # Check for clustering or dispersion at different scales
            for i, r in enumerate(results['distances']):
                l_val = l_function[i]
                if l_val > 0.1:  # Positive L function suggests clustering
                    interpretation.append(f"Clustering at distance {r:.2f}")
                elif l_val < -0.1:  # Negative L function suggests dispersion
                    interpretation.append(f"Dispersion at distance {r:.2f}")
            
            results['interpretation'] = interpretation
            return results
            
        elif method.lower() == 'nearest_neighbor':
            # Simple nearest neighbor analysis
            n = len(points)
            all_distances = np.zeros((n, n))
            
            # Calculate all pairwise distances
            for i in range(n):
                for j in range(i+1, n):
                    dist = np.sqrt(np.sum((points[i] - points[j])**2))
                    all_distances[i, j] = dist
                    all_distances[j, i] = dist
            
            # Get nearest neighbor distances (excluding self)
            nearest_distances = []
            for i in range(n):
                distances = all_distances[i]
                nearest = np.min(distances[distances > 0])
                nearest_distances.append(nearest)
            
            # Calculate nearest neighbor statistics
            mean_nearest = np.mean(nearest_distances)
            
            # Get or calculate area
            area = kwargs.get('area', None)
            if area is None:
                # Calculate area of minimum bounding rectangle
                min_x, min_y = np.min(points, axis=0)
                max_x, max_y = np.max(points, axis=0)
                area = (max_x - min_x) * (max_y - min_y)
            
            # Calculate density
            density = n / area
            
            # Expected mean distance for a random pattern
            expected_distance = 0.5 / np.sqrt(density)
            
            # Calculate R statistic
            r_statistic = mean_nearest / expected_distance
            
            # Standard error
            se = 0.26136 / np.sqrt(n * density)
            
            # Z score
            z_score = (mean_nearest - expected_distance) / se
            
            # P-value (simplified calculation)
            p_value = 2 * (1 - np.abs(np.clip(z_score, -8, 8) / 8))
            
            return {
                'nearest_distances': np.array(nearest_distances),
                'mean_distance': mean_nearest,
                'expected_distance': expected_distance,
                'r_statistic': r_statistic,
                'z_score': z_score,
                'p_value': p_value,
                'interpretation': "Clustered" if r_statistic < 1 else "Dispersed" if r_statistic > 1 else "Random"
            }
        
        else:
            raise ValueError(f"Unknown method: {method}. Choose from 'ripley' or 'nearest_neighbor'.")
    
    def spatial_interpolation(
        self,
        known_points: np.ndarray,
        known_values: np.ndarray,
        query_points: np.ndarray,
        method: str = 'idw',
        **kwargs
    ) -> np.ndarray:
        """
        Perform spatial interpolation to estimate values at unsampled locations.
        
        Args:
            known_points: Array of coordinates with known values (n x 2)
            known_values: Array of known values (n)
            query_points: Array of coordinates to interpolate values for (m x 2)
            method: Interpolation method ('idw', 'kriging', 'nearest')
            **kwargs: Additional parameters for the specific method
            
        Returns:
            Array of interpolated values (m)
        """
        if self.verbose:
            print(f"Performing {method} spatial interpolation...")
        
        if method.lower() == 'idw':
            # Inverse Distance Weighting interpolation
            power = kwargs.get('power', 2)
            max_points = kwargs.get('max_points', None)
            
            n_known = len(known_points)
            n_query = len(query_points)
            
            # Calculate distances between all known and query points
            distances = np.zeros((n_query, n_known))
            for i in range(n_query):
                for j in range(n_known):
                    distances[i, j] = np.sqrt(np.sum((query_points[i] - known_points[j])**2))
            
            # Handle points that exactly match known points
            exact_matches = distances == 0
            
            # Calculate weights (inverse distance)
            # Add small epsilon to avoid division by zero
            epsilon = 1e-10
            weights = 1 / (distances + epsilon) ** power
            
            # If max_points is specified, only use the nearest N points
            if max_points is not None and max_points < n_known:
                for i in range(n_query):
                    # Get indices of points to exclude (beyond max_points nearest)
                    idx = np.argsort(distances[i])[max_points:]
                    weights[i, idx] = 0
            
            # Normalize weights to sum to 1
            row_sums = weights.sum(axis=1)
            weights = weights / row_sums[:, np.newaxis]
            
            # Calculate interpolated values
            interpolated_values = np.sum(weights * known_values, axis=1)
            
            # Override with exact values where points match
            for i in range(n_query):
                if np.any(exact_matches[i]):
                    idx = np.where(exact_matches[i])[0][0]
                    interpolated_values[i] = known_values[idx]
            
            return interpolated_values
            
        elif method.lower() == 'nearest':
            # Simple nearest neighbor interpolation
            n_known = len(known_points)
            n_query = len(query_points)
            
            interpolated_values = np.zeros(n_query)
            
            for i in range(n_query):
                # Calculate distances to all known points
                distances = np.zeros(n_known)
                for j in range(n_known):
                    distances[j] = np.sqrt(np.sum((query_points[i] - known_points[j])**2))
                
                # Find nearest neighbor
                nearest_idx = np.argmin(distances)
                interpolated_values[i] = known_values[nearest_idx]
            
            return interpolated_values
            
        else:
            raise ValueError(f"Unknown method: {method}. Choose from 'idw' or 'nearest'.")
    
    def distance_matrix(
        self,
        points1: np.ndarray,
        points2: Optional[np.ndarray] = None,
        method: str = 'euclidean',
        **kwargs
    ) -> np.ndarray:
        """
        Calculate a distance matrix between two sets of points.
        
        Args:
            points1: First set of points (n x 2)
            points2: Second set of points (m x 2), defaults to points1 if None
            method: Distance calculation method ('euclidean', 'haversine', 'manhattan')
            **kwargs: Additional parameters for the specific method
            
        Returns:
            Distance matrix (n x m)
        """
        if self.verbose:
            print(f"Calculating {method} distance matrix...")
        
        if points2 is None:
            points2 = points1
        
        n = len(points1)
        m = len(points2)
        
        distance_matrix = np.zeros((n, m))
        
        if method.lower() == 'euclidean':
            # Calculate Euclidean distance matrix
            for i in range(n):
                for j in range(m):
                    distance_matrix[i, j] = np.sqrt(np.sum((points1[i] - points2[j])**2))
            
            return distance_matrix
            
        elif method.lower() == 'haversine':
            # Calculate Haversine distance matrix (for geographic coordinates)
            for i in range(n):
                for j in range(m):
                    distance_matrix[i, j] = haversine_distance(
                        points1[i, 0], points1[i, 1],
                        points2[j, 0], points2[j, 1]
                    )
            
            return distance_matrix
            
        elif method.lower() == 'manhattan':
            # Calculate Manhattan distance matrix
            for i in range(n):
                for j in range(m):
                    distance_matrix[i, j] = np.sum(np.abs(points1[i] - points2[j]))
            
            return distance_matrix
            
        else:
            raise ValueError(f"Unknown method: {method}. Choose from 'euclidean', 'haversine', or 'manhattan'.")
    
    def descriptive_statistics(
        self,
        values: np.ndarray,
        coordinates: Optional[np.ndarray] = None
    ) -> Dict[str, Any]:
        """
        Calculate descriptive statistics for spatial data.
        
        Args:
            values: Array of values
            coordinates: Optional array of coordinates (n x 2)
            
        Returns:
            Dictionary of descriptive statistics
        """
        if self.verbose:
            print("Calculating descriptive statistics...")
        
        if coordinates is not None:
            # Calculate spatial descriptive statistics
            stats = spatial_descriptive_statistics(coordinates, values)
            
            return {
                'mean': stats.mean,
                'median': stats.median,
                'stdev': stats.stdev,
                'variance': stats.variance,
                'min_value': stats.min_value,
                'max_value': stats.max_value,
                'centroid': stats.centroid,
                'dispersion': stats.dispersion,
                'skewness': stats.skewness,
                'kurtosis': stats.kurtosis
            }
        else:
            # Calculate basic descriptive statistics
            return {
                'mean': np.mean(values),
                'median': np.median(values),
                'stdev': np.std(values),
                'variance': np.var(values),
                'min_value': np.min(values),
                'max_value': np.max(values),
                'skewness': None,  # Requires scipy.stats
                'kurtosis': None   # Requires scipy.stats
            }

# Create a singleton instance for easy access
spatial_analysis = SpatialAnalysisAPI()

__all__ = [
    "SpatialAnalysisAPI",
    "spatial_analysis"
] 