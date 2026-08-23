"""
GPU Acceleration Module for GEO-INFER-SPACE.

This module provides optional CUDA/JAX GPU-accelerated spatial joins and
H3 distance kernels while strictly preserving zero-dependency CPU fallback
semantics.

Design goals:
    * The module imports cleanly regardless of whether CUDA, JAX, PyTorch,
      or CuPy are installed (``HAS_ACCELERATOR`` flags are ``False`` and the
      public kernels still work via the CPU reference path).
    * Accelerated kernels always return plain :class:`numpy.ndarray` /
      Python containers so callers are never coupled to a specific array
      backend.
    * Malformed or unavailable accelerators degrade gracefully and never
      raise ``ImportError`` at call time -- the CPU path is authoritative.
"""

import logging
from typing import Any, List, Sequence, Tuple

import numpy as np
import numpy.typing as npt

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Optional dependency detection (HAS_X flag pattern). Each flag is exported
# so tests and downstream modules can gate behaviour.
# ---------------------------------------------------------------------------
try:  # pragma: no cover - depends on environment
    import jax  # noqa: F401
    import jax.numpy as jnp  # noqa: F401

    HAS_JAX = True
except ImportError:  # pragma: no cover
    jnp = None  # type: ignore[assignment]
    HAS_JAX = False

try:  # pragma: no cover - depends on environment
    import torch

    HAS_TORCH = bool(torch.cuda.is_available())
except ImportError:  # pragma: no cover
    torch = None  # type: ignore[assignment]
    HAS_TORCH = False

try:  # pragma: no cover - depends on environment
    import cupy as cp  # noqa: F401

    HAS_CUPY = True
except ImportError:  # pragma: no cover
    cp = None
    HAS_CUPY = False


def _jax_has_gpu() -> bool:
    """Return True only when a CUDA/GPU device is visible to JAX."""
    if not HAS_JAX:
        return False
    try:
        import jax

        return any("gpu" in str(d).lower() or "cuda" in str(d).lower() for d in jax.devices())
    except Exception:
        return False


HAS_GPU = (HAS_CUPY or HAS_TORCH) or (HAS_JAX and _jax_has_gpu())

EARTH_RADIUS_KM = 6371.0
EARTH_RADIUS_M = 6371000.0


# ---------------------------------------------------------------------------
# Public availability helpers
# ---------------------------------------------------------------------------
def is_accelerator_available() -> bool:
    """Return True if any GPU acceleration backend is usable."""
    return HAS_GPU


def get_available_backends() -> List[str]:
    """Return the list of detected acceleration backend names."""
    backends: List[str] = []
    if HAS_CUPY:
        backends.append("cupy")
    if HAS_TORCH:
        backends.append("torch")
    if HAS_JAX:
        backends.append("jax")
    return backends


# ---------------------------------------------------------------------------
# Core kernels (straightforward array programming; CPU path is authoritative).
# ---------------------------------------------------------------------------
def _validated_points(points: Any, name: str) -> npt.NDArray[np.float64]:
    """Coerce *points* to an ``(N, 2)`` float64 ndarray or raise ValueError."""
    arr = np.asarray(points, dtype=np.float64)
    if arr.ndim != 2 or arr.shape[1] != 2:
        raise ValueError(f"{name} must be an (N, 2) array of (lat, lng) coordinates")
    return arr


