#!/usr/bin/env python3
"""
Command-line wrapper for the OSC setup and status utilities (using forks).
"""

import sys
import os
from pathlib import Path

# Add the src directory to Python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir.resolve()))

from geo_infer_space.osc_geo.utils.osc_wrapper import main

if __name__ == "__main__":
    sys.exit(main()) 