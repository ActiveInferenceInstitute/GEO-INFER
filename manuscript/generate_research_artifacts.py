#!/usr/bin/env python3
"""Generate repository-derived manuscript variables, figures, and evidence.

The tracked manuscript is intentionally authored with ``{{UPPERCASE_TOKENS}}``.
This module is the single producer for those values.  It scans the checkout,
creates figures from the scan, registers their captions and provenance, and
writes resolved manuscript copies to ``output/manuscript``.  Generated output
is disposable; the source markdown remains the reviewable manuscript surface.

The optional ``--verify`` and ``--full-validation`` modes record the commands
that were actually executed.  A failed or unrun command is never represented
as a passing research result.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tomllib
from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

TOKEN_RE = re.compile(r"\{\{([A-Z][A-Z0-9_]*)\}\}")
EXCLUDED_MANUSCRIPT_DOCS = frozenset({"README.md", "AGENTS.md", "SYNTAX.md"})
FIGURE_SCHEMA = "geo-infer-manuscript-figures/v1"
RESEARCH_SCHEMA = "geo-infer-manuscript-evidence/v1"
FOCUS_MODULES = ("GEO-INFER-ACT", "GEO-INFER-BAYES", "GEO-INFER-RISK")

# Editorial grouping of the module set, mirroring the "Module Themes" table in
# README.md. This is a classification, not a measurement: the counts beside
# each module are read from the checkout, but which theme a module belongs to
# is a judgement and has to be declared somewhere. ``_module_table`` refuses to
# render unless every measured module appears in exactly one theme, so adding a
# module without theming it fails the build instead of dropping it silently.
MODULE_THEMES: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "Spatial and place-based",
        (
            "GEO-INFER-SPACE",
            "GEO-INFER-PLACE",
            "GEO-INFER-TIME",
            "GEO-INFER-MARINE",
            "GEO-INFER-WATER",
            "GEO-INFER-FOREST",
            "GEO-INFER-CLIMATE",
            "GEO-INFER-ENERGY",
            "GEO-INFER-TRANSPORT",
            "GEO-INFER-EMERGENCY",
        ),
    ),
    (
        "Bayesian and active inference",
        (
            "GEO-INFER-BAYES",
            "GEO-INFER-SIM",
            "GEO-INFER-SPM",
            "GEO-INFER-COG",
            "GEO-INFER-ACT",
            "GEO-INFER-MATH",
        ),
    ),
    (
        "Agents and AI orchestration",
        (
            "GEO-INFER-AGENT",
            "GEO-INFER-AG",
            "GEO-INFER-AI",
            "GEO-INFER-ANT",
            "GEO-INFER-OPS",
            "GEO-INFER-COMMS",
        ),
    ),
    (
        "Governance, risk and domain",
        (
            "GEO-INFER-INSURANCE",
            "GEO-INFER-RISK",
            "GEO-INFER-METAGOV",
            "GEO-INFER-NORMS",
            "GEO-INFER-ECON",
            "GEO-INFER-PEP",
            "GEO-INFER-REQ",
            "GEO-INFER-SEC",
            "GEO-INFER-CIV",
            "GEO-INFER-HEALTH",
            "GEO-INFER-ORG",
        ),
    ),
    (
        "Data, API and applications",
        (
            "GEO-INFER-API",
            "GEO-INFER-APP",
            "GEO-INFER-DATA",
            "GEO-INFER-IOT",
            "GEO-INFER-ART",
            "GEO-INFER-EDU",
        ),
    ),
    (
        "Infrastructure and validation",
        (
            "GEO-INFER-INTRA",
            "GEO-INFER-TEST",
            "GEO-INFER-LOG",
            "GEO-INFER-GIT",
            "GEO-INFER-EXAMPLES",
            "GEO-INFER-BIO",
        ),
    ),
)

# Printable geometry of the template's LaTeX text block, in inches, read from
# output/pdf/_combined_manuscript.log (textwidth 430.00462pt, textheight
# 556.47656pt).  Every figure is typeset inside this box, so a figure drawn
# larger than it is scaled DOWN and its type shrinks with it: a 13in canvas
# lettered at 8.5pt printed at 3.1pt, roughly half the ~6pt floor for legible
# print.  Drawing at the printed size keeps the scale near 1.0 and the type at
# its authored point size.
TEXT_BLOCK_WIDTH_IN = 5.95
TEXT_BLOCK_HEIGHT_IN = 7.70
# Must stay in lock-step with ``rendering.figure_height_fraction`` in
# manuscript/config.yaml, which is what the renderer writes into the
# ``height=<fraction>\textheight`` bound on every \includegraphics.
FIGURE_HEIGHT_FRACTION = 0.9
MAX_FIGURE_HEIGHT_IN = TEXT_BLOCK_HEIGHT_IN * FIGURE_HEIGHT_FRACTION
FIGURE_DPI = 220
# Inches of vertical space per module row in the inventory figure.  At 8pt type
# this is about 11pt of leading per label.
INVENTORY_ROW_HEIGHT_IN = 0.153


@dataclass(frozen=True)
class ModuleMetrics:
    """Measured implementation and test surfaces for one module."""

    name: str
    package: str
    source_files: int
    source_lines: int
    test_files: int
    tests_by_category: dict[str, int]


@dataclass(frozen=True)
class FigureSpec:
    """Publication figure metadata generated with the corresponding image.

    ``sha256`` is the digest of the PNG bytes actually written, so the registry
    carries per-figure content provenance rather than only the repository-wide
    build hash.  It is empty until the image exists and is filled in by
    :func:`generate_figures`; :func:`write_figure_registry` refuses a spec that
    still carries an empty digest.
    """

    label: str
    filename: str
    caption: str
    generated_by: str
    alt_text: str
    sha256: str = ""


@dataclass(frozen=True)
class RepositoryInventory:
    """Deterministic repository measurements used by the manuscript."""

    project_version: str
    project_license: str
    commit: str
    branch: str
    commit_date: str
    manuscript_source_date: str
    dirty_file_count: int
    source_hash: str
    modules: tuple[ModuleMetrics, ...]
    test_files_by_category: dict[str, int]
    h3_test_files: int
    documentation_pages: int
    validator_files: int
    test_tooling_files: int
    source_files: int
    source_lines: int
    test_files: int
    python_version: str

    @property
    def module_count(self) -> int:
        return len(self.modules)

    @property
    def modules_with_tests(self) -> int:
        return sum(module.test_files > 0 for module in self.modules)

    @property
    def focused_modules(self) -> tuple[ModuleMetrics, ...]:
        by_name = {module.name: module for module in self.modules}
        return tuple(by_name[name] for name in FOCUS_MODULES if name in by_name)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": RESEARCH_SCHEMA,
            "project_version": self.project_version,
            "project_license": self.project_license,
            "commit": self.commit,
            "branch": self.branch,
            "commit_date": self.commit_date,
            "manuscript_source_date": self.manuscript_source_date,
            "dirty_file_count": self.dirty_file_count,
            "source_hash": self.source_hash,
            "modules": [asdict(module) for module in self.modules],
            "test_files_by_category": dict(self.test_files_by_category),
            "h3_test_files": self.h3_test_files,
            "documentation_pages": self.documentation_pages,
            "validator_files": self.validator_files,
            "test_tooling_files": self.test_tooling_files,
            "source_files": self.source_files,
            "source_lines": self.source_lines,
            "test_files": self.test_files,
            "python_version": self.python_version,
        }


@dataclass(frozen=True)
class VerificationResult:
    """Outcome of one explicitly executed research verification command."""

    name: str
    command: str
    status: str
    return_code: int | None
    duration_seconds: float | None
    output_tail: str


VERIFICATION_COMMANDS: tuple[tuple[str, str], ...] = (
    (
        "compile",
        "python -m compileall -q GEO-INFER-*/src GEO-INFER-*/examples manuscript",
    ),
    (
        "repository-contracts",
        "uv run python GEO-INFER-TEST/validate_repo_contracts.py --strict-source-language",
    ),
    (
        "documentation",
        "uv run python GEO-INFER-TEST/validate_documentation.py --strict",
    ),
    (
        "skills",
        "uv run python GEO-INFER-TEST/validate_skills.py --check-xrefs",
    ),
    (
        "test-contracts",
        "uv run python GEO-INFER-TEST/validate_test_contracts.py --strict",
    ),
    (
        "model-contracts",
        "uv run python GEO-INFER-TEST/validate_model_contracts.py --strict --seed 42",
    ),
    (
        "reproducibility",
        "uv run python GEO-INFER-TEST/run_model_audit.py --seed 42 --reproducible",
    ),
)

FULL_VALIDATION_COMMANDS: tuple[tuple[str, str], ...] = (
    ("unit-tests", "uv run python GEO-INFER-TEST/run_unified_tests.py --category unit"),
    (
        "integration-tests",
        "uv run python GEO-INFER-TEST/run_unified_tests.py --category integration",
    ),
    (
        "performance-tests",
        "uv run python GEO-INFER-TEST/run_unified_tests.py --category performance",
    ),
    (
        "h3-contracts",
        "uv run python GEO-INFER-TEST/run_unified_tests.py --h3-migration",
    ),
)


def _iter_files(directory: Path, suffix: str | None = None) -> Iterable[Path]:
    if not directory.is_dir():
        return ()
    paths = directory.rglob("*")
    return (
        path
        for path in paths
        if path.is_file()
        and ".git" not in path.parts
        and "__pycache__" not in path.parts
        and (suffix is None or path.suffix == suffix)
    )


def _python_files(directory: Path) -> tuple[Path, ...]:
    return tuple(sorted(_iter_files(directory, ".py")))


def _nonempty_lines(path: Path) -> int:
    return sum(
        bool(line.strip()) for line in path.read_text(encoding="utf-8").splitlines()
    )


def _run_git(root: Path, *args: str, default: str = "unavailable") -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), *args],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return default
    return result.stdout.strip() or default


def _dirty_file_count(root: Path) -> int:
    """Count working-tree entries that differ from the tracked commit.

    ``git status --porcelain`` prints one line per added, modified, deleted,
    renamed, unmerged or untracked path.  A clean checkout prints nothing, so
    the honest answer for a clean tree is ``0``.

    Returns:
        The number of differing entries, or ``-1`` when git cannot answer.
        ``-1`` is deliberately not ``0``: an unavailable answer must never be
        published as a clean tree.
    """
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "status", "--porcelain"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return -1
    return sum(bool(line.strip()) for line in result.stdout.splitlines())


def _dirty_marker(count: int) -> str:
    """Return the commit-stamp suffix that describes ``count``."""
    if count > 0:
        return "-dirty"
    if count < 0:
        return "-unverified"
    return ""


def _project_metadata(root: Path) -> dict[str, str]:
    path = root / "pyproject.toml"
    try:
        with path.open("rb") as handle:
            project = tomllib.load(handle).get("project", {})
    except (OSError, tomllib.TOMLDecodeError):
        return {"version": "unavailable", "license": "unavailable"}
    license_value = project.get("license", {})
    if isinstance(license_value, dict):
        license_text = license_value.get("text") or license_value.get("file")
    else:
        license_text = license_value
    return {
        "version": str(project.get("version", "unavailable")),
        "license": str(license_text or "unavailable"),
    }


def _source_hash(root: Path) -> str:
    digest = hashlib.sha256()
    paths: set[Path] = set(_iter_files(root / "manuscript"))
    for module in _module_paths(root):
        paths.update(_python_files(module / "src"))
        paths.update(
            path
            for path in _python_files(module / "tests")
            if path.name.startswith("test_")
        )
    paths.update(
        path for path in (root / "GEO-INFER-TEST").glob("*.py") if path.is_file()
    )
    paths.update(
        path for path in (root / "pyproject.toml", root / "uv.lock") if path.is_file()
    )
    for path in sorted(paths, key=lambda item: item.relative_to(root).as_posix()):
        digest.update(path.relative_to(root).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
    return digest.hexdigest()[:16]


def _module_package(module_path: Path) -> str:
    """Return the importable package directory shipped under ``src/``."""
    packages = sorted(
        path.name
        for path in (module_path / "src").iterdir()
        if path.is_dir() and (path / "__init__.py").is_file()
    )
    return packages[0] if packages else "unavailable"


def _module_paths(root: Path) -> tuple[Path, ...]:
    return tuple(
        sorted(
            path
            for path in root.glob("GEO-INFER-*")
            if path.is_dir() and (path / "src").is_dir()
        )
    )


def _test_files(root: Path) -> tuple[Path, ...]:
    paths: list[Path] = []
    for module in _module_paths(root):
        paths.extend(
            path
            for path in _python_files(module / "tests")
            if path.name.startswith("test_")
        )
    paths.extend(
        path
        for path in _python_files(root / "GEO-INFER-TEST" / "tests")
        if path.name.startswith("test_")
    )
    return tuple(sorted(set(paths)))


TEST_CATEGORIES: tuple[str, ...] = ("unit", "integration", "performance", "other")


def _test_category(path: Path) -> str:
    """Classify a test file on the mutually-exclusive directory axis.

    Every test lands in exactly one of :data:`TEST_CATEGORIES`, so the four
    published category counts always sum to the published total.

    Subject-matter tags such as H3 are deliberately *not* on this axis.  They
    were, and the bucket was unreachable: an H3 test lives under ``tests/unit``
    or ``tests/integration`` like any other, matched an earlier branch, and the
    ``h3`` count published as zero while H3-named files existed.  H3 is now
    counted orthogonally by :func:`_h3_test_files`.
    """
    parts = {part.lower() for part in path.parts}
    for category in ("unit", "integration", "performance"):
        if category in parts:
            return category
    return "other"


def _h3_test_files(paths: Iterable[Path]) -> int:
    """Count H3-named test files, independently of their directory category."""
    return sum("h3" in path.name.lower() for path in paths)


def collect_inventory(
    root: Path, *, dirty_file_count: int | None = None
) -> RepositoryInventory:
    """Measure the current checkout without importing application modules.

    Args:
        root: Repository root to measure.
        dirty_file_count: Pre-measured working-tree dirtiness.  ``generate``
            passes the count taken *before* it writes anything, so the
            generator's own outputs are never mistaken for un-stamped source.
            ``None`` measures it here.
    """
    modules: list[ModuleMetrics] = []
    all_tests = _test_files(root)
    category_counts: dict[str, int] = {}
    for path in all_tests:
        category = _test_category(path)
        category_counts[category] = category_counts.get(category, 0) + 1

    for module_path in _module_paths(root):
        source = _python_files(module_path / "src")
        tests = tuple(path for path in all_tests if module_path in path.parents)
        by_category: dict[str, int] = {}
        for path in tests:
            category = _test_category(path)
            by_category[category] = by_category.get(category, 0) + 1
        modules.append(
            ModuleMetrics(
                name=module_path.name,
                package=_module_package(module_path),
                source_files=len(source),
                source_lines=sum(_nonempty_lines(path) for path in source),
                test_files=len(tests),
                tests_by_category=dict(sorted(by_category.items())),
            )
        )

    source_files = tuple(
        path for module in _module_paths(root) for path in _python_files(module / "src")
    )
    documentation_pages = len(
        tuple(_iter_files(root / "GEO-INFER-INTRA" / "docs", ".md"))
    )
    # A validator is a ``validate_*.py`` entry point, not every top-level file
    # in GEO-INFER-TEST: that directory also holds packaging (setup.py), build
    # (build_package_wheels.py), documentation (rewrite_readme_agents.py) and
    # runner (run_unified_tests.py) utilities, none of which validate anything.
    validator_files = len(
        tuple(
            path
            for path in (root / "GEO-INFER-TEST").glob("validate_*.py")
            if path.is_file()
        )
    )
    test_tooling_files = len(
        tuple(path for path in (root / "GEO-INFER-TEST").glob("*.py") if path.is_file())
    )
    project_metadata = _project_metadata(root)
    dirty_files = (
        _dirty_file_count(root) if dirty_file_count is None else dirty_file_count
    )
    commit = _run_git(root, "rev-parse", "--short", "HEAD")
    return RepositoryInventory(
        project_version=project_metadata["version"],
        project_license=project_metadata["license"],
        commit=commit + _dirty_marker(dirty_files),
        branch=_run_git(root, "branch", "--show-current"),
        commit_date=_run_git(root, "show", "-s", "--format=%cI", default="unavailable"),
        manuscript_source_date=_manuscript_source_date(root),
        dirty_file_count=dirty_files,
        source_hash=_source_hash(root),
        modules=tuple(modules),
        test_files_by_category=dict(sorted(category_counts.items())),
        h3_test_files=_h3_test_files(all_tests),
        documentation_pages=documentation_pages,
        validator_files=validator_files,
        test_tooling_files=test_tooling_files,
        source_files=len(source_files),
        source_lines=sum(_nonempty_lines(path) for path in source_files),
        test_files=len(all_tests),
        python_version=platform.python_version(),
    )


def _module_table(inventory: RepositoryInventory) -> str:
    """Render every measured module as a themed Markdown table.

    Raises:
        ValueError: when a measured module has no theme, or a declared theme
            names a module that is not in the checkout.  Either way the table
            would silently misrepresent the module set.
    """
    measured = {module.name: module for module in inventory.modules}
    declared = [name for _theme, names in MODULE_THEMES for name in names]
    duplicates = sorted({name for name in declared if declared.count(name) > 1})
    if duplicates:
        raise ValueError(f"modules declared in more than one theme: {duplicates}")
    unthemed = sorted(set(measured) - set(declared))
    if unthemed:
        raise ValueError(f"measured modules with no declared theme: {unthemed}")
    missing = sorted(set(declared) - set(measured))
    if missing:
        raise ValueError(f"themed modules absent from the checkout: {missing}")
    # Pandoc derives each column's relative width from the dash count in the
    # separator row.  Equal dashes gave the Module column less width than
    # ``GEO-INFER-INSURANCE`` needs, and the template's breakable-monospace
    # macro then split module names mid-word ("GEO-INFER-IN / SURANCE") or ran
    # them into the Package column.  The proportions below are sized from the
    # longest value each column actually holds.
    rows = [
        "| Theme | Module | Package | Source files | Test files |",
        "| " + " | ".join(("-" * 16, "-" * 21, "-" * 21, "-" * 7 + ":", "-" * 7 + ":")) + " |",
    ]
    for theme, names in MODULE_THEMES:
        ordered = sorted(
            (measured[name] for name in names),
            key=lambda item: (-item.source_files, item.name),
        )
        for position, module in enumerate(ordered):
            label = theme if position == 0 else ""
            rows.append(
                f"| {label} | `{module.name}` | `{module.package}` | "
                f"{module.source_files} | {module.test_files} |"
            )
    return "\n".join(rows)


def _format_count(value: int) -> str:
    return f"{value:,}"


def _caption_module_inventory(inventory: RepositoryInventory) -> str:
    return (
        f"Repository-derived inventory of {inventory.module_count} src/-bearing GEO-INFER modules at "
        f"commit {inventory.commit}. Horizontal bars show Python source-file and test-file counts "
        "for every module, with modules ordered by source-file count; values are measured from the "
        "checkout rather than entered manually."
    )


def _caption_research_spine(inventory: RepositoryInventory) -> str:
    focus = ", ".join(
        module.name.removeprefix("GEO-INFER-") for module in inventory.focused_modules
    )
    return (
        f"Implementation and verification surfaces for the {focus} research spine. "
        "Each group reports the tracked Python source-file count and test-file count for the "
        "corresponding module, exposing where the repository concentrates active-inference, "
        "Bayesian, and risk-analysis evidence."
    )


def _caption_validation_surface(inventory: RepositoryInventory) -> str:
    categories = (
        ", ".join(inventory.test_files_by_category) or "the discovered test suite"
    )
    return (
        f"Repository validation surface at commit {inventory.commit}. The left panel counts test "
        f"files by discovered category ({categories}); the right panel reports the measured module, "
        "documentation, and validator surfaces. These counts describe available evidence surfaces, "
        "not claims that a test command passed."
    )


def _alt_module_inventory(inventory: RepositoryInventory) -> str:
    return (
        f"Horizontal grouped bar chart with one row per module for "
        f"{inventory.module_count} modules, sorted with the largest source-file "
        "count at the top. Each row carries two bars, Python source files and "
        "test files, on a shared count axis."
    )


def _alt_research_spine(inventory: RepositoryInventory) -> str:
    focus = ", ".join(
        module.name.removeprefix("GEO-INFER-") for module in inventory.focused_modules
    )
    return (
        f"Grouped bar chart with one group per module for {focus}. Each group "
        "pairs a source-file bar with a test-file bar on a shared count axis, so "
        "implementation and verification height can be compared per module."
    )


def _alt_validation_surface(inventory: RepositoryInventory) -> str:
    categories = (
        ", ".join(inventory.test_files_by_category) or "the discovered test suite"
    )
    return (
        "Two-panel figure. The left panel is a bar chart of test-file counts per "
        f"discovered category ({categories}). The right panel is a bar chart of "
        "the measured module, documentation, and validator surface counts."
    )


def _import_matplotlib() -> tuple[Any, Any]:
    os.environ.setdefault("MPLBACKEND", "Agg")
    import matplotlib

    matplotlib.use("Agg", force=True)
    import matplotlib.pyplot as plt

    return matplotlib, plt


def _png_size_inches(path: Path, dpi: int) -> tuple[float, float]:
    """Return the (width, height) of a PNG in inches at ``dpi``.

    Read from the IHDR chunk rather than an image library: the pixel geometry
    is the only thing needed and it must be readable wherever the generator
    runs.
    """
    header = path.read_bytes()[:24]
    if header[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"not a PNG: {path}")
    width = int.from_bytes(header[16:20], "big")
    height = int.from_bytes(header[20:24], "big")
    return width / dpi, height / dpi


def _save_figure(fig: Any, path: Path, caption: str, source_hash: str) -> str:
    """Write one figure and return the SHA-256 of the bytes that were written.

    Raises:
        ValueError: when the written figure is larger than the printable text
            block, which would force the typesetter to scale it down and take
            its type below the legibility floor with it.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(
        path,
        dpi=FIGURE_DPI,
        bbox_inches="tight",
        metadata={
            "Title": path.stem.replace("_", " ").title(),
            "Description": caption,
            "Source": f"GEO-INFER repository source hash {source_hash}",
        },
    )
    width_in, height_in = _png_size_inches(path, FIGURE_DPI)
    tolerance = 1.02
    if (
        width_in > TEXT_BLOCK_WIDTH_IN * tolerance
        or height_in > MAX_FIGURE_HEIGHT_IN * tolerance
    ):
        raise ValueError(
            f"{path.name} is {width_in:.2f}in x {height_in:.2f}in, larger than the "
            f"printable box {TEXT_BLOCK_WIDTH_IN}in x {MAX_FIGURE_HEIGHT_IN:.2f}in; "
            "it would be scaled down at typeset time and its type with it"
        )
    return hashlib.sha256(path.read_bytes()).hexdigest()


