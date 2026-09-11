#!/usr/bin/env python3
"""Per-module coverage measurement for the TEST-03 baseline.

Runs each module's own test selection (unit + integration categories;
performance and system suites are excluded from the baseline and noted)
under pytest-cov, and records the measured line coverage of the module's
``src`` package.

Usage::

    uv run --no-sync --with pytest-cov python \
        GEO-INFER-TEST/measure_module_coverage.py \
        [--modules GEO-INFER-ACT,GEO-INFER-MATH] [--json PATH]

pytest-cov is used deliberately: plain ``coverage run -m pytest`` cannot
see xdist's execnet workers (the controller imports none of the source),
while pytest-cov distributes coverage to workers and combines it.  The
in-module pytest parallelism stays at ``-n 4``; module jobs run with at
most four concurrent processes.

Output: one JSON object per module on stdout
(``{"module": ..., "coverage_percent": ..., "seconds": ..., "status": ...}``).
A module whose suite crashes is reported with ``status: "error"`` and no
coverage number; it is never silently skipped.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MAX_MODULE_WORKERS = 4
MODULE_TIMEOUT_SECONDS = 1800


def _module_package(module: str) -> str | None:
    src = REPO_ROOT / module / "src"
    if not src.is_dir():
        return None
    for child in sorted(src.iterdir()):
        if child.is_dir() and child.name.startswith("geo_infer_"):
            return child.name
    return None


def measure_module(module: str) -> dict:
    """Measure one module's line coverage over its unit+integration tests."""
    package = _module_package(module)
    if package is None:
        return {"module": module, "status": "error", "reason": "no src package"}
    with tempfile.TemporaryDirectory(prefix=f"cov-{module}-") as data_dir:
        report_path = Path(data_dir) / "report.json"
        started = time.monotonic()
        completed = subprocess.run(
            [
                "uv",
                "run",
                "--no-sync",
                "--with",
                "pytest-cov",
                "python",
                "-m",
                "pytest",
                (REPO_ROOT / module / "tests").relative_to(REPO_ROOT).as_posix(),
                "-n",
                "4",
                "-q",
                "-p",
                "no:cacheprovider",
                # The repo's filterwarnings=["error"] promotes
                # pytest-benchmark's xdist advisory into a fatal
                # INTERNALERROR; benchmarks are advisory here.
                "-W",
                "ignore::pytest_benchmark.logger.PytestBenchmarkWarning",
                "--ignore",
                (REPO_ROOT / module / "tests" / "performance")
                .relative_to(REPO_ROOT)
                .as_posix(),
                "--ignore",
                (REPO_ROOT / module / "tests" / "system")
                .relative_to(REPO_ROOT)
                .as_posix(),
                f"--cov={package}",
                "--cov-report=json:" + str(report_path),
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=MODULE_TIMEOUT_SECONDS,
            # Concurrent module jobs share this cwd; without an isolated
            # data file each job's combine step globs the other jobs'
            # in-flight .coverage.* files and cross-pollutes every report.
            env={
                **os.environ,
                "COVERAGE_FILE": str(Path(data_dir) / ".coverage"),
            },
        )
        seconds = round(time.monotonic() - started, 1)
        if completed.returncode not in (0, 1):
            return {
                "module": module,
                "status": "error",
                "reason": (
                    f"pytest failed rc={completed.returncode}: "
                    f"stderr={completed.stderr[-300:]!r}"
                ),
                "pytest_tail": completed.stdout[-500:],
                "pytest_err_tail": completed.stderr[-500:],
                "seconds": seconds,
            }
        if not report_path.is_file() or report_path.stat().st_size == 0:
            return {
                "module": module,
                "status": "error",
                "reason": "pytest-cov produced no report",
                "pytest_rc": completed.returncode,
                "pytest_tail": completed.stdout[-500:],
                "pytest_err_tail": completed.stderr[-500:],
                "seconds": seconds,
            }
        payload = json.loads(report_path.read_text(encoding="utf-8"))
        return {
            "module": module,
            "status": "measured",
            "coverage_percent": round(payload["totals"]["percent_covered"], 1),
            "pytest_rc": completed.returncode,
            "seconds": seconds,
        }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--modules", default="", help="comma-separated subset")
    parser.add_argument("--json", default="", help="write the results array here")
    args = parser.parse_args(argv)

    if args.modules:
        modules = [
            name for name in (part.strip() for part in args.modules.split(",")) if name
        ]
    else:
        modules = sorted(
            path.name
            for path in REPO_ROOT.iterdir()
            if path.is_dir()
            and path.name.startswith("GEO-INFER-")
            and (path / "tests").is_dir()
        )
    results: list[dict] = []
    with ThreadPoolExecutor(max_workers=MAX_MODULE_WORKERS) as pool:
        futures = {pool.submit(measure_module, module): module for module in modules}
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            print(json.dumps(result), flush=True)
    results.sort(key=lambda entry: entry["module"])
    if args.json:
        Path(args.json).write_text(
            json.dumps(results, indent=1, sort_keys=True), encoding="utf-8"
        )
    failures = [entry for entry in results if entry["status"] != "measured"]
    if failures:
        print(f"coverage sweep: {len(failures)} module(s) errored", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