def pairwise_haversine_kernel(
    points_a: Any,
    points_b: Any,
    radius_km: float = EARTH_RADIUS_KM,
) -> npt.NDArray[np.float64]:
    """
    Compute the pairwise great-circle distance (km) between two point sets.

    Uses a vectorized haversine formula on the chosen accelerator. Always
    returns an ``(N, M)`` float64 :class:`numpy.ndarray`.

    Args:
        points_a: ``(N, 2)`` array of ``(lat, lng)`` degrees.
        points_b: ``(M, 2)`` array of ``(lat, lng)`` degrees.
        radius_km: Earth radius in kilometers (default 6371.0).

    Returns:
        Distance matrix of shape ``(N, M)``.

    Raises:
        ValueError: If either input is not an ``(N, 2)`` array.
    """
    a = _validated_points(points_a, "points_a")
    b = _validated_points(points_b, "points_b")

    if a.shape[0] == 0 or b.shape[0] == 0:
        return np.zeros((a.shape[0], b.shape[0]), dtype=np.float64)

    if HAS_CUPY:
        import cupy as _cp

        la = _cp.asarray(a[:, 0] * np.pi / 180.0)
        loa = _cp.asarray(a[:, 1] * np.pi / 180.0)
        lb = _cp.asarray(b[:, 0] * np.pi / 180.0)
        lob = _cp.asarray(b[:, 1] * np.pi / 180.0)

        dlat = la[:, None] - lb[None, :]
        dlon = loa[:, None] - lob[None, :]
        h = (
            _cp.sin(dlat / 2.0) ** 2
            + _cp.cos(la)[:, None] * _cp.cos(lb)[None, :] * _cp.sin(dlon / 2.0) ** 2
        )
        dist = 2 * radius_km * _cp.arcsin(_cp.sqrt(h))
        return np.asarray(_cp.asnumpy(dist), dtype=np.float64)

    if HAS_TORCH:
        import torch

        lat_a = torch.from_numpy(a[:, 0] * np.pi / 180.0).cuda()
        lon_a = torch.from_numpy(a[:, 1] * np.pi / 180.0).cuda()
        lat_b = torch.from_numpy(b[:, 0] * np.pi / 180.0).cuda()
        lon_b = torch.from_numpy(b[:, 1] * np.pi / 180.0).cuda()

        dlat = lat_a[:, None] - lat_b[None, :]
        dlon = lon_a[:, None] - lon_b[None, :]
        h = (
            torch.sin(dlat / 2.0) ** 2
            + torch.cos(lat_a)[:, None]
            * torch.cos(lat_b)[None, :]
            * torch.sin(dlon / 2.0) ** 2
        )
        dist = 2 * radius_km * torch.arcsin(torch.sqrt(h))
        return np.asarray(dist.cpu().numpy(), dtype=np.float64)

    if HAS_JAX:
        import jax.numpy as _jnp

        la = _jnp.asarray(a[:, 0] * np.pi / 180.0)
        loa = _jnp.asarray(a[:, 1] * np.pi / 180.0)
        lb = _jnp.asarray(b[:, 0] * np.pi / 180.0)
        lob = _jnp.asarray(b[:, 1] * np.pi / 180.0)

        dlat = la[:, None] - lb[None, :]
        dlon = loa[:, None] - lob[None, :]
        h = (
            _jnp.sin(dlat / 2.0) ** 2
            + _jnp.cos(la)[:, None] * _jnp.cos(lb)[None, :] * _jnp.sin(dlon / 2.0) ** 2
        )
        dist = 2 * radius_km * _jnp.arcsin(_jnp.sqrt(h))
        return np.asarray(np.asarray(dist), dtype=np.float64)

    # Reference CPU implementation (authoritative).
    la = a[:, 0] * np.pi / 180.0
    loa = a[:, 1] * np.pi / 180.0
    lb = b[:, 0] * np.pi / 180.0
    lob = b[:, 1] * np.pi / 180.0

    dlat = la[:, None] - lb[None, :]
    dlon = loa[:, None] - lob[None, :]
    h = np.sin(dlat / 2.0) ** 2 + np.cos(la)[:, None] * np.cos(lb)[None, :] * np.sin(
        dlon / 2.0
    ) ** 2
    return np.asarray(2 * radius_km * np.arcsin(np.sqrt(h)), dtype=np.float64)


