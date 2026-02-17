"""
Cross-Module Integration Convenience Methods

This module provides convenience methods for integrating across
different GEO-INFER modules.
"""

import numpy as np
from typing import Union, Optional, List, Tuple, Dict, Any
import logging

logger = logging.getLogger(__name__)


def cross_module_helper(
    module_name: str,
    operation: str,
    data: Dict[str, Any],
    **kwargs
) -> Any:
    """
    Helper for cross-module operations.

    Args:
        module_name: Name of module to use
        operation: Operation to perform
        data: Input data
        **kwargs: Additional parameters

    Returns:
        Operation result
    """
    if module_name == 'act':
        from geo_infer_math.api.convenience.act_convenience import (
            ActiveInferenceConvenience
        )
        conv = ActiveInferenceConvenience()
        if operation == 'free_energy':
            return conv.calculate_free_energy(
                data.get('observations'),
                data.get('beliefs'),
                **kwargs
            )
    
    elif module_name == 'bayes':
        from geo_infer_math.api.convenience.bayes_convenience import (
            BayesianConvenience
        )
        conv = BayesianConvenience()
        if operation == 'posterior':
            return conv.calculate_posterior(
                data.get('prior'),
                data.get('likelihood'),
                data.get('data'),
                **kwargs
            )
    
    elif module_name == 'ai':
        from geo_infer_math.api.convenience.ai_convenience import AIConvenience
        conv = AIConvenience()
        if operation == 'gradient':
            return conv.compute_gradient(
                data.get('function'),
                data.get('parameters'),
                **kwargs
            )
    
    else:
        raise ValueError(f"Unknown module: {module_name}")
    
    return None


class IntegrationConvenience:
    """
    Convenience class for cross-module integration.
    
    Provides methods for integrating operations across modules.
    """
    
    def __init__(self):
        """Initialize integration convenience class."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._module_registry: Dict[str, Any] = {}
        self.logger.debug("IntegrationConvenience initialized")
    
    def execute_cross_module(
        self,
        module_name: str,
        operation: str,
        data: Dict[str, Any],
        **kwargs
    ) -> Any:
        """
        Execute cross-module operation.
        
        Args:
            module_name: Module name
            operation: Operation name
            data: Input data
            **kwargs: Additional parameters
        
        Returns:
            Operation result
        """
        return cross_module_helper(module_name, operation, data, **kwargs)

