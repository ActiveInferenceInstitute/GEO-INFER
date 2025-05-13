#!/usr/bin/env python3
"""
Simple OS Climate Status Script

This script performs a basic check of the OS Climate repositories.
It checks if repositories exist and generates a report with their basic status.
"""

import os
import sys
import logging
import argparse
import json
import subprocess
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("geo_infer_space.osc_geo.utils.osc_simple_status")

# Define OSC repositories
OSC_REPOS = {
    "h3grid": {
        "name": "OS Climate H3 Grid Server",
        "clone_url": "https://github.com/os-climate/osc-geo-h3grid-srv.git",
        "branch": "main",
        "path": "ext/os-climate/osc-geo-h3grid-srv",
    },
    "h3loader": {
        "name": "OS Climate H3 Loader CLI",
        "clone_url": "https://github.com/os-climate/osc-geo-h3loader-cli.git",
        "branch": "main",
        "path": "ext/os-climate/osc-geo-h3loader-cli",
    }
}

def check_git_installed():
    """Check if Git is installed."""
    try:
        result = subprocess.run(
            ["git", "--version"], 
            capture_output=True, 
            text=True, 
            check=False
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False

def get_repo_info(repo_path):
    """Get basic information about a repository."""
    info = {
        "exists": False,
        "is_git_repo": False,
        "current_branch": "",
        "latest_commit": "",
        "has_venv": False,
    }
    
    # Check if directory exists
    if not os.path.exists(repo_path):
        return info
    
    info["exists"] = True
    
    # Check if it's a git repository
    if os.path.exists(os.path.join(repo_path, ".git")):
        info["is_git_repo"] = True
        
        # Try to get branch
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode == 0:
                info["current_branch"] = result.stdout.strip()
        except Exception:
            pass
        
        # Try to get latest commit
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode == 0:
                info["latest_commit"] = result.stdout.strip()
        except Exception:
            pass
    
    # Check if it has a venv
    info["has_venv"] = os.path.exists(os.path.join(repo_path, "venv"))
    
    return info

def check_repo_status():
    """Check the status of all OSC repositories."""
    status = {
        "timestamp": datetime.now().isoformat(),
        "repositories": {},
        "all_repos_exist": True,
    }
    
    for repo_key, repo_info in OSC_REPOS.items():
        path = os.path.normpath(os.path.join(os.getcwd(), repo_info["path"]))
        
        repo_status = {
            "key": repo_key,
            "name": repo_info["name"],
            "path": path,
            "clone_url": repo_info["clone_url"],
            **get_repo_info(path)
        }
        
        status["repositories"][repo_key] = repo_status
        
        if not repo_status["exists"]:
            status["all_repos_exist"] = False
    
    return status

def generate_summary(status):
    """Generate a human-readable summary of the repository status."""
    lines = [
        f"OSC Repository Status (as of {status['timestamp']})",
        f"All repositories exist: {status['all_repos_exist']}"
    ]
    
    lines.append("\nRepository Status:")
    for repo_key, repo_status in status["repositories"].items():
        status_emoji = "✅" if repo_status["exists"] else "❌"
        lines.append(f"  {status_emoji} {repo_status['name']} ({repo_key})")
        
        if repo_status["exists"]:
            lines.append(f"     Path: {repo_status['path']}")
            if repo_status["is_git_repo"]:
                lines.append(f"     Branch: {repo_status['current_branch']}")
                lines.append(f"     Latest commit: {repo_status['latest_commit'][:8]}")
            git_status = "✅" if repo_status["is_git_repo"] else "❌"
            venv_status = "✅" if repo_status["has_venv"] else "❌"
            lines.append(f"     Git repository: {git_status}  Virtual environment: {venv_status}")
    
    return "\n".join(lines)

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Simple OS Climate Status Script")
    parser.add_argument(
        "--output-file",
        help="Path to save the status report JSON file"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress output to console"
    )
    
    args = parser.parse_args()
    
    # Check if git is installed
    if not check_git_installed():
        logger.error("Git is not installed. Please install Git and try again.")
        return 1
    
    # Generate default filename if not specified
    if not args.output_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_dir = Path.cwd() / "reports"
        report_dir.mkdir(exist_ok=True)
        args.output_file = str(report_dir / f"osc_simple_status_{timestamp}.json")
    
    # Get the repository status
    status = check_repo_status()
    
    # Print summary
    if not args.quiet:
        summary = generate_summary(status)
        print(summary)
    
    # Save the report
    with open(args.output_file, "w") as f:
        json.dump(status, f, indent=2)
    
    # Highlight the report location
    report_path = os.path.abspath(args.output_file)
    logger.info(f"\n{'='*80}")
    logger.info(f"Status report saved to: {report_path}")
    logger.info(f"{'='*80}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 