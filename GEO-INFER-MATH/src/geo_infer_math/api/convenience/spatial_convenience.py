"""
Enhanced Spatial Analysis Convenience Methods

This module provides enhanced convenience methods for spatial analysis.
"""

import numpy as np
from typing import Union, Optional, List, Tuple, Dict, Any
import logging

from geo_infer_math.api.spatial_analysis import SpatialAnalysisAPI

logger = logging.getLogger(__name__)


def enhanced_spatial_analysis(
    coordinates: np.ndarray,
    values: np.ndarray,
    analysis_types: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Enhanced spatial analysis combining multiple methods.

    Args:
        coordinates: Spatial coordinates
        values: Values at locations
        analysis_types: Types of analysis to perform

    Returns:
        Dictionary of analysis results
    """
    analysis_types = analysis_types or ['autocorrelation', 'descriptive', 'interpolation']
    
    api = SpatialAnalysisAPI()
    results = {}
    
    if 'autocorrelation' in analysis_types:
        results['autocorrelation'] = api.autocorrelation_analysis(
            values, coordinates, method='moran'
        )
    
    if 'descriptive' in analysis_types:
        results['descriptive'] = api.descriptive_statistics(values, coordinates)
    
    if 'interpolation' in analysis_types:
        # Create query grid
        x_min, x_max = coordinates[:, 0].min(), coordinates[:, 0].max()
        y_min, y_max = coordinates[:, 1].min(), coordinates[:, 1].max()
        x_grid = np.linspace(x_min, x_max, 20)
        y_grid = np.linspace(y_min, y_max, 20)
        xx, yy = np.meshgrid(x_grid, y_grid)
        query_points = np.column_stack([xx.flatten(), yy.flatten()])
        
        results['interpolation'] = api.spatial_interpolation(
            coordinates, values, query_points, method='idw'
        )
    
    return results


class SpatialConvenience:
    """
    Convenience class for enhanced spatial analysis.
    
    Provides high-level methods for comprehensive spatial analysis.
    """
    
    def __init__(self):
        """Initialize spatial convenience class."""
        self.api = SpatialAnalysisAPI()
    
    def comprehensive_analysis(
        self,
        coordinates: np.ndarray,
        values: np.ndarray,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Perform comprehensive spatial analysis.
        
        Args:
            coordinates: Spatial coordinates
            values: Values at locations
            **kwargs: Additional parameters
        
        Returns:
            Dictionary of analysis results
        """
        return enhanced_spatial_analysis(coordinates, values, **kwargs)

