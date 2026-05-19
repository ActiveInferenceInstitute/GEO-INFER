#!/usr/bin/env python3
"""Thin wrapper for the ACT debug scenario."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ACT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ACT_ROOT / "src"))

from geo_infer_act.runners.wrapper import run_wrapper  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    """Run the package-owned debug scenario."""
    _: type[argparse.ArgumentParser] = argparse.ArgumentParser
    return run_wrapper("debug", argv, program="debug_models.py")


if __name__ == "__main__":
    raise SystemExit(main())
