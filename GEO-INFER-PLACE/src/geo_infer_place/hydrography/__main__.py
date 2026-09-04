"""Command-line orchestration for an explicit bounded hydrography selection."""

import argparse

from .ingestion import (
    HydrographySelection,
    NHDPlusHRIngestor,
    SMITH_RIVER_HUC8,
    SMITH_RIVER_PILOT_BBOX,
)


def main() -> None:
    """Acquire the selected region, resuming verified pages in the output directory."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    parser.add_argument(
        "--pilot",
        action="store_true",
        help="Lower Smith River excerpt (34 reaches in the bundled snapshot)",
    )
    parser.add_argument(
        "--bbox", nargs=4, type=float, metavar=("WEST", "SOUTH", "EAST", "NORTH")
    )
    parser.add_argument("--huc8")
    parser.add_argument("--max-features", type=int, default=10_000)
    parser.add_argument("--max-bytes", type=int, default=128 * 1024 * 1024)
    parser.add_argument("--page-size", type=int, default=200)
    args = parser.parse_args()
    if args.pilot and (args.bbox is not None or args.huc8 is not None):
        parser.error("--pilot cannot be combined with --bbox or --huc8")
    if not args.pilot and args.bbox is None and args.huc8 is None:
        parser.error("Select --pilot, --bbox, or --huc8")
    selection = (
        HydrographySelection(SMITH_RIVER_PILOT_BBOX, SMITH_RIVER_HUC8)
        if args.pilot
        else HydrographySelection(tuple(args.bbox) if args.bbox else None, args.huc8)
    )
    ingestor = NHDPlusHRIngestor(
        max_features=args.max_features,
        max_bytes=args.max_bytes,
        page_size=args.page_size,
    )
    print(ingestor.ingest(selection, args.output))


if __name__ == "__main__":
    main()
