"""API interfaces for Bayesian inference engines."""

from typing import Any, Optional, Type

# External library interfaces
try:
    from .pymc_interface import PyMCInterface
except ImportError:
    PyMCInterface: Optional[Type[Any]] = None  # type: ignore[no-redef]

try:
    from .stan_interface import StanInterface
except ImportError:
    StanInterface: Optional[Type[Any]] = None  # type: ignore[no-redef]

try:
    from .tfp_interface import TFPInterface
except ImportError:
    TFPInterface: Optional[Type[Any]] = None  # type: ignore[no-redef]

__all__ = [
    'PyMCInterface',
    'StanInterface', 
    'TFPInterface'
] 