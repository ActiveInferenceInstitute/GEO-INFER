"""Minimal zoning analysis example for GEO-INFER-NORMS.

Thin orchestration over geo_infer_norms.core.zoning_analysis.ZoningAnalyzer:
build a small set of zoning districts and codes, run boundary analysis,
change evaluation, conflict detection, and export a GeoDataFrame.

Run: uv run --no-sync python examples/minimal_zoning_example.py
"""

import matplotlib

matplotlib.use("Agg")  # headless-safe

from shapely.geometry import Point, Polygon

from geo_infer_norms.core.zoning_analysis import ZoningAnalyzer
from geo_infer_norms.models.zoning import ZoningCode, ZoningDistrict


def build_analyzer() -> ZoningAnalyzer:
    """Create a ZoningAnalyzer with a few example districts and codes."""
    codes = [
        ZoningCode.create(
            code="R-1",
            name="Single-Family Residential",
            description="Low-density residential",
            category="residential",
            jurisdiction_id="jur-1",
            allowed_uses=["single_family", "park"],
        ),
        ZoningCode.create(
            code="C-2",
            name="Commercial",
            description="General commercial",
            category="commercial",
            jurisdiction_id="jur-1",
            allowed_uses=["retail", "office"],
        ),
    ]

    districts = [
        ZoningDistrict.create(
            name="North Residential",
            zoning_code="R-1",
            jurisdiction_id="jur-1",
            geometry=Polygon([(0, 0), (2, 0), (2, 2), (0, 2)]),
        ),
        ZoningDistrict.create(
            name="Downtown Commercial",
            zoning_code="C-2",
            jurisdiction_id="jur-1",
            geometry=Polygon([(2, 0), (4, 0), (4, 2), (2, 2)]),
        ),
        ZoningDistrict.create(
            name="South Residential",
            zoning_code="R-1",
            jurisdiction_id="jur-1",
            geometry=Polygon([(0, 2), (4, 2), (4, 4), (0, 4)]),
        ),
    ]

    analyzer = ZoningAnalyzer()
    for code in codes:
        analyzer.add_zoning_code(code)
    for district in districts:
        analyzer.add_zoning_district(district)
    return analyzer


def main() -> None:
    analyzer = build_analyzer()
    print(analyzer)

    point = Point(1, 1)
    for district in analyzer.get_zoning_at_point(point):
        print(f"Zone at {point}: {district.name} ({district.zoning_code})")

    boundaries = analyzer.analyze_zoning_boundaries()
    print(f"Boundary analysis: {len(boundaries.get('adjacencies', boundaries))} entries")

    change = analyzer.evaluate_zoning_change(
        district_id=analyzer.zoning_districts[0].id, new_code="C-2"
    )
    print(f"Rezone R-1 -> C-2: {change}")

    conflicts = analyzer.find_zoning_conflicts(threshold=0.3)
    print(f"Conflicts found: {len(conflicts)}")

    stats = analyzer.get_zoning_statistics()
    print(f"Statistics: {stats}")

    gdf = analyzer.export_districts_to_geodataframe()
    print(f"Exported {len(gdf)} districts to GeoDataFrame (CRS {gdf.crs})")


if __name__ == "__main__":
    main()