def generate_figures(
    inventory: RepositoryInventory, output_dir: Path
) -> tuple[FigureSpec, ...]:
    """Generate publication figures from the measured inventory."""
    _matplotlib, plt = _import_matplotlib()
    specs = (
        FigureSpec(
            "fig:module_inventory",
            "module_inventory.png",
            _caption_module_inventory(inventory),
            "manuscript.generate_research_artifacts.generate_figures",
            _alt_module_inventory(inventory),
        ),
        FigureSpec(
            "fig:research_spine",
            "research_spine.png",
            _caption_research_spine(inventory),
            "manuscript.generate_research_artifacts.generate_figures",
            _alt_research_spine(inventory),
        ),
        FigureSpec(
            "fig:validation_surface",
            "validation_surface.png",
            _caption_validation_surface(inventory),
            "manuscript.generate_research_artifacts.generate_figures",
            _alt_validation_surface(inventory),
        ),
    )
    digests: dict[str, str] = {}
    module_rows = sorted(
        inventory.modules, key=lambda item: (-item.source_files, item.name)
    )
    labels = [item.name.removeprefix("GEO-INFER-") for item in module_rows]
    source_counts = [item.source_files for item in module_rows]
    test_counts = [item.test_files for item in module_rows]

    with plt.rc_context(
        {
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "grid.alpha": 0.25,
            "font.size": 8,
            "axes.titleweight": "bold",
        }
    ):
        inventory_height = min(
            MAX_FIGURE_HEIGHT_IN,
            max(4.0, len(labels) * INVENTORY_ROW_HEIGHT_IN),
        )
        fig, axes = plt.subplots(
            1, 2, figsize=(TEXT_BLOCK_WIDTH_IN, inventory_height), sharey=True
        )
        y = list(range(len(labels)))
        axes[0].barh(y, source_counts, color="#2f6f9f", alpha=0.9)
        axes[1].barh(y, test_counts, color="#d17a2f", alpha=0.9)
        axes[0].set_title("Python source files")
        axes[1].set_title("Test files")
        axes[0].set_xlabel("Files")
        axes[1].set_xlabel("Files")
        axes[0].set_yticks(y, labels)
        axes[0].invert_yaxis()
        axes[0].set_axisbelow(True)
        axes[1].set_axisbelow(True)
        fig.suptitle(
            "GEO-INFER module evidence inventory", fontsize=11, fontweight="bold"
        )
        fig.tight_layout()
        digests[specs[0].filename] = _save_figure(
            fig, output_dir / specs[0].filename, specs[0].caption, inventory.source_hash
        )
        plt.close(fig)

        focus = inventory.focused_modules
        focus_labels = [item.name.removeprefix("GEO-INFER-") for item in focus]
        focus_source = [item.source_files for item in focus]
        focus_tests = [item.test_files for item in focus]
        fig, ax = plt.subplots(figsize=(5.8, 3.6))
        positions = list(range(len(focus_labels)))
        width = 0.36
        ax.bar(
            [position - width / 2 for position in positions],
            focus_source,
            width,
            label="Source files",
            color="#2f6f9f",
        )
        ax.bar(
            [position + width / 2 for position in positions],
            focus_tests,
            width,
            label="Test files",
            color="#d17a2f",
        )
        ax.set_title(
            "Active Inference, Bayesian, and RISK evidence surfaces", fontweight="bold"
        )
        ax.set_ylabel("Files")
        ax.set_xticks(positions, focus_labels)
        ax.legend(frameon=False)
        ax.set_axisbelow(True)
        fig.tight_layout()
        digests[specs[1].filename] = _save_figure(
            fig, output_dir / specs[1].filename, specs[1].caption, inventory.source_hash
        )
        plt.close(fig)

        categories = tuple(inventory.test_files_by_category)
        category_counts = [
            inventory.test_files_by_category[category] for category in categories
        ]
        evidence_labels = ("Modules", "Documentation\npages", "Validator\nPython files")
        evidence_counts = (
            inventory.module_count,
            inventory.documentation_pages,
            inventory.validator_files,
        )
        fig, axes = plt.subplots(1, 2, figsize=(5.8, 3.6))
        axes[0].bar(categories, category_counts, color="#5b8e7d")
        axes[0].set_title("Test-file categories", fontweight="bold")
        axes[0].set_ylabel("Files")
        axes[0].tick_params(axis="x", rotation=25)
        axes[1].bar(evidence_labels, evidence_counts, color="#6f5b9e")
        axes[1].set_title("Repository evidence surfaces", fontweight="bold")
        axes[1].set_ylabel("Count")
        axes[1].tick_params(axis="x", rotation=20)
        for axis in axes:
            axis.set_axisbelow(True)
        fig.suptitle(
            "Validation and documentation evidence", fontsize=11, fontweight="bold"
        )
        fig.tight_layout()
        digests[specs[2].filename] = _save_figure(
            fig, output_dir / specs[2].filename, specs[2].caption, inventory.source_hash
        )
        plt.close(fig)
    return tuple(
        replace(spec, sha256=digests[spec.filename]) for spec in specs
    )


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    temporary.replace(path)


