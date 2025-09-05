#!/usr/bin/env python3
"""
Fix relative imports in H3 modules by converting to absolute imports.
"""

import re
from pathlib import Path


def resolve_module_root() -> Path:
    return Path(__file__).resolve().parents[3]


def fix_relative_imports_in_file(filepath: Path) -> bool:
    if not filepath.exists() or not filepath.is_file():
        return False
    content = filepath.read_text(encoding="utf-8")
    new_content = re.sub(r"from \.([\w_]+) import", r"from \1 import", content)
    if new_content != content:
        filepath.write_text(new_content, encoding="utf-8")
        return True
    return False


def main() -> None:
    module_root = resolve_module_root()
    h3_dir = module_root / "src" / "h3"
    if not h3_dir.exists():
        print(f"H3 directory not found: {h3_dir}")
        return

    for path in h3_dir.glob("*.py"):
        if path.name == "__init__.py":
            continue
        print(f"Fixing relative imports in {path.name}")
        try:
            modified = fix_relative_imports_in_file(path)
            print("  ✅ Modified" if modified else "  ✅ No changes")
        except Exception as exc:
            print(f"  ❌ Error: {exc}")


if __name__ == "__main__":
    main()


