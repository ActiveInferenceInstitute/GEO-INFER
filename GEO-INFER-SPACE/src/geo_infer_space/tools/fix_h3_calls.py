from __future__ import annotations

import re
from pathlib import Path


_H3_CALLS = (
    "is_valid_cell",
    "cell_to_boundary",
    "get_resolution",
    "cell_area",
    "cell_to_latlng",
    "latlng_to_cell",
)


def fix_h3_calls_in_file(path: str) -> bool:
    """
    Prefix bare H3 function calls with `h3_lib.`.

    This is a simple text-level fixer intended for small repository migration tasks.
    Returns True if the file content changed.
    """
    p = Path(path)
    original = p.read_text(encoding="utf-8")

    pattern = re.compile(rf"(?<!\.)\b({'|'.join(_H3_CALLS)})\s*\(")
    updated = pattern.sub(lambda m: f"h3_lib.{m.group(1)}(", original)

    if updated == original:
        return False

    p.write_text(updated, encoding="utf-8")
    return True

