from __future__ import annotations

import re
from pathlib import Path


_RELATIVE_FROM = re.compile(r"^(\s*from\s+)\.(\S+)(\s+import\s+)", re.MULTILINE)


def fix_relative_imports_in_file(path: str) -> bool:
    """
    Convert `from .x import y` to `from x import y` (single-dot only).

    Returns True if the file content changed.
    """
    p = Path(path)
    original = p.read_text(encoding="utf-8")
    updated = _RELATIVE_FROM.sub(r"\1\2\3", original)
    if updated == original:
        return False
    p.write_text(updated, encoding="utf-8")
    return True

