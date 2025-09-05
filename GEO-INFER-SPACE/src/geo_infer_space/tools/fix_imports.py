#!/usr/bin/env python3
"""
Fix import statements in H3 examples by removing the "h3." package prefix.
"""

import re
from pathlib import Path


def resolve_module_root() -> Path:
    return Path(__file__).resolve().parents[3]


def fix_imports_in_file(filepath: Path) -> bool:
    if not filepath.exists() or not filepath.is_file():
        return False
    content = filepath.read_text(encoding="utf-8")
    new_content = re.sub(r"from h3\.(\w+) import", r"from \1 import", content)
    if new_content != content:
        filepath.write_text(new_content, encoding="utf-8")
        return True
    return False


def main() -> None:
    module_root = resolve_module_root()
    examples_dir = module_root / "src" / "h3" / "examples"
    if not examples_dir.exists():
        print(f"Examples directory not found: {examples_dir}")
        return

    for path in examples_dir.glob("*.py"):
        print(f"Fixing imports in {path.name}")
        try:
            modified = fix_imports_in_file(path)
            print("  ✅ Modified" if modified else "  ✅ No changes")
        except Exception as exc:
            print(f"  ❌ Error: {exc}")


if __name__ == "__main__":
    main()