def write_figure_registry(
    path: Path, specs: Sequence[FigureSpec], inventory: RepositoryInventory
) -> None:
    """Write a fail-closed registry for the generated figure set."""
    if not specs:
        raise ValueError("figure registry requires at least one generated figure")
    filenames = [spec.filename for spec in specs]
    labels = [spec.label for spec in specs]
    if len(set(filenames)) != len(filenames) or len(set(labels)) != len(labels):
        raise ValueError("figure registry labels and filenames must be unique")
    for spec in specs:
        if not spec.label.startswith("fig:") or not spec.caption.strip():
            raise ValueError(f"invalid figure specification: {spec!r}")
        if not spec.alt_text.strip():
            raise ValueError(f"invalid figure specification: {spec!r}")
        if len(spec.sha256) != 64:
            raise ValueError(
                f"figure {spec.filename} carries no content digest: {spec.sha256!r}"
            )
        if not (path.parent / spec.filename).is_file():
            raise FileNotFoundError(path.parent / spec.filename)
    _write_json(
        path,
        {
            "schema_version": FIGURE_SCHEMA,
            "source_commit": inventory.commit,
            "source_hash": inventory.source_hash,
            "figures": [
                asdict(spec) for spec in sorted(specs, key=lambda item: item.label)
            ],
        },
    )


