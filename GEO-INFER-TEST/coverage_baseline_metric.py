#!/usr/bin/env python3
"""TEST-03 coverage-baseline completeness metric for GEO-INFER.

The TEST-03 ledger row requires a recorded per-module coverage baseline
with a documented floor, enforced by a diff-scoped CI gate.  This script
is the benchmark instrument: it counts the modules that lack a baseline
entry (measured coverage and floor) in the committed
``GEO-INFER-TEST/coverage_baseline.json`` manifest.

Metrics are printed one per line as ``METRIC name=value``; diagnostics as
``ASI key=value``.  The harness exits non-zero only when it cannot
measure; the measured count is data.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MANIFEST = REPO_ROOT / "GEO-INFER-TEST" / "coverage_baseline.json"


def _discover_modules() -> list[str]:
    """Every GEO-INFER-* module directory that ships a test suite."""
    modules = sorted(
        path.name
        for path in REPO_ROOT.iterdir()
        if path.is_dir()
        and path.name.startswith("GEO-INFER-")
        and (path / "tests").is_dir()
    )
    return modules


def _fail(message: str) -> None:
    """Print a harness failure and exit non-zero."""
    print(f"harness failure: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> int:
    modules = _discover_modules()
    if not modules:
        _fail("no module directories discovered")
    manifest: dict = {}
    if MANIFEST.is_file():
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    entries = manifest.get("modules", {})

    missing = [
        name
        for name in modules
        if name not in entries
        or not isinstance(entries[name].get("coverage_percent"), (int, float))
        or not isinstance(entries[name].get("floor_percent"), (int, float))
    ]
    measured = sorted(set(modules) - set(missing))

    print(f"METRIC modules_missing_coverage_baseline={len(missing)}")
    print(f"ASI coverage_modules_total={len(modules)}")
    print(f"ASI coverage_modules_measured={len(measured)}")
    for name in missing:
        print(f"ASI module_missing_baseline={name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
