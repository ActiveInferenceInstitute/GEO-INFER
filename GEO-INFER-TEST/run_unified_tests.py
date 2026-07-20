#!/usr/bin/env python3
"""Run GEO-INFER test and validation suites.

The runner intentionally mirrors the commands documented in the root README:

* ``--module NAME`` runs one module's tests.
* ``--category unit|integration|performance|coverage`` runs a focused suite.
* ``--h3-migration`` runs the H3/Active Inference contract validators.

With no arguments, the runner executes the same broad module sweep that older
versions performed.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODULE_PREFIX = "GEO-INFER-"
TEST_DIR_NAME = "tests"
RESULTS_DIR = PROJECT_ROOT / ".geo-infer-test-results"
PYTEST_NO_TESTS_EXIT_CODE = 5
TEST_FILE_PATTERNS = ("test_*.py", "*_test.py")


@dataclass
class CommandResult:
    name: str
    success: bool
    duration: float
    command: list[str]
    stdout: str = ""
    stderr: str = ""


@dataclass
class Module:
    name: str
    path: Path
    test_path: Path
    has_tests: bool


@dataclass
class SuiteReport:
    results: list[CommandResult] = field(default_factory=list)

    def add(self, result: CommandResult) -> None:
        self.results.append(result)

    @property
    def success(self) -> bool:
        return all(result.success for result in self.results)


def discover_geo_infer_modules() -> list[Module]:
    """Discover all top-level GEO-INFER modules in stable order."""
    modules: list[Module] = []
    for item in sorted(PROJECT_ROOT.iterdir()):
        if not item.is_dir() or not item.name.startswith(MODULE_PREFIX):
            continue
        test_path = item / TEST_DIR_NAME
        modules.append(
            Module(
                name=item.name.removeprefix(MODULE_PREFIX),
                path=item,
                test_path=test_path,
                has_tests=has_test_files(test_path),
            )
        )
    return modules


def ensure_results_dir(clean: bool = False) -> None:
    RESULTS_DIR.mkdir(exist_ok=True)
    if not clean:
        return
    for path in RESULTS_DIR.iterdir():
        if path.is_symlink() or path.is_file():
            path.unlink()
        elif path.is_dir():
            shutil.rmtree(path)


def workspace_src_paths() -> list[Path]:
    """Return all workspace source directories in deterministic order."""
    return [
        module.path / "src"
        for module in discover_geo_infer_modules()
        if (module.path / "src").exists()
    ]


def build_subprocess_env() -> dict[str, str]:
    """Build the child-process environment used for pytest subprocesses."""
    env = os.environ.copy()
    pythonpath_parts = [str(path) for path in workspace_src_paths()]
    existing_pythonpath = env.get("PYTHONPATH")
    if existing_pythonpath:
        pythonpath_parts.extend(
            part for part in existing_pythonpath.split(os.pathsep) if part
        )
    env["PYTHONPATH"] = os.pathsep.join(dict.fromkeys(pythonpath_parts))
    return env


def junit_path(command: list[str]) -> Path | None:
    """Return the JUnit path embedded in a pytest command, if present."""
    prefix = "--junitxml="
    for argument in command:
        if argument.startswith(prefix):
            return Path(argument.removeprefix(prefix))
    return None


def junit_contract_errors(path: Path | None) -> list[str]:
    """Reject skipped, xfailed, and xpassed entries in a JUnit report."""
    if path is None or not path.exists():
        return []
    root = ET.parse(path).getroot()
    errors: list[str] = []
    for testcase in root.iter("testcase"):
        skipped = testcase.find("skipped")
        if skipped is not None:
            name = (
                testcase.attrib.get("classname", "")
                + "::"
                + testcase.attrib.get("name", "")
            )
            reason = skipped.attrib.get("message", "") or (skipped.text or "")
            errors.append(f"forbidden skipped/xfail testcase {name}: {reason}")
    return errors


def run_command(
    command: list[str],
    name: str,
    timeout: int,
    cwd: Path = PROJECT_ROOT,
) -> CommandResult:
    """Run a subprocess and capture a compact result."""
    print(f"\n== {name}")
    print("$ " + " ".join(command))
    started = time.time()
    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            env=build_subprocess_env(),
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        duration = time.time() - started
        print(f"TIMEOUT after {duration:.2f}s")
        return CommandResult(
            name=name,
            success=False,
            duration=duration,
            command=command,
            stdout=exc.stdout or "",
            stderr=exc.stderr or f"Timed out after {timeout}s",
        )

    duration = time.time() - started
    junit_errors = junit_contract_errors(junit_path(command))
    if completed.returncode == PYTEST_NO_TESTS_EXIT_CODE:
        junit_errors.append("pytest collected no tests (exit code 5)")
    if junit_errors:
        completed.stderr = "\n".join((*filter(None, [completed.stderr]), *junit_errors))
    success = completed.returncode == 0 and not junit_errors
    outcome = "PASS" if success else "FAIL"
    print(f"{outcome} in {duration:.2f}s")
    if not success:
        failure_output = "\n".join(
            part[-4000:] for part in (completed.stdout, completed.stderr) if part
        )
        if failure_output:
            print(failure_output)

    return CommandResult(
        name=name,
        success=success,
        duration=duration,
        command=command,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )


def module_by_name(name: str) -> Module:
    wanted = name.upper().removeprefix(MODULE_PREFIX)
    for module in discover_geo_infer_modules():
        if module.name.upper() == wanted:
            return module
    known = ", ".join(module.name for module in discover_geo_infer_modules())
    raise SystemExit(f"Unknown module {name!r}. Known modules: {known}")


def pytest_base_args() -> list[str]:
    return [
        sys.executable,
        "-m",
        "pytest",
        "-c",
        str(PROJECT_ROOT / "pyproject.toml"),
        "-v",
        "--tb=short",
        "--durations=10",
        "-W",
        "error",
    ]


def test_file_paths(path: Path, *, recursive: bool = True) -> list[Path]:
    """Return deterministic pytest file paths below *path*.

    Keeping file discovery in one helper prevents the module, category, and
    performance runners from silently diverging as legacy test layouts are
    migrated.
    """
    if not path.is_dir():
        return []
    glob = path.rglob if recursive else path.glob
    return sorted(
        {
            candidate
            for pattern in TEST_FILE_PATTERNS
            for candidate in glob(pattern)
            if candidate.is_file()
        }
    )


def has_test_files(path: Path) -> bool:
    """Return true when a directory contains pytest-discoverable test files."""
    return bool(test_file_paths(path))


def category_test_paths(module: Module, category: str) -> list[Path]:
    """Resolve a module's test files for one canonical category.

    Unit tests in older modules may live directly under ``tests/``.  Only the
    unit category receives that compatibility fallback; integration and
    performance remain bounded by their named directories.
    """
    category_path = module.test_path / category
    paths = test_file_paths(category_path)
    if paths or category != "unit":
        return paths
    return test_file_paths(module.test_path, recursive=False)


def run_module_tests(module: Module, timeout: int) -> CommandResult:
    test_files = test_file_paths(module.test_path)
    if not test_files:
        return CommandResult(
            name=f"{module.name} tests",
            success=False,
            duration=0.0,
            command=[],
            stderr=f"No tests found in {module.test_path}",
        )
    ensure_results_dir()
    command = [
        *pytest_base_args(),
        *map(str, test_files),
        f"--junitxml={RESULTS_DIR / f'{module.name}_results.xml'}",
    ]
    return run_command(command, f"{module.name} tests", timeout=timeout)


def run_module_category_tests(category: str, timeout: int) -> SuiteReport:
    """Run one test category per module to avoid cross-module pytest state leaks."""
    report = SuiteReport()
    ensure_results_dir(clean=True)
    discovered = False
    for module in discover_geo_infer_modules():
        paths = category_test_paths(module, category)
        if not paths:
            continue
        discovered = True
        command = [
            *pytest_base_args(),
            *map(str, paths),
            f"--junitxml={RESULTS_DIR / f'{module.name}_{category}_results.xml'}",
        ]
        report.add(
            run_command(command, f"{module.name} {category} tests", timeout=timeout)
        )

    if not discovered:
        report.add(
            CommandResult(
                name=f"{category} tests",
                success=False,
                duration=0.0,
                command=[],
                stderr=f"No {category} tests discovered.",
            )
        )
    return report


def run_unit_tests(timeout: int) -> SuiteReport:
    return run_module_category_tests("unit", timeout=timeout)


def run_integration_tests(timeout: int) -> SuiteReport:
    return run_module_category_tests("integration", timeout=timeout)


def run_performance_tests(timeout: int) -> SuiteReport:
    report = SuiteReport()
    ensure_results_dir(clean=True)
    discovered = False
    for module in discover_geo_infer_modules():
        performance_dir = module.test_path / "performance"
        # The directory is the canonical category boundary.  A unit test can
        # legitimately contain "performance" in its filename while still
        # exercising a small utility in the unit suite; selecting by filename
        # made this command silently execute unit tests twice.
        performance_files = test_file_paths(performance_dir)
        if not performance_files:
            continue
        discovered = True
        command = [
            *pytest_base_args(),
            *map(str, performance_files),
            f"--junitxml={RESULTS_DIR / f'{module.name}_performance_results.xml'}",
        ]
        report.add(
            run_command(command, f"{module.name} performance tests", timeout=timeout)
        )

    if not discovered:
        report.add(
            CommandResult(
                name="performance tests",
                success=False,
                duration=0.0,
                command=[],
                stderr="No performance tests discovered.",
            )
        )
        return report
    return report


def run_coverage_analysis(timeout: int) -> SuiteReport:
    report = SuiteReport()
    source_dirs = [
        module.path / "src"
        for module in discover_geo_infer_modules()
        if (module.path / "src").exists()
    ]
    test_paths = [
        module.test_path for module in discover_geo_infer_modules() if module.has_tests
    ]
    command = [
        sys.executable,
        "-m",
        "pytest",
        *map(str, test_paths),
        "--cov",
        ",".join(str(path) for path in source_dirs),
        "--cov-report=term-missing",
    ]
    report.add(run_command(command, "coverage analysis", timeout=timeout))
    return report


def run_h3_contracts(timeout: int) -> SuiteReport:
    report = SuiteReport()
    validators = [
        "validate_act_geospatial_contract.py",
        "validate_h3_active_inference_contract.py",
    ]
    for validator in validators:
        command = [sys.executable, str(PROJECT_ROOT / "GEO-INFER-TEST" / validator)]
        report.add(run_command(command, validator, timeout=timeout))
    return report


def run_all_modules(timeout: int) -> SuiteReport:
    report = SuiteReport()
    ensure_results_dir(clean=True)
    for module in discover_geo_infer_modules():
        report.add(run_module_tests(module, timeout=timeout))
    return report


def _text_tail(value: object, limit: int = 2000) -> str:
    """Return a JSON-safe tail for subprocess output.

    ``subprocess.TimeoutExpired`` can expose captured output as ``bytes`` even
    when ``text=True`` was requested.  Normalizing at the report boundary keeps
    a timed-out command from causing the overall test run to fail while its
    diagnostic summary is being written.
    """
    if value is None:
        return ""
    if isinstance(value, bytes):
        value = value.decode("utf-8", errors="replace")
    elif not isinstance(value, str):
        value = str(value)
    return value[-limit:]


def write_summary(report: SuiteReport) -> None:
    ensure_results_dir()
    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "success": report.success,
        "results": [
            {
                "name": result.name,
                "success": result.success,
                "duration": round(result.duration, 3),
                "command": result.command,
                "stdout_tail": _text_tail(result.stdout),
                "stderr_tail": _text_tail(result.stderr),
            }
            for result in report.results
        ],
    }
    (RESULTS_DIR / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n",
        encoding="utf-8",
    )

    total = len(report.results)
    passed = sum(1 for result in report.results if result.success)
    print("\n== Summary")
    print(f"Passed: {passed}/{total}")
    print(f"Summary: {RESULTS_DIR / 'summary.json'}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--module", help="Run tests for one GEO-INFER module.")
    parser.add_argument(
        "--category",
        choices=["unit", "integration", "performance", "coverage", "all"],
        help="Run a focused test category.",
    )
    parser.add_argument(
        "--h3-migration",
        action="store_true",
        help="Run H3/Active Inference migration contract validators.",
    )
    parser.add_argument(
        "--list-modules",
        action="store_true",
        help="Print discovered modules and exit.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="Per-command timeout in seconds.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.list_modules:
        for module in discover_geo_infer_modules():
            print(module.name)
        return 0

    report = SuiteReport()

    if args.module:
        report.add(run_module_tests(module_by_name(args.module), timeout=args.timeout))
    elif args.h3_migration:
        report = run_h3_contracts(timeout=args.timeout)
    elif args.category == "unit":
        report = run_unit_tests(timeout=args.timeout)
    elif args.category == "integration":
        report = run_integration_tests(timeout=args.timeout)
    elif args.category == "performance":
        report = run_performance_tests(timeout=args.timeout)
    elif args.category == "coverage":
        report = run_coverage_analysis(timeout=args.timeout)
    else:
        report = run_all_modules(timeout=args.timeout)

    write_summary(report)
    return 0 if report.success else 1


if __name__ == "__main__":
    raise SystemExit(main())
