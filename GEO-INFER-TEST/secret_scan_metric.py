#!/usr/bin/env python3
"""SEC-02 secret-scan metric for the GEO-INFER monorepo.

The SEC-02 ledger row requires a secret-scanning gate over the full git
history with a committed policy for the pre-rewrite objects GitHub may
still serve by exact SHA.  This script is the benchmark instrument: it
runs gitleaks over the full history, using the committed
``.gitleaks.toml`` policy when one exists (default rules otherwise), and
reports the number of unresolved findings.

The committed policy allowlists only synthetic-credential sites
(documented API examples and test fixtures), each with a written
justification in ``GEO-INFER-TEST/docs/secret_scan_policy.md``; a real
credential is never allowlisted - it is a finding and must be revoked.

Metrics are printed one per line as ``METRIC name=value``; diagnostics as
``ASI key=value``.  The harness exits non-zero only when it cannot
measure (gitleaks unavailable, scan crashed); the measured count is data.

Environment contract: gitleaks (>=8.30, pinned in ci.yml) must be on
PATH; the scan is fully offline.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG = REPO_ROOT / ".gitleaks.toml"


def _fail(message: str) -> None:
    """Print a harness failure and exit non-zero."""
    print(f"harness failure: {message}", file=sys.stderr)
    raise SystemExit(1)


def _scan() -> tuple[int, list[dict], int]:
    """Run gitleaks over the full history; return (findings, report, rc)."""
    gitleaks = shutil.which("gitleaks")
    if gitleaks is None:
        _fail("gitleaks is not installed (pinned 8.30.x in ci.yml)")
    command = [gitleaks, "detect", "--source", str(REPO_ROOT)]
    if CONFIG.is_file():
        command.extend(["--config", str(CONFIG)])
    command.extend(["--report-format", "json", "--report-path"])
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as handle:
        report_path = Path(handle.name)
    command.append(str(report_path))
    completed = subprocess.run(
        command, cwd=REPO_ROOT, capture_output=True, text=True, timeout=1800
    )
    # gitleaks exits 1 when leaks are found: that is data, not a crash.
    if completed.returncode not in (0, 1):
        _fail(f"gitleaks failed ({completed.returncode}): {completed.stderr[-2000:]}")
    report: list[dict] = []
    if report_path.is_file() and report_path.stat().st_size > 0:
        report = json.loads(report_path.read_text(encoding="utf-8"))
    report_path.unlink(missing_ok=True)
    return len(report), report, completed.returncode


def main() -> int:
    findings, report, returncode = _scan()
    by_rule = Counter(entry.get("RuleID", "unknown") for entry in report)
    by_file = Counter(entry.get("File", "unknown") for entry in report)

    print(f"METRIC secret_scan_findings={findings}")
    print(f"ASI secret_scan_policy={'committed' if CONFIG.is_file() else 'default'}")
    print(f"ASI secret_scan_exit={returncode}")
    for rule, count in by_rule.most_common(6):
        print(f"ASI secret_scan_rule={rule}:{count}")
    for path, count in by_file.most_common(6):
        print(f"ASI secret_scan_file={path}:{count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
