"""
Generic spatial analytics interface for GEO-INFER-SPACE.

This module defines the generic interface for spatial analytics operations
that can be implemented by different backends (H3, SRAI, etc.).
"""

from typing import Dict, Any, List, Optional, Tuple, Union
import logging
import numpy as np

logger = logging.getLogger(__name__)


class SpatialAnalyticsInterface:
    """
    Generic interface for spatial analytics operations.

    This class provides a unified API for spatial analytics that can dispatch
    to different backends based on configuration.
    """

    def __init__(self, backend: Optional[str] = None):
        from .dispatcher import get_backend_dispatcher
        self.dispatcher = get_backend_dispatcher()
        self.backend = backend

    def analyze_hotspots(self, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Analyze spatial hotspots in the data.

        Args:
            data: Spatial data with values to analyze
            **kwargs: Additional backend-specific parameters

        Returns:
            Hotspot analysis results
        """
        return self.dispatcher.dispatch_analytics_operation(
            'analyze_hotspots', data, backend=self.backend, **kwargs
        )

    def analyze_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze spatial context for a given location or area.

        Args:
            context: Spatial context information

        Returns:
            Analysis results for the spatial context
        """
        return self.dispatcher.dispatch_analytics_operation(
            'analyze_context', context, backend=self.backend
        )

    def analyze_clusters(self, data: np.ndarray, method: str = 'kmeans', **kwargs) -> Dict[str, Any]:
        """
        Analyze spatial clustering patterns in data.

        Args:
            data: Spatial data points
            method: Clustering method to use
            **kwargs: Additional clustering parameters

        Returns:
            Clustering analysis results
        """
        return self.dispatcher.dispatch_analytics_operation(
            'analyze_clusters', data, method=method, backend=self.backend, **kwargs
        )

    def find_hotspots(self, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Find spatial hotspots in data.

        Args:
            data: Spatial data with intensity values
            **kwargs: Additional hotspot detection parameters

        Returns:
            Hotspot detection results
        """
        return self.dispatcher.dispatch_analytics_operation(
            'find_hotspots', data, backend=self.backend, **kwargs
        )

    def compute_proximity(self, points: List[Tuple[float, float]], **kwargs) -> Dict[str, Any]:
        """
        Compute proximity analysis between points.

        Args:
            points: List of (lat, lng) coordinate pairs
            **kwargs: Additional backend-specific parameters

        Returns:
            Proximity analysis results
        """
        return self.dispatcher.dispatch_analytics_operation(
            'compute_proximity', points, backend=self.backend, **kwargs
        )

    def cluster_points(self, points: List[Tuple[float, float]], **kwargs) -> Dict[str, Any]:
        """
        Cluster spatial points.

        Args:
            points: List of (lat, lng) coordinate pairs
            **kwargs: Additional backend-specific parameters (e.g., num_clusters, method)

        Returns:
            Clustering results with cluster assignments
        """
        return self.dispatcher.dispatch_analytics_operation(
            'cluster_points', points, backend=self.backend, **kwargs
        )

    def interpolate_values(self, points: List[Tuple[float, float, float]], **kwargs) -> Dict[str, Any]:
        """
        Interpolate values across a spatial surface.

        Args:
            points: List of (lat, lng, value) tuples
            **kwargs: Additional backend-specific parameters (e.g., method, resolution)

        Returns:
            Interpolated surface data
        """
        return self.dispatcher.dispatch_analytics_operation(
            'interpolate_values', points, backend=self.backend, **kwargs
        )

    def analyze_network(self, edges: List[Tuple[int, int, float]], **kwargs) -> Dict[str, Any]:
        """
        Analyze spatial network structure.

        Args:
            edges: List of (source_id, target_id, weight) tuples
            **kwargs: Additional backend-specific parameters

        Returns:
            Network analysis results (centrality, connectivity, etc.)
        """
        return self.dispatcher.dispatch_analytics_operation(
            'analyze_network', edges, backend=self.backend, **kwargs
        )

    def detect_patterns(self, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Detect spatial patterns in the data.

        Args:
            data: Spatial data to analyze for patterns
            **kwargs: Additional backend-specific parameters

        Returns:
            Pattern detection results
        """
        return self.dispatcher.dispatch_analytics_operation(
            'detect_patterns', data, backend=self.backend, **kwargs
        )

    def compute_density(self, points: List[Tuple[float, float]], **kwargs) -> Dict[str, Any]:
        """
        Compute spatial density.

        Args:
            points: List of (lat, lng) coordinate pairs
            **kwargs: Additional backend-specific parameters (e.g., bandwidth, resolution)

        Returns:
            Density analysis results
        """
        return self.dispatcher.dispatch_analytics_operation(
            'compute_density', points, backend=self.backend, **kwargs
        )

    def analyze_accessibility(self, origins: List[Tuple[float, float]],
                            destinations: List[Tuple[float, float]], **kwargs) -> Dict[str, Any]:
        """
        Analyze spatial accessibility between origins and destinations.

        Args:
            origins: List of origin (lat, lng) coordinates
            destinations: List of destination (lat, lng) coordinates
            **kwargs: Additional backend-specific parameters

        Returns:
            Accessibility analysis results
        """
        return self.dispatcher.dispatch_analytics_operation(
            'analyze_accessibility', origins, destinations, backend=self.backend, **kwargs
        )