def _verification_payload(
    results: Sequence[VerificationResult], full_validation: bool
) -> dict[str, Any]:
    return {
        "schema_version": RESEARCH_SCHEMA,
        "full_validation_requested": full_validation,
        "results": [asdict(result) for result in results],
    }


def run_verification(
    root: Path, *, full_validation: bool = False
) -> tuple[VerificationResult, ...]:
    """Run and record the research verification commands."""
    commands = (
        *VERIFICATION_COMMANDS,
        *(FULL_VALIDATION_COMMANDS if full_validation else ()),
    )
    results: list[VerificationResult] = []
    for name, command in commands:
        started = datetime.now(tz=timezone.utc)
        completed = subprocess.run(
            command,
            cwd=root,
            shell=True,
            capture_output=True,
            text=True,
            check=False,
        )
        elapsed = (datetime.now(tz=timezone.utc) - started).total_seconds()
        combined = f"{completed.stdout}\n{completed.stderr}".strip()
        results.append(
            VerificationResult(
                name=name,
                command=command,
                status="passed" if completed.returncode == 0 else "failed",
                return_code=completed.returncode,
                duration_seconds=round(elapsed, 3),
                output_tail=combined[-2000:],
            )
        )
    return tuple(results)


def defined_command_groups(*, full_validation: bool) -> tuple[str, ...]:
    """Return the names of every verification command group this build defines."""
    commands = (
        *VERIFICATION_COMMANDS,
        *(FULL_VALIDATION_COMMANDS if full_validation else ()),
    )
    return tuple(name for name, _command in commands)