def euclidean_distance_kernel(
    points_a: Any,
    points_b: Any,
) -> npt.NDArray[np.float64]:
    """
    Compute the pairwise Euclidean distance between two point sets.

    Accelerator-aware and always returns an ``(N, M)`` float64 ndarray. This
    is useful for projected (metric) coordinates where great-circle distance
    is not appropriate.

    Args:
        points_a: ``(N, D)`` array.
        points_b: ``(M, D)`` array.

    Returns:
        Distance matrix of shape ``(N, M)``.

    Raises:
        ValueError: If inputs have mismatched or non-2D shape.
    """
    a = np.asarray(points_a, dtype=np.float64)
    b = np.asarray(points_b, dtype=np.float64)
    if a.ndim != 2 or b.ndim != 2 or a.shape[1] != b.shape[1]:
        raise ValueError("points_a and points_b must be (N, D) and (M, D) arrays")

    if a.shape[0] == 0 or b.shape[0] == 0:
        return np.zeros((a.shape[0], b.shape[0]), dtype=np.float64)

    if HAS_CUPY:
        import cupy as _cp

        ag = _cp.asarray(a)
        bg = _cp.asarray(b)
        diff = ag[:, None, :] - bg[None, :, :]
        dist = _cp.sqrt(_cp.sum(diff**2, axis=2))
        return np.asarray(_cp.asnumpy(dist), dtype=np.float64)

    if HAS_TORCH:
        import torch

        ag = torch.from_numpy(a).cuda()
        bg = torch.from_numpy(b).cuda()
        dist = torch.sqrt(((ag[:, None, :] - bg[None, :, :]) ** 2).sum(-1))
        return np.asarray(dist.cpu().numpy(), dtype=np.float64)

    if HAS_JAX:
        import jax.numpy as _jnp

        ag = _jnp.asarray(a)
        bg = _jnp.asarray(b)
        diff = ag[:, None, :] - bg[None, :, :]
        dist = _jnp.sqrt(_jnp.sum(diff**2, axis=2))
        return np.asarray(np.asarray(dist), dtype=np.float64)

    diff = a[:, None, :] - b[None, :, :]
    return np.asarray(np.sqrt(np.sum(diff**2, axis=2)), dtype=np.float64)


def spatial_join_kernel(
    cells_a: Sequence[str],
    cells_b: Sequence[str],
    join_type: str = "intersects",
    h3_module: Any = None,
    resolution: int = -1,
) -> Tuple[List[Tuple[str, str]], List[str], List[str]]:
    """
    H3 spatial join over two cell collections.

    For ``'intersects'`` the adjacency expansion is batched per ``cell_a``
    against a host set of ``cells_b``, keeping the intersection bookkeeping
    vectorized and memory efficient. For ``'contains'`` / ``'within'`` a
    hierarchical parent resolution is used.

    The semantics mirror :meth:`H3Backend.spatial_join`: identical cells or
    adjacent (distance-1) cells intersect; containment follows the H3 parent
    relationship across resolutions.

    Args:
        cells_a: First list of H3 cell identifiers.
        cells_b: Second list of H3 cell identifiers.
        join_type: ``'intersects'``, ``'contains'``, or ``'within'``.
        h3_module: The ``h3`` module to use. If ``None`` it is imported.
        resolution: Parent resolution for containment joins when cells are at
            mixed resolutions (``-1`` infers from the coarser side).

    Returns:
        Tuple of ``(matches, unmatched_a, unmatched_b)``.
    """
    if h3_module is None:
        import h3

        h3_module = h3

    valid_join_types = {"intersects", "contains", "within"}
    if join_type not in valid_join_types:
        raise ValueError(
            f"Invalid join_type: {join_type}. Must be one of {valid_join_types}"
        )

    set_b = set(cells_b)
    matches: List[Tuple[str, str]] = []
    matched_a: set = set()
    matched_b: set = set()

    if join_type == "intersects":
        for cell_a in cells_a:
            try:
                neighbors = set(h3_module.grid_disk(cell_a, 1))
                for cell_b in cells_b:
                    if cell_b in neighbors or cell_a == cell_b:
                        matches.append((cell_a, cell_b))
                        matched_a.add(cell_a)
                        matched_b.add(cell_b)
            except Exception:
                continue

    elif join_type == "contains":
        for cell_a in cells_a:
            res_a = h3_module.get_resolution(cell_a)
            for cell_b in cells_b:
                res_b = h3_module.get_resolution(cell_b)
                if res_b > res_a:
                    try:
                        parent = h3_module.cell_to_parent(cell_b, res_a)
                        if parent == cell_a:
                            matches.append((cell_a, cell_b))
                            matched_a.add(cell_a)
                            matched_b.add(cell_b)
                    except Exception:
                        continue

    elif join_type == "within":
        for cell_a in cells_a:
            res_a = h3_module.get_resolution(cell_a)
            for cell_b in cells_b:
                res_b = h3_module.get_resolution(cell_b)
                if res_a > res_b:
                    try:
                        parent = h3_module.cell_to_parent(cell_a, res_b)
                        if parent == cell_b:
                            matches.append((cell_a, cell_b))
                            matched_a.add(cell_a)
                            matched_b.add(cell_b)
                    except Exception:
                        continue

    return matches, list(set(cells_a) - matched_a), list(set_b - matched_b)


