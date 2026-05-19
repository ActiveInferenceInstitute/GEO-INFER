#!/usr/bin/env python3
"""Thin wrapper for the urban-planning Active Inference scenario."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ACT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ACT_ROOT / "src"))

from geo_infer_act.runners.wrapper import run_wrapper  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    """Run the package-owned urban-planning scenario."""
    _: type[argparse.ArgumentParser] = argparse.ArgumentParser
    return run_wrapper("urban_planning", argv, program="urban_planning.py")


if __name__ == "__main__":
    raise SystemExit(main())
