#!/usr/bin/env python3
"""Diff-scoped coverage-floor gate for the TEST-03 baseline.

Re-measures line coverage for every module whose ``src`` or ``tests``
changed between two revisions and fails when a touched module's measured
coverage falls below its recorded floor in
``GEO-INFER-TEST/coverage_baseline.json``.

Usage::

    uv run --with pytest-cov python GEO-INFER-TEST/check_coverage_floor.py \
        --base <sha> --head <sha> [--modules M1,M2]

``--modules`` forces a module set regardless of the diff (used for local
verification).  With no changed modules the gate passes immediately.
Failures are reported per module and the exit code is 1.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

from measure_module_coverage import measure_module  # noqa: E402

MANIFEST = REPO_ROOT / "GEO-INFER-TEST" / "coverage_baseline.json"
DIFF_FILTER = "ACMRTUXB"


def _fail(message: str) -> None:
    """Print a gate failure and exit non-zero."""
    print(f"coverage floor gate failure: {message}", file=sys.stderr)
    raise SystemExit(1)


def _changed_modules(base: str, head: str) -> set[str]:
    completed = subprocess.run(
        [
            "git",
            "diff",
            "--name-only",
            f"--diff-filter={DIFF_FILTER}",
            base,
            head,
            "--",
            "GEO-INFER-*/src/*.py",
            "GEO-INFER-*/tests/*.py",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        _fail(f"git diff failed: {completed.stderr[-400:]}")
    modules: set[str] = set()
    for line in completed.stdout.splitlines():
        top = line.split("/", 1)[0]
        if top.startswith("GEO-INFER-"):
            modules.add(top)
    return modules


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", required=True)
    parser.add_argument("--head", required=True)
    parser.add_argument("--modules", default="", help="force a module set")
    args = parser.parse_args(argv)

    import json

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    entries = manifest.get("modules", {})

    if args.modules:
        modules = {name for name in args.modules.split(",") if name}
    else:
        modules = _changed_modules(args.base, args.head)
    if not modules:
        print("no module changes; coverage floor gate passes")
        return 0

    all_modules = {
        path.name
        for path in REPO_ROOT.iterdir()
        if path.is_dir()
        and path.name.startswith("GEO-INFER-")
        and (path / "tests").is_dir()
    }
    missing = sorted(all_modules - set(entries))
    if missing:
        _fail(f"coverage_baseline.json lacks floors for: {missing}")

    violations: list[str] = []
    for module in sorted(modules):
        floor = entries[module]["floor_percent"]
        result = measure_module(module)
        if result["status"] != "measured":
            violations.append(
                f"{module}: measurement failed ({result.get('reason', 'unknown')})"
            )
            continue
        measured = float(result["coverage_percent"])
        verdict = "ok" if measured >= floor else "VIOLATION"
        print(f"{module}: measured {measured}% vs floor {floor}% -> {verdict}")
        if measured < floor:
            violations.append(f"{module}: {measured}% < floor {floor}%")
    if violations:
        for line in violations:
            print(f"coverage floor violation: {line}", file=sys.stderr)
        _fail(f"{len(violations)} module(s) below their coverage floor")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
