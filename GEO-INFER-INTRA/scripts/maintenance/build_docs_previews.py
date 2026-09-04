"""
Documentation builder for spatial visual previews (DOCS-01).

Provides a reproducible CLI entry that emits pre-rendered Leaflet HTML,
SVG, and PNG preview bundles for every GEO-INFER domain module, plus a preview
index page referenced from the module documentation.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from geo_infer_intra.core.documentation.visual_preview import build_previews


def main() -> int:
    """CLI entry point for regenerating module spatial preview documentation."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--modules-dir",
        type=Path,
        default=Path("GEO-INFER-INTRA/docs/modules"),
        help="Path to the documentation modules directory.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("GEO-INFER-INTRA/docs/modules/previews"),
        help="Directory into which preview bundle files are written.",
    )
    args = parser.parse_args()

    if not args.modules_dir.is_dir():
        raise SystemExit(f"Modules docs directory missing: {args.modules_dir}")

    emitted = build_previews(args.modules_dir, args.output_dir)
    print(f"Emitted {emitted} spatial preview bundles to {args.output_dir}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
