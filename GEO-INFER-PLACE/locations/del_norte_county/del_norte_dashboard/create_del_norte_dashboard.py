#!/usr/bin/env python3
"""
Thin orchestrator for creating the Del Norte dashboard.

Behavior:
- Checks for cached real datasets in this folder (fire perimeters, tide levels)
- If not present or if --refresh is passed, fetches fresh data
- Generates the dashboard HTML under this folder

Usage:
  python3 create_del_norte_dashboard.py            # use cache when available
  python3 create_del_norte_dashboard.py --refresh  # force refetch
"""
from __future__ import annotations

import argparse
from pathlib import Path

from geo_infer_place.locations.del_norte_county.advanced_dashboard import AdvancedDashboard


def main() -> None:
    parser = argparse.ArgumentParser(description="Create Del Norte dashboard")
    parser.add_argument("--refresh", action="store_true", help="Fetch new data instead of using cache")
    args = parser.parse_args()

    # Output directory is the current folder
    out_dir = Path(__file__).parent

    dash = AdvancedDashboard(output_dir=str(out_dir))
    if not args.refresh:
        # Load cached datasets if present
        dash.load_cached_data()

    path = dash.save_dashboard(fetch_data=args.refresh)
    print(path)


if __name__ == "__main__":
    main()


