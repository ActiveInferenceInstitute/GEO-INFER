#!/usr/bin/env python3
"""Thin wrapper for the complete ACT examples suite."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ACT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ACT_ROOT / "src"))

from geo_infer_act.runners.wrapper import run_scenario_entrypoint  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    """Run all package-owned ACT scenarios."""
    _: type[argparse.ArgumentParser] = argparse.ArgumentParser
    return run_scenario_entrypoint("all", argv, program="run_all_examples.py")


if __name__ == "__main__":
    raise SystemExit(main())
