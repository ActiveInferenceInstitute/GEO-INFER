#!/usr/bin/env python3
"""
OS-Climate Repository Status Script

This script reports the status of all OS-Climate repositories.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from geo_infer_space.osc_geo.utils.repo_management import RepoManager
from geo_infer_space.osc_geo.utils.enhanced_reporting import generate_enhanced_status_report

def main():
    try:
        manager = RepoManager()
        
        print("=== OS-Climate Repository Status ===\n")
        
        # Check repository status
        for repo_name, repo_info in manager.osc_repos.items():
            repo_path = manager.get_repo_path(repo_name)
            if repo_path and os.path.exists(repo_path):
                print(f"✅ {repo_name}: Found at {repo_path}")
            else:
                print(f"❌ {repo_name}: Not found")
        
        print("\n=== Enhanced Status Report ===\n")
        
        # Generate enhanced report
        report = generate_enhanced_status_report()
        print("Enhanced status report generated successfully!")
        print(f"Report saved to: {report.get('report_metadata', {}).get('timestamp', 'Unknown')}")
        
    except Exception as e:
        print(f"Error generating status report: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 