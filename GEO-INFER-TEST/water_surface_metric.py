#!/usr/bin/env python3
"""WATER-01 not-implemented-surface metric for GEO-INFER-WATER.

The WATER-01 ledger row declares four hydrology surfaces not implemented
in GEO-INFER-WATER's SKILL.md (Green-Ampt infiltration,
aquifer/well-drawdown modeling, flood-frequency analysis, inundation
mapping) and directs that Green-Ampt be implemented first, with the
remainder re-scoped.  This script is the benchmark instrument: it counts
the surfaces still listed on the SKILL.md ``Not implemented:`` line.

Metrics are printed one per line as ``METRIC name=value``; diagnostics as
``ASI key=value``.  The harness exits non-zero only when it cannot
measure; the measured count is data.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import NoReturn

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL = REPO_ROOT / "GEO-INFER-WATER" / "SKILL.md"
SENTINEL = "Groundwater is limited to"


def _fail(message: str) -> NoReturn:
    """Print a harness failure and exit non-zero."""
    print(f"harness failure: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> int:
    if not SKILL.is_file():
        _fail(f"missing SKILL.md: {SKILL}")
    text = SKILL.read_text(encoding="utf-8")
    match = re.search(r"^Not implemented:\s*(.+)$", text, re.MULTILINE)
    if match is None:
        _fail("SKILL.md has no 'Not implemented:' line")
    line = match.group(1).split(SENTINEL)[0].rstrip(" .")
    surfaces = [item.strip() for item in line.split(",") if item.strip()]

    print(f"METRIC water_not_implemented_surfaces={len(surfaces)}")
    for surface in surfaces:
        print(f"ASI water_not_implemented={surface}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
