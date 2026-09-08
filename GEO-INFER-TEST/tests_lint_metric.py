#!/usr/bin/env python3
"""HYG-04 tests-suite import audit metric for the GEO-INFER monorepo.

The HYG-04 ledger row tracks the dead-import surface of every module test
suite: ``ruff check GEO-INFER-*/tests --select F401,F841,F811`` measured 398
hits on 2026-09-07 (361 F401, 35 F841, 2 F811; ``src`` is already clean).
The cleanup method mirrors HYG-01: per-site classification, where pure dead
imports and unused locals are removed, while sanctioned availability probes
and deliberate re-exports are preserved in redundant-alias form that the
selected rules do not flag.

This script is the benchmark instrument for that row: it runs the pinned
ruff over the module test suites and reports the measured count.

Metrics are printed one per line as ``METRIC name=value``; the per-rule and
per-file breakdown follow as ``ASI key=value`` diagnostics.  The harness
exits non-zero only when it cannot measure (ruff unavailable, working tree
unreadable); the measured count is data, never a harness failure.

Environment contract: the shared uv workspace is already synced; the only
tool is ruff resolved through ``uv run --with``, so the workload never
touches the network once the pinned wheel is cached.
"""

from __future__ import annotations

import subprocess
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TEST_GLOB = "GEO-INFER-*/tests"
RULES = ("F401", "F841", "F811")
RUFF_PIN = "ruff>=0.15.6,<0.16"

_TOP_FILE_LIMIT = 8


def _fail(message: str) -> None:
    """Print a harness failure and exit non-zero."""
    print(f"harness failure: {message}", file=sys.stderr)
    raise SystemExit(1)


def _count_hits() -> list[tuple[str, str, str]]:
    """Run the pinned ruff over the module test suites; return the hits."""
    command = [
        "uv",
        "run",
        "--with",
        RUFF_PIN,
        "ruff",
        "check",
        *sorted(Path(REPO_ROOT).glob(TEST_GLOB)),
        "--select",
        ",".join(RULES),
        "--output-format",
        "concise",
    ]
    completed = subprocess.run(command, cwd=REPO_ROOT, capture_output=True, text=True)
    if completed.returncode not in (0, 1):
        _fail(f"ruff failed ({completed.returncode}): {completed.stderr[-2000:]}")
    hits: list[tuple[str, str, str]] = []
    for line in completed.stdout.splitlines():
        parts = line.split(":", 3)
        if len(parts) != 4:
            continue
        path, _line_no, _col, rest = parts
        code = rest.split()[0] if rest.split() else ""
        if code in RULES:
            hits.append((path, code, rest))
    return hits


def main() -> int:
    hits = _count_hits()
    by_rule = Counter(code for _path, code, _rest in hits)
    by_file = Counter(path for path, _code, _rest in hits)

    print(f"METRIC tests_lint_hits={len(hits)}")
    for rule in RULES:
        print(f"ASI tests_lint_{rule.lower()}={by_rule.get(rule, 0)}")
    print(f"ASI tests_lint_files={len(by_file)}")
    for path, count in by_file.most_common(_TOP_FILE_LIMIT):
        print(f"ASI tests_lint_top={path.removeprefix('GEO-INFER-')}:{count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
