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
- Requirements parity: every runtime dependency declared in a module's
  ``[project.dependencies]`` must appear in the module's ``requirements.txt``
  (the module's own distribution name is exempt), and every
  ``requirements.txt`` entry must be declared by the module in
  ``[project.dependencies]``, any ``[project.optional-dependencies]`` group,
  or a legacy ``setup.py`` ``install_requires``. Names compare normalized
  (lowercase, ``_`` == ``-``) with version specifiers and extras stripped.
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

# Requirements-line name extraction: strips environment markers, extras
# brackets and version specifiers so requirements.txt lines and pyproject
# dependency strings compare by normalized distribution name only.
_REQUIREMENT_NAME_RE = re.compile(r"^\s*([A-Za-z0-9][A-Za-z0-9._-]*)")


def normalize_dependency_name(raw: str) -> str:
    """Normalize a distribution name (lowercase, underscores -> dashes)."""
    match = _REQUIREMENT_NAME_RE.match(raw.strip())
    if not match:
        return ""
    return match.group(1).lower().replace("_", "-")


def parse_requirements_names(path: Path) -> List[str]:
    """Return normalized dependency names from a ``requirements.txt`` file.

    Blank lines, comments and pip options (``-r``/``-e``/``--index-url``...)
    are ignored; extras and version specifiers are stripped so lines compare
    by name only.
    """
    if not path.is_file():
        return []
    names: List[str] = []
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("-"):
            continue
        name = normalize_dependency_name(stripped.split(";", 1)[0])
        if name:
            names.append(name)
    return names


def parse_setup_py_requires(module_dir: Path) -> tuple[Optional[set], bool]:
    """Return ``(setup.py install_requires names, setup.py reads requirements.txt)``.

    ``(None, False)`` when setup.py is absent. Some modules build through a
    legacy setup.py that reads ``requirements.txt`` directly; for those the
    requirements file is the authoritative install source.
    """
    setup = module_dir / "setup.py"
    if not setup.is_file():
        return None, False
    text = setup.read_text(encoding="utf-8", errors="ignore")
    reads_requirements = bool(re.search(r"requirements\.txt", text))
    names: set = set()
    match = re.search(r"install_requires\s*=\s*[\[\(](.*?)[\]\)]", text, re.S)
    if match:
        for literal in re.findall(r"['\"]([^'\"]+)['\"]", match.group(1)):
            name = normalize_dependency_name(literal.split(";", 1)[0])
            if name:
                names.add(name)
    return names, reads_requirements


def pyproject_dependency_names(pyproject: dict) -> set:
    """Return normalized runtime dependency names from [project.dependencies]."""
    deps = pyproject.get("project", {}).get("dependencies") or []
    return {
        name
        for name in (normalize_dependency_name(str(d)) for d in deps)
        if name
    }


def pyproject_optional_names(pyproject: dict) -> set:
    """Return normalized names across all [project.optional-dependencies] groups."""
    groups = pyproject.get("project", {}).get("optional-dependencies") or {}
    names: set = set()
    for group in groups.values():
        for dep in group:
            name = normalize_dependency_name(str(dep))
            if name:
                names.add(name)
    return names


def validate_requirements_parity(
    module_dir: Path, pyproject: dict, report: ContractReport
) -> None:
    """Enforce two-way parity between [project.dependencies] and requirements.txt.

    Forward direction: every runtime dependency declared in
    ``[project.dependencies]`` must appear in the module's
    ``requirements.txt``. The module's own distribution name (a
    self-dependency such as ``geo-infer-x`` inside GEO-INFER-X) is exempt.

    Reverse direction: every ``requirements.txt`` entry must be declared by
    the module — in ``[project.dependencies]``, any
    ``[project.optional-dependencies]`` group, or a legacy ``setup.py``
    ``install_requires``. Modules whose ``setup.py`` feeds
    ``install_requires`` from ``requirements.txt`` are treated as
    requirements-authoritative and are exempt from the reverse direction.
    """
    label = module_dir.name
    distribution = distribution_name(pyproject)
    required = pyproject_dependency_names(pyproject)
    optional = pyproject_optional_names(pyproject)
    declared = required | optional
    listed = parse_requirements_names(module_dir / "requirements.txt")
    setup_names, setup_reads_requirements = parse_setup_py_requires(module_dir)

    for dep in sorted(required):
        if dep == distribution:
            continue
        if dep not in listed:
            report.errors.append(
                f"{label}: requirements.txt missing runtime dependency "
                f"{dep!r} declared in [project.dependencies]"
            )

    if setup_reads_requirements:
        return
    accepted = declared | (setup_names or set())
    for name in sorted(set(listed)):
        if name not in accepted:
            report.errors.append(
                f"{label}: requirements.txt lists {name!r} which is not "
                "declared in [project.dependencies], "
                "[project.optional-dependencies] or setup.py install_requires"
            )




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
        validate_requirements_parity(module_dir, pyproject, report)
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