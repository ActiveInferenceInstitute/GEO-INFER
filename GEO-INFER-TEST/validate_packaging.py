#!/usr/bin/env python3
"""
Packaging-configuration validation for the GEO-INFER monorepo platform.

This validator enforces the unified multi-package wheel-release contract
across all ``GEO-INFER-*`` modules:

- PyPI distribution namespace: every ``[project].name`` must use the
  ``geo-infer-*`` distribution prefix and normalize to a lowercase package
  directory under ``src/``.
- Version uniformity: member pyprojects must agree on ``[project].version``
  (warn on outliers, error under ``--strict``). Known deviations are listed
  in ``KNOWN_VERSION_DEVIATIONS`` and surfaced as diagnostics only — the
  promotion decision belongs to the release process (TODO REL-01).
- Classifier consistency: modules declaring a ``Development Status``
  classifier must agree on the fleet mode; the root framework distribution's
  status is expected to differ and is surfaced as a diagnostic.
- Package-data inclusion: every wheel must ship its YAML/JSON/MD/TXT
  configuration resources so runtime config discovery works from an
  installed wheel without relying on repository-local ``config/`` roots.
  Declared globs are expanded against the package tree on disk, so a data
  file matching no glob (a resource that would silently miss the wheel) is
  an error, and per-module deviations from the canonical pattern set are
  surfaced.
- Requirements parity: every runtime dependency declared in a module's
  ``[project.dependencies]`` must appear in the module's
  ``requirements.txt`` (the module's own distribution name is exempt), and
  every ``requirements.txt`` entry must be declared by the module in
  ``[project.dependencies]``, any ``[project.optional-dependencies]`` group,
  or a legacy ``setup.py`` ``install_requires``. Names compare normalized
  (lowercase, ``_`` == ``-``) with version specifiers and extras stripped.
- Out-of-package source traversal is reported as a diagnostic so authors can
  migrate ``Path(__file__).parent...`` config lookups to an installed-wheel
  safe discovery mechanism when publishing wheels.
"""

from __future__ import annotations

import argparse
import fnmatch
import re
from collections import Counter
from pathlib import Path
from typing import List, Optional

from _validator_common import (
    ContractReport,
    discover_module_dirs,
    distribution_name,
    package_name_from_distribution,
    parse_requirements_names,
    parse_setup_py_requires,
    pyproject_dependency_names,
    pyproject_optional_names,
    read_pyproject as parse_pyproject,
    read_toml,
)

REPO_ROOT = Path(__file__).resolve().parent.parent

# Distribution namespace used for every published PyPI package.
DISTRIBUTION_PREFIX = "geo-infer-"

# Package-data resource globs expected in [tool.setuptools.package-data].
PACKAGE_DATA_RESOURCES = ("*.yaml", "*.yml", "*.json", "*.md", "*.txt")

PROJECT_NAME_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")

DEVELOPMENT_STATUS_PATTERN = re.compile(r"^Development Status :: (\d) - ")

# Member versions that intentionally deviate from the fleet majority. Keyed
# by module directory name. The release gate (REL-01) owns promoting these;
# the uniformity check reports them as diagnostics so --strict stays
# meaningful for NEW outliers.
KNOWN_VERSION_DEVIATIONS: dict[str, str] = {}

_PACKAGE_DATA_EXCLUDED_DIRS = ("__pycache__",)


def module_dirs() -> List[Path]:
    """Return ``GEO-INFER-*`` module directories in stable order."""
    return discover_module_dirs(REPO_ROOT)


def wheel_metadata_name(distribution: str) -> str:
    """The normalized package-name prefix used in built wheel filenames."""
    return package_name_from_distribution(distribution)


def valid_distribution_namespace(name: str) -> bool:
    """True when a distribution name conforms to the shared PyPI namespace."""
    if not name.startswith(DISTRIBUTION_PREFIX):
        return False
    suffix = name[len(DISTRIBUTION_PREFIX) :]
    return bool(PROJECT_NAME_PATTERN.fullmatch(suffix))


def wheel_filename_is_valid(built_name: str, expected_distribution: str) -> bool:
    """True when a built wheel filename belongs to the expected distribution."""
    normalized = wheel_metadata_name(expected_distribution)
    return built_name.startswith(f"{normalized}-")


def _package_data_patterns(pyproject: dict) -> List[str] | None:
    """Return the union of [tool.setuptools.package-data] globs, or None."""
    table = pyproject.get("tool", {}).get("setuptools", {}).get("package-data")
    if not isinstance(table, dict) or not table:
        return None
    patterns: List[str] = []
    for patterns_by_key in table.values():
        if not isinstance(patterns_by_key, list):
            continue
        for pattern in patterns_by_key:
            if isinstance(pattern, str) and pattern not in patterns:
                patterns.append(pattern)
    return patterns


def _package_data_files(package_dir: Path):
    """Yield non-Python data files under a package directory."""
    for path in sorted(package_dir.rglob("*")):
        if path.is_dir():
            continue
        parts = path.relative_to(package_dir).parts
        if any(
            part.startswith(".")
            or part in _PACKAGE_DATA_EXCLUDED_DIRS
            or part.endswith(".egg-info")
            for part in parts[:-1]
        ):
            continue
        name = path.name
        if name.endswith((".py", ".pyc")) or name.startswith("."):
            continue
        yield path.relative_to(package_dir).as_posix()


