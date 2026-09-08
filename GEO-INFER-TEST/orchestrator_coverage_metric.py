#!/usr/bin/env python3
"""EXAMPLES-01 orchestrator-coverage metric for GEO-INFER.

The EXAMPLES-01 ledger row requires a dedicated thin orchestrator example
for every module: ``examples/module_orchestrators/<MODULE>/scripts/
run_orchestrator.py`` following the delivered INSURANCE exemplar.  This
script is the benchmark instrument: it counts the ledger-named modules
that still lack that script.

Metrics are printed one per line as ``METRIC name=value``; diagnostics as
``ASI key=value``.  The harness exits non-zero only when it cannot
measure; the measured count is data.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ORCHESTRATORS = REPO_ROOT / "GEO-INFER-EXAMPLES" / "examples" / "module_orchestrators"
LEDGER_NAMED_MODULES = (
    "CLIMATE",
    "EDU",
    "EMERGENCY",
    "ENERGY",
    "FOREST",
    "MARINE",
    "TRANSPORT",
    "WATER",
)


def _fail(message: str) -> None:
    """Print a harness failure and exit non-zero."""
    print(f"harness failure: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> int:
    if not ORCHESTRATORS.is_dir():
        _fail(f"missing orchestrators directory: {ORCHESTRATORS}")
    missing = [
        name
        for name in LEDGER_NAMED_MODULES
        if not (ORCHESTRATORS / name / "scripts" / "run_orchestrator.py").is_file()
    ]

    print(f"METRIC modules_without_orchestrator_example={len(missing)}")
    print(f"ASI orchestrator_ledger_modules={len(LEDGER_NAMED_MODULES)}")
    for name in missing:
        print(f"ASI module_without_example={name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
