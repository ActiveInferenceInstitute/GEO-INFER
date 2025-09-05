#!/usr/bin/env python3
"""
Fix h3 function calls by prefixing with h3_lib in target files.
"""

import re
from pathlib import Path


def resolve_module_root() -> Path:
    return Path(__file__).resolve().parents[3]


def fix_h3_calls_in_file(filepath: Path) -> bool:
    """Fix h3 function calls in a file.

    Returns True if modified, else False.
    """
    if not filepath.exists() or not filepath.is_file():
        return False

    content = filepath.read_text(encoding="utf-8")

    replacements = [
        (r"\bis_valid_cell\b", "h3_lib.is_valid_cell"),
        (r"\bcell_to_boundary\b", "h3_lib.cell_to_boundary"),
        (r"\bget_resolution\b", "h3_lib.get_resolution"),
        (r"\bcell_area\b", "h3_lib.cell_area"),
        (r"\bcell_to_latlng\b", "h3_lib.cell_to_latlng"),
        (r"\blatlng_to_cell\b", "h3_lib.latlng_to_cell"),
    ]

    new_content = content
    for pattern, replacement in replacements:
        new_content = re.sub(pattern, replacement, new_content)

    if new_content != content:
        filepath.write_text(new_content, encoding="utf-8")
        return True
    return False


def main() -> None:
    module_root = resolve_module_root()
    files = [
        module_root / "src" / "h3" / "visualization.py",
        module_root / "src" / "h3" / "animation.py",
        module_root / "src" / "h3" / "interactive.py",
    ]
    for filepath in files:
        print(f"Fixing h3 calls in {filepath}")
        try:
            modified = fix_h3_calls_in_file(filepath)
            print("  ✅ Modified" if modified else "  ✅ No changes (or file not found)")
        except Exception as exc:
            print(f"  ❌ Error: {exc}")


if __name__ == "__main__":
    main()


