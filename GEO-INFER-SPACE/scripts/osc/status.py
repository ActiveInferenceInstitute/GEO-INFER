#!/usr/bin/env python3
"""
OS-Climate Repository Status Script

This script reports the status of all OS-Climate repositories.
"""

import sys
import os

# Prefer installed packages; avoid prepending local src to prevent shadowing third-party packages like h3

from geo_infer_space.osc_geo.utils.repo_management import RepoManager
from geo_infer_space.osc_geo.utils.enhanced_reporting import generate_enhanced_status_report

def main():
    try:
        manager = RepoManager()
        
        print("=== OS-Climate Repository Status ===\n")
        
        # Check repository status
        # Report configured repos; detailed statuses are emitted by the reporter
        for repo_name in manager.osc_repos.keys():
            print(f"- {repo_name}")
        
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