def _verification_summary(
    results: Sequence[VerificationResult],
    *,
    full_validation: bool,
) -> tuple[str, int, int, int]:
    """Summarise a verification record against the command groups it defines.

    ``unrun`` is measured, never assumed: it is the number of defined command
    groups with no recorded outcome, plus any group explicitly recorded as
    ``not-run``.  An empty record therefore reports every defined group as
    skipped rather than a constant, and a full pass reports zero.
    """
    defined = defined_command_groups(full_validation=full_validation)
    passed = sum(result.status == "passed" for result in results)
    failed = sum(result.status == "failed" for result in results)
    recorded = {result.name for result in results}
    missing = sum(name not in recorded for name in defined)
    unrun = missing + sum(result.status == "not-run" for result in results)
    if not results:
        return "not run", passed, failed, unrun
    if failed:
        return f"{passed} passed, {failed} failed", passed, failed, unrun
    return f"{passed} passed", passed, failed, unrun


def build_variables(
    inventory: RepositoryInventory,
    specs: Sequence[FigureSpec],
    verification: Sequence[VerificationResult],
    *,
    full_validation: bool = False,
) -> dict[str, str]:
    """Return every manuscript replacement from measured inputs.

    Raises:
        ValueError: when the published per-category test counts do not sum to
            the published total, so a distribution that silently loses a bucket
            fails the build instead of shipping.
    """
    verification_summary, passed, failed, unrun = _verification_summary(
        verification, full_validation=full_validation
    )
    distribution = inventory.test_files_by_category
    unnamed = set(distribution) - set(TEST_CATEGORIES)
    if unnamed:
        raise ValueError(
            "test categories are published individually and must all be named; "
            f"unnamed: {', '.join(sorted(unnamed))}"
        )
    categorised = sum(distribution.values())
    if categorised != inventory.test_files:
        raise ValueError(
            f"test-file distribution sums to {categorised} against a total of "
            f"{inventory.test_files}"
        )
    variables: dict[str, str] = {
        "PROJECT_VERSION": inventory.project_version,
        "PROJECT_LICENSE": inventory.project_license,
        "MODULE_COUNT": str(inventory.module_count),
        "MODULE_NAMES": ", ".join(module.name for module in inventory.modules),
        "MODULE_TABLE": _module_table(inventory),
        "MODULE_THEME_COUNT": str(len(MODULE_THEMES)),
        "MODULES_WITH_TESTS_COUNT": str(inventory.modules_with_tests),
        "SOURCE_FILE_COUNT": _format_count(inventory.source_files),
        "SOURCE_LINE_COUNT": _format_count(inventory.source_lines),
        "TEST_FILE_COUNT": _format_count(inventory.test_files),
        "UNIT_TEST_FILE_COUNT": str(inventory.test_files_by_category.get("unit", 0)),
        "INTEGRATION_TEST_FILE_COUNT": str(
            inventory.test_files_by_category.get("integration", 0)
        ),
        "PERFORMANCE_TEST_FILE_COUNT": str(
            inventory.test_files_by_category.get("performance", 0)
        ),
        "OTHER_TEST_FILE_COUNT": str(inventory.test_files_by_category.get("other", 0)),
        "H3_TEST_FILE_COUNT": str(inventory.h3_test_files),
        "DOCUMENTATION_PAGE_COUNT": str(inventory.documentation_pages),
        "VALIDATOR_FILE_COUNT": str(inventory.validator_files),
        "TEST_TOOLING_FILE_COUNT": str(inventory.test_tooling_files),
        "RESEARCH_COMMIT": inventory.commit,
        "RESEARCH_BRANCH": inventory.branch,
        "RESEARCH_TREE_DIRTY_FILE_COUNT": (
            "unavailable"
            if inventory.dirty_file_count < 0
            else str(inventory.dirty_file_count)
        ),
        "RESEARCH_COMMIT_DATE": inventory.commit_date,
        "RESEARCH_YEAR": (
            inventory.commit_date[:4]
            if inventory.commit_date[:4].isdigit()
            else "unavailable"
        ),
        "MANUSCRIPT_SOURCE_DATE": inventory.manuscript_source_date,
        "MANUSCRIPT_SOURCE_YEAR": _research_year(inventory.manuscript_source_date),
        "RESEARCH_SOURCE_HASH": inventory.source_hash,
        "PYTHON_VERSION": inventory.python_version,
        "FIGURE_COUNT": str(len(specs)),
        "FIGURE_LABELS": ", ".join(spec.label for spec in specs),
        "VERIFICATION_STATUS": verification_summary,
        "VERIFICATION_PASS_COUNT": str(passed),
        "VERIFICATION_FAIL_COUNT": str(failed),
        "VERIFICATION_UNRUN_COUNT": str(unrun),
        "VERIFICATION_DEFINED_COUNT": str(
            len(defined_command_groups(full_validation=full_validation))
        ),
    }
    for module in inventory.focused_modules:
        key = module.name.removeprefix("GEO-INFER-")
        variables[f"{key}_SOURCE_FILE_COUNT"] = str(module.source_files)
        variables[f"{key}_TEST_FILE_COUNT"] = str(module.test_files)
        variables[f"{key}_SOURCE_LINE_COUNT"] = _format_count(module.source_lines)
    for spec in specs:
        token = spec.label.removeprefix("fig:").upper()
        variables[f"{token}_CAPTION"] = spec.caption
    return variables


