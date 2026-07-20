#!/usr/bin/env python3
"""Thin wrapper for the ACT verification scenario."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ACT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ACT_ROOT / "src"))

from geo_infer_act.runners.wrapper import run_scenario_entrypoint  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    """Run the package-owned verification scenario."""
    _: type[argparse.ArgumentParser] = argparse.ArgumentParser
    return run_scenario_entrypoint("verification", argv, program="verify_pipeline.py")


if __name__ == "__main__":
    raise SystemExit(main())
