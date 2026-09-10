"""Shared plumbing for the GEO-INFER-TEST validators.

``validate_packaging.py``, ``validate_repo_contracts.py`` and
``rewrite_readme_agents.py`` previously re-implemented module discovery,
pyproject parsing, requirement-name normalization and the error/warning
report independently. This module is the single definition of that plumbing.

Repository-root discipline: helpers take ``repo_root`` (or operate on a
passed module directory) as an explicit parameter and never capture a
repository root at import time. Each validator keeps its own module-global
``REPO_ROOT`` and passes it in, so test suites can monkeypatch one
validator's root without silently retargeting the shared helpers.
"""

from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

MODULE_PREFIX = "GEO-INFER-"


@dataclass
class ContractReport:
    """Accumulated validator findings.

    ``errors`` fail the run, ``warnings`` fail under ``--strict``-style
    promotion, and ``diagnostics`` are informational only.
    """

    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    diagnostics: list[str] = field(default_factory=list)

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warning(self, message: str) -> None:
        self.warnings.append(message)

    def diagnostic(self, message: str) -> None:
        self.diagnostics.append(message)


def discover_module_dirs(repo_root: Path, prefix: str = MODULE_PREFIX) -> list[Path]:
    """Return tracked module directories (``GEO-INFER-*``) in stable order."""
    return sorted(
        path
        for path in repo_root.iterdir()
        if path.is_dir() and path.name.startswith(prefix)
    )


def read_toml(path: Path) -> dict:
    """Parse a TOML file, raising ``FileNotFoundError``/``TOMLDecodeError``."""
    with open(path, "rb") as handle:
        return tomllib.load(handle)


def read_pyproject(module_dir: Path) -> dict:
    """Parse a module's ``pyproject.toml`` ({} when absent or invalid).

    Lenient by design: callers that must surface missing/invalid metadata
    report it themselves (see ``validate_repo_contracts.parse_pyproject``).
    """
    pyproject = module_dir / "pyproject.toml"
    if not pyproject.is_file():
        return {}
    try:
        return read_toml(pyproject)
    except tomllib.TOMLDecodeError:
        return {}


def distribution_name(pyproject: dict) -> str | None:
    """Return the declared PyPI distribution name, or None when absent."""
    name = pyproject.get("project", {}).get("name")
    return name if isinstance(name, str) and name else None


def package_name_from_distribution(distribution: str) -> str:
    """Map a distribution name to its importable package name (``-`` -> ``_``)."""
    return distribution.replace("-", "_")


def expected_package_name(pyproject: dict) -> str | None:
    """Return the package directory name implied by ``[project].name``."""
    distribution = distribution_name(pyproject)
    if distribution is None:
        return None
    return package_name_from_distribution(distribution)


# Requirements-name normalization: one definition shared by the validators
# so requirements.txt lines and pyproject dependency strings compare by
# normalized distribution name only.
_REQUIREMENT_NAME_RE = re.compile(r"^\s*([A-Za-z0-9][A-Za-z0-9._-]*)")


def normalize_dependency_name(raw: str) -> str:
    """Normalize a distribution name (lowercase, underscores -> dashes)."""
    match = _REQUIREMENT_NAME_RE.match(raw.strip())
    if not match:
        return ""
    return match.group(1).lower().replace("_", "-")


def parse_requirements_names(path: Path) -> list[str]:
    """Return normalized dependency names from a ``requirements.txt`` file.

    Blank lines, comments and pip options (``-r``/``-e``/``--index-url``...)
    are ignored; extras and version specifiers are stripped so lines compare
    by name only.
    """
    if not path.is_file():
        return []
    names: list[str] = []
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("-"):
            continue
        name = normalize_dependency_name(stripped.split(";", 1)[0])
        if name:
            names.append(name)
    return names


def pyproject_dependency_names(pyproject: dict) -> set:
    """Return normalized runtime dependency names from [project.dependencies]."""
    deps = pyproject.get("project", {}).get("dependencies") or []
    return {name for name in (normalize_dependency_name(str(d)) for d in deps) if name}


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


def parse_setup_py_requires(module_dir: Path) -> tuple[set | None, bool]:
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


# Standard-library modules that must never be listed as PyPI dependencies.
STDLIB_REQUIREMENT_NAMES = {
    "argparse",
    "asyncio",
    "ast",
    "bz2",
    "colorsys",
    "concurrent",
    "configparser",
    "contextlib",
    "csv",
    "email",
    "functools",
    "gc",
    "gzip",
    "hashlib",
    "heapq",
    "inspect",
    "io",
    "itertools",
    "json",
    "math",
    "pickle",
    "queue",
    "random",
    "re",
    "secrets",
    "shutil",
    "sqlite3",
    "statistics",
    "subprocess",
    "tempfile",
    "threading",
    "unittest",
    "urllib",
    "uuid",
    "weakref",
}


def internal_requirement_names(repo_root: Path) -> frozenset[str]:
    """Internal distribution names, derived from the workspace tree.

    A requirement line pinned ``>=0.0.0`` names an internal workspace member
    masquerading as a PyPI dependency; such lines must be resolved through
    ``[tool.uv.sources]`` instead. The derivation covers every live surface:
    each member's own ``geo-infer-*`` distribution name comes from its
    ``pyproject.toml``.

    Historically requirements files also referenced bare sub-distribution
    names (for example ``cognitive-engine``) with placeholder pins; no
    requirements file in the tree contains such a line any more (verified
    2026-09-09 against every ``GEO-INFER-*/requirements*.txt``). Bare
    sub-distribution names are therefore not enumerable from the tree; if
    one returns, extend this derivation explicitly rather than growing a
    hand-maintained allowlist.
    """
    names: set[str] = set()
    for module_dir in discover_module_dirs(repo_root):
        distribution = distribution_name(read_pyproject(module_dir))
        if distribution:
            names.add(distribution)
    return frozenset(names)
