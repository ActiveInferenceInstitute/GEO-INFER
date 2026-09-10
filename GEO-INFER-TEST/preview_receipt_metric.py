#!/usr/bin/env python3
"""DOCS-01 preview-verification metric for GEO-INFER.

The DOCS-01 ledger row (browser verification of the 45 spatial preview
cards) requires, as its acceptance evidence, a committed verification
receipt recording the live-browser checks and asset receipts that still
match the bundles.  This script is the benchmark instrument:

1.  It recomputes the SHA-256 digest and byte size of every artifact
    (html, svg, png) across the 45 module manifests - the receipt is
    never trusted for this part; the hashes are always recomputed from
    the files on disk.
2.  It resolves every ``previews_index.md`` link target against the
    filesystem.
3.  It counts the DOCS-01 acceptance checks that lack a recorded PASS in
    ``GEO-INFER-INTRA/docs/modules/previews/verification/verification.json``.
    A missing receipt leaves every defined check open.

Metrics are printed one per line as ``METRIC name=value``; diagnostics as
``ASI key=value``.  The harness exits non-zero only when it cannot
measure; the measured counts are data.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PREVIEWS = REPO_ROOT / "GEO-INFER-INTRA" / "docs" / "modules" / "previews"
RECEIPT = PREVIEWS / "verification" / "verification.json"
INDEX = REPO_ROOT / "GEO-INFER-INTRA" / "docs" / "modules" / "previews_index.md"

DEFINED_CHECKS = (
    "all_45_pages_load_no_unexpected_console_errors",
    "map_renders_online_representative",
    "cdn_failure_static_fallback_usable",
    "narrow_viewport_usable",
    "keyboard_navigation_operable",
    "accessible_labels_present",
    "asset_receipts_match_45_bundles",
    "representative_page_versions_saved",
    "verification_receipt_present",
)


def _fail(message: str) -> None:
    """Print a harness failure and exit non-zero."""
    print(f"harness failure: {message}", file=sys.stderr)
    raise SystemExit(1)


def _receipt_mismatches() -> list[str]:
    """Recompute artifact digests against the manifests."""
    mismatches: list[str] = []
    manifests = sorted(PREVIEWS.glob("*_preview.manifest.json"))
    if not manifests:
        _fail(f"no manifests found under {PREVIEWS}")
    for manifest_path in manifests:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for artifact in manifest.get("artifacts", ()):
            name = artifact["name"]
            path = PREVIEWS / name
            if not path.is_file():
                mismatches.append(f"{name}: missing on disk")
                continue
            data = path.read_bytes()
            if len(data) != artifact["bytes"]:
                mismatches.append(f"{name}: bytes {len(data)} != {artifact['bytes']}")
            digest = hashlib.sha256(data).hexdigest()
            if digest != artifact["sha256"]:
                mismatches.append(f"{name}: sha256 mismatch")
    return mismatches


def _index_link_mismatches() -> list[str]:
    """Every previews_index.md link target missing on disk."""
    if not INDEX.is_file():
        return [f"{INDEX.name}: missing"]
    text = INDEX.read_text(encoding="utf-8")
    return [
        f"index link target missing: {match.group(1)}"
        for match in re.finditer(r"\((previews/[^)]+)\)", text)
        if not (
            REPO_ROOT / "GEO-INFER-INTRA" / "docs" / "modules" / match.group(1)
        ).is_file()
    ]


def _open_checks(mismatches: list[str]) -> list[str]:
    """Count defined acceptance checks without a recorded PASS."""
    receipt: dict | None = None
    if RECEIPT.is_file():
        try:
            receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            receipt = None
    recorded: dict[str, str] = {}
    if receipt:
        recorded = {
            entry.get("check", ""): str(entry.get("status", "")).lower()
            for entry in receipt.get("checks", [])
        }
    open_checks: list[str] = []
    for check in DEFINED_CHECKS:
        if check == "asset_receipts_match_45_bundles":
            # Authoritative recomputation: a receipt claim cannot pass this
            # check while the digests on disk disagree.
            if mismatches:
                open_checks.append(check)
                continue
        if recorded.get(check) != "pass":
            open_checks.append(check)
    return open_checks


def main() -> int:
    if not PREVIEWS.is_dir():
        _fail(f"missing previews directory: {PREVIEWS}")
    mismatches = _receipt_mismatches()
    link_mismatches = _index_link_mismatches()
    open_checks = _open_checks(mismatches + link_mismatches)

    print(f"METRIC docs01_verification_checks_open={len(open_checks)}")
    print(
        f"METRIC preview_asset_receipt_mismatches={len(mismatches) + len(link_mismatches)}"
    )
    print(f"ASI index_link_mismatches={len(link_mismatches)}")
    print(
        f"ASI preview_manifests={len(list(PREVIEWS.glob('*_preview.manifest.json')))}"
    )
    for check in open_checks:
        print(f"ASI docs01_check_open={check}")
    for mismatch in (mismatches + link_mismatches)[:8]:
        print(f"ASI preview_receipt_mismatch={mismatch}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