def validate_package_data(
    module_dir: Path, pyproject: dict, report: ContractReport
) -> None:
    """Validate [tool.setuptools.package-data] against the package tree.

    Missing canonical patterns are warnings (the wheel will not ship those
    resource classes); extra patterns beyond the canonical set are
    diagnostics (intentional additions, e.g. PLACE's ``*.geojson``); a data
    file on disk matching no declared glob is an error, because it would
    silently miss the built wheel.
    """
    label = module_dir.name
    patterns = _package_data_patterns(pyproject)
    if patterns is None:
        report.warning(
            f"{label}: missing [tool.setuptools.package-data]; wheel will not "
            "ship YAML/JSON configuration resources"
        )
        return

    declared = set(patterns)
    for resource in PACKAGE_DATA_RESOURCES:
        if resource not in declared:
            report.warning(f"{label}: package-data does not include {resource}")
    for pattern in sorted(declared - set(PACKAGE_DATA_RESOURCES)):
        report.diagnostic(
            f"{label}: package-data includes {pattern} beyond the canonical "
            f"resource set {list(PACKAGE_DATA_RESOURCES)}"
        )

    distribution = distribution_name(pyproject) or ""
    package_dir = module_dir / "src" / package_name_from_distribution(distribution)
    if not package_dir.is_dir():
        return
    for relative in _package_data_files(package_dir):
        if not any(fnmatch.fnmatch(relative, pattern) for pattern in declared):
            report.error(
                f"{label}: package data file {relative} matches no "
                "[tool.setuptools.package-data] glob; it would be omitted "
                "from the built wheel"
            )


def _development_status(pyproject: dict) -> str | None:
    """Return the ``Development Status :: X - Y`` classifier, or None."""
    classifiers = pyproject.get("project", {}).get("classifiers") or []
    for classifier in classifiers:
        if isinstance(classifier, str) and DEVELOPMENT_STATUS_PATTERN.match(classifier):
            return classifier.split("::")[-1].strip()
    return None


def validate_version_uniformity(
    inventories: List[tuple[str, dict]], report: ContractReport
) -> None:
    """Member pyprojects must agree on ``[project].version``."""
    versions = {
        module_name: version
        for module_name, pyproject in inventories
        if isinstance(version := pyproject.get("project", {}).get("version"), str)
        and version
    }
    counts = Counter(versions.values())
    if len(counts) < 2:
        return
    majority_version, _ = counts.most_common(1)[0]
    for module_name, version in sorted(versions.items()):
        if version == majority_version:
            continue
        if KNOWN_VERSION_DEVIATIONS.get(module_name) == version:
            report.diagnostic(
                f"{module_name}: version {version!r} deviates from the fleet "
                f"majority {majority_version!r} (known deviation; the release "
                "gate owns promotion)"
            )
        else:
            report.warning(
                f"{module_name}: version {version!r} deviates from the fleet "
                f"majority {majority_version!r}"
            )


def validate_classifier_consistency(
    inventories: List[tuple[str, dict]], report: ContractReport
) -> None:
    """Warn on module Development Status outliers; root asymmetry is a note."""
    statuses = {
        module_name: status
        for module_name, pyproject in inventories
        if (status := _development_status(pyproject)) is not None
    }
    undeclared = sorted(
        module_name for module_name, _ in inventories if module_name not in statuses
    )
    for module_name in undeclared:
        report.diagnostic(f"{module_name}: no Development Status classifier declared")
    counts = Counter(statuses.values())
    if not counts:
        return
    majority_status, _ = counts.most_common(1)[0]
    for module_name, status in sorted(statuses.items()):
        if status != majority_status:
            report.warning(
                f"{module_name}: Development Status {status!r} deviates from "
                f"the fleet majority {majority_status!r}"
            )
    root_pyproject = REPO_ROOT / "pyproject.toml"
    root_status = (
        _development_status(read_toml(root_pyproject))
        if root_pyproject.is_file()
        else None
    )
    if root_status is not None and root_status != majority_status:
        report.diagnostic(
            f"root pyproject: Development Status {root_status!r} differs from "
            f"the member fleet {majority_status!r} (framework meta-package "
            "asymmetry; the release gate owns alignment)"
        )


def validate_module(module_dir: Path, pyproject: dict, report: ContractReport) -> None:
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

    package = package_name_from_distribution(distribution)
    if package != distribution.lower().replace("-", "_"):
        report.errors.append(
            f"{label}: project name must normalize to lowercase Python package"
        )

    src_dir = module_dir / "src"
    package_dir = src_dir / package
    if src_dir.is_dir() and not package_dir.is_dir():
        report.errors.append(f"{label}: expected package directory src/{package}")

    validate_package_data(module_dir, pyproject, report)


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
    inventories: List[tuple[str, dict]] = []
    for module_dir in target_dirs:
        pyproject = parse_pyproject(module_dir)
        if not pyproject:
            report.errors.append(f"{module_dir.name}: invalid/missing pyproject")
            continue
        inventories.append((module_dir.name, pyproject))
        validate_module(module_dir, pyproject, report)
        validate_requirements_parity(module_dir, pyproject, report)
        validate_source_traversal(module_dir, report)
    validate_version_uniformity(inventories, report)
    validate_classifier_consistency(inventories, report)
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
        help="Show out-of-package __file__ traversal and metadata diagnostics.",
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
