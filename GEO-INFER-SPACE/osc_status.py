#!/usr/bin/env python3
"""
Command-line script to check the status of OS Climate repositories.
"""

import sys
import os
from pathlib import Path

# Add the src directory to Python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir.resolve()))

from geo_infer_space.osc_geo.utils.osc_simple_status import main

if __name__ == "__main__":
    sys.exit(main()) 