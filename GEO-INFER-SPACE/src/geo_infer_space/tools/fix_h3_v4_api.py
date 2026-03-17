from __future__ import annotations

from pathlib import Path
from typing import List, Tuple


Change = Tuple[str, str]

_V3_TO_V4: Tuple[Change, ...] = (
    ("h3.geo_to_h3", "h3.latlng_to_cell"),
    ("h3.h3_to_geo", "h3.cell_to_latlng"),
    ("h3.k_ring", "h3.grid_disk"),
)


def fix_h3_v3_api_calls(path: str) -> Tuple[bool, List[Change]]:
    """
    Apply a small set of H3 v3->v4 call rewrites.

    Returns:
      - modified: True if file changed
      - changes: list of changes that were applied
    """
    p = Path(path)
    original = p.read_text(encoding="utf-8")
    updated = original
    applied: List[Change] = []

    for old, new in _V3_TO_V4:
        if old in updated:
            updated = updated.replace(old, new)
            applied.append((old, new))

    if updated == original:
        return False, []

    p.write_text(updated, encoding="utf-8")
    return True, applied

