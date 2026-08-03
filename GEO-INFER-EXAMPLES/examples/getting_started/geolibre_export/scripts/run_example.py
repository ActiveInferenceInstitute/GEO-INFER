"""Export an H3 grid as a GeoLibre ``.geolibre.json`` project.

This example walks through the recommended GEO-INFER × GeoLibre integration:
compute an H3 grid over a polygon with GEO-INFER-SPACE, style it, and emit a
``.geolibre.json`` project that opens directly in the GeoLibre web/desktop/Jupyter
viewer (https://geolibre.app).

It exercises three of the integration points added for GeoLibre compatibility:

1. ``suggest_h3_resolution`` — pick a resolution whose cell estimate stays
   within a target (with a hard-cap guard).
2. ``polygon_to_cells`` — discretise a polygon to H3 cells.
3. ``build_h3_grid_project`` / ``write_project`` — emit the ``.geolibre.json``.

Run from the repository root:

    uv run python \
        GEO-INFER-EXAMPLES/examples/getting_started/geolibre_export/scripts/run_example.py \
        --output ./geolibre-demo/
"""

from __future__ import annotations

import argparse
from pathlib import Path

from geo_infer_space import polygon_to_cells
from geo_infer_space.core import (
    SpatialIndexingInterface,
    build_h3_grid_project,
    suggest_h3_resolution,
    write_project,
)

# A small sample polygon (a rough bounding box around the San Francisco Bay).
SAMPLE_POLYGON = {
    "type": "Polygon",
    "coordinates": [
        [
            [-122.5, 37.4],
            [-122.5, 37.9],
            [-122.0, 37.9],
            [-122.0, 37.4],
            [-122.5, 37.4],
        ]
    ],
}


def _estimate_area_km2(polygon: dict) -> float:
    """Rough planar area (km^2) from a polygon's bbox, for resolution choice."""
    xs = [c[0] for ring in polygon["coordinates"] for c in ring]
    ys = [c[1] for ring in polygon["coordinates"] for c in ring]
    mid_lat = (min(ys) + max(ys)) / 2.0
    km_per_deg_lon = 111.32 * _cos_deg(mid_lat)
    km_per_deg_lat = 110.574
    return (max(xs) - min(xs)) * km_per_deg_lon * (max(ys) - min(ys)) * km_per_deg_lat


def _cos_deg(deg: float) -> float:
    import math

    return math.cos(math.radians(deg))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=str,
        default="./geolibre-demo/",
        help="Output directory for the .geolibre.json project",
    )
    args = parser.parse_args()

    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    area_km2 = _estimate_area_km2(SAMPLE_POLYGON)
    suggestion = suggest_h3_resolution(area_km2, target_cells=500, max_res=9)
    resolution = int(suggestion["resolution"])
    print(f"Area ~{area_km2:.0f} km^2 -> suggested H3 resolution {resolution}")

    cells = polygon_to_cells(SAMPLE_POLYGON, resolution)
    print(f"Grid covers {len(cells)} H3 cells at resolution {resolution}")

    # Build a GeoJSON FeatureCollection from the grid cell boundaries.
    indexer = SpatialIndexingInterface()
    features = []
    for cell in cells:
        boundary = indexer.get_cell_boundary(cell)  # [(lat, lng), ...]
        ring = [[lng, lat] for lat, lng in boundary]
        features.append(
            {
                "type": "Feature",
                "properties": {"h3": cell, "resolution": resolution},
                "geometry": {"type": "Polygon", "coordinates": [ring]},
            }
        )
    grid_geojson = {"type": "FeatureCollection", "features": features}

    project = build_h3_grid_project(
        f"GEO-INFER H3 grid (res {resolution})",
        grid_geojson,
        center=[-122.25, 37.65],
        zoom=9,
        fill_color="#3b82f6",
        fill_opacity=0.4,
        metadata={"h3_resolution": resolution, "cell_count": len(cells)},
    )

    out_path = out_dir / "h3_grid.geolibre.json"
    write_project(project, out_path)
    print(f"Wrote GeoLibre project: {out_path.resolve()}")
    print("Open it at https://geolibre.app or in the GeoLibre desktop app.")


if __name__ == "__main__":
    main()
