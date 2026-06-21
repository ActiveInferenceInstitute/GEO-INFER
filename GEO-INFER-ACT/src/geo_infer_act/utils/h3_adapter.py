"""
H3 access helpers for GEO-INFER-ACT.

The adapter prefers the canonical GEO-INFER-SPACE indexing interface when it is
available and uses direct H3 v4 calls for operations SPACE does not expose.
"""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Any, Dict, Iterable, List, Optional


class H3Adapter:
    """Small compatibility layer over SPACE H3 indexing and direct H3 v4."""

    def __init__(self, prefer_space: bool = True):
        """Initialize SPACE-backed and direct H3 access."""
        self.space_indexer = None
        self.h3 = None
        self.source = "direct"

        if prefer_space:
            try:
                from geo_infer_space.core.spatial_indexing import (  # noqa: PLC0415
                    SpatialIndexingInterface,
                )

                self.space_indexer = SpatialIndexingInterface(backend="h3")
                self.source = "geo_infer_space"
            except Exception:
                self.space_indexer = None

        try:
            import h3  # noqa: PLC0415

            self.h3 = h3
        except ImportError:
            self.h3 = None

        if self.space_indexer is None and self.h3 is None:
            raise RuntimeError("H3 is not available through GEO-INFER-SPACE or h3-py")

    def latlng_to_cell(self, lat: float, lng: float, resolution: int) -> str:
        """Convert latitude/longitude to an H3 cell."""
        if self.space_indexer is not None:
            return self.space_indexer.latlng_to_cell(lat, lng, resolution)
        return self.h3.latlng_to_cell(lat, lng, resolution)

    def cell_to_latlng(self, cell: str) -> tuple[float, float]:
        """Convert an H3 cell to latitude/longitude."""
        if self.space_indexer is not None:
            return self.space_indexer.cell_to_latlng(cell)
        return self.h3.cell_to_latlng(cell)

    def cell_to_boundary(self, cell: str) -> List[tuple[float, float]]:
        """Return the H3 cell boundary as latitude/longitude pairs."""
        if self.h3 is not None:
            return [(lat, lng) for lat, lng in self.h3.cell_to_boundary(cell)]
        if self.space_indexer is not None:
            backend = getattr(self.space_indexer, "backend", None)
            if backend is not None and hasattr(backend, "get_cell_boundary"):
                return list(backend.get_cell_boundary(cell))
        lat, lng = self.cell_to_latlng(cell)
        return [(lat, lng)]

    def polygon_to_cells(self, polygon: Dict[str, Any], resolution: int) -> List[str]:
        """Convert a GeoJSON-like polygon to H3 cells."""
        if self.space_indexer is not None:
            try:
                cells = self.space_indexer.polygon_to_cells(polygon, resolution)
                if cells:
                    return list(cells)
            except Exception:
                if self.h3 is None:
                    raise

        if self.h3 is None:
            return []

        coordinates = polygon.get("coordinates", [])
        if not coordinates:
            return []

        def _is_pair(value: Any) -> bool:
            return (
                isinstance(value, (list, tuple))
                and len(value) >= 2
                and isinstance(value[0], (int, float))
                and isinstance(value[1], (int, float))
            )

        def _extract_first_ring(value: Any) -> List[Any]:
            if not isinstance(value, (list, tuple)) or not value:
                return []
            if _is_pair(value[0]):
                return list(value)
            for child in value:
                ring_values = _extract_first_ring(child)
                if ring_values:
                    return ring_values
            return []

        ring = _extract_first_ring(coordinates)
        if not ring:
            return []
        h3_polygon = self.h3.LatLngPoly([(lat, lng) for lng, lat in ring])
        return list(self.h3.h3shape_to_cells(h3_polygon, resolution))

    def grid_disk(self, cell: str, k: int = 1) -> List[str]:
        """Return H3 cells within k grid steps of a cell."""
        if self.h3 is not None:
            return list(self.h3.grid_disk(cell, k))
        if self.space_indexer is not None:
            cells = {cell}
            for radius in range(1, k + 1):
                cells.update(self.space_indexer.get_cell_neighbors(cell, radius))
            return list(cells)
        return []

    def grid_ring(self, cell: str, k: int = 1) -> List[str]:
        """Return H3 cells exactly k grid steps from a cell."""
        if self.h3 is not None:
            return list(self.h3.grid_ring(cell, k))
        if self.space_indexer is not None:
            return list(self.space_indexer.get_cell_neighbors(cell, k))
        return []

    def get_resolution(self, cell: str) -> int:
        """Return the H3 resolution of a cell."""
        if self.space_indexer is not None:
            return self.space_indexer.get_cell_resolution(cell)
        return self.h3.get_resolution(cell)

    def cell_to_parent(self, cell: str, resolution: int) -> str:
        """Return the parent cell at a coarser resolution."""
        if self.space_indexer is not None:
            return self.space_indexer.get_cell_parent(cell, resolution)
        return self.h3.cell_to_parent(cell, resolution)

    def cell_to_children(self, cell: str, resolution: int) -> List[str]:
        """Return child cells at a finer resolution."""
        if self.space_indexer is not None:
            return self.space_indexer.get_cell_children(cell, resolution)
        return list(self.h3.cell_to_children(cell, resolution))

    def is_valid_cell(self, cell: str) -> bool:
        """Return true when a value is a valid H3 cell identifier."""
        if self.h3 is not None:
            try:
                return bool(self.h3.is_valid_cell(cell))
            except Exception:
                return False
        try:
            self.cell_to_latlng(cell)
            return True
        except Exception:
            return False

    def validate_cells(
        self, cells: Iterable[str], allow_synthetic: bool = False
    ) -> List[str]:
        """Validate and normalize H3 cell identifiers."""
        normalized = [str(cell) for cell in cells]
        invalid = [
            cell
            for cell in normalized
            if not (allow_synthetic and cell.startswith("cell_"))
            and not self.is_valid_cell(cell)
        ]
        if invalid:
            raise ValueError(f"Invalid H3 cell identifiers: {invalid[:5]}")
        return normalized