def substitute_manuscript_text(
    text: str, variables: Mapping[str, str]
) -> tuple[str, tuple[str, ...]]:
    """Resolve uppercase manuscript tokens and return unresolved names."""
    unresolved: set[str] = set()

    def replace(match: re.Match[str]) -> str:
        key = match.group(1)
        if key not in variables:
            unresolved.add(key)
            return match.group(0)
        return str(variables[key])

    return TOKEN_RE.sub(replace, text), tuple(sorted(unresolved))


_CONFIG_OWNED_FIELDS: tuple[tuple[str, str, str], ...] = (
    ("  version: ", "PROJECT_VERSION", "paper.version"),
    ("  date: ", "MANUSCRIPT_SOURCE_DATE", "paper.date"),
    ("  year: ", "MANUSCRIPT_SOURCE_YEAR", "publication.year"),
    ("  license: ", "PROJECT_LICENSE", "metadata.license"),
)


def _manuscript_source_date(root: Path) -> str:
    """Commit date of the last change to anything but the generator-owned config.

    ``manuscript/config.yaml`` is tracked *and* generator-owned: it carries the
    title-page date, derived from git.  Deriving it from ``HEAD`` makes the
    value un-settleable — recording the refreshed file creates a newer commit
    whose date the file no longer holds — so a clean-tree publication build
    could never start.  Excluding the file from its own input reaches a fixed
    point: committing the refreshed config does not move the date it carries.

    ``RESEARCH_COMMIT_DATE`` is unaffected and still reports ``HEAD``, which is
    what section 6.3 quotes beside ``RESEARCH_COMMIT``.
    """
    return _run_git(
        root,
        "log",
        "-1",
        "--format=%cI",
        "--",
        ":/",
        ":(top,exclude)manuscript/config.yaml",
        default="unavailable",
    )


def _research_year(commit_date: str) -> str:
    return commit_date[:4] if commit_date[:4].isdigit() else "unavailable"


def config_metadata_values(root: Path) -> dict[str, str]:
    """Derive the generator-owned ``config.yaml`` values without a full scan.

    ``config.yaml`` is inside the source-hash input set, so it has to be
    written *before* the digest is taken.  These four values are cheap and come
    from the same producers ``build_variables`` uses (``pyproject.toml`` and
    ``git show``), which is what lets ``generate`` cross-check the two.
    """
    metadata = _project_metadata(root)
    source_date = _manuscript_source_date(root)
    return {
        "PROJECT_VERSION": metadata["version"],
        "PROJECT_LICENSE": metadata["license"],
        "MANUSCRIPT_SOURCE_DATE": source_date,
        "MANUSCRIPT_SOURCE_YEAR": _research_year(source_date),
    }


