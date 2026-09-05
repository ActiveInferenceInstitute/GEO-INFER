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
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

TOKEN_RE = re.compile(r"\{\{([A-Z][A-Z0-9_]*)\}\}")
EXCLUDED_MANUSCRIPT_DOCS = frozenset({"README.md", "AGENTS.md", "SYNTAX.md"})
FIGURE_SCHEMA = "geo-infer-manuscript-figures/v1"
RESEARCH_SCHEMA = "geo-infer-manuscript-evidence/v1"
FOCUS_MODULES = ("GEO-INFER-ACT", "GEO-INFER-BAYES", "GEO-INFER-RISK")


@dataclass(frozen=True)
class ModuleMetrics:
    """Measured implementation and test surfaces for one module."""

    name: str
    source_files: int
    source_lines: int
    test_files: int
    tests_by_category: dict[str, int]


@dataclass(frozen=True)
class FigureSpec:
    """Publication figure metadata generated with the corresponding image."""

    label: str
    filename: str
    caption: str
    generated_by: str
    alt_text: str


@dataclass(frozen=True)
class RepositoryInventory:
    """Deterministic repository measurements used by the manuscript."""

    project_version: str
    project_license: str
    commit: str
    branch: str
    commit_date: str
    source_hash: str
    modules: tuple[ModuleMetrics, ...]
    test_files_by_category: dict[str, int]
    documentation_pages: int
    validator_files: int
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
            "source_hash": self.source_hash,
            "modules": [asdict(module) for module in self.modules],
            "test_files_by_category": dict(self.test_files_by_category),
            "documentation_pages": self.documentation_pages,
            "validator_files": self.validator_files,
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


def _test_category(path: Path) -> str:
    parts = {part.lower() for part in path.parts}
    for category in ("unit", "integration", "performance"):
        if category in parts:
            return category
    if "h3" in path.name.lower() or "h3" in path.parent.name.lower():
        return "h3"
    return "other"


def collect_inventory(root: Path) -> RepositoryInventory:
    """Measure the current checkout without importing application modules."""
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
    validator_files = len(
        tuple(path for path in (root / "GEO-INFER-TEST").glob("*.py") if path.is_file())
    )
    project_metadata = _project_metadata(root)
    return RepositoryInventory(
        project_version=project_metadata["version"],
        project_license=project_metadata["license"],
        commit=_run_git(root, "rev-parse", "--short", "HEAD"),
        branch=_run_git(root, "branch", "--show-current"),
        commit_date=_run_git(root, "show", "-s", "--format=%cI", default="unavailable"),
        source_hash=_source_hash(root),
        modules=tuple(modules),
        test_files_by_category=dict(sorted(category_counts.items())),
        documentation_pages=documentation_pages,
        validator_files=validator_files,
        source_files=len(source_files),
        source_lines=sum(_nonempty_lines(path) for path in source_files),
        test_files=len(all_tests),
        python_version=platform.python_version(),
    )


def _format_count(value: int) -> str:
    return f"{value:,}"


def _caption_module_inventory(inventory: RepositoryInventory) -> str:
    return (
        f"Repository-derived inventory of {inventory.module_count} importable GEO-INFER modules at "
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


def _save_figure(fig: Any, path: Path, caption: str, source_hash: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(
        path,
        dpi=220,
        bbox_inches="tight",
        metadata={
            "Title": path.stem.replace("_", " ").title(),
            "Description": caption,
            "Source": f"GEO-INFER repository source hash {source_hash}",
        },
    )


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
            "font.size": 8.5,
            "axes.titleweight": "bold",
        }
    ):
        fig, axes = plt.subplots(
            1, 2, figsize=(13, max(8, len(labels) * 0.24)), sharey=True
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
            "GEO-INFER module evidence inventory", fontsize=13, fontweight="bold"
        )
        fig.tight_layout()
        _save_figure(
            fig, output_dir / specs[0].filename, specs[0].caption, inventory.source_hash
        )
        plt.close(fig)

        focus = inventory.focused_modules
        focus_labels = [item.name.removeprefix("GEO-INFER-") for item in focus]
        focus_source = [item.source_files for item in focus]
        focus_tests = [item.test_files for item in focus]
        fig, ax = plt.subplots(figsize=(8.5, 5.5))
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
        _save_figure(
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
        fig, axes = plt.subplots(1, 2, figsize=(10, 5.5))
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
            "Validation and documentation evidence", fontsize=13, fontweight="bold"
        )
        fig.tight_layout()
        _save_figure(
            fig, output_dir / specs[2].filename, specs[2].caption, inventory.source_hash
        )
        plt.close(fig)
    return specs


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


