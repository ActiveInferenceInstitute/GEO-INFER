"""Optional float64 GPU numeric distances and authoritative host H3 topology.

Accelerators load only on a capability probe or numeric GPU request. NumPy CPU
execution is always available without accelerator packages. Legacy HAS_* flags
are lazy attributes; availability means a usable float64 GPU, not installation.
"""

from . import gpu_acceleration
from .gpu_acceleration import (
    AcceleratorUnavailableError,
    DEFAULT_CHUNK_SIZE,
    EARTH_RADIUS_KM,
    EARTH_RADIUS_M,
    euclidean_distance_kernel,
    get_available_backends,
    get_backend_diagnostics,
    gpu_spatial_join_by_distance,
    h3_grid_distance_kernel,
    is_accelerator_available,
    pairwise_haversine_kernel,
    spatial_join_kernel,
)

__version__ = "1.1.0"


def __getattr__(name: str) -> bool:
    if name in {"HAS_CUPY", "HAS_GPU", "HAS_JAX", "HAS_TORCH"}:
        return getattr(gpu_acceleration, name)
    raise AttributeError(name)


__all__ = [
    "AcceleratorUnavailableError",
    "DEFAULT_CHUNK_SIZE",
    "EARTH_RADIUS_KM",
    "EARTH_RADIUS_M",
    "HAS_CUPY",
    "HAS_GPU",
    "HAS_JAX",
    "HAS_TORCH",
    "euclidean_distance_kernel",
    "get_available_backends",
    "get_backend_diagnostics",
    "gpu_spatial_join_by_distance",
    "h3_grid_distance_kernel",
    "is_accelerator_available",
    "pairwise_haversine_kernel",
    "spatial_join_kernel",
]
