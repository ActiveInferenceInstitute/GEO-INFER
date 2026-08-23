#!/usr/bin/env python3
"""
Packaging-configuration validation for the GEO-INFER monorepo platform.

ARCH-01: This validator enforces the unified multi-package wheel-release
contract across all ``GEO-INFER-*`` modules:

- PyPI distribution namespace: every ``[project].name`` must use the
  ``geo-infer-*`` distribution prefix and normalize to a lowercase package
  directory under ``src/``.
- Package-data inclusion: every wheel must ship its YAML/JSON/MD/TXT
  configuration resources so runtime config discovery works from an
  installed wheel without relying on repository-local ``config/`` roots.
- Out-of-package source traversal is reported as a diagnostic so authors can
  migrate ``Path(__file__).parent...`` config lookups to an installed-wheel
  safe discovery mechanism when publishing wheels.
"""

from __future__ import annotations

import argparse
import re
import sys
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
MODULE_PREFIX = "GEO-INFER-"

# Distribution namespace used for every published PyPI package.
DISTRIBUTION_PREFIX = "geo-infer-"

# Package-data resource globs expected in [tool.setuptools.package-data].
PACKAGE_DATA_RESOURCES = ("*.yaml", "*.yml", "*.json", "*.md", "*.txt")

PROJECT_NAME_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")


def module_dirs() -> List[Path]:
    """Return ``GEO-INFER-*`` module directories in stable order."""
    return sorted(p for p in REPO_ROOT.glob(f"{MODULE_PREFIX}*") if p.is_dir())


def parse_pyproject(module_dir: Path) -> dict:
    """Parse a module's pyproject.toml into a dict ({} when absent/invalid)."""
    pyproject = module_dir / "pyproject.toml"
    if not pyproject.is_file():
        return {}
    try:
        return tomllib.loads(pyproject.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError:
        return {}


def distribution_name(pyproject: dict) -> Optional[str]:
    """Return the declared PyPI distribution name (``geo-infer-*``) or None."""
    name = pyproject.get("project", {}).get("name")
    return name if isinstance(name, str) and name else None


def expected_package_name(distribution: str) -> str:
    """Map a distribution name to its importable package name (``-`` -> ``_``)."""
    return distribution.replace("-", "_")


def wheel_metadata_name(distribution: str) -> str:
    """The normalized package-name prefix used in built wheel filenames."""
    return distribution.replace("-", "_")


def valid_distribution_namespace(name: str) -> bool:
    """True when a distribution name conforms to the shared PyPI namespace."""
    if not name.startswith(DISTRIBUTION_PREFIX):
        return False
    suffix = name[len(DISTRIBUTION_PREFIX):]
    return bool(PROJECT_NAME_PATTERN.fullmatch(suffix))


def wheel_filename_is_valid(built_name: str, expected_distribution: str) -> bool:
    """True when a built wheel filename belongs to the expected distribution."""
    normalized = wheel_metadata_name(expected_distribution)
    return built_name.startswith(f"{normalized}-")


@dataclass
class ContractReport:
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    diagnostics: List[str] = field(default_factory=list)


def validate_module(
    module_dir: Path, pyproject: dict, report: ContractReport
) -> None:
    """Validate namespace and package-data metadata for one module."""
    label = module_dir.name
    distribution = distribution_name(pyproject)
    if not distribution:
        report.errors.append(f"{label}: missing [project].name")
        return

    if not valid_distribution_namespace(distribution):
        report.errors.append(
            f"{label}: distribution name {distribution!r} must use the "
            f"{DISTRIBUTION_PREFIX}* namespace"
        )

    package = expected_package_name(distribution)
    if package != distribution.lower().replace("-", "_"):
        report.errors.append(
            f"{label}: project name must normalize to lowercase Python package"
        )

    src_dir = module_dir / "src"
    package_dir = src_dir / package
    if src_dir.is_dir() and not package_dir.is_dir():
        report.errors.append(f"{label}: expected package directory src/{package}")

    text = (module_dir / "pyproject.toml").read_text(encoding="utf-8", errors="ignore")
    if "[tool.setuptools.package-data]" not in text:
        report.warnings.append(
            f"{label}: missing [tool.setuptools.package-data]; wheel will not "
            "ship YAML/JSON configuration resources"
        )
    else:
        for resource in PACKAGE_DATA_RESOURCES:
            if resource not in text:
                report.warnings.append(
                    f"{label}: package-data does not include {resource}"
                )


def validate_source_traversal(module_dir: Path, report: ContractReport) -> None:
    """Flag source files that reach outside the module package for resources."""
    src_dir = module_dir / "src"
    if not src_dir.is_dir():
        return
    for path in src_dir.rglob("*.py"):
        if path.name.startswith("test_") or path.name.endswith("_test.py"):
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if "__file__" not in text:
            continue
        matches = re.findall(r"\.parent(?:\.parent)*", text)
        climbs = max((len(m.split(".")) for m in matches), default=0)
        if climbs >= 1:
            rel = path.relative_to(src_dir)
            report.diagnostics.append(
                f"{module_dir.name}/{rel}: climbs parent dirs from __file__"
            )


def validate_all(target_dirs: Optional[List[Path]] = None) -> ContractReport:
    report = ContractReport()
    if target_dirs is None:
        target_dirs = module_dirs()
    for module_dir in target_dirs:
        pyproject = parse_pyproject(module_dir)
        if not pyproject:
            report.errors.append(f"{module_dir.name}: invalid/missing pyproject")
            continue
        validate_module(module_dir, pyproject, report)
        validate_source_traversal(module_dir, report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate GEO-INFER packaging configuration"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Promote packaging warnings to errors.",
    )
    parser.add_argument(
        "--diagnostics",
        action="store_true",
        help="Show out-of-package __file__ traversal diagnostics.",
    )
    args = parser.parse_args()

    report = validate_all()
    if args.strict:
        report.errors.extend(report.warnings)
        report.warnings = []
    print(f"Modules checked: {len(module_dirs())}")
    print(f"Errors: {len(report.errors)}")
    for error in report.errors:
        print(f"ERROR: {error}")
    print(f"Warnings: {len(report.warnings)}")
    for warning in report.warnings:
        print(f"WARNING: {warning}")
    if args.diagnostics:
        for diag in report.diagnostics:
            print(f"DIAG: {diag}")

    return 1 if report.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())