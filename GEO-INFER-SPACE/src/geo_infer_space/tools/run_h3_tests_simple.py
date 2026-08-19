"""Run a small set of H3 v4 round-trip checks and report the outcome.

The checks exercise the H3 v4 API surface this package depends on --
``latlng_to_cell``, ``cell_to_latlng``, ``cell_to_boundary``, and
``grid_disk`` -- so that an environment problem (missing or wrong-major
``h3``) is reported as a non-zero exit code rather than surfacing later
as an opaque failure inside an analysis run.
"""

from __future__ import annotations

import logging
from typing import Callable

logger = logging.getLogger(__name__)

# (latitude, longitude) probes spanning both hemispheres and the prime meridian.
_PROBES = (
    (37.7749, -122.4194),
    (-33.8688, 151.2093),
    (0.0, 0.0),
    (51.5074, -0.1278),
)
_RESOLUTIONS = (0, 5, 9, 12)
# H3 resolution 9 cells are ~174 m across, so a round trip must land well
# inside a kilometre of the input point at that resolution or finer.
_MAX_ROUND_TRIP_DEGREES = 0.05


def _check_round_trip(h3) -> None:
    """Assert lat/lng -> cell -> lat/lng returns to the neighbourhood of the input."""
    for lat, lng in _PROBES:
        for resolution in _RESOLUTIONS:
            cell = h3.latlng_to_cell(lat, lng, resolution)
            if not h3.is_valid_cell(cell):
                raise ValueError(f"invalid cell {cell!r} for ({lat}, {lng}) at r{resolution}")
            if h3.get_resolution(cell) != resolution:
                raise ValueError(f"cell {cell!r} reports resolution {h3.get_resolution(cell)}")
            back_lat, back_lng = h3.cell_to_latlng(cell)
            if resolution >= 9 and (
                abs(back_lat - lat) > _MAX_ROUND_TRIP_DEGREES
                or abs(back_lng - lng) > _MAX_ROUND_TRIP_DEGREES
            ):
                raise ValueError(
                    f"round trip for ({lat}, {lng}) at r{resolution} returned "
                    f"({back_lat}, {back_lng})"
                )


def _check_boundary(h3) -> None:
    """Assert cell boundaries are closed rings of plausible coordinates."""
    for lat, lng in _PROBES:
        cell = h3.latlng_to_cell(lat, lng, 9)
        boundary = h3.cell_to_boundary(cell)
        # Hexagons have 6 vertices; the 12 pentagons per resolution have 5.
        if len(boundary) not in (5, 6):
            raise ValueError(f"cell {cell!r} boundary has {len(boundary)} vertices")
        for vertex_lat, vertex_lng in boundary:
            if not (-90.0 <= vertex_lat <= 90.0 and -180.0 <= vertex_lng <= 180.0):
                raise ValueError(f"cell {cell!r} boundary vertex out of range")


def _check_grid_disk(h3) -> None:
    """Assert a k-ring contains its origin and the expected hexagon count."""
    for lat, lng in _PROBES:
        cell = h3.latlng_to_cell(lat, lng, 9)
        disk = h3.grid_disk(cell, 1)
        if cell not in disk:
            raise ValueError(f"grid_disk({cell!r}, 1) does not contain its origin")
        # 1 + 6 for a hexagon; one fewer when the origin is a pentagon.
        if len(disk) not in (6, 7):
            raise ValueError(f"grid_disk({cell!r}, 1) returned {len(disk)} cells")


CHECKS: tuple[tuple[str, Callable[[object], None]], ...] = (
    ("round_trip", _check_round_trip),
    ("boundary", _check_boundary),
    ("grid_disk", _check_grid_disk),
)


def main() -> int:
    """Run every H3 check and return 0 when all of them pass, 1 otherwise.

    Returns an integer exit code so the module doubles as a console
    entrypoint and an importable smoke check.
    """
    try:
        import h3
    except ImportError:
        logger.error("h3 is not installed; install the h3 extra to run these checks")
        return 1

    failures = 0
    for name, check in CHECKS:
        try:
            check(h3)
        except Exception as exc:
            failures += 1
            logger.error("H3 check %s failed: %s", name, exc)
        else:
            logger.info("H3 check %s passed", name)

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
