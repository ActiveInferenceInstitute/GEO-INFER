"""Explicit random-number-generator plumbing for GEO-INFER-RISK.

Catastrophe simulation, exposure sampling and Monte Carlo loss aggregation are
all stochastic, and a risk number is only defensible if the run behind it can
be replayed. This module holds the single conversion from a user-supplied seed
to a :class:`numpy.random.Generator`, so no module in the package has to touch
the process-wide ``numpy.random`` singleton.
"""

from __future__ import annotations

import warnings
from typing import Union

import numpy as np

__all__ = ["SeedLike", "derive_int_seed", "resolve_rng", "spawn_rng"]

#: Anything accepted by :func:`resolve_rng`.
SeedLike = Union[
    None,
    int,
    np.random.SeedSequence,
    np.random.BitGenerator,
    np.random.Generator,
    np.random.RandomState,
]

# Upper bound for seeds derived from a legacy ``RandomState`` bridge.
_DERIVED_SEED_BOUND = 2**63 - 1


def resolve_rng(seed: SeedLike = None) -> np.random.Generator:
    """Return a :class:`numpy.random.Generator` for ``seed``.

    Every stochastic entry point in this package funnels its ``random_seed`` /
    ``random_state`` argument through this function so that randomness is
    always drawn from an explicit generator instance rather than the
    process-wide ``numpy.random`` singleton. Threading a generator through a
    call graph keeps parallel and nested simulations statistically independent
    and makes a run replayable from its seed alone.

    Parameters
    ----------
    seed:
        Accepted forms:

        * ``None`` -- a fresh generator seeded from OS entropy. Results are
          not reproducible; pass an ``int`` when replay matters.
        * ``int`` -- a deterministic generator. Equal ints give equal streams.
        * :class:`numpy.random.SeedSequence` or
          :class:`numpy.random.BitGenerator` -- used directly, which is the
          supported way to hand out independent child streams.
        * :class:`numpy.random.Generator` -- returned unchanged, so callers can
          thread one generator through a whole pipeline.
        * :class:`numpy.random.RandomState` -- supported for backward
          compatibility with callers still holding a legacy object. A seed is
          drawn *from* that state, so the result stays deterministic with
          respect to it, but the two objects do not share a stream afterwards.

    Returns
    -------
    numpy.random.Generator
        A generator instance. Never the ``numpy.random`` module.

    Raises
    ------
    TypeError
        If ``seed`` is of a type that cannot produce a generator.

    Examples
    --------
    >>> import numpy as np
    >>> resolve_rng(11).integers(0, 10) == resolve_rng(11).integers(0, 10)
    True
    >>> shared = np.random.default_rng(0)
    >>> resolve_rng(shared) is shared
    True
    """
    if isinstance(seed, np.random.Generator):
        return seed
    if isinstance(seed, np.random.RandomState):
        # Legacy bridge: derive a deterministic seed from the caller's state.
        return np.random.default_rng(int(seed.randint(0, _DERIVED_SEED_BOUND)))
    # Checked before the accepted forms because the old code in this package
    # used `rng = np.random`, so a caller migrating from it may still pass the
    # module. Compared by type name rather than isinstance so that the branch
    # stays reachable under a type checker: SeedLike excludes ModuleType, but
    # untyped callers reach here anyway.
    if type(seed).__name__ == "module":
        warnings.warn(
            "Passing the numpy.random module as a seed is not supported; "
            "returning an independent generator seeded from OS entropy. "
            "Pass an int or a numpy.random.Generator instead.",
            RuntimeWarning,
            stacklevel=2,
        )
        return np.random.default_rng()
    if seed is None or isinstance(
        seed, (int, np.integer, np.random.SeedSequence, np.random.BitGenerator)
    ):
        return np.random.default_rng(seed)
    raise TypeError(
        "seed must be None, an int, a SeedSequence, a BitGenerator, a "
        f"Generator, or a RandomState; got {type(seed).__name__}"
    )


def spawn_rng(seed: SeedLike, n: int) -> list[np.random.Generator]:
    """Return ``n`` statistically independent generators derived from ``seed``.

    Uses :meth:`numpy.random.SeedSequence.spawn`, the supported mechanism for
    splitting one seed into non-overlapping streams. Use this instead of
    seeding several generators with ``seed``, ``seed + 1``, ... which gives no
    independence guarantee.

    Parameters
    ----------
    seed:
        Any value accepted by :func:`resolve_rng`.
    n:
        Number of child generators to produce. Must be non-negative.

    Returns
    -------
    list of numpy.random.Generator
        ``n`` independent generators.

    Raises
    ------
    ValueError
        If ``n`` is negative.
    """
    if n < 0:
        raise ValueError("n must be non-negative")
    parent = resolve_rng(seed)
    # Draw a 128-bit entropy value from the parent so the children are
    # reproducible whenever the parent is, without assuming a bit generator
    # type or mutating a caller-supplied SeedSequence.
    entropy = int(parent.integers(0, 2**63 - 1, dtype=np.int64))
    return [
        np.random.default_rng(child)
        for child in np.random.SeedSequence(entropy).spawn(n)
    ]

def derive_int_seed(seed: SeedLike = None) -> int:
    """Derive a plain ``int`` seed from any seed-like value.

    Some libraries -- scikit-learn's ``random_state``, several SciPy routines --
    accept only an int or a legacy ``RandomState``, not a
    :class:`numpy.random.Generator`. Use this at those boundaries so that a
    caller who passed a generator still gets a deterministic, reproducible
    downstream split or draw.

    Parameters
    ----------
    seed:
        Any value accepted by :func:`resolve_rng`. Note that passing a
        ``Generator`` advances it, which is what makes repeated calls on one
        generator produce distinct downstream seeds.

    Returns
    -------
    int
        A seed in ``[0, 2**32)``, the range accepted by scikit-learn.
    """
    return int(resolve_rng(seed).integers(0, 2**32, dtype=np.int64))
