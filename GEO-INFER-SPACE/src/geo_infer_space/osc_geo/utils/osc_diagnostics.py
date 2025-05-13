#!/usr/bin/env python3
"""
OS Climate Diagnostics Script

This script runs diagnostics on the OS Climate repositories and generates a detailed report.
It's designed to be run from the GEO-INFER-SPACE directory and directly imports the status module.
"""

import os
import sys
import logging
import argparse
import json
from datetime import datetime
from pathlib import Path
import subprocess

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("osc_diagnostics")

def install_dependencies():
    """Install required dependencies if they're not already installed."""
    try:
        import git
        logger.info("GitPython is already installed.")
    except ImportError:
        logger.info("Installing GitPython...")
        subprocess.run([sys.executable, "-m", "pip", "install", "gitpython"], check=True)
        logger.info("GitPython installed successfully.")

def import_status_module():
    """Import the status module directly from its location."""
    # Get the script directory
    script_dir = Path(__file__).parent.resolve()
    
    # Path to the status.py module
    status_module_path = script_dir / "src" / "geo_infer_space" / "osc_geo" / "core"
    
    # Add to path
    sys.path.insert(0, str(status_module_path))
    
    try:
        # Install dependencies first
        install_dependencies()
        
        # Now import the status module
        from status import check_integration_status, run_diagnostics, detailed_report
        logger.info("Successfully imported status module directly")
        return check_integration_status, run_diagnostics, detailed_report
    except ImportError as e:
        logger.error(f"Failed to import from status module: {e}")
        sys.exit(1)

def run_diagnostics(repos_dir=None):
    """Run diagnostics on OS Climate repositories.
    
    Args:
        repos_dir: Optional path to the repositories directory.
                  If not provided, uses the default location.
    
    Returns:
        A dictionary containing diagnostic results.
    """
    # Import required modules
    check_integration_status, run_diagnostics, detailed_report = import_status_module()
    
    # Run diagnostics
    results = run_diagnostics(repos_dir)
    return results

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="OS Climate Diagnostics Script")
    parser.add_argument(
        "--output-file",
        help="Path to save the diagnostics report JSON file"
    )
    parser.add_argument(
        "--repos-dir",
        help="Base directory for OS Climate repositories"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress output to console"
    )
    
    args = parser.parse_args()
    
    # Generate default filename if not specified
    if not args.output_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_dir = Path.cwd() / "reports"
        report_dir.mkdir(exist_ok=True)
        args.output_file = str(report_dir / f"osc_diagnostics_{timestamp}.json")
    
    # Run diagnostics
    logger.info("Running diagnostics...")
    results = run_diagnostics(args.repos_dir)
    
    if not args.quiet:
        report = detailed_report(results)
        print(report)
    
    # Save the report
    with open(args.output_file, "w") as f:
        json.dump(results, f, indent=2)
    
    # Highlight the report location
    report_path = os.path.abspath(args.output_file)
    logger.info(f"\n{'='*80}")
    logger.info(f"Diagnostics report saved to: {report_path}")
    logger.info(f"{'='*80}")
    
    # Consider it a success if there are no critical issues
    critical_issues = [issue for issue in results.get("issues", []) 
                      if issue.get("level", "WARNING") == "ERROR"]
    return 0 if not critical_issues else 1

if __name__ == "__main__":
    sys.exit(main()) 