def refresh_config_metadata(
    root: Path, variables: Mapping[str, str], *, dry_run: bool = False
) -> tuple[str, ...]:
    """Write measured metadata into the authored ``manuscript/config.yaml``.

    The render template copies ``config.yaml`` verbatim, so a ``{{TOKEN}}``
    placed there is never substituted and reaches the title page as literal
    text (or, once LaTeX sees the underscores, as mangled math). The template's
    own exemplar therefore keeps literal metadata refreshed by a script. This
    function is that script for GEO-INFER: the values stay measured rather than
    hand-entered, and the file stays verbatim-copyable.

    Args:
        root: Repository root holding ``manuscript/config.yaml``.
        variables: Resolved values keyed by the token each field is owned by.
        dry_run: Report the fields that are stale without writing them.

    Returns:
        The dotted names of the fields that changed (or would change).
    """
    config = root / "manuscript" / "config.yaml"
    if not config.is_file():
        raise FileNotFoundError(config)
    lines = config.read_text(encoding="utf-8").splitlines(keepends=True)
    updated: list[str] = []
    for prefix, key, field in _CONFIG_OWNED_FIELDS:
        if key not in variables:
            raise KeyError(f"config metadata variable is not produced: {key}")
        value = variables[key]
        for index, line in enumerate(lines):
            if not line.startswith(prefix):
                continue
            replacement = f'{prefix}"{value}"  # generator-owned ({key})\n'
            if lines[index] != replacement:
                lines[index] = replacement
                updated.append(field)
            break
        else:
            raise ValueError(f"config.yaml has no line starting with {prefix!r}")
    if updated and not dry_run:
        config.write_text("".join(lines), encoding="utf-8")
    return tuple(updated)


def write_resolved_manuscript(
    root: Path, variables: Mapping[str, str]
) -> tuple[Path, ...]:
    """Write only publication manuscript files with all tokens resolved."""
    source_dir = root / "manuscript"
    output_dir = root / "output" / "manuscript"
    output_dir.mkdir(parents=True, exist_ok=True)
    for stale in output_dir.glob("*.md"):
        stale.unlink()
    for stale in output_dir.glob("*.bib"):
        stale.unlink()
    for filename in ("config.yaml", "preamble.md"):
        stale = output_dir / filename
        if stale.exists():
            stale.unlink()
    written: list[Path] = []
    unresolved: dict[str, tuple[str, ...]] = {}
    for source in sorted(source_dir.glob("*.md")):
        if source.name in EXCLUDED_MANUSCRIPT_DOCS:
            continue
        resolved, missing = substitute_manuscript_text(
            source.read_text(encoding="utf-8"), variables
        )
        if missing:
            unresolved[source.name] = missing
        resolved = resolved.replace("../output/figures/", "../figures/")
        destination = output_dir / source.name
        destination.write_text(resolved, encoding="utf-8")
        written.append(destination)
    for filename in ("config.yaml", "preamble.md"):
        source = source_dir / filename
        if source.is_file():
            resolved, missing = substitute_manuscript_text(
                source.read_text(encoding="utf-8"), variables
            )
            if missing:
                unresolved[source.name] = missing
            (output_dir / filename).write_text(resolved, encoding="utf-8")
    for source in sorted(source_dir.glob("*.bib")):
        shutil.copy2(source, output_dir / source.name)
    if unresolved:
        details = "; ".join(
            f"{name}: {', '.join(keys)}" for name, keys in unresolved.items()
        )
        raise ValueError(f"unresolved manuscript variables: {details}")
    return tuple(written)


BIB_ENTRY_RE = re.compile(r"^@[A-Za-z]+\{\s*([^,\s]+)\s*,", re.MULTILINE)
# A pandoc citation key is introduced by ``@`` at the start of a token, so the
# ``@`` must follow whitespace or a bracket. Without that guard an email
# address in the author block reads as a citation.
CITATION_RE = re.compile(r"(?:^|[\s\[;(])@([A-Za-z][A-Za-z0-9_.:+-]*)", re.MULTILINE)
# pandoc-crossref references share the citation syntax but resolve against
# labels in the document, not against the bibliography.
CROSSREF_PREFIXES = ("fig:", "tbl:", "sec:", "eq:", "lst:")

# ``bibliography.fail_on_missing`` / ``fail_on_unused`` are documented config
# keys that no renderer code reads, so a project could set them and get no
# gate. The generator honours them here, using the same line-oriented read as
# _CONFIG_OWNED_FIELDS so config.yaml stays parseable without a YAML dependency.
_BIBLIOGRAPHY_POLICY: tuple[tuple[str, str, bool], ...] = (
    ("  fail_on_missing: ", "fail_on_missing", True),
    ("  fail_on_unused: ", "fail_on_unused", False),
)


def bibliography_policy(root: Path) -> dict[str, bool]:
    """Read the bibliography gate settings from ``manuscript/config.yaml``."""
    config = root / "manuscript" / "config.yaml"
    text = config.read_text(encoding="utf-8") if config.is_file() else ""
    lines = text.splitlines()
    policy: dict[str, bool] = {}
    for prefix, name, default in _BIBLIOGRAPHY_POLICY:
        policy[name] = default
        for line in lines:
            if line.startswith(prefix):
                policy[name] = line[len(prefix) :].strip().lower() == "true"
                break
    return policy


