#!/usr/bin/env python3
"""Run a configured GEO-INFER-RISK analysis.

The example requires real hazard and exposure data paths. It intentionally does
not create an in-memory dataset or substitute a simulated result when inputs
are absent.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from geo_infer_risk.core.risk_engine import EnhancedRiskEngine


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hazard-data", type=Path, required=True)
    parser.add_argument("--exposure-data", type=Path, required=True)
    parser.add_argument("--hazard-type", default="flood")
    parser.add_argument("--exposure-type", default="property")
    parser.add_argument("--output", type=Path)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    for path in (args.hazard_data, args.exposure_data):
        if not path.is_file():
            raise FileNotFoundError(f"Configured data file does not exist: {path}")

    config = {
        "hazards": {
            args.hazard_type: {
                "enabled": True,
                "historical_data_source": f"file://{args.hazard_data.resolve()}",
            }
        },
        "exposure": {
            args.exposure_type: {
                "enabled": True,
                "data_sources": [f"file://{args.exposure_data.resolve()}"],
            }
        },
    }
    if args.output:
        config["general"] = {"output_directory": str(args.output.parent)}

    engine = EnhancedRiskEngine(config)
    results = engine.run_enhanced_analysis("comprehensive")
    output_path = engine.save_enhanced_results(
        results, args.output.name if args.output else None
    )
    print(
        f"Loaded models: {results['core_analysis']['model_status']['loaded_models_count']}"
    )
    print(f"Results written to {output_path}")


if __name__ == "__main__":
    main()
