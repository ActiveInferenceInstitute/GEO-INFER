from __future__ import annotations

from pathlib import Path


def fix_double_h3_lib(path: str) -> bool:
    """
    Replace accidental `h3_lib.h3_lib.` occurrences with `h3_lib.`.

    Returns True if the file content changed.
    """
    p = Path(path)
    original = p.read_text(encoding="utf-8")
    updated = original.replace("h3_lib.h3_lib.", "h3_lib.")
    if updated == original:
        return False
    p.write_text(updated, encoding="utf-8")
    return True

