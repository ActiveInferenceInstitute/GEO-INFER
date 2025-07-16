#!/usr/bin/env python3
"""
Debug H3DataLoader initialization issue
"""

import sys
import os
from pathlib import Path

# Add paths
cascadian_dir = os.path.dirname(os.path.realpath(__file__))
project_root = os.path.abspath(os.path.join(cascadian_dir, '..', '..', '..'))

# Set OSC repository path environment variable
osc_repo_path = os.path.join(project_root, 'GEO-INFER-SPACE', 'repo')
os.environ['OSC_REPOS_DIR'] = osc_repo_path
print(f"Set OSC_REPOS_DIR to: {osc_repo_path}")

space_src_path = os.path.join(project_root, 'GEO-INFER-SPACE', 'src')
if space_src_path not in sys.path:
    sys.path.insert(0, space_src_path)

import logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

from geo_infer_space.osc_geo.core.repos import get_repo_path
from geo_infer_space.osc_geo.core.loader import H3DataLoader

def debug_h3_loader():
    """Debug H3DataLoader initialization"""
    
    print("=== H3DataLoader Debug ===")
    
    # Test repo path detection
    repo_path = get_repo_path("h3loader-cli", osc_repo_path)
    print(f"Repository path: {repo_path}")
    print(f"Repository exists: {os.path.exists(repo_path) if repo_path else False}")
    
    if repo_path and os.path.exists(repo_path):
        print(f"Repository contents:")
        for item in os.listdir(repo_path):
            print(f"  {item}")
        
        # Check virtual environment
        venv_path = os.path.join(repo_path, 'venv')
        print(f"venv path: {venv_path}")
        print(f"venv exists: {os.path.exists(venv_path)}")
        
        if os.path.exists(venv_path):
            # Check Python executables
            python_candidates = [
                os.path.join(repo_path, 'venv', 'bin', 'python'),
                os.path.join(repo_path, 'venv', 'bin', 'python3'),
                os.path.join(repo_path, 'venv', 'Scripts', 'python.exe')
            ]
            
            for candidate in python_candidates:
                exists = os.path.exists(candidate)
                print(f"  Python candidate {candidate}: {exists}")
                if exists:
                    # Test if it's executable
                    print(f"    Executable: {os.access(candidate, os.X_OK)}")
        
        # Try initializing H3DataLoader
        print("\n=== Testing H3DataLoader Initialization ===")
        try:
            loader = H3DataLoader(repo_base_dir=osc_repo_path)
            print("✅ H3DataLoader initialized successfully!")
        except Exception as e:
            print(f"❌ H3DataLoader initialization failed: {e}")
            import traceback
            traceback.print_exc()
    
    else:
        print("❌ Repository path not found or doesn't exist")

if __name__ == "__main__":
    debug_h3_loader() 