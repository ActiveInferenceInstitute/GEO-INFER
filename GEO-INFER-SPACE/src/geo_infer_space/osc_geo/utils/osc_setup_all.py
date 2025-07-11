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
                size = entry.stat().st_size
                size_str = f"{size/1024:.1f}KB" if size >= 1024 else f"{size}B"
                tree_output.append(f"{new_prefix}{entry.name} ({size_str})")
    
    print_tree(path_obj)
    tree_str = "\n".join(tree_output)
    print(tree_str)
    return tree_str

def setup_and_test_repository(repo_path):
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
    
    # Create a temporary setup script that bypasses the repository scripts
    script_step = {
        "name": "setup_script",
        "action": "create_and_run"
    }
    result_info["steps"].append(script_step)
    
    temp_script = os.path.join(repo_path, "temp_setup.sh")
    with open(temp_script, "w") as f:
        f.write(f"""#!/bin/bash
set -e
cd {repo_path}

# Activate virtual environment directly
source {os.path.join(venv_dir, 'bin', 'activate')}

# Set up environment variables
export HOME_DIR="{os.path.expanduser('~')}"
export PROJECT_DIR="{repo_path}"
export PROJECT="{os.path.basename(repo_path)}"
export PYTHONPATH={repo_path}:$PYTHONPATH

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

# Create minimal setup.py if needed
if [ ! -f "setup.py" ]; then
    echo "Creating minimal setup.py for installation..."
    cat > setup.py << EOF
from setuptools import setup, find_packages
setup(
    name="{os.path.basename(repo_path)}",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={{"": "src"}},
)
EOF
fi

# Install the package in development mode
pip install -e .

# Run tests
echo ""
echo "Running tests for {os.path.basename(repo_path)}..."
python -m pytest test/ -v
TEST_EXIT_CODE=$?

# Report results
if [ $TEST_EXIT_CODE -eq 0 ]; then
  echo "TEST SUMMARY: All tests passed successfully!"
else
  echo "TEST SUMMARY: Tests failed with exit code $TEST_EXIT_CODE"
fi

exit $TEST_EXIT_CODE
""")
    
    # Make the script executable
    os.chmod(temp_script, 0o755)
    script_step["script_path"] = temp_script
    
    # Run the script
    logger.info("Installing requirements and running tests")
    success, stdout, stderr = run_command([temp_script], cwd=repo_path, shell=True)
    script_step["success"] = success
    script_step["stdout"] = stdout
    script_step["stderr"] = stderr
    
    # Report test results
    if success:
        logger.info(f"Tests for {os.path.basename(repo_path)} completed successfully")
        result_info["tests_passed"] = True
    else:
        logger.error(f"Tests for {os.path.basename(repo_path)} failed")
        result_info["tests_passed"] = False
    
    # Clean up
    cleanup_step = {
        "name": "cleanup",
        "action": "remove_temp_script"
    }
    result_info["steps"].append(cleanup_step)
    
    try:
        os.remove(temp_script)
        cleanup_step["success"] = True
    except Exception as e:
        logger.warning(f"Failed to remove temporary script {temp_script}: {e}")
        cleanup_step["success"] = False
        cleanup_step["error"] = str(e)
    
    result_info["success"] = success
    return success, result_info

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="OS Climate Setup and Test Script")
    parser.add_argument(
        "--output-dir",
        default="./ext",
        help="Directory to clone repositories into"
    )
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Skip running tests"
    )
    parser.add_argument(
        "--force-clone",
        action="store_true",
        help="Force re-cloning of repositories even if they exist"
    )
    parser.add_argument(
        "--report-file",
        help="Path to save the detailed report (default: auto-generated)"
    )
    
    args = parser.parse_args()
    
    # Create a reports directory if it doesn't exist
    script_dir = Path(__file__).parent.resolve()
    reports_dir = script_dir / "reports"
    reports_dir.mkdir(exist_ok=True)
    
    # Generate a report filename if not provided
    if not args.report_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        args.report_file = str(reports_dir / f"osc_setup_report_{timestamp}.json")
    
    # Initialize report data
    report_data = {
        "timestamp": datetime.now().isoformat(),
        "command": " ".join(sys.argv),
        "args": vars(args),
        "repos": [],
        "steps": [],
        "test_results": {}
    }
    
    # Ensure the output directory exists
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Step 1: Clone the repositories
    logger.info("\n=== STEP 1: CLONING OS CLIMATE REPOSITORIES ===")
    report_data["steps"].append({
        "name": "clone_repositories",
        "start_time": datetime.now().isoformat()
    })
    
    all_cloned = True
    clone_results = {}
    
    for repo in REPOS:
        success, stdout, stderr, clone_info = clone_repository(
            repo["url"], 
            repo["name"], 
            args.output_dir, 
            force=args.force_clone
        )
        
        clone_results[repo["name"]] = success
        report_data["repos"].append(clone_info)
        
        if not success:
            logger.error(f"Failed to clone {repo['name']}")
            all_cloned = False
    
    report_data["steps"][-1]["end_time"] = datetime.now().isoformat()
    report_data["steps"][-1]["success"] = all_cloned
    
    if not all_cloned:
        logger.error("Failed to clone all repositories")
        report_data["overall_success"] = False
        
        # Save the report before exiting
        with open(args.report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        logger.info(f"\n{'='*80}")
        logger.info(f"Setup report saved to: {os.path.abspath(args.report_file)}")
        logger.info(f"{'='*80}")
        
        return 1
    
    # Step 2: List the repositories' file structures
    logger.info("\n=== STEP 2: LISTING REPOSITORY STRUCTURES ===")
    report_data["steps"].append({
        "name": "list_structures",
        "start_time": datetime.now().isoformat()
    })
    
    listing_errors = False
    directory_structures = {}
    
    for repo in REPOS:
        repo_path = os.path.join(args.output_dir, repo["name"])
        try:
            tree_output = list_directory_tree(repo_path)
            directory_structures[repo["name"]] = tree_output
        except Exception as e:
            logger.error(f"Error listing directory structure for {repo['name']}: {e}")
            directory_structures[repo["name"]] = f"ERROR: {str(e)}"
            listing_errors = True
    
    report_data["steps"][-1]["end_time"] = datetime.now().isoformat()
    report_data["steps"][-1]["success"] = not listing_errors
    report_data["directory_structures"] = directory_structures
    
    # Note: We continue even if directory listing fails
    
    # Step 3: Set up and test each repository
    if not args.skip_tests:
        logger.info("\n=== STEP 3: SETTING UP AND TESTING REPOSITORIES ===")
        report_data["steps"].append({
            "name": "setup_and_test",
            "start_time": datetime.now().isoformat()
        })
        
        test_results = {}
        for repo in REPOS:
            repo_path = os.path.join(args.output_dir, repo["name"])
            try:
                test_success, result_info = setup_and_test_repository(repo_path)
                test_results[repo["name"]] = test_success
                report_data["test_results"][repo["name"]] = result_info
                
                if not test_success:
                    logger.error(f"Failed to set up and test {repo['name']}")
            except Exception as e:
                logger.error(f"Error during setup and test for {repo['name']}: {e}")
                test_results[repo["name"]] = False
                report_data["test_results"][repo["name"]] = {
                    "success": False,
                    "error": str(e),
                    "repo": repo["name"],
                    "timestamp": datetime.now().isoformat()
                }
        
        report_data["steps"][-1]["end_time"] = datetime.now().isoformat()
        report_data["steps"][-1]["success"] = all(test_results.values())
        
        # Display test summary
        logger.info("\n=== TEST SUMMARY ===")
        all_tests_passed = True
        for repo_name, success in test_results.items():
            status = "PASSED" if success else "FAILED"
            logger.info(f"{repo_name}: {status}")
            if not success:
                all_tests_passed = False
        
        report_data["all_tests_passed"] = all_tests_passed
        
        if not all_tests_passed:
            logger.error("Not all tests passed")
            report_data["overall_success"] = False
            
            # Save the report before exiting
            with open(args.report_file, 'w') as f:
                json.dump(report_data, f, indent=2)
            
            logger.info(f"\n{'='*80}")
            logger.info(f"Setup report saved to: {os.path.abspath(args.report_file)}")
            logger.info(f"{'='*80}")
            
            return 1
    
    # Overall success
    report_data["overall_success"] = True
    
    # Success message, but include a warning if listing had errors
    if listing_errors:
        logger.warning("\n=== COMPLETED WITH WARNINGS ===")
        logger.warning("OS Climate repositories have been cloned successfully, but there were issues listing some files.")
    else:
        logger.info("\n=== COMPLETE ===")
        logger.info("OS Climate repositories have been cloned, listed, and tested successfully.")
    
    # Save the final report
    with open(args.report_file, 'w') as f:
        json.dump(report_data, f, indent=2)
    
    # Generate enhanced visualizations and reporting
    try:
        from .enhanced_reporting import EnhancedOSCReporter
        
        logger.info("\n=== GENERATING ENHANCED REPORTS AND VISUALIZATIONS ===")
        
        # Initialize enhanced reporter
        reporter = EnhancedOSCReporter(reports_dir)
        
        # Generate comprehensive report with visualizations
        comprehensive_report = reporter.generate_comprehensive_report(args.report_file)
        
        logger.info("✅ Enhanced status dashboard generated")
        logger.info("✅ Test analysis visualizations created")
        logger.info("✅ Interactive HTML report generated")
        
        if "comprehensive_html" in comprehensive_report:
            html_path = reports_dir / comprehensive_report["comprehensive_html"]
            logger.info(f"📊 Interactive dashboard: {html_path}")
        
        # Generate additional status visualizations
        status_report = reporter.generate_enhanced_status_report()
        if "html_dashboard" in status_report:
            dashboard_path = reports_dir / status_report["html_dashboard"]
            logger.info(f"📈 Status dashboard: {dashboard_path}")
            
    except ImportError as e:
        logger.warning(f"Enhanced reporting not available: {e}")
        logger.warning("Install matplotlib, seaborn for visualizations")
    except Exception as e:
        logger.error(f"Error generating enhanced reports: {e}")
    
    logger.info(f"\n{'='*80}")
    logger.info(f"Setup report saved to: {os.path.abspath(args.report_file)}")
    logger.info(f"Enhanced reports saved to: {reports_dir}")
    logger.info(f"{'='*80}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 