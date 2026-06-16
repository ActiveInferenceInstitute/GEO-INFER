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
import subprocess
import sys
import tomllib
from dataclasses import dataclass, field
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
EXPECTED_MODULE_COUNT = 44
SIGNPOST_FILES = ("README.md", "AGENTS.md", "SKILL.md")
MIN_TEST_FILES_PER_MODULE = 4
CANONICAL_UV_SYNC_COMMAND = "uv sync --all-packages --all-extras"
CANONICAL_UV_DOC_FILES = (
    "README.md",
    "AGENTS.md",
    "SKILL.md",
    "GEO-INFER-TEST/README.md",
    "GEO-INFER-TEST/AGENTS.md",
)
SOURCE_LANGUAGE_PATTERN = re.compile(
    r"\b(mock|stub|fake|placeholder)\b|NotImplementedError",
    re.IGNORECASE,
)
TASK_MARKER_PATTERN = re.compile(r"\b(TODO|FIXME|XXX|HACK|TBD)\b")
TASK_MARKER_SCAN_GLOBS = (
    "GEO-INFER-*/src/**/*.py",
    "GEO-INFER-*/tests/**/*.py",
)
PYTHON_VERSION_PIN_PATTERN = re.compile(r"^3\.(11|12)(?:\.\d+)?$")
LOGGING_BASIC_CONFIG_ATTR = "basicConfig"
SOURCE_LANGUAGE_ALLOWLIST = (
    "placeholder=",
    "Subclasses must implement",
    "Must be implemented by subclasses",
    "If not implemented in subclass",
    "If requested optimization is not supported",
    "abstract",
    "not supported",
    "not available",
    "for testing",
    "fake data",
)
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
INTERNAL_REQUIREMENT_NAMES = {
    "adapters",
    "agent-base",
    "algorithms",
    "analysis",
    "api",
    "applications",
    "base",
    "bayesian",
    "bayesian-network",
    "bayesian-timeseries",
    "behavioral-economics",
    "bioregional",
    "bioregional-governance",
    "bioregional-markets",
    "catastrophe-models",
    "claim-models",
    "claims-processing",
    "cloud",
    "cognitive-engine",
    "cognitive-models",
    "cognitive-security",
    "compliance-status",
    "compliance-tracking",
    "config",
    "contrasts",
    "core",
    "crm",
    "crm-endpoints",
    "crm-models",
    "crm-reports",
    "crm-visuals",
    "data-integration",
    "data-io",
    "data-loader",
    "data-models",
    "data-processing",
    "database",
    "delivery",
    "diagnostics",
    "digital-security",
    "digital-stigmergy",
    "dirichlet-process",
    "disaster",
    "dynamic-spatial",
    "economic-api",
    "econometrics-engine",
    "ecological-economics",
    "ecosystem-services",
    "endpoints",
    "environmental",
    "error-handling",
    "file",
    "generic-report-generator",
    "geospatial-utils",
    "github-api",
    "glm",
    "growth-models",
    "hazard-model",
    "helpers",
    "hierarchical",
    "hmc",
    "hr",
    "hr-endpoints",
    "hr-models",
    "hr-reports",
    "hr-visuals",
    "importer",
    "indicators",
    "inference",
    "integration-models",
    "legal-entity",
    "legal-frameworks",
    "likelihoods",
    "log-integration",
    "market-structure",
    "metrics",
    "microeconomics",
    "model-comparison",
    "model-validation",
    "modeling-engine",
    "models",
    "monitoring",
    "multilevel",
    "normative-inference",
    "patterns",
    "pep-engine",
    "physical-security",
    "policy",
    "policy-engine",
    "policy-impact",
    "posterior",
    "priors",
    "processor",
    "producer-theory",
    "pymc-interface",
    "registry",
    "regulation",
    "risk-assessment",
    "risk-engine",
    "risk-models",
    "routing",
    "smc",
    "space-integration",
    "spatial-analysis",
    "spatial-causal",
    "spatial-clustering",
    "spatial-ecology",
    "spatial-gp",
    "spatial-language",
    "spatial-memory",
    "spatial-perception",
    "spatial-reasoning",
    "spatial-regression",
    "spatiotemporal-gp",
    "stan-interface",
    "support",
    "supply-chain",
    "sustainability-metrics",
    "talent",
    "talent-endpoints",
    "talent-models",
    "talent-reports",
    "talent-visuals",
    "test-discoverer",
    "test-orchestrator",
    "test-runner",
    "tfp-interface",
    "time-integration",
    "transport",
    "underwriting-models",
    "underwriting-rules",
    "user-profiles",
    "utils",
    "validation",
    "validator",
    "variational",
    "visualization",
    "visualizations",
    "zoning",
    "zoning-analysis",
}
MARKDOWN_LINK_PATTERN = re.compile(r"!?\[[^\]]+\]\(([^)]+)\)")
LEGACY_PYTHON_METADATA_PATTERN = re.compile(
    r"Programming Language :: Python :: 3\.(8|9|10)"
    r"|python_requires\s*=\s*[\"']>=3\.(8|9|10)[\"']"
    r"|requires-python\s*=\s*[\"']>=3\.(8|9|10)[\"']"
)
LEGACY_H3_PATTERN = re.compile(r"\bh3\s*>=\s*3\.", re.IGNORECASE)


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


