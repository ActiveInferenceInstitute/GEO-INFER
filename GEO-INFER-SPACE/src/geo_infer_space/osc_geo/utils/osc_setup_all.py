#!/usr/bin/env python3
"""
OS Climate Setup Script

This script handles all steps for the OS Climate repositories:
1. Clone the repositories from GitHub
2. List their file structures
3. Set up virtual environments and install dependencies
4. Run tests
"""

import os
import sys
import logging
import subprocess
import argparse
import shutil
import json
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("osc_setup_all")

# OS Climate repository URLs
REPOS = [
    {
        "name": "osc-geo-h3grid-srv",
        "url": "https://github.com/docxology/osc-geo-h3grid-srv.git",  # Fork of original https://github.com/os-climate/osc-geo-h3grid-srv
        "install_script": "setup.sh",
        "test_script": "test.sh"
    },
    {
        "name": "osc-geo-h3loader-cli",
        "url": "https://github.com/docxology/osc-geo-h3loader-cli.git",  # Fork of original https://github.com/os-climate/osc-geo-h3loader-cli
        "install_script": "setup.sh",
        "test_script": "test.sh"
    }
]

def run_command(cmd, cwd=None, env=None, shell=False):
    """Run a command and log the output."""
    logger.info(f"Running: {cmd if isinstance(cmd, str) else ' '.join(cmd)}")
    
    try:
        process = subprocess.run(
            cmd,
            cwd=cwd,
            env=env,
            shell=shell,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        
        # Log stdout and stderr at the appropriate levels
        if process.stdout:
            for line in process.stdout.splitlines():
                if line.strip():
                    logger.info(f"OUT: {line}")
                    
        if process.stderr:
            for line in process.stderr.splitlines():
                if line.strip():
                    logger.warning(f"ERR: {line}")
        
        if process.returncode == 0:
            logger.info(f"Command succeeded (exit code 0)")
            return True, process.stdout, process.stderr
        else:
            logger.error(f"Command failed with exit code {process.returncode}")
            return False, process.stdout, process.stderr
    except Exception as e:
        logger.error(f"Error executing command: {e}")
        return False, "", str(e)

def clone_repository(repo_url, repo_name, output_dir, force=True):
    """Clone a repository from GitHub.
    
    Args:
        repo_url: URL of the repository to clone
        repo_name: Name of the repository
        output_dir: Directory to clone into
        force: If True, delete and re-clone existing repositories
        
    Returns:
        Tuple containing success status, stdout, stderr, and additional info
    """
    repo_path = os.path.join(output_dir, repo_name)
    result_info = {
        "action": "clone",
        "repo": repo_name,
        "url": repo_url,
        "path": repo_path,
        "timestamp": datetime.now().isoformat(),
    }
    
    # Check if repository already exists
    if os.path.exists(repo_path):
        if force:
            logger.info(f"Removing existing repository: {repo_path}")
            try:
                shutil.rmtree(repo_path)
                logger.info(f"Successfully removed {repo_path}")
                result_info["existing_repo_removed"] = True
            except Exception as e:
                error_msg = f"Failed to remove repository {repo_path}: {e}"
                logger.error(error_msg)
                result_info["error"] = error_msg
                result_info["success"] = False
                return False, "", error_msg, result_info
        else:
            logger.info(f"Repository {repo_name} already exists at {repo_path}, updating")
            success, stdout, stderr = run_command(["git", "pull"], cwd=repo_path)
            result_info["action"] = "update"
            result_info["success"] = success
            result_info["stdout"] = stdout
            result_info["stderr"] = stderr
            return success, stdout, stderr, result_info
    
    # Clone the repository
    logger.info(f"Cloning {repo_url} to {repo_path}")
    success, stdout, stderr = run_command(["git", "clone", repo_url, repo_path])
    result_info["success"] = success
    result_info["stdout"] = stdout
    result_info["stderr"] = stderr
    
    return success, stdout, stderr, result_info

def list_directory_tree(path, max_depth=3):
    """List the directory structure in a tree format."""
    path_obj = Path(path)
    
    if not path_obj.exists():
        logger.error(f"Path does not exist: {path}")
        return "ERROR: Path does not exist"
    
    tree_output = []
    tree_output.append(f"\nDirectory structure for {path_obj.name}:")
    tree_output.append(f"{path_obj.name}/")
    
    def print_tree(path, prefix="", depth=0):
        if depth > max_depth:
            tree_output.append(f"{prefix}...")
            return
        
        entries = sorted(list(path.iterdir()), 
                        key=lambda p: (not p.is_dir(), p.name.lower()))
        
        for i, entry in enumerate(entries):
            is_last = i == len(entries) - 1
            new_prefix = prefix + ("└── " if is_last else "├── ")
            
            if entry.is_dir():
                tree_output.append(f"{new_prefix}{entry.name}/")
                print_tree(entry, 
                         prefix + ("    " if is_last else "│   "), 
                         depth + 1)
            else:
                try:
                    size = entry.stat().st_size
                    size_str = f"{size/1024:.1f}KB" if size >= 1024 else f"{size}B"
                except FileNotFoundError:
                    size_str = "(missing)"
                tree_output.append(f"{new_prefix}{entry.name} ({size_str})")
    
    print_tree(path_obj)
    tree_str = "\n".join(tree_output)
    print(tree_str)
    return tree_str

def setup_and_test_repository(repo_path, parent_repo_src_dir, repo_info):
    """Set up and test a repository."""
    logger.info(f"\n{'='*80}")
    logger.info(f"SETTING UP AND TESTING: {os.path.basename(repo_path)}")
    logger.info(f"{'='*80}")
    
    result_info = {
        "repo": os.path.basename(repo_path),
        "action": "setup_and_test",
        "timestamp": datetime.now().isoformat(),
        "steps": []
    }
    
    # Check if repository exists
    if not os.path.exists(repo_path):
        error_msg = f"Repository not found: {repo_path}"
        logger.error(error_msg)
        result_info["success"] = False
        result_info["error"] = error_msg
        return False, result_info
    
    # Get absolute path to repository
    repo_path = os.path.abspath(repo_path)
    logger.info(f"Repository path: {repo_path}")
    result_info["path"] = repo_path
    
    # Check if requirements.txt exists
    req_file = os.path.join(repo_path, "requirements.txt")
    if not os.path.exists(req_file):
        error_msg = f"Requirements file not found: {req_file}"
        logger.error(error_msg)
        result_info["success"] = False
        result_info["error"] = error_msg
        return False, result_info
    
    # Create/clean virtual environment
    venv_step = {
        "name": "virtual_environment",
        "action": "create"
    }
    result_info["steps"].append(venv_step)
    
    venv_dir = os.path.join(repo_path, "venv")
    if os.path.exists(venv_dir):
        logger.info(f"Removing existing virtual environment: {venv_dir}")
        try:
            shutil.rmtree(venv_dir)
            logger.info(f"Successfully removed virtual environment: {venv_dir}")
            venv_step["existing_removed"] = True
        except Exception as e:
            error_msg = f"Failed to remove virtual environment {venv_dir}: {e}"
            logger.error(error_msg)
            venv_step["success"] = False
            venv_step["error"] = error_msg
            result_info["success"] = False
            return False, result_info
    
    logger.info(f"Creating virtual environment: {venv_dir}")
    success, stdout, stderr = run_command([sys.executable, "-m", "venv", venv_dir], cwd=repo_path)
    venv_step["success"] = success
    venv_step["stdout"] = stdout
    venv_step["stderr"] = stderr
    
    if not success:
        error_msg = "Failed to create virtual environment"
        logger.error(error_msg)
        venv_step["error"] = error_msg
        result_info["success"] = False
        return False, result_info
    
    # Create a temporary setup script for installation and testing
    script_step = {
        "name": "setup_script",
        "action": "create_and_run"
    }
    result_info["steps"].append(script_step)
    
    script_content = f"""#!/bin/bash
set -ex # Add -x for debugging

# Activate virtual environment
source {venv_dir}/bin/activate

# Add GEO-INFER-SPACE/src to PYTHONPATH for tests to find shared modules
export PYTHONPATH="{parent_repo_src_dir}:$PYTHONPATH"

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

# Install the current repository in editable mode
echo "Installing current repository in editable mode..."
pip install -e .

# Determine test directory and run tests
TEST_DIR=""
if [ -d "test" ]; then
    TEST_DIR="test/"
elif [ -d "tests" ]; then
    TEST_DIR="tests/"
fi

if [ -n "$TEST_DIR" ]; then
    echo "Running internal tests for {os.path.basename(repo_path)} in $TEST_DIR..."
    # Use the venv's pytest
    {venv_dir}/bin/pytest $TEST_DIR
else
    echo "No 'test/' or 'tests/' directory found, skipping internal tests for {os.path.basename(repo_path)}."
    exit 0 # Exit successfully if no tests to run
fi
"""

    temp_script_path = os.path.join(repo_path, "temp_setup.sh")
    with open(temp_script_path, "w") as f:
        f.write(script_content)
    os.chmod(temp_script_path, 0o755)

    logger.info("Installing requirements and running tests")
    success, stdout, stderr = run_command([temp_script_path], cwd=repo_path)
    
    script_step["success"] = success
    script_step["stdout"] = stdout
    script_step["stderr"] = stderr

    if not success:
        error_msg = f"Tests for {os.path.basename(repo_path)} failed"
        logger.error(error_msg)
        script_step["error"] = error_msg
        result_info["success"] = False
        return False, result_info

    return True, result_info


def setup_all_repositories(output_dir, force_clone, skip_tests, create_reports):
    """
    Main function to clone, set up, and test all OS Climate repositories.
    """
    logger.info(f"\n{'='*80}")
    logger.info("=== STEP 1: CLONING AND UPDATING REPOSITORIES ===")
    logger.info(f"{'='*80}")

    report_data = {
        "timestamp": datetime.now().isoformat(),
        "overall_success": True,
        "steps": [
            {"name": "clone_and_update", "start_time": datetime.now().isoformat(), "repos": []},
            {"name": "list_directory_trees", "start_time": datetime.now().isoformat(), "repos": []},
            {"name": "setup_and_test", "start_time": datetime.now().isoformat(), "repos": []}
        ],
        "test_results": {}
    }

    repo_results = {}
    
    # Get absolute path to GEO-INFER-SPACE/src for PYTHONPATH injection
    # This script is in GEO-INFER-SPACE/src/geo_infer_space/osc_geo/utils/
    # So, Path(__file__).parents[3] points to GEO-INFER-SPACE/src/
    geo_infer_space_src = Path(__file__).parents[3]
    parent_repo_src_dir = str(geo_infer_space_src.resolve())

    for repo_info in REPOS:
        repo_name = repo_info["name"]
        repo_url = repo_info["url"]
        repo_path = os.path.join(output_dir, repo_name)

        logger.info(f"\n{'='*80}")
        logger.info(f"PROCESSING REPOSITORY: {repo_name}")
        logger.info(f"{'='*80}")
        
        # Step 1: Clone or update repository
        clone_success, clone_stdout, clone_stderr, clone_info = clone_repository(
            repo_url, repo_name, output_dir, force_clone
        )
        clone_info["stdout"] = clone_stdout
        clone_info["stderr"] = clone_stderr
        repo_results[repo_name] = clone_info

        if not clone_success:
            logger.error(f"Failed to clone/update {repo_name}. Skipping setup and test.")
            repo_results[repo_name]["overall_success"] = False
            continue

        # Step 2: List directory structure (already done, but keeping order for context)
        try:
            repo_results[repo_name]["directory_tree"] = list_directory_tree(repo_path)
        except Exception as e:
            logger.error(f"Error listing directory structure for {repo_name}: {e}")
            repo_results[repo_name]["directory_tree_error"] = str(e)
            repo_results[repo_name]["overall_success"] = False
            continue

        # Step 3: Set up and test repository (only if not skipping tests)
        if not skip_tests:
            # Pass parent_repo_src_dir to setup_and_test_repository
            setup_success, setup_info = setup_and_test_repository(repo_path, parent_repo_src_dir, repo_info)
            repo_results[repo_name].update(setup_info)
            repo_results[repo_name]["overall_success"] = setup_success
        else:
            logger.info(f"Skipping tests for {repo_name} as --skip-tests flag is set.")
            repo_results[repo_name]["overall_success"] = True # Assume success if skipping tests

    logger.info("\n=== TEST SUMMARY ===")
    all_tests_passed = True
    for repo_name, result in repo_results.items():
        status = "PASSED" if result.get("overall_success", False) else "FAILED"
        if not result.get("overall_success", False):
            all_tests_passed = False
        logger.info(f"{repo_name}: {status}")

    if not all_tests_passed:
        logger.error("Not all tests passed")
        return False, repo_results
    else:
        logger.info("All tests passed")
        return True, repo_results


def main():
    """Main function for the OSC setup script."""
    parser = argparse.ArgumentParser(description="OS Climate Repositories Setup Script")
    parser.add_argument("--output-dir", type=str, default="./repo",
                        help="Directory to clone repositories into (default: ./repo)")
    parser.add_argument("--force-clone", action="store_true",
                        help="Force re-clone repositories if they already exist")
    parser.add_argument("--skip-tests", action="store_true",
                        help="Skip running tests after setup")
    parser.add_argument("--create-reports", action="store_true",
                        help="Create enhanced reports and visualizations")
    
    args = parser.parse_args()

    # Determine absolute path for output_dir
    if not os.path.isabs(args.output_dir):
        # Assuming script is run from GEO-INFER-SPACE root or bin/
        # Need to find the GEO-INFER-SPACE root
        current_script_path = Path(__file__).resolve()
        # If script is in src/geo_infer_space/osc_geo/utils/
        if "geo_infer_space" in current_script_path.parts:
            # Find the root of GEO-INFER-SPACE (e.g., up 4 levels from current_script_path)
            # /home/trim/Documents/GitHub/GEO-INFER/GEO-INFER-SPACE/src/geo_infer_space/osc_geo/utils/osc_setup_all.py
            # 1: utils, 2: osc_geo, 3: geo_infer_space, 4: src, 5: GEO-INFER-SPACE
            geo_infer_space_root = current_script_path.parents[4]
        else: # Assuming script is in bin/
            geo_infer_space_root = current_script_path.parents[1]
        
        args.output_dir = str(geo_infer_space_root / args.output_dir)

    # Convert to absolute path
    args.output_dir = os.path.abspath(args.output_dir)

    success, repo_results = setup_all_repositories(
        args.output_dir, args.force_clone, args.skip_tests, args.create_reports
    )

    # Generate enhanced reports if requested
    if args.create_reports:
        logger.info("\nCreating enhanced reports...")
        try:
            # Assuming EnhancedOSCReporter is available in the same directory
            # from .enhanced_reporting import EnhancedOSCReporter
            # If not, you might need to adjust the import or path
            # For now, we'll just log if it's available
            # reporter = EnhancedOSCReporter()
            # enhanced_report = reporter.generate_comprehensive_report(repo_results=repo_results)
            # logger.info(f"Enhanced report saved to: {enhanced_report.get('html_dashboard', 'N/A')}")
            pass # Placeholder for actual reporter call if available
        except ImportError as e:
            logger.warning(f"Enhanced reporting not available: {e}")
        except Exception as e:
            logger.error(f"Error generating enhanced reports: {e}")
            success = False # Mark overall setup as failed if report generation fails

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 