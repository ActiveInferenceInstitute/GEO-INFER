#!/usr/bin/env python3
"""
OS Climate Status Script

This script checks the status of OS Climate repositories and generates a report.
It can be used to verify that the repositories are correctly set up and functioning.
"""

import os
import sys
import logging
import argparse
import json
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("osc_status")

def import_modules():
    """Try different import strategies to load the required modules."""
    # Strategy 1: Direct import (assuming package is installed)
    try:
        from geo_infer_space.osc_geo import (
            check_integration_status,
            run_diagnostics,
            detailed_report
        )
        logger.info("Successfully imported from installed package")
        return check_integration_status, run_diagnostics, detailed_report
    except ImportError:
        logger.warning("Failed to import from installed package, trying alternative paths...")
    
    # Strategy 2: Add src directory to path and try direct import
    script_dir = Path(__file__).parent.resolve()
    src_path = script_dir / "src"
    if src_path.exists():
        sys.path.insert(0, str(src_path))
        try:
            from geo_infer_space.osc_geo import (
                check_integration_status,
                run_diagnostics,
                detailed_report
            )
            logger.info("Successfully imported modules from src directory")
            return check_integration_status, run_diagnostics, detailed_report
        except ImportError:
            logger.warning("Failed to import from src directory")
    
    # Strategy 3: Try to import directly from relative path
    try:
        sys.path.insert(0, str(script_dir))
        from src.geo_infer_space.osc_geo.core.status import (
            check_integration_status,
            run_diagnostics,
            detailed_report
        )
        logger.info("Successfully imported from explicit core.status module")
        return check_integration_status, run_diagnostics, detailed_report
    except ImportError as e:
        logger.warning(f"Failed to import from explicit path: {e}")
    
    # Strategy 4: Try parent directory
    parent_dir = script_dir.parent
    if parent_dir.exists():
        sys.path.insert(0, str(parent_dir))
        try:
            # Fix the invalid module name with hyphens
            module_path = str(parent_dir / "GEO-INFER-SPACE" / "src")
            if os.path.exists(module_path):
                sys.path.insert(0, module_path)
                from geo_infer_space.osc_geo import (
                    check_integration_status,
                    run_diagnostics,
                    detailed_report
                )
                logger.info("Successfully imported modules from parent directory")
                return check_integration_status, run_diagnostics, detailed_report
        except ImportError:
            logger.warning("Failed to import from parent directory")
    
    # Strategy 5: Try to install the package
    try:
        logger.info("Attempting to install the package...")
        import subprocess
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-e", "."],
            cwd=str(script_dir),
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            logger.info("Package installed successfully, trying import again")
            try:
                from geo_infer_space.osc_geo import (
                    check_integration_status,
                    run_diagnostics,
                    detailed_report
                )
                logger.info("Successfully imported after installation")
                return check_integration_status, run_diagnostics, detailed_report
            except ImportError:
                logger.warning("Still failed to import after installation")
    except Exception as install_error:
        logger.error(f"Failed to install package: {install_error}")
    
    # Strategy 6: Last resort - try to import from core_status directly
    try:
        sys.path.insert(0, str(script_dir / "src" / "geo_infer_space" / "osc_geo" / "core"))
        from status import (
            check_integration_status,
            run_diagnostics,
            detailed_report
        )
        logger.info("Successfully imported directly from core/status.py")
        return check_integration_status, run_diagnostics, detailed_report
    except ImportError as e:
        logger.warning(f"Failed direct core status import: {e}")
    
    logger.error("All import strategies failed. Make sure GEO-INFER-SPACE is installed and in your Python path")
    sys.exit(1)

def get_osc_status(repos_dir=None):
    """Get the status of OS Climate repositories.
    
    Args:
        repos_dir: Optional path to the repositories directory.
                  If not provided, uses the default location.
    
    Returns:
        A status object containing repository information.
    """
    # Import required modules
    check_integration_status, run_diagnostics, detailed_report = import_modules()
    
    # Get the repository status
    status = check_integration_status(repos_dir)
    return status

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="OS Climate Status Script")
    parser.add_argument(
        "--output-file",
        help="Path to save the status report JSON file"
    )
    parser.add_argument(
        "--repos-dir",
        help="Base directory for OS Climate repositories"
    )
    parser.add_argument(
        "--detailed",
        action="store_true",
        help="Generate a detailed diagnostic report"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress output to console"
    )
    
    args = parser.parse_args()
    
    # Import required modules
    check_integration_status, run_diagnostics, detailed_report = import_modules()
    
    # Generate default filename if not specified
    if not args.output_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_dir = Path.cwd() / "reports"
        report_dir.mkdir(exist_ok=True)
        
        if args.detailed:
            args.output_file = str(report_dir / f"osc_diagnostics_{timestamp}.json")
        else:
            args.output_file = str(report_dir / f"osc_status_{timestamp}.json")
    elif args.output_file == "auto":
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_dir = Path.cwd() / "reports"
        report_dir.mkdir(exist_ok=True)
        
        if args.detailed:
            args.output_file = str(report_dir / f"osc_diagnostics_{timestamp}.json")
        else:
            args.output_file = str(report_dir / f"osc_status_{timestamp}.json")
    
    # Get the repository status
    if args.detailed:
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
    else:
        logger.info("Checking integration status...")
        status = check_integration_status(args.repos_dir)
        
        if not args.quiet:
            print(status.summary())
        
        # Save the report
        # Check if the object has a save_to_file method
        if hasattr(status, 'save_to_file'):
            status.save_to_file(args.output_file)
        else:
            # Fallback to manual JSON serialization
            status_dict = status.__dict__ if hasattr(status, '__dict__') else {"status": str(status)}
            with open(args.output_file, "w") as f:
                json.dump(status_dict, f, indent=2)
        
        # Highlight the report location
        report_path = os.path.abspath(args.output_file)
        logger.info(f"\n{'='*80}")
        logger.info(f"Status report saved to: {report_path}")
        logger.info(f"{'='*80}")
        
        # Consider it a success if all repositories exist
        return 0 if hasattr(status, 'all_repos_exist') and status.all_repos_exist else 1

if __name__ == "__main__":
    sys.exit(main()) 