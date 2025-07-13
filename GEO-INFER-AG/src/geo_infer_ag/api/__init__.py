"""
GEO-INFER-AG API Module

This module provides API functionality for agricultural applications
in the GEO-INFER framework.
"""

from .agricultural_api import AgriculturalAPI, AgriculturalConfig, create_agricultural_api, get_crop_recommendations

__all__ = [
    'AgriculturalAPI',
    'AgriculturalConfig', 
    'create_agricultural_api',
    'get_crop_recommendations'
] 