#!/usr/bin/env python3
"""
Fix double h3_lib references in target files.

This tool scans specific files and replaces occurrences of
"h3_lib.h3_lib." with "h3_lib.". Paths are resolved relative to the
GEO-INFER-SPACE module root so the script can be run from anywhere.
"""

import re
from pathlib import Path


def resolve_module_root() -> Path:
    """Return the GEO-INFER-SPACE module root directory.

    The file layout is .../GEO-INFER-SPACE/src/geo_infer_space/tools/this_file.py
    so parents[3] should be GEO-INFER-SPACE.
    """
    return Path(__file__).resolve().parents[3]


def fix_double_h3_lib(filepath: Path) -> bool:
    """Fix double h3_lib references in a file.

    Args:
        filepath: Absolute path to the file to mutate.

    Returns:
        True if the file was modified, False otherwise.
    """
    if not filepath.exists() or not filepath.is_file():
        return False

    content = filepath.read_text(encoding="utf-8")
    new_content = re.sub(r"h3_lib\.h3_lib\.", "h3_lib.", content)
    if new_content != content:
        filepath.write_text(new_content, encoding="utf-8")
        return True
    return False


def main() -> None:
    """Fix double h3_lib references in known modules."""
    module_root = resolve_module_root()
    targets = [
        module_root / "src" / "h3" / "visualization.py",
        module_root / "src" / "h3" / "animation.py",
        module_root / "src" / "h3" / "interactive.py",
    ]

    for path in targets:
        print(f"Fixing double h3_lib references in {path}")
        try:
            modified = fix_double_h3_lib(path)
            if modified:
                print("  ✅ Modified")
            else:
                print("  ✅ No changes (or file not found)")
        except Exception as exc:
            print(f"  ❌ Error: {exc}")


if __name__ == "__main__":
    main()


