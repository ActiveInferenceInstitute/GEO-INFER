#!/usr/bin/env python3
"""
Thin wrapper around :mod:`geo_infer_git.main`.

Delegates all cloning behavior (CloneConfig, retry/rate-limit handling,
parallelism, report generation, gitignore-entry logic) to the package
pipeline so there is a single implementation to maintain.
"""

import os
import sys

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "src"))
)

from geo_infer_git.main import main

import logging

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.getLogger("geo_infer_git").info("Operation canceled by user.")
        sys.exit(1)