"""
GPU Acceleration backend for GEO-INFER-SPACE.

Provides optional CUDA/JAX GPU-accelerated spatial joins and H3 distance
kernels with strict zero-dependency CPU fallback semantics. The module
imports cleanly whether or not any accelerator library is installed; the
CPU reference path is authoritative.
"""

__version__ = "1.0.0"

from .gpu_acceleration import (
    EARTH_RADIUS_KM,
    EARTH_RADIUS_M,
    HAS_CUPY,
    HAS_GPU,
    HAS_JAX,
    HAS_TORCH,
    euclidean_distance_kernel,
    get_available_backends,
    gpu_spatial_join_by_distance,
    h3_grid_distance_kernel,
    is_accelerator_available,
    pairwise_haversine_kernel,
    spatial_join_kernel,
)

__all__ = [
    "EARTH_RADIUS_KM",
    "EARTH_RADIUS_M",
    "HAS_CUPY",
    "HAS_GPU",
    "HAS_JAX",
    "HAS_TORCH",
    "euclidean_distance_kernel",
    "get_available_backends",
    "gpu_spatial_join_by_distance",
    "h3_grid_distance_kernel",
    "is_accelerator_available",
    "pairwise_haversine_kernel",
    "spatial_join_kernel",
]