"""Packaging-safety tests: every Python package directory ships in wheels.

setuptools' ``find_packages`` only includes directories containing an
``__init__.py``. A package directory missing that file is silently dropped
from built wheels (it still imports in the dev tree as an implicit namespace
package), which broke ``geo_infer_risk.utils`` once. These tests pin the invariant.
"""

from pathlib import Path

PKG_ROOT = Path(__file__).resolve().parents[2] / "src" / "geo_infer_risk"


def _python_dirs(root: Path) -> list[str]:
    return sorted(
        str(p.relative_to(root)) for p in root.rglob("*") if p.is_dir()
    )


def test_every_directory_with_modules_is_a_package() -> None:
    for rel in _python_dirs(PKG_ROOT):
        directory = PKG_ROOT / rel
        has_modules = any(directory.glob("*.py"))
        if has_modules:
            assert (directory / "__init__.py").is_file(), (
                f"{rel} contains Python modules but has no __init__.py; "
                "find_packages would exclude it from built wheels"
            )


def test_utils_package_imports() -> None:
    import geo_infer_risk.utils as utils_pkg

    for name in ("resolve_rng", "spawn_rng", "derive_int_seed", "SeedLike"):
        assert hasattr(utils_pkg, name), f"geo_infer_risk.utils missing {name}"

