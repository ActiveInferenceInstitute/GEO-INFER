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
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODULE_PREFIX = "GEO-INFER-"
TEST_DIR_NAME = "tests"
RESULTS_DIR = PROJECT_ROOT / ".geo-infer-test-results"


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
                has_tests=test_path.exists() and any(test_path.iterdir()),
            )
        )
    return modules


def ensure_results_dir(clean: bool = False) -> None:
    RESULTS_DIR.mkdir(exist_ok=True)
    if not clean:
        return
    for path in RESULTS_DIR.iterdir():
        if path.is_file():
            path.unlink()


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
    success = completed.returncode == 0
    print(f"{'PASS' if success else 'FAIL'} in {duration:.2f}s")
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
    return [sys.executable, "-m", "pytest", "-v", "--tb=short", "--durations=10"]


def has_test_files(path: Path) -> bool:
    """Return true when a directory contains pytest-discoverable test files."""
    return any(path.rglob("test_*.py")) or any(path.rglob("*_test.py"))


def run_module_tests(module: Module, timeout: int) -> CommandResult:
    if not module.has_tests:
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
        str(module.test_path),
        f"--junitxml={RESULTS_DIR / f'{module.name}_results.xml'}",
    ]
    return run_command(command, f"{module.name} tests", timeout=timeout)


def run_module_category_tests(category: str, timeout: int) -> SuiteReport:
    """Run one test category per module to avoid cross-module pytest state leaks."""
    report = SuiteReport()
    ensure_results_dir(clean=True)
    discovered = False
    for module in discover_geo_infer_modules():
        category_path = module.test_path / category
        if not category_path.exists():
            continue
        discovered = True
        if not has_test_files(category_path):
            report.add(
                CommandResult(
                    name=f"{module.name} {category} tests",
                    success=True,
                    duration=0.0,
                    command=[],
                    stdout=f"No pytest files discovered in {category_path}.",
                )
            )
            continue
        command = [
            *pytest_base_args(),
            str(category_path),
            f"--junitxml={RESULTS_DIR / f'{module.name}_{category}_results.xml'}",
        ]
        report.add(
            run_command(command, f"{module.name} {category} tests", timeout=timeout)
        )

    if not discovered:
        report.add(
            CommandResult(
                name=f"{category} tests",
                success=True,
                duration=0.0,
                command=[],
                stdout=f"No {category} tests discovered.",
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
        performance_files = sorted(module.test_path.glob("**/*performance*.py"))
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
                success=True,
                duration=0.0,
                command=[],
                stdout="No performance tests discovered.",
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
                "stdout_tail": result.stdout[-2000:],
                "stderr_tail": result.stderr[-2000:],
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
