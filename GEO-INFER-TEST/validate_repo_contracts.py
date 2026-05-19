#!/usr/bin/env python3
"""
Validate repo-wide GEO-INFER structural contracts.

The default mode fails on structural drift that should never be tolerated:
module inventory, local signposting, package casing, setup.py syntax, and
pyproject package-name sanity. Source-language debt is reported by default and
can be made fatal with ``--strict-source-language``.
"""

from __future__ import annotations

import argparse
import ast
import importlib
import re
import sys
import tomllib
from dataclasses import dataclass, field
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
EXPECTED_MODULE_COUNT = 44
SIGNPOST_FILES = ("README.md", "AGENTS.md", "SKILL.md")
SOURCE_LANGUAGE_PATTERN = re.compile(
    r"\b(mock|stub|fake|placeholder)\b|NotImplementedError",
    re.IGNORECASE,
)
SOURCE_LANGUAGE_ALLOWLIST = (
    "placeholder=",
    "Subclasses must implement",
    "abstract",
    "not supported",
    "not available",
)


@dataclass
class ContractReport:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warning(self, message: str) -> None:
        self.warnings.append(message)


def find_module_dirs() -> list[Path]:
    return sorted(
        path
        for path in REPO_ROOT.iterdir()
        if path.is_dir() and path.name.startswith("GEO-INFER-")
    )


def parse_pyproject(module_dir: Path, report: ContractReport) -> dict:
    pyproject = module_dir / "pyproject.toml"
    if not pyproject.exists():
        report.error(f"{module_dir.name}: missing pyproject.toml")
        return {}
    try:
        return tomllib.loads(pyproject.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as exc:
        report.error(f"{module_dir.name}: invalid pyproject.toml: {exc}")
        return {}


def expected_package_name(pyproject: dict) -> str | None:
    project = pyproject.get("project", {})
    name = project.get("name")
    if not isinstance(name, str) or not name:
        return None
    return name.replace("-", "_")


def validate_inventory(module_dirs: list[Path], report: ContractReport) -> None:
    if len(module_dirs) != EXPECTED_MODULE_COUNT:
        report.error(
            f"Expected {EXPECTED_MODULE_COUNT} GEO-INFER-* modules, found {len(module_dirs)}"
        )


def validate_signposting(module_dirs: list[Path], report: ContractReport) -> None:
    for module_dir in module_dirs:
        for filename in SIGNPOST_FILES:
            if not (module_dir / filename).exists():
                report.error(f"{module_dir.name}: missing {filename}")


def validate_package_casing(module_dirs: list[Path], report: ContractReport) -> None:
    uppercase_package_dirs: list[str] = []
    for module_dir in module_dirs:
        for path in (module_dir / "src").glob("geo_infer_*"):
            if path.is_dir() and any(char.isupper() for char in path.name):
                uppercase_package_dirs.append(str(path.relative_to(REPO_ROOT)))
    if uppercase_package_dirs:
        for path in uppercase_package_dirs:
            report.error(f"Uppercase Python package directory: {path}")


def validate_pyproject_packages(
    module_dirs: list[Path], report: ContractReport
) -> None:
    for module_dir in module_dirs:
        pyproject = parse_pyproject(module_dir, report)
        package_name = expected_package_name(pyproject)
        if package_name is None:
            report.error(f"{module_dir.name}: missing [project].name")
            continue

        if package_name.lower() != package_name:
            report.error(f"{module_dir.name}: project name must normalize to lowercase")

        src_dir = module_dir / "src"
        package_dir = src_dir / package_name
        if src_dir.exists() and not package_dir.exists():
            report.error(
                f"{module_dir.name}: expected package directory {package_dir.relative_to(REPO_ROOT)}"
            )

        dependencies = pyproject.get("project", {}).get("dependencies", [])
        if dependencies is not None and not isinstance(dependencies, list):
            report.error(f"{module_dir.name}: project.dependencies must be a list")


def validate_setup_syntax(module_dirs: list[Path], report: ContractReport) -> None:
    for setup_py in sorted(module_dir / "setup.py" for module_dir in module_dirs):
        if not setup_py.exists():
            continue
        try:
            ast.parse(setup_py.read_text(encoding="utf-8"), filename=str(setup_py))
        except SyntaxError as exc:
            report.error(f"{setup_py.relative_to(REPO_ROOT)}: syntax error: {exc}")


def validate_import_smoke(module_dirs: list[Path], report: ContractReport) -> None:
    """Best-effort package import smoke check with local src paths."""
    for module_dir in module_dirs:
        pyproject = parse_pyproject(module_dir, report)
        package_name = expected_package_name(pyproject)
        if not package_name:
            continue
        src_dir = module_dir / "src"
        if not src_dir.exists():
            continue

        sys.path.insert(0, str(src_dir))
        try:
            importlib.import_module(package_name)
        except Exception as exc:  # noqa: BLE001 - smoke check reports any import break
            report.warning(
                f"{module_dir.name}: import {package_name} raised {type(exc).__name__}: {exc}"
            )
        finally:
            try:
                sys.path.remove(str(src_dir))
            except ValueError:
                pass
            sys.modules.pop(package_name, None)


def validate_source_language(report: ContractReport, strict: bool) -> None:
    hits: list[str] = []
    for source_file in sorted(REPO_ROOT.glob("GEO-INFER-*/src/**/*.py")):
        text = source_file.read_text(encoding="utf-8", errors="ignore")
        for lineno, line in enumerate(text.splitlines(), start=1):
            if not SOURCE_LANGUAGE_PATTERN.search(line):
                continue
            if any(
                allowed.lower() in line.lower() for allowed in SOURCE_LANGUAGE_ALLOWLIST
            ):
                continue
            hits.append(
                f"{source_file.relative_to(REPO_ROOT)}:{lineno}: {line.strip()}"
            )

    if not hits:
        return

    message = f"Source-language debt hits: {len(hits)}. First hits: " + "; ".join(
        hits[:8]
    )
    if strict:
        report.error(message)
    else:
        report.warning(message)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate GEO-INFER repo contracts")
    parser.add_argument(
        "--strict-source-language",
        action="store_true",
        help="Fail when mock/stub/fake/placeholder language remains in source.",
    )
    parser.add_argument(
        "--skip-import-smoke",
        action="store_true",
        help="Skip best-effort per-package import smoke warnings.",
    )
    args = parser.parse_args()

    report = ContractReport()
    module_dirs = find_module_dirs()

    validate_inventory(module_dirs, report)
    validate_signposting(module_dirs, report)
    validate_package_casing(module_dirs, report)
    validate_pyproject_packages(module_dirs, report)
    validate_setup_syntax(module_dirs, report)
    if not args.skip_import_smoke:
        validate_import_smoke(module_dirs, report)
    validate_source_language(report, strict=args.strict_source_language)

    print(f"Modules checked: {len(module_dirs)}")
    print(f"Errors: {len(report.errors)}")
    for error in report.errors:
        print(f"ERROR: {error}")
    print(f"Warnings: {len(report.warnings)}")
    for warning in report.warnings:
        print(f"WARNING: {warning}")

    return 1 if report.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