def _verification_summary(
    results: Sequence[VerificationResult],
) -> tuple[str, int, int, int]:
    passed = sum(result.status == "passed" for result in results)
    failed = sum(result.status == "failed" for result in results)
    unrun = sum(result.status == "not-run" for result in results)
    if not results:
        return "not run", passed, failed, 1
    if failed:
        return f"{passed} passed, {failed} failed", passed, failed, unrun
    return f"{passed} passed", passed, failed, unrun


def build_variables(
    inventory: RepositoryInventory,
    specs: Sequence[FigureSpec],
    verification: Sequence[VerificationResult],
) -> dict[str, str]:
    """Return every manuscript replacement from measured inputs."""
    verification_summary, passed, failed, unrun = _verification_summary(verification)
    variables: dict[str, str] = {
        "PROJECT_VERSION": inventory.project_version,
        "PROJECT_LICENSE": inventory.project_license,
        "MODULE_COUNT": str(inventory.module_count),
        "MODULE_NAMES": ", ".join(module.name for module in inventory.modules),
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
        "H3_TEST_FILE_COUNT": str(inventory.test_files_by_category.get("h3", 0)),
        "DOCUMENTATION_PAGE_COUNT": str(inventory.documentation_pages),
        "VALIDATOR_FILE_COUNT": str(inventory.validator_files),
        "RESEARCH_COMMIT": inventory.commit,
        "RESEARCH_BRANCH": inventory.branch,
        "RESEARCH_COMMIT_DATE": inventory.commit_date,
        "RESEARCH_YEAR": (
            inventory.commit_date[:4]
            if inventory.commit_date[:4].isdigit()
            else "unavailable"
        ),
        "RESEARCH_SOURCE_HASH": inventory.source_hash,
        "PYTHON_VERSION": inventory.python_version,
        "FIGURE_COUNT": str(len(specs)),
        "FIGURE_LABELS": ", ".join(spec.label for spec in specs),
        "VERIFICATION_STATUS": verification_summary,
        "VERIFICATION_PASS_COUNT": str(passed),
        "VERIFICATION_FAIL_COUNT": str(failed),
        "VERIFICATION_UNRUN_COUNT": str(unrun),
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
    ("  date: ", "RESEARCH_COMMIT_DATE", "paper.date"),
    ("  year: ", "RESEARCH_YEAR", "publication.year"),
    ("  license: ", "PROJECT_LICENSE", "metadata.license"),
)


def refresh_config_metadata(root: Path, variables: Mapping[str, str]) -> tuple[str, ...]:
    """Write measured metadata into the authored ``manuscript/config.yaml``.

    The render template copies ``config.yaml`` verbatim, so a ``{{TOKEN}}``
    placed there is never substituted and reaches the title page as literal
    text (or, once LaTeX sees the underscores, as mangled math). The template's
    own exemplar therefore keeps literal metadata refreshed by a script. This
    function is that script for GEO-INFER: the values stay measured rather than
    hand-entered, and the file stays verbatim-copyable.
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


def generate(
    root: Path, *, verify: bool = False, full_validation: bool = False
) -> dict[str, Any]:
    """Generate the complete evidence bundle and resolved manuscript."""
    inventory = collect_inventory(root)
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
    variables = build_variables(inventory, specs, verification)
    _write_json(data_dir / "manuscript_variables.json", variables)
    refresh_config_metadata(root, variables)
    written = write_resolved_manuscript(root, variables)
    manifest = {
        "schema_version": RESEARCH_SCHEMA,
        "source_commit": inventory.commit,
        "source_hash": inventory.source_hash,
        "resolved_manuscript_files": [
            path.relative_to(root).as_posix() for path in written
        ],
        "figure_registry": "output/figures/figure_registry.json",
        "variables": "output/data/manuscript_variables.json",
        "verification": "output/data/research_verification.json",
    }
    _write_json(data_dir / "research_manifest.json", manifest)
    if verify:
        failures = [result for result in verification if result.status != "passed"]
        if failures:
            raise RuntimeError(
                "research verification failed: "
                + ", ".join(result.name for result in failures)
            )
    return manifest


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
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    root = args.root.resolve()
    try:
        manifest = generate(
            root,
            verify=args.verify or args.full_validation,
            full_validation=args.full_validation,
        )
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"research artifact generation failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
