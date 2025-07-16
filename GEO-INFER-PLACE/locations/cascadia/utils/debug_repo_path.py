#!/usr/bin/env python3
"""
Debug script to understand repository path detection issues
"""

import sys
import os
from pathlib import Path

# Add paths
cascadian_dir = os.path.dirname(os.path.realpath(__file__))
project_root = os.path.abspath(os.path.join(cascadian_dir, '..', '..', '..'))
space_src_path = os.path.join(project_root, 'GEO-INFER-SPACE', 'src')

if space_src_path not in sys.path:
    sys.path.insert(0, space_src_path)

from geo_infer_space.osc_geo.core.repos import get_repo_path, OSC_REPOS

def debug_repo_path():
    """Debug the repository path detection"""
    
    print("=== Repository Path Debug ===")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Project root: {project_root}")
    print(f"SPACE src path: {space_src_path}")
    
    # Expected repo directory
    expected_repo_dir = os.path.join(project_root, 'GEO-INFER-SPACE', 'repo')
    print(f"Expected repo directory: {expected_repo_dir}")
    print(f"Expected repo directory exists: {os.path.exists(expected_repo_dir)}")
    
    if os.path.exists(expected_repo_dir):
        print(f"Contents of repo directory:")
        for item in os.listdir(expected_repo_dir):
            item_path = os.path.join(expected_repo_dir, item)
            if os.path.isdir(item_path):
                print(f"  📁 {item}/")
            else:
                print(f"  📄 {item}")
    
    print("\n=== OSC_REPOS Configuration ===")
    for key, info in OSC_REPOS.items():
        print(f"{key}:")
        for k, v in info.items():
            print(f"  {k}: {v}")
    
    print("\n=== Testing get_repo_path ===")
    
    # Test with different base directories
    test_base_dirs = [
        None,  # Let it auto-detect
        expected_repo_dir,  # Full path to repo directory
        os.path.join(project_root, 'GEO-INFER-SPACE'),  # Path to SPACE root
    ]
    
    for base_dir in test_base_dirs:
        print(f"\n--- Testing with base_dir: {base_dir} ---")
        
        for repo_key in OSC_REPOS.keys():
            print(f"  Testing repo key: {repo_key}")
            try:
                result = get_repo_path(repo_key, base_dir)
                print(f"    Result: {result}")
                if result:
                    print(f"    Exists: {os.path.exists(result)}")
                    if os.path.exists(result):
                        print(f"    Is directory: {os.path.isdir(result)}")
                else:
                    # Manual check
                    repo_name = OSC_REPOS[repo_key]["repo"]
                    if base_dir:
                        manual_path = os.path.join(base_dir, repo_name)
                        print(f"    Manual check path: {manual_path}")
                        print(f"    Manual check exists: {os.path.exists(manual_path)}")
            except Exception as e:
                print(f"    ERROR: {e}")

if __name__ == "__main__":
    debug_repo_path() 