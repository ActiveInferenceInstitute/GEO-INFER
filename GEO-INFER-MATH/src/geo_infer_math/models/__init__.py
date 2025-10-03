"""
Statistical and machine learning models for geospatial data.

This package provides specialized mathematical models designed specifically
for analyzing geographical and spatial patterns and relationships.
"""

# Try to import available model modules
_available_models = []

try:
    from geo_infer_math.models import regression
    _available_models.append("regression")
except ImportError:
    pass

try:
    from geo_infer_math.models import clustering
    _available_models.append("clustering")
except ImportError:
    pass

# Future modules (when implemented)
# try:
#     from geo_infer_math.models import dimension_reduction
#     _available_models.append("dimension_reduction")
# except ImportError:
#     pass

# try:
#     from geo_infer_math.models import manifold_learning
#     _available_models.append("manifold_learning")
# except ImportError:
#     pass

# try:
#     from geo_infer_math.models import spectral_analysis
#     _available_models.append("spectral_analysis")
# except ImportError:
#     pass

__all__ = _available_models
