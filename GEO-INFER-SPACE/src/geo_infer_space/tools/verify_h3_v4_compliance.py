from __future__ import annotations

from pathlib import Path
from typing import List, Tuple


_V3_PATTERNS = (
    "h3.geo_to_h3",
    "h3.h3_to_geo",
    "h3.k_ring",
)

_V4_PATTERNS = (
    "h3.latlng_to_cell",
    "h3.cell_to_latlng",
    "h3.grid_disk",
)


def check_file_for_v3_api(path: str) -> Tuple[bool, List[str]]:
    """
    Return whether H3 v3 API usage is present and a list of matched patterns.
    """
    content = Path(path).read_text(encoding="utf-8")
    issues = [p for p in _V3_PATTERNS if p in content]
    return (len(issues) > 0), issues


def check_file_for_v4_api(path: str) -> Tuple[bool, List[str]]:
    """
    Return whether H3 v4 API usage is present and a list of matched patterns.
    """
    content = Path(path).read_text(encoding="utf-8")
    usage = [p for p in _V4_PATTERNS if p in content]
    return (len(usage) > 0), usage