def get_h3_adapter(prefer_space: bool = True) -> H3Adapter:
    """Create an H3 adapter for ACT spatial methods."""
    return H3Adapter(prefer_space=prefer_space)


def get_nested_h3_grid_class() -> Any:
    """Return SPACE's ``NestedH3Grid`` class in installed or repo-local runs."""
    try:
        from geo_infer_space.nested import NestedH3Grid  # noqa: PLC0415

        return NestedH3Grid
    except ImportError:
        repo_root = Path(__file__).resolve().parents[4]
        space_src = repo_root / "GEO-INFER-SPACE" / "src"
        if space_src.exists() and str(space_src) not in sys.path:
            sys.path.insert(0, str(space_src))
        from geo_infer_space.nested import NestedH3Grid  # noqa: PLC0415

        return NestedH3Grid


def normalize_belief_vector(values: Any) -> Any:
    """Normalize a belief vector with a finite, nonnegative distribution."""
    import numpy as np

    array = np.asarray(values, dtype=float).reshape(-1)
    if array.size == 0:
        raise ValueError("Belief vectors must not be empty")
    if not np.all(np.isfinite(array)):
        raise ValueError("Belief vectors must contain finite values")
    array = np.maximum(array, 0.0)
    total = float(np.sum(array))
    if total <= 1e-12:
        return np.ones_like(array) / array.size
    return array / total


def edge_count_from_graph(graph: Optional[Dict[str, Iterable[str]]]) -> int:
    """Count undirected edges in a cell-neighbor graph."""
    if not graph:
        return 0
    edges = {
        tuple(sorted((str(cell), str(neighbor))))
        for cell, neighbors in graph.items()
        for neighbor in neighbors
    }
    return len(edges)