def audit_bibliography(
    root: Path, manuscript_files: Sequence[Path]
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Compare the reference database against the citations that use it.

    Returns:
        ``(uncited, undefined)`` — bibliography keys that no manuscript file
        cites, and citation keys with no bibliography entry.
    """
    bib = root / "manuscript" / "references.bib"
    if not bib.is_file():
        return (), ()
    entries = set(BIB_ENTRY_RE.findall(bib.read_text(encoding="utf-8")))
    cited: set[str] = set()
    for path in manuscript_files:
        cited.update(CITATION_RE.findall(path.read_text(encoding="utf-8")))
    undefined = {
        key
        for key in cited - entries
        if not key.startswith(CROSSREF_PREFIXES)
    }
    return tuple(sorted(entries - cited)), tuple(sorted(undefined))


def generate(
    root: Path,
    *,
    verify: bool = False,
    full_validation: bool = False,
    allow_dirty: bool = False,
    publication: bool = False,
) -> dict[str, Any]:
    """Generate the complete evidence bundle and resolved manuscript.

    The working-tree dirtiness is measured once, before anything is written,
    so the commit stamp describes the state that was actually measured and the
    generator's own outputs are never counted against it.

    Raises:
        RuntimeError: when the checkout is dirty (or git cannot say) and
            ``allow_dirty`` is not set.  A publication build must not attribute
            uncommitted work to a commit that does not contain it.
    """
    dirty_files = _dirty_file_count(root)
    if dirty_files != 0 and not allow_dirty:
        detail = (
            "git could not report working-tree state"
            if dirty_files < 0
            else f"{dirty_files} uncommitted working-tree entries"
        )
        raise RuntimeError(
            f"refusing to generate from an unclean checkout: {detail}. "
            "Commit the tree, or pass --allow-dirty to stamp the build "
            "'<sha>-dirty' and record the count in "
            "RESEARCH_TREE_DIRTY_FILE_COUNT."
        )
    if publication and not verify:
        raise RuntimeError(
            "a publication build must execute its verification commands; "
            "re-run with --verify or --full-validation"
        )
    # config.yaml is a hashed input, so refresh it before the digest is taken.
    # Writing it afterwards would publish a fingerprint of a tree that no
    # longer exists by the time the run ends.
    refresh_config_metadata(root, config_metadata_values(root))
    inventory = collect_inventory(root, dirty_file_count=dirty_files)
    output = root / "output"
    data_dir = output / "data"
    figures_dir = output / "figures"
    _write_json(data_dir / "research_inventory.json", inventory.to_dict())
    specs = generate_figures(inventory, figures_dir)
    write_figure_registry(figures_dir / "figure_registry.json", specs, inventory)
    verification = (
        run_verification(root, full_validation=full_validation) if verify else ()
    )
    _write_json(
        data_dir / "research_verification.json",
        _verification_payload(verification, full_validation),
    )
    variables = build_variables(
        inventory, specs, verification, full_validation=full_validation
    )
    _write_json(data_dir / "manuscript_variables.json", variables)
    stale_config = refresh_config_metadata(root, variables, dry_run=True)
    if stale_config:
        raise RuntimeError(
            "config.yaml disagrees with the measured variables after the "
            f"pre-scan refresh: {', '.join(stale_config)}"
        )
    written = write_resolved_manuscript(root, variables)
    uncited, undefined = audit_bibliography(root, written)
    policy = bibliography_policy(root)
    if undefined and policy["fail_on_missing"]:
        raise ValueError(
            "citations with no bibliography entry: " + ", ".join(undefined)
        )
    if uncited:
        message = (
            "bibliography entries are never cited: " + ", ".join(uncited)
        )
        if policy["fail_on_unused"]:
            raise ValueError(message)
        print(f"warning: {message}", file=sys.stderr)
    manifest = {
        "schema_version": RESEARCH_SCHEMA,
        "source_commit": inventory.commit,
        "dirty_file_count": inventory.dirty_file_count,
        "source_hash": inventory.source_hash,
        "resolved_manuscript_files": [
            path.relative_to(root).as_posix() for path in written
        ],
        "figure_registry": "output/figures/figure_registry.json",
        "variables": "output/data/manuscript_variables.json",
        "verification": "output/data/research_verification.json",
    }
    _write_json(data_dir / "research_manifest.json", manifest)
    if publication and not verification:
        raise RuntimeError(
            "refusing to publish an empty evidence record: "
            f"{len(defined_command_groups(full_validation=full_validation))} "
            "verification command groups are defined and none ran"
        )
    if verify:
        failures = [result for result in verification if result.status != "passed"]
        if failures:
            raise RuntimeError(
                "research verification failed: "
                + ", ".join(result.name for result in failures)
            )
    return manifest


def check_published_artifacts(root: Path) -> tuple[str, ...]:
    """Return every reason the published artifacts no longer describe the tree.

    Two comparisons, both of which were missing.

    ``RESEARCH_SOURCE_HASH`` is computed on every run and published in four
    places, but nothing ever compared it to anything: a render that skipped
    regeneration would republish stale counts and exit 0.

    ``manuscript/config.yaml`` supplies the title page and is generator-owned.
    It is checked against the *published variables*, not against a fresh read
    of ``HEAD``: the file is tracked, so the commit that records it is always
    newer than the commit date it holds, and comparing to ``HEAD`` could never
    pass.  What must hold — and what the published PDF depends on — is that the
    title page and the evidence bundle shipped beside it describe the same
    build.

    Returns:
        Every reason the artifacts are stale.  An empty tuple is the only
        passing answer.
    """
    problems: list[str] = []
    variables_path = root / "output" / "data" / "manuscript_variables.json"
    if not variables_path.is_file():
        return (
            f"no published variables at {variables_path.relative_to(root).as_posix()}",
        )
    try:
        published = json.loads(variables_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return (f"published variables are unreadable: {exc}",)
    measured = _source_hash(root)
    if published.get("RESEARCH_SOURCE_HASH") != measured:
        problems.append(
            "RESEARCH_SOURCE_HASH is stale: published "
            f"{published.get('RESEARCH_SOURCE_HASH')!r}, measured {measured!r}"
        )
    missing = [key for _prefix, key, _field in _CONFIG_OWNED_FIELDS if key not in published]
    if missing:
        problems.append(
            "published variables omit config metadata: " + ", ".join(missing)
        )
    else:
        problems.extend(
            f"manuscript/config.yaml disagrees with the published build: {field}"
            for field in refresh_config_metadata(root, published, dry_run=True)
        )
    return tuple(problems)


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[1]
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="run strict research verification commands",
    )
    parser.add_argument(
        "--full-validation",
        action="store_true",
        help="also run the full unit, integration, performance, and H3 suites",
    )
    parser.add_argument(
        "--publication",
        action="store_true",
        help=(
            "refuse to produce a build whose evidence record is empty; implies "
            "that verification must have been requested and produced results"
        ),
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help=(
            "write nothing; exit non-zero when the published source hash or "
            "the generator-owned config.yaml metadata no longer match the tree"
        ),
    )
    parser.add_argument(
        "--allow-dirty",
        action="store_true",
        help=(
            "generate from an unclean checkout; the build is stamped "
            "'<sha>-dirty' and the uncommitted entry count is published"
        ),
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    root = args.root.resolve()
    if args.check:
        problems = check_published_artifacts(root)
        for problem in problems:
            print(f"stale manuscript artifact: {problem}", file=sys.stderr)
        if problems:
            return 1
        print("manuscript artifacts match the current tree")
        return 0
    try:
        manifest = generate(
            root,
            verify=args.verify or args.full_validation,
            full_validation=args.full_validation,
            allow_dirty=args.allow_dirty,
            publication=args.publication,
        )
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"research artifact generation failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
