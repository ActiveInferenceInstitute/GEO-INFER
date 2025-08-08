#!/usr/bin/env python3
"""
Del Norte County analysis orchestrator.

Runs forest health, coastal resilience, and fire risk analyzers using real
data integrators where implemented, and saves outputs in the location's
`del_norte_dashboard/` directory.

Usage:
  python3 run_analysis.py
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from geo_infer_place.locations.del_norte_county.forest_health_monitor import (
    ForestHealthMonitor,
)
from geo_infer_place.locations.del_norte_county.coastal_resilience_analyzer import (
    CoastalResilienceAnalyzer,
)
from geo_infer_place.locations.del_norte_county.fire_risk_assessor import (
    FireRiskAssessor,
)
from geo_infer_place.locations.del_norte_county.advanced_dashboard import (
    AdvancedDashboard,
)
from geo_infer_place.utils.integration import DelNorteDataIntegrator


def load_location_config() -> dict:
    config_path = (
        Path(__file__).parent / "config" / "analysis_config.yaml"
    )
    try:
        import yaml

        with open(config_path, "r") as f:
            return yaml.safe_load(f) or {}
    except Exception:
        # Minimal default bounds if YAML not available
        return {
            "location": {
                "bounds": {
                    "north": 42.006,
                    "south": 41.458,
                    "east": -123.536,
                    "west": -124.408,
                }
            },
            "spatial": {"h3_resolution": 8},
            "analyses": {
                "forest_health": {},
                "coastal_resilience": {},
                "fire_risk": {},
            },
        }


def main() -> None:
    base_dir = Path(__file__).parent
    output_dir = base_dir / "del_norte_dashboard"
    output_dir.mkdir(parents=True, exist_ok=True)

    config = load_location_config()
    bounds = config.get("location", {}).get("bounds", {})
    bbox = (bounds.get("west"), bounds.get("south"), bounds.get("east"), bounds.get("north"))
    h3_res = config.get("spatial", {}).get("h3_resolution", 8)

    # Data integrator (real API wrappers)
    integrator = DelNorteDataIntegrator()

    # Initialize analyzers with shared integrator and write outputs next to dashboard
    forest = ForestHealthMonitor(config=config, data_integrator=integrator, spatial_processor=None, output_dir=output_dir)
    coastal = CoastalResilienceAnalyzer(config=config, data_integrator=integrator, spatial_processor=None, output_dir=output_dir)
    fire = FireRiskAssessor(config=config, data_integrator=integrator, spatial_processor=None, output_dir=output_dir)

    # Run analyses
    results = {
        "forest_health": forest.run_analysis(),
        "coastal_resilience": coastal.run_analysis(),
        "fire_risk": fire.run_analysis(),
    }

    # Persist unified results
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    (output_dir / f"del_norte_combined_results_{ts}.json").write_text(
        json.dumps(results, indent=2, default=str)
    )

    # Generate and save interactive dashboard
    dash = AdvancedDashboard(output_dir=str(output_dir))
    html_path = dash.save_dashboard()
    print(html_path)


if __name__ == "__main__":
    main()


