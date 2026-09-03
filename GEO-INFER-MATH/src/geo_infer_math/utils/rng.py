"""
Deterministic random-number-generator resolution helpers for GEO-INFER-MATH.

All seeded workflows in GEO-INFER-MATH should obtain their RNG via
`resolve_rng(seed)`.
"""

from __future__ import annotations

from typing import Any, Optional, Union
import numpy as np

SeedLike = Union[
    int,
    np.integer,
    np.random.SeedSequence,
    np.random.BitGenerator,
    np.random.Generator,
    np.random.RandomState,
    None,
]


def resolve_rng(seed: SeedLike = None) -> np.random.Generator:
    """Resolve an arbitrary seed or generator specification into a NumPy Generator.

    Parameters
    ----------
    seed : int, SeedSequence, BitGenerator, Generator, RandomState, or None
        Seed or generator specification.
        - If already a `np.random.Generator`, returned directly.
        - If an int or SeedSequence, passed to `np.random.default_rng`.
        - If a legacy `np.random.RandomState`, a fresh `default_rng` seeded with
          an integer drawn from that RandomState is returned.
        - If None, `np.random.default_rng(None)` is returned (fresh entropy).

    Returns
    -------
    np.random.Generator
        Deterministic, isolated NumPy Generator.

    Examples
    --------
    Library modules accept a ``SeedLike`` and resolve it through this
    helper instead of touching the global ``np.random`` state:

    >>> from geo_infer_math.utils.rng import resolve_rng
    >>> def sample_noise(seed: SeedLike = None) -> float:
    ...     rng = resolve_rng(seed)
    ...     return float(rng.normal(0.0, 1.0))
    >>> sample_noise(0) == sample_noise(0)
    True
    """
    if isinstance(seed, np.random.Generator):
        return seed
    if isinstance(seed, np.random.RandomState):
        derived = int(seed.randint(0, 2**31 - 1))
        return np.random.default_rng(derived)
    return np.random.default_rng(seed)
