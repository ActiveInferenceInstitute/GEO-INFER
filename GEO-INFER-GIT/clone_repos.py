#!/usr/bin/env python3
"""
Script to run GEO-INFER-GIT repository cloning.

This is a convenience script that calls the main module
to clone repositories based on configuration.
"""

import os
import sys
import logging

# Add the src directory to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

# Import the main module
from geo_infer_git.main import main

if __name__ == "__main__":
    # Configure basic logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Run the main function
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation canceled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1) 