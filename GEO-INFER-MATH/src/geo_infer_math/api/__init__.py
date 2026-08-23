"""
API interfaces for GEO-INFER-MATH functionality.

This package provides clean, consistent interfaces for accessing the
mathematical operations and models provided by GEO-INFER-MATH.
"""

# Import convenience modules first. They are the lightweight, non-web public
# API and must remain available without Flask or Werkzeug installed.
try:
    from geo_infer_math.api.convenience import (
        AIConvenience as AIConvenience,
        ActiveInferenceConvenience as ActiveInferenceConvenience,
        BayesianConvenience as BayesianConvenience,
        InformationTheoryConvenience as InformationTheoryConvenience,
        IntegrationConvenience as IntegrationConvenience,
        SpatialConvenience as SpatialConvenience,
    )

    _convenience_available = True
except ImportError:
    _convenience_available = False


_available_apis = []
_missing_optional_dependencies = {}

try:
    from geo_infer_math.api.spatial_analysis import SpatialAnalysisAPI

    _available_apis.append("SpatialAnalysisAPI")
except ImportError as exc:
    _missing_optional_dependencies["SpatialAnalysisAPI"] = str(exc)

__all__ = list(_available_apis)

if _convenience_available:
    __all__.extend(
        [
            "ActiveInferenceConvenience",
            "BayesianConvenience",
            "AIConvenience",
            "InformationTheoryConvenience",
            "SpatialConvenience",
            "IntegrationConvenience",
        ]
    )
