"""
Utility modules for GEO-INFER-ANT
"""

try:
    from .config import (
        load_config,
        validate_config,
        save_config,
        get_default_config,
        update_config,
        AntModuleConfig,
        SwarmConfig,
        AlgorithmConfig,
        StigmergyConfig,
        SpatialConfig,
        PerformanceConfig,
        LoggingConfig,
    )

    __all__ = [
        "load_config",
        "validate_config",
        "save_config",
        "get_default_config",
        "update_config",
        "AntModuleConfig",
        "SwarmConfig",
        "AlgorithmConfig",
        "StigmergyConfig",
        "SpatialConfig",
        "PerformanceConfig",
        "LoggingConfig",
    ]
except ImportError as e:
    import logging

    logging.warning(f"Config utilities not available: {e}")
    __all__ = []

from .spatial import parse_h3_resolution, validate_bounds, validate_numeric_matrix

__all__ = [
    *__all__,
    "parse_h3_resolution",
    "validate_bounds",
    "validate_numeric_matrix",
]
