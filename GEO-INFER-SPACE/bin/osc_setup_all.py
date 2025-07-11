#!/usr/bin/env python3
"""
Command-line wrapper for the OSC setup utility.
Now using docxology forks of original OS-Climate repositories.
"""

import sys
import os
from pathlib import Path

# Add the src directory to Python path
src_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir.resolve()))

from geo_infer_space.osc_geo.utils.osc_setup_all import main

if __name__ == "__main__":
    sys.exit(main()) 