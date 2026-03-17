from __future__ import annotations

import re
from pathlib import Path


_FROM_H3_DOTTED = re.compile(r"^(\s*from\s+)h3\.(.+\s+import\s+.+)$", re.MULTILINE)


def fix_imports_in_file(path: str) -> bool:
    """
    Rewrite `from h3.<module> import ...` to `from <module> import ...`.

    Returns True if the file content changed.
    """
    p = Path(path)
    original = p.read_text(encoding="utf-8")
    updated = _FROM_H3_DOTTED.sub(r"\1\2", original)
    if updated == original:
        return False
    p.write_text(updated, encoding="utf-8")
    return True

