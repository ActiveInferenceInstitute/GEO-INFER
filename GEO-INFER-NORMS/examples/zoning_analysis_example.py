"""Zoning analysis example for GEO-INFER-NORMS.

Thin orchestration over geo_infer_norms.core.zoning_analysis.ZoningAnalyzer.
Builds districts and codes, evaluates a zoning change, detects conflicts,
optimizes layout, computes development potential, compares scenarios, and
renders a map plus a report into examples/output/.

Run: uv run --no-sync python examples/zoning_analysis_example.py
"""

import os

import matplotlib

matplotlib.use("Agg")  # headless-safe

from shapely.geometry import Polygon

from geo_infer_norms.core.zoning_analysis import ZoningAnalyzer
from geo_infer_norms.models.zoning import ZoningCode, ZoningDistrict

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")

DISTRICT_SHAPES = {
    "R-1": [Polygon([(0, 0), (2, 0), (2, 2), (0, 2)])],
    "C-2": [Polygon([(2, 0), (4, 0), (4, 2), (2, 2)])],
    "M-1": [Polygon([(0, 2), (2, 2), (2, 4), (0, 4)])],
}

CODES = {
    "R-1": ("Single-Family Residential", "Low-density residential", "residential"),
    "C-2": ("Commercial", "General commercial", "commercial"),
    "M-1": ("Light Industrial", "Light industrial use", "industrial"),
}


def build_analyzer() -> ZoningAnalyzer:
    """Create a populated ZoningAnalyzer with three codes and four districts."""
    analyzer = ZoningAnalyzer()
    for code, (name, description, category) in CODES.items():
        analyzer.add_zoning_code(
            ZoningCode.create(
                code=code,
                name=name,
                description=description,
                category=category,
                jurisdiction_id="jur-1",
            )
        )
    district_no = 1
    for code, shapes in DISTRICT_SHAPES.items():
        for geometry in shapes:
            analyzer.add_zoning_district(
                ZoningDistrict.create(
                    name=f"District {district_no}",
                    zoning_code=code,
                    jurisdiction_id="jur-1",
                    geometry=geometry,
                )
            )
            district_no += 1
    # A second residential district adjacent to the industrial one.
    analyzer.add_zoning_district(
        ZoningDistrict.create(
            name="District 5",
            zoning_code="R-1",
            jurisdiction_id="jur-1",
            geometry=Polygon([(2, 2), (4, 2), (4, 4), (2, 4)]),
        )
    )
    return analyzer


def main() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    analyzer = build_analyzer()
    print(analyzer)

    # Scenario: rezone a residential district to commercial.
    residential_id = next(
        d.id for d in analyzer.zoning_districts if d.zoning_code == "R-1"
    )
    change = analyzer.evaluate_zoning_change(residential_id, new_code="C-2")
    print(f"Rezone evaluation: {change}")

    conflicts = analyzer.find_zoning_conflicts(threshold=0.3)
    print(f"Conflicts: {conflicts}")

    optimization = analyzer.optimize_zoning_layout(target_compatibility=0.7)
    print(f"Optimization suggestion: {optimization}")

    for district in analyzer.zoning_districts:
        potential = analyzer.calculate_development_potential(district.id)
        print(f"Development potential for {district.name}: {potential}")

    scenario_a = {"name": "status quo", "rezones": {}}
    scenario_b = {"name": "commercial expansion", "rezones": {residential_id: "C-2"}}
    comparison = analyzer.compare_zoning_scenarios([scenario_a, scenario_b])
    print(f"Scenario comparison: {comparison}")

    figure = analyzer.visualize_zoning(
        save_path=os.path.join(OUTPUT_DIR, "zoning_map.png")
    )
    print(f"Saved zoning map ({figure.canvas.get_width_height()})")

    report_path = os.path.join(OUTPUT_DIR, "zoning_report.txt")
    report = analyzer.generate_zoning_report(output_path=report_path)
    print(f"Report written to {report_path}: {report[:120]}...")


if __name__ == "__main__":
    main()
