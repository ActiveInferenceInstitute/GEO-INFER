#!/usr/bin/env python3
"""Thin wrapper for the H3 Active Inference scenario."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ACT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ACT_ROOT / "src"))

from geo_infer_act.runners.h3 import (  # noqa: E402
    generate_realistic_environmental_observations,
    run_h3_active_inference,
    setup_san_francisco_boundary,
)
from geo_infer_act.runners.wrapper import run_scenario_entrypoint  # noqa: E402

__all__ = [
    "generate_realistic_environmental_observations",
    "run_h3_active_inference",
    "setup_san_francisco_boundary",
    "main",
]


def main(argv: list[str] | None = None) -> int:
    """Run the package-owned H3 scenario."""
    _: type[argparse.ArgumentParser] = argparse.ArgumentParser
    return run_scenario_entrypoint("h3", argv, program="h3_active_inference.py")


if __name__ == "__main__":
    raise SystemExit(main())
