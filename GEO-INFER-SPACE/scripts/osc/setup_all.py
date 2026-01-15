#!/usr/bin/env python3
"""
OS-Climate Repository Setup Script

This script clones and sets up all OS-Climate repositories for GEO-INFER-SPACE.
"""

import argparse
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from geo_infer_space.osc_geo.utils.repo_management import RepoManager

def main():
    parser = argparse.ArgumentParser(description='Setup all OS-Climate repositories')
    parser.add_argument('--output-dir', '-o', 
                       help='Output directory for repositories (default: ./repo)')
    parser.add_argument('--skip-tests', action='store_true',
                       help='Skip running tests after setup')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose output')
    
    args = parser.parse_args()
    
    # Set output directory
    if args.output_dir:
        os.environ['OSC_REPOS_DIR'] = args.output_dir
    
    try:
        manager = RepoManager(verbose=args.verbose)
        success = manager.run_all()
        
        if success and not args.skip_tests:
            print("Running tests for all repositories...")
            test_success = True
            for repo_name in manager.osc_repos.keys():
                if not manager.run_repo_tests(repo_name=repo_name):
                    test_success = False
            
            if not test_success:
                print("Some tests failed. Check the output above for details.")
                sys.exit(1)
        
        if success:
            print("All repositories set up successfully!")
        else:
            print("Some repositories failed to set up. Check the output above for details.")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error during setup: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 