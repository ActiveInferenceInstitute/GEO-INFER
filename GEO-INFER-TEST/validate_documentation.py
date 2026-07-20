#!/usr/bin/env python3
"""Validate the repository's authoritative documentation paths.

The repository contains historical and module-specific Markdown in addition to
the maintained documentation hub. This validator intentionally checks the
authoritative navigation and workflow pages rather than treating every
historical assessment link as a release contract.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
AUTHORITATIVE_DOCS = (
    "README.md",
    "AGENTS.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "GEO-INFER-INTRA/docs/index.md",
    "GEO-INFER-INTRA/docs/overview.md",
    "GEO-INFER-INTRA/docs/getting_started/index.md",
    "GEO-INFER-INTRA/docs/getting_started/installation_guide.md",
    "GEO-INFER-INTRA/docs/getting_started/first_analysis.md",
    "GEO-INFER-INTRA/docs/developer_guide/index.md",
    "GEO-INFER-INTRA/docs/developer_guide/testing_guide.md",
    "GEO-INFER-INTRA/docs/developer_guide/contributing.md",
    "GEO-INFER-INTRA/docs/developer_guide/code_structure.md",
    "GEO-INFER-INTRA/docs/developer_guide/repo_guidelines.md",
    "GEO-INFER-INTRA/docs/architecture/index.md",
    "GEO-INFER-INTRA/docs/modules/index.md",
    "GEO-INFER-INTRA/docs/geospatial/data_formats/h3/index.md",
    "GEO-INFER-INTRA/docs/api/index.md",
    "GEO-INFER-INTRA/docs/api/reference.md",
    "GEO-INFER-INTRA/docs/integration/index.md",
    "GEO-INFER-INTRA/docs/deployment/index.md",
    "GEO-INFER-INTRA/docs/installation.md",
    "GEO-INFER-INTRA/docs/security/index.md",
    "GEO-INFER-INTRA/docs/support/index.md",
    "GEO-INFER-TEST/docs/index.md",
    "GEO-INFER-TEST/docs/api_reference.md",
    "GEO-INFER-TEST/docs/getting_started.md",
    "GEO-INFER-TEST/docs/examples/basic_example.md",
    "GEO-INFER-TEST/docs/examples/advanced_example.md",
)
LINK_PATTERN = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
FORBIDDEN_CURRENT_STATE_PATTERNS = (
    re.compile(r"python\s+3\.(?:7|8|9|10)\+", re.IGNORECASE),
    re.compile(r"geo-infer-intra\.git", re.IGNORECASE),
    re.compile(r"geo-infer\.org", re.IGNORECASE),
    re.compile(r"implementation here", re.IGNORECASE),
    re.compile(r"total tests:\s*\d+", re.IGNORECASE),
)


def _iter_links(path: Path):
    """Yield relative Markdown targets outside fenced code blocks."""
    in_fence = False
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8", errors="replace").splitlines(), 1
    ):
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        for match in LINK_PATTERN.finditer(line):
            target = match.group(1).strip().strip("<>")
            target = target.split("#", 1)[0].split("?", 1)[0]
            if not target or target.startswith(("http://", "https://", "mailto:")):
                continue
            yield line_number, target


def validate_links(paths: tuple[Path, ...]) -> list[str]:
    """Return errors for missing relative documentation targets."""
    errors: list[str] = []
    for path in paths:
        for line_number, target in _iter_links(path):
            if not (path.parent / target).resolve().exists():
                errors.append(
                    f"{path.relative_to(REPO_ROOT)}:{line_number}: missing {target}"
                )
    return errors


def validate_current_state_language(paths: tuple[Path, ...]) -> list[str]:
    """Return errors for known stale current-state claims."""
    errors: list[str] = []
    for path in paths:
        text = path.read_text(encoding="utf-8", errors="replace")
        for pattern in FORBIDDEN_CURRENT_STATE_PATTERNS:
            match = pattern.search(text)
            if match:
                errors.append(
                    f"{path.relative_to(REPO_ROOT)}: stale current-state text "
                    f"{match.group(0)!r}"
                )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat missing authoritative pages and stale claims as errors.",
    )
    args = parser.parse_args()

    paths = tuple(REPO_ROOT / relative for relative in AUTHORITATIVE_DOCS)
    missing_pages = [
        str(path.relative_to(REPO_ROOT)) for path in paths if not path.is_file()
    ]
    errors = validate_links(tuple(path for path in paths if path.is_file()))
    if args.strict:
        errors.extend(
            f"missing authoritative page: {relative}" for relative in missing_pages
        )
        errors.extend(
            validate_current_state_language(
                tuple(path for path in paths if path.is_file())
            )
        )

    if errors:
        print("Documentation validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(
        f"Documentation validation passed for {len(paths) - len(missing_pages)} "
        f"authoritative pages."
    )
    if missing_pages:
        print("Untracked optional pages: " + ", ".join(missing_pages))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