def validate_uv_environment(report: ContractReport) -> None:
    """Validate the root uv workspace and Python version pin."""
    root_pyproject = REPO_ROOT / "pyproject.toml"
    if not root_pyproject.exists():
        report.error("Root pyproject.toml is required for uv workspace resolution")
        return

    try:
        root_config = tomllib.loads(root_pyproject.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as exc:
        report.error(f"Root pyproject.toml is invalid: {exc}")
        return

    requires_python = root_config.get("project", {}).get("requires-python")
    if requires_python != ">=3.11":
        report.error(
            "Root pyproject.toml must declare project.requires-python = '>=3.11'"
        )

    workspace_members = (
        root_config.get("tool", {})
        .get("uv", {})
        .get("workspace", {})
        .get("members")
    )
    if workspace_members != ["GEO-INFER-*"]:
        report.error("Root [tool.uv.workspace].members must be ['GEO-INFER-*']")

    if not (REPO_ROOT / "uv.lock").exists():
        report.error("Root uv.lock is required; do not rely on module-local locks")

    python_version_file = REPO_ROOT / ".python-version"
    if not python_version_file.exists():
        report.error("Root .python-version is required for reproducible uv runs")
        return
    python_version = python_version_file.read_text(encoding="utf-8").strip()
    if not PYTHON_VERSION_PIN_PATTERN.match(python_version):
        report.error(
            f".python-version must pin Python 3.11 or 3.12, got {python_version!r}"
        )


def validate_uv_setup_documentation(report: ContractReport) -> None:
    """Ensure signposts advertise the workspace-wide uv sync command."""
    for relative_path in CANONICAL_UV_DOC_FILES:
        doc_path = REPO_ROOT / relative_path
        if not doc_path.exists():
            report.error(f"{relative_path}: missing uv setup signpost")
            continue
        doc_text = doc_path.read_text(encoding="utf-8", errors="ignore")
        if CANONICAL_UV_SYNC_COMMAND not in doc_text:
            report.error(
                f"{relative_path}: must document `{CANONICAL_UV_SYNC_COMMAND}`"
            )


def validate_test_inventory(module_dirs: list[Path], report: ContractReport) -> None:
    """Ensure every module keeps a minimally useful local pytest surface."""
    for module_dir in module_dirs:
        tests_dir = module_dir / "tests"
        if not tests_dir.exists():
            report.error(f"{module_dir.name}: missing tests/")
            continue
        test_files = {
            *tests_dir.rglob("test_*.py"),
            *tests_dir.rglob("*_test.py"),
        }
        if len(test_files) < MIN_TEST_FILES_PER_MODULE:
            report.error(
                f"{module_dir.name}: expected at least "
                f"{MIN_TEST_FILES_PER_MODULE} test files, found {len(test_files)}"
            )


def validate_module_task_markers(report: ContractReport) -> None:
    """Keep actionable planning markers out of source and tests."""
    hits: list[str] = []
    scan_files = {
        path
        for pattern in TASK_MARKER_SCAN_GLOBS
        for path in REPO_ROOT.glob(pattern)
        if path.is_file()
    }
    for source_file in sorted(scan_files):
        text = source_file.read_text(encoding="utf-8", errors="ignore")
        for lineno, line in enumerate(text.splitlines(), start=1):
            if TASK_MARKER_PATTERN.search(line):
                hits.append(
                    f"{source_file.relative_to(REPO_ROOT)}:{lineno}: {line.strip()}"
                )

    if hits:
        report.error(
            "Module-local task markers found; track planned work in root TODO.md "
            "or issues. First hits: "
            + "; ".join(hits[:8])
        )


def validate_logging_configuration(report: ContractReport) -> None:
    """Library imports should not configure process-wide logging."""
    hits: list[str] = []
    for source_file in sorted(REPO_ROOT.glob("GEO-INFER-*/src/**/*.py")):
        text = source_file.read_text(encoding="utf-8", errors="ignore")
        try:
            tree = ast.parse(text, filename=str(source_file))
        except SyntaxError:
            continue

        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                continue
            if isinstance(node, ast.If) and is_main_guard(node.test):
                continue
            for child in ast.walk(node):
                if is_logging_basic_config_call(child):
                    line = text.splitlines()[child.lineno - 1].strip()
                    hits.append(
                        f"{source_file.relative_to(REPO_ROOT)}:{child.lineno}: {line}"
                    )

    if hits:
        report.error(
            "Importable library code must not call logging.basicConfig() at import "
            "time. Configure handlers only in explicit setup functions or CLI "
            "entrypoints. First hits: "
            + "; ".join(hits[:8])
        )


def is_logging_basic_config_call(node: ast.AST) -> bool:
    if not isinstance(node, ast.Call):
        return False
    func = node.func
    return (
        isinstance(func, ast.Attribute)
        and func.attr == LOGGING_BASIC_CONFIG_ATTR
        and isinstance(func.value, ast.Name)
        and func.value.id == "logging"
    )


def is_main_guard(node: ast.AST) -> bool:
    if not isinstance(node, ast.Compare) or len(node.ops) != 1 or len(node.comparators) != 1:
        return False
    if not isinstance(node.ops[0], ast.Eq):
        return False
    left = node.left
    right = node.comparators[0]
    return (
        isinstance(left, ast.Name)
        and left.id == "__name__"
        and isinstance(right, ast.Constant)
        and right.value == "__main__"
    ) or (
        isinstance(right, ast.Name)
        and right.id == "__name__"
        and isinstance(left, ast.Constant)
        and left.value == "__main__"
    )


def validate_setup_syntax(module_dirs: list[Path], report: ContractReport) -> None:
    for setup_py in sorted(module_dir / "setup.py" for module_dir in module_dirs):
        if not setup_py.exists():
            continue
        try:
            ast.parse(setup_py.read_text(encoding="utf-8"), filename=str(setup_py))
        except SyntaxError as exc:
            report.error(f"{setup_py.relative_to(REPO_ROOT)}: syntax error: {exc}")


def validate_python_source_syntax(report: ContractReport) -> None:
    """Fail fast on any syntax errors in module source and examples."""
    source_files = [
        *REPO_ROOT.glob("GEO-INFER-*/src/**/*.py"),
        *REPO_ROOT.glob("GEO-INFER-*/examples/**/*.py"),
    ]

    for source_file in sorted(source_files):
        if not source_file.is_file():
            continue
        try:
            compile(
                source_file.read_text(encoding="utf-8"),
                filename=str(source_file),
                mode="exec",
            )
        except SyntaxError as exc:
            line = exc.text.strip() if exc.text else "n/a"
            report.error(
                f"{source_file.relative_to(REPO_ROOT)}:{exc.lineno}:{exc.offset}: "
                f"{exc.msg} ({line})"
            )
            return
        except UnicodeDecodeError as exc:
            report.error(
                f"{source_file.relative_to(REPO_ROOT)}: decoding error: {exc.reason}"
            )
            return


def validate_runtime_metadata(module_dirs: list[Path], report: ContractReport) -> None:
    metadata_files = [
        REPO_ROOT / "pyproject.toml",
        *REPO_ROOT.glob("GEO-INFER-*/**/pyproject.toml"),
        *REPO_ROOT.glob("GEO-INFER-*/**/setup.py"),
    ]

    for metadata_file in sorted(set(metadata_files)):
        text = metadata_file.read_text(encoding="utf-8", errors="ignore")
        for lineno, line in enumerate(text.splitlines(), start=1):
            if LEGACY_PYTHON_METADATA_PATTERN.search(line):
                report.error(
                    f"{metadata_file.relative_to(REPO_ROOT)}:{lineno}: "
                    "metadata advertises Python < 3.11"
                )


def validate_h3_dependency_metadata(report: ContractReport) -> None:
    metadata_files = [
        *REPO_ROOT.glob("GEO-INFER-*/pyproject.toml"),
        *REPO_ROOT.glob("GEO-INFER-*/setup.py"),
        *REPO_ROOT.glob("GEO-INFER-*/requirements*.txt"),
        *REPO_ROOT.glob("GEO-INFER-*/locations/*/requirements*.txt"),
        REPO_ROOT / "pyproject.toml",
    ]
    for metadata_file in sorted(path for path in metadata_files if path.exists()):
        text = metadata_file.read_text(encoding="utf-8", errors="ignore")
        for lineno, line in enumerate(text.splitlines(), start=1):
            if LEGACY_H3_PATTERN.search(line):
                report.error(
                    f"{metadata_file.relative_to(REPO_ROOT)}:{lineno}: "
                    "H3 dependency must use H3 v4 API support (h3>=4.0.0)"
                )


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


def requirement_name(requirement: str) -> str:
    cleaned = requirement.split("#", 1)[0].split(";", 1)[0].strip()
    for token in ("==", ">=", "<=", "~=", "!=", ">", "<"):
        cleaned = cleaned.split(token, 1)[0]
    return cleaned.split("[", 1)[0].strip().replace("_", "-").lower()


def validate_requirements_files(report: ContractReport) -> None:
    for requirements_file in sorted(REPO_ROOT.glob("GEO-INFER-*/requirements*.txt")):
        for lineno, line in enumerate(
            requirements_file.read_text(encoding="utf-8", errors="ignore").splitlines(),
            start=1,
        ):
            stripped = line.strip()
            if not stripped or stripped.startswith(("#", "-")):
                continue
            name = requirement_name(stripped)
            if not name:
                continue
            normalized = name.replace("-", "_")
            if normalized in STDLIB_REQUIREMENT_NAMES:
                report.error(
                    f"{requirements_file.relative_to(REPO_ROOT)}:{lineno}: "
                    f"stdlib module listed as dependency: {stripped}"
                )
            if stripped.endswith(">=0.0.0") and name in INTERNAL_REQUIREMENT_NAMES:
                report.error(
                    f"{requirements_file.relative_to(REPO_ROOT)}:{lineno}: "
                    f"internal/local module listed as PyPI dependency: {stripped}"
                )


def validate_markdown_local_links(report: ContractReport) -> None:
    for markdown_file in sorted(
        path
        for pattern in ("README.md", "AGENTS.md")
        for path in REPO_ROOT.glob(f"**/{pattern}")
        if not {
            ".git",
            ".pytest_cache",
            ".venv",
            "__pycache__",
            ".geo-infer-test-results",
        }.intersection(path.parts)
    ):
        text = markdown_file.read_text(encoding="utf-8", errors="ignore")
        for match in MARKDOWN_LINK_PATTERN.finditer(text):
            target = match.group(1).strip()
            if (
                not target
                or target.startswith(("#", "http://", "https://", "mailto:"))
                or target.startswith("app://")
                or target.startswith("/")
            ):
                continue
            target_path = target.split("#", 1)[0].strip("<>")
            if not target_path:
                continue
            candidate = (markdown_file.parent / target_path).resolve()
            try:
                candidate.relative_to(REPO_ROOT)
            except ValueError:
                report.error(
                    f"{markdown_file.relative_to(REPO_ROOT)}: link escapes repo: {target}"
                )
                continue
            if not candidate.exists():
                report.error(
                    f"{markdown_file.relative_to(REPO_ROOT)}: broken local link: {target}"
                )


def validate_runner_documentation(report: ContractReport) -> None:
    runner = REPO_ROOT / "GEO-INFER-TEST" / "run_unified_tests.py"
    readme = REPO_ROOT / "README.md"
    runner_text = runner.read_text(encoding="utf-8", errors="ignore")
    readme_text = readme.read_text(encoding="utf-8", errors="ignore")
    for flag in ("--module", "--category", "--h3-migration"):
        if flag in readme_text and flag not in runner_text:
            report.error(f"README documents {flag}, but run_unified_tests.py lacks it")


def validate_generated_artifacts(report: ContractReport) -> None:
    root_logs = REPO_ROOT / "logs"
    if root_logs.exists():
        report.error(
            "Root logs/ exists; imports and validators must not create log files"
        )

    try:
        status = subprocess.run(
            ["git", "status", "--short", "--", "logs", ".geo-infer-test-results"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
    except OSError:
        return

    generated_lines = [line for line in status.stdout.splitlines() if line.strip()]
    if generated_lines:
        report.error(
            "Generated artifact churn detected: " + "; ".join(generated_lines[:8])
        )


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
    validate_uv_environment(report)
    validate_uv_setup_documentation(report)
    validate_test_inventory(module_dirs, report)
    validate_setup_syntax(module_dirs, report)
    validate_python_source_syntax(report)
    validate_runtime_metadata(module_dirs, report)
    validate_h3_dependency_metadata(report)
    validate_requirements_files(report)
    validate_markdown_local_links(report)
    validate_runner_documentation(report)
    validate_generated_artifacts(report)
    validate_module_task_markers(report)
    validate_logging_configuration(report)
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