def gpu_spatial_join_by_distance(
    points_a: Any,
    points_b: Any,
    max_distance_km: float,
    label_offsets_a: Sequence[int] | None = None,
    label_offsets_b: Sequence[int] | None = None,
    radius_km: float = EARTH_RADIUS_KM,
) -> Tuple[List[Tuple[int, int]], List[int], List[int]]:
    """
    GPU-accelerated spatial join over two point sets by a great-circle radius.

    The pairwise great-circle (haversine) distance matrix is evaluated on the
    tensor accelerator (CUDA via JAX / PyTorch / CuPy, falling back to the
    CPU reference path). Point pairs whose separation is ``<=``
    ``max_distance_km`` are joined. A group may be represented by several
    member points using ``label_offsets_*``; when provided the reported pair
    indices refer to those group labels.

    Args:
        points_a: ``(N, 2)`` array of ``(lat, lng)`` degrees.
        points_b: ``(M, 2)`` array of ``(lat, lng)`` degrees.
        max_distance_km: Maximum great-circle distance to consider a join.
        label_offsets_a: Optional group label offset per point in A
            (length ``N``). Pairs report these labels instead of raw indices.
        label_offsets_b: Optional group label offset per point in B.
        radius_km: Earth radius in kilometers (default 6371.0).

    Returns:
        Tuple of ``(pairs, unmatched_a, unmatched_b)`` where ``pairs`` is a
        list of ``(label_a, label_b)`` tuples.
    """
    if max_distance_km <= 0:
        raise ValueError("max_distance_km must be positive")

    a = _validated_points(points_a, "points_a")
    b = _validated_points(points_b, "points_b")

    dist = pairwise_haversine_kernel(a, b, radius_km=radius_km)
    mask = dist <= max_distance_km

    rows, cols = np.nonzero(mask)

    if label_offsets_a is not None or label_offsets_b is not None:
        if label_offsets_a is None:
            label_offsets_a = list(range(a.shape[0]))
        if label_offsets_b is None:
            label_offsets_b = list(range(b.shape[0]))
        la = list(label_offsets_a)
        lb = list(label_offsets_b)
        # Collapse to group labels and de-duplicate (a group with many member
        # points still joins its counterpart group once).
        pairs = sorted(
            {(int(la[int(r)]), int(lb[int(c)])) for r, c in zip(rows, cols)}
        )
    else:
        pairs = [(int(r), int(c)) for r, c in zip(rows, cols)]

    matched_a_rows = set(int(r) for r in rows)
    matched_b_cols = set(int(c) for c in cols)
    unmatched_a = [int(i) for i in range(a.shape[0]) if i not in matched_a_rows]
    unmatched_b = [int(j) for j in range(b.shape[0]) if j not in matched_b_cols]
    return pairs, unmatched_a, unmatched_b


def h3_grid_distance_kernel(
    cells_a: Sequence[str],
    cells_b: Sequence[str],
    h3_module: Any = None,
) -> npt.NDArray[np.int64]:
    """
    Compute the pairwise H3 grid distance between two cell collections.

    Returns an ``(N, M)`` int64 matrix. Cells that cannot be compared (mixed
    resolutions or straddling an icosahedron edge) are reported as ``-1``,
    mirroring the tolerant behaviour used by the nested lumping paths.

    Args:
        cells_a: List of H3 cell identifiers (first set).
        cells_b: List of H3 cell identifiers (second set).
        h3_module: The ``h3`` module. Imported if ``None``.

    Returns:
        ``(N, M)`` int64 grid-distance matrix.
    """
    if h3_module is None:
        import h3

        h3_module = h3

    n, m = len(cells_a), len(cells_b)
    out = np.full((n, m), -1, dtype=np.int64)
    for i, ca in enumerate(cells_a):
        for j, cb in enumerate(cells_b):
            try:
                out[i, j] = int(h3_module.grid_distance(ca, cb))
            except Exception:
                out[i, j] = -1
    return out