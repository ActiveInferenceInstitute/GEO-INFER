#!/usr/bin/env python3
"""
OS Climate Wrapper Script

This script wraps the setup and status scripts to provide a unified interface
for working with OS Climate repositories.
"""

import os
import sys
import logging
import argparse
import subprocess
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def run_script(script_path, args=None, env=None):
    """Run a script and log its output."""
    if args is None:
        args = []
    
    cmd = [sys.executable, script_path] + args
    logger.info(f"Executing: {' '.join(cmd)}")
    
    try:
        # Merge environment variables if provided
        exec_env = os.environ.copy()
        if env:
            exec_env.update(env)
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=exec_env
        )
        
        # Process output in real-time
        for line in process.stdout:
            logger.info(f"SETUP: {line.strip()}")
        
        # Wait for process to complete
        process.wait()
        
        # Process any remaining stderr
        stderr_output = process.stderr.read()
        if stderr_output:
            for line in stderr_output.splitlines():
                logger.warning(f"SETUP ERR: {line.strip()}")
        
        if process.returncode != 0:
            logger.error(f"Script {script_path} failed with exit code {process.returncode}")
            return False
        
        return True
    except Exception as e:
        logger.error(f"Error running script {script_path}: {e}")
        return False

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="OS Climate Wrapper Script")
    parser.add_argument(
        "--skip-setup",
        action="store_true",
        help="Skip the setup steps"
    )
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Skip running tests"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Get the script directory
    script_dir = Path(__file__).parent.resolve()
    
    # Create reports directory if it doesn't exist
    reports_dir = script_dir / "reports"
    reports_dir.mkdir(exist_ok=True)
    
    # Generate timestamps for report files
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    setup_log = reports_dir / f"osc_setup_{timestamp}.log"
    setup_report = reports_dir / f"osc_setup_report_{timestamp}.json"
    status_report = reports_dir / f"osc_status_{timestamp}.json"
    
    success = True
    
    # Run the setup script
    if not args.skip_setup:
        logger.info("Running OSC setup script")
        
        setup_args = []
        if args.skip_tests:
            setup_args.append("--skip-tests")
        
        setup_args.extend([
            "--output-dir", str(reports_dir),
            "--report-file", str(setup_report)
        ])
        
        # Add Python path to include the current directory
        env = {"PYTHONPATH": str(script_dir.parent)}
        
        setup_success = run_script(
            str(script_dir / "osc_setup_all.py"),
            setup_args,
            env
        )
        
        if setup_success:
            logger.info("Setup completed successfully")
            logger.info(f"Setup log saved to: {setup_log}")
        else:
            logger.error("Setup failed")
            success = False
    
    # Check the status
    logger.info("Checking OSC repository status")
    
    # Use the new simple status script for more reliable execution
    status_script = script_dir / "osc_simple_status.py"
    status_args = [
        "--output-file", str(status_report)
    ]
    
    env = {"PYTHONPATH": str(script_dir.parent)}
    status_success = run_script(
        str(status_script),
        status_args,
        env
    )
    
    if not status_success:
        logger.warning("Some repositories may not be properly set up")
        success = False
    
    # Print summary
    logger.info("\nSUMMARY:")
    logger.info("=" * 40)
    
    if not args.skip_setup:
        logger.info(f"Setup log: {setup_log}")
    
    logger.info(f"Status report: {status_report}")
    logger.info("=" * 40)
    
    return 0 if success else 1

class OSCWrapper:
    """Wrapper class for OS Climate repository management."""
    
    def __init__(self, repos_dir=None):
        """Initialize the wrapper.
        
        Args:
            repos_dir: Optional path to the repositories directory.
                      If not provided, uses the default location.
        """
        self.repos_dir = repos_dir
        self.script_dir = Path(__file__).parent.resolve()
        self.reports_dir = self.script_dir / "reports"
        self.reports_dir.mkdir(exist_ok=True)
    
    def run_script(self, script_path, args=None, env=None):
        """Run a script and log its output."""
        return run_script(script_path, args, env)
    
    def setup(self, skip_tests=False):
        """Set up the OS Climate repositories.
        
        Args:
            skip_tests: Whether to skip running tests.
        
        Returns:
            True if setup was successful, False otherwise.
        """
        logger.info("Running OSC setup script")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        setup_report = self.reports_dir / f"osc_setup_report_{timestamp}.json"
        
        setup_args = []
        if skip_tests:
            setup_args.append("--skip-tests")
        
        setup_args.extend([
            "--output-dir", str(self.reports_dir),
            "--report-file", str(setup_report)
        ])
        
        if self.repos_dir:
            setup_args.extend(["--repos-dir", str(self.repos_dir)])
        
        env = {"PYTHONPATH": str(self.script_dir.parent)}
        
        return self.run_script(
            str(self.script_dir / "osc_setup_all.py"),
            setup_args,
            env
        )
    
    def check_status(self, detailed=False):
        """Check the status of OS Climate repositories.
        
        Args:
            detailed: Whether to generate a detailed diagnostic report.
        
        Returns:
            True if status check was successful, False otherwise.
        """
        logger.info("Checking OSC repository status")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        status_report = self.reports_dir / f"osc_status_{timestamp}.json"
        
        status_args = [
            "--output-file", str(status_report)
        ]
        
        if self.repos_dir:
            status_args.extend(["--repos-dir", str(self.repos_dir)])
        
        if detailed:
            status_args.append("--detailed")
        
        env = {"PYTHONPATH": str(self.script_dir.parent)}
        script = self.script_dir / ("osc_diagnostics.py" if detailed else "osc_simple_status.py")
        
        return self.run_script(str(script), status_args, env)

if __name__ == "__main__":
    sys.exit(main())
