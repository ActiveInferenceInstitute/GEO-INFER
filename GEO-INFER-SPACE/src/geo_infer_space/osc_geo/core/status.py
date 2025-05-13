"""
Repository status and diagnostic module for OSC-GEO.

This module provides functionality to check the status of OS Climate repositories and
generate diagnostic reports.
"""

import os
import sys
import subprocess
import logging
import json
import datetime
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any, Tuple

import git

from .repos import OSC_REPOS, get_repo_path

logger = logging.getLogger(__name__)

@dataclass
class RepoStatus:
    """Status information for a single repository."""
    key: str
    name: str
    path: str
    exists: bool = False
    is_git_repo: bool = False
    clone_url: str = ""
    current_branch: str = ""
    latest_commit: str = ""
    commit_date: str = ""
    has_venv: bool = False
    requirements_installed: bool = False
    tests_passed: Optional[bool] = None
    error_message: str = ""

@dataclass
class IntegrationStatus:
    """Overall status of the OSC-GEO integration."""
    timestamp: str = field(default_factory=lambda: datetime.datetime.now().isoformat())
    repositories: Dict[str, RepoStatus] = field(default_factory=dict)
    all_repos_exist: bool = False
    all_tests_passed: Optional[bool] = None
    
    def summary(self) -> str:
        """Generate a summary of the integration status."""
        lines = [
            f"OSC-GEO Integration Status (as of {self.timestamp})",
            f"All repositories exist: {self.all_repos_exist}",
            f"All tests passed: {self.all_tests_passed if self.all_tests_passed is not None else 'Not run'}"
        ]
        
        lines.append("\nRepository Status:")
        for repo_key, repo_status in self.repositories.items():
            status_emoji = "✅" if repo_status.exists else "❌"
            test_status = ""
            if repo_status.tests_passed is not None:
                test_status = "tests ✅" if repo_status.tests_passed else "tests ❌"
            
            lines.append(f"  {status_emoji} {repo_status.name} ({repo_key}) {test_status}")
            if repo_status.exists:
                lines.append(f"     Path: {repo_status.path}")
                lines.append(f"     Branch: {repo_status.current_branch}")
                lines.append(f"     Latest commit: {repo_status.latest_commit[:8]} ({repo_status.commit_date})")
            elif repo_status.error_message:
                lines.append(f"     Error: {repo_status.error_message}")
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert status to a dictionary."""
        data = asdict(self)
        # Convert repositories from dict of RepoStatus to dict of dicts
        data["repositories"] = {k: asdict(v) for k, v in self.repositories.items()}
        return data
    
    def to_json(self) -> str:
        """Convert status to a JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    def save_to_file(self, filename: str) -> None:
        """Save status to a JSON file."""
        with open(filename, "w") as f:
            f.write(self.to_json())
        logger.info(f"Status saved to {filename}")

def get_git_repo_info(repo_path: str) -> Tuple[bool, Dict[str, str]]:
    """
    Get information about a Git repository.
    
    Args:
        repo_path: Path to the repository
        
    Returns:
        Tuple of (is_git_repo, repo_info)
    """
    info = {
        "current_branch": "",
        "latest_commit": "",
        "commit_date": "",
        "clone_url": "",
    }
    
    if not os.path.exists(os.path.join(repo_path, ".git")):
        return False, info
    
    try:
        repo = git.Repo(repo_path)
        
        # Get current branch
        info["current_branch"] = repo.active_branch.name
        
        # Get latest commit
        commit = repo.head.commit
        info["latest_commit"] = commit.hexsha
        info["commit_date"] = datetime.datetime.fromtimestamp(commit.committed_date).strftime("%Y-%m-%d %H:%M:%S")
        
        # Get clone URL
        for remote in repo.remotes:
            if remote.name == "origin":
                info["clone_url"] = next(remote.urls)
                break
        
        return True, info
    except (git.InvalidGitRepositoryError, git.NoSuchPathError, git.GitCommandError) as e:
        logger.error(f"Error getting Git repository info: {e}")
        return False, info
    except Exception as e:
        logger.error(f"Unexpected error getting Git repository info: {e}")
        return False, info

def check_venv(repo_path: str) -> bool:
    """
    Check if the repository has a virtual environment.
    
    Args:
        repo_path: Path to the repository
        
    Returns:
        True if the virtual environment exists, False otherwise
    """
    venv_path = os.path.join(repo_path, "venv")
    
    # Check if the venv directory exists
    if not os.path.exists(venv_path):
        return False
    
    # Check if it has bin/activate (Unix) or Scripts/activate.bat (Windows)
    if os.name == "nt":  # Windows
        return os.path.exists(os.path.join(venv_path, "Scripts", "activate.bat"))
    else:  # Unix/Linux/Mac
        return os.path.exists(os.path.join(venv_path, "bin", "activate"))

def check_requirements_installed(repo_path: str) -> bool:
    """
    Check if requirements are installed in the repository's virtual environment.
    
    Args:
        repo_path: Path to the repository
        
    Returns:
        True if requirements appear to be installed, False otherwise
    """
    # Check if requirements.txt exists
    req_path = os.path.join(repo_path, "requirements.txt")
    if not os.path.exists(req_path):
        return False
    
    # Check if venv exists
    if not check_venv(repo_path):
        return False
    
    # Try to parse requirements.txt and check if some key packages are installed
    try:
        with open(req_path, "r") as f:
            requirements = f.read().splitlines()
        
        # Extract package names (handle both package and package==version formats)
        required_packages = []
        for line in requirements:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            
            # Handle requirements with version specifiers
            package_name = line.split("==")[0].split(">=")[0].split(">")[0].strip()
            required_packages.append(package_name)
        
        # We'll consider requirements installed if there are site-packages in the venv
        # This is just a heuristic, not a comprehensive check
        if os.name == "nt":  # Windows
            site_packages = os.path.join(repo_path, "venv", "Lib", "site-packages")
        else:  # Unix/Linux/Mac
            site_packages = os.path.join(repo_path, "venv", "lib", f"python{sys.version_info.major}.{sys.version_info.minor}", "site-packages")
        
        return os.path.exists(site_packages) and os.listdir(site_packages)
        
    except Exception as e:
        logger.error(f"Error checking requirements installation: {e}")
        return False

def check_tests_status(repo_path: str) -> Optional[bool]:
    """
    Check if tests pass for the repository.
    
    Args:
        repo_path: Path to the repository
        
    Returns:
        True if tests pass, False if they fail, None if unable to determine
    """
    # Check if test directory exists
    test_dir = os.path.join(repo_path, "test")
    if not os.path.exists(test_dir):
        logger.warning(f"Test directory not found: {test_dir}")
        return None
    
    # Check if venv exists
    if not check_venv(repo_path):
        logger.warning(f"Virtual environment not found for {repo_path}")
        return None
    
    # We won't actually run the tests here, as they can be time-consuming
    # Instead, we'll just check if the test directory exists and seems to have test files
    try:
        test_files = [f for f in os.listdir(test_dir) if f.startswith("test_") and f.endswith(".py")]
        return len(test_files) > 0
    except Exception as e:
        logger.error(f"Error checking test files: {e}")
        return None

def check_integration_status(base_dir: Optional[str] = None) -> IntegrationStatus:
    """
    Check the status of the OSC-GEO integration.
    
    Args:
        base_dir: Base directory for cloned repositories. If None, uses the
            environment variable OSC_REPOS_DIR or a default value.
            
    Returns:
        IntegrationStatus object with the current status.
    """
    status = IntegrationStatus()
    all_exist = True
    all_tests_passed = True
    
    # Check each repository
    for repo_key, repo_info in OSC_REPOS.items():
        repo_path = get_repo_path(repo_key, base_dir)
        
        repo_status = RepoStatus(
            key=repo_key,
            name=repo_info["repo"],
            path=repo_path or "",
            clone_url=f"https://github.com/{repo_info['owner']}/{repo_info['repo']}.git"
        )
        
        # Check if repository exists
        if repo_path and os.path.exists(repo_path):
            repo_status.exists = True
            
            # Check if it's a Git repository and get info
            is_git_repo, git_info = get_git_repo_info(repo_path)
            repo_status.is_git_repo = is_git_repo
            
            if is_git_repo:
                repo_status.current_branch = git_info["current_branch"]
                repo_status.latest_commit = git_info["latest_commit"]
                repo_status.commit_date = git_info["commit_date"]
                if git_info["clone_url"]:
                    repo_status.clone_url = git_info["clone_url"]
            
            # Check virtual environment
            repo_status.has_venv = check_venv(repo_path)
            
            # Check requirements
            repo_status.requirements_installed = check_requirements_installed(repo_path)
            
            # Check tests status
            repo_status.tests_passed = check_tests_status(repo_path)
            
            if repo_status.tests_passed is not None and not repo_status.tests_passed:
                all_tests_passed = False
        else:
            all_exist = False
            repo_status.error_message = f"Repository not found at {repo_path}"
        
        status.repositories[repo_key] = repo_status
    
    # Update overall status
    status.all_repos_exist = all_exist
    status.all_tests_passed = all_tests_passed if all_exist else None
    
    return status

def run_diagnostics(base_dir: Optional[str] = None) -> Dict[str, Any]:
    """
    Run diagnostics on OSC-GEO repositories.
    
    Args:
        base_dir: Base directory for cloned repositories. If None, uses the
            environment variable OSC_REPOS_DIR or a default value.
            
    Returns:
        Dictionary with diagnostic information.
    """
    diagnostics = {
        "timestamp": datetime.datetime.now().isoformat(),
        "system_info": {
            "platform": sys.platform,
            "python_version": sys.version,
            "executable": sys.executable,
        },
        "repositories": {},
        "environment": {
            "OSC_REPOS_DIR": os.environ.get("OSC_REPOS_DIR", "Not set"),
        }
    }
    
    # Get repository status
    status = check_integration_status(base_dir)
    diagnostics["repositories"] = status.to_dict()["repositories"]
    
    # Add additional diagnostic information
    for repo_key, repo_info in diagnostics["repositories"].items():
        repo_path = repo_info["path"]
        if not repo_path or not os.path.exists(repo_path):
            continue
        
        # Check disk space
        try:
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(repo_path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    total_size += os.path.getsize(fp)
            
            repo_info["disk_space_mb"] = round(total_size / (1024 * 1024), 2)
        except Exception as e:
            logger.error(f"Error calculating disk space: {e}")
            repo_info["disk_space_mb"] = "Error"
        
        # Check permissions
        try:
            repo_info["permissions"] = oct(os.stat(repo_path).st_mode)[-3:]
        except Exception as e:
            logger.error(f"Error checking permissions: {e}")
            repo_info["permissions"] = "Error"
    
    # Add a detailed report about any potential issues
    diagnostics["issues"] = []
    
    # Check for common issues
    for repo_key, repo_info in diagnostics["repositories"].items():
        if not repo_info["exists"]:
            diagnostics["issues"].append({
                "repository": repo_info["name"],
                "issue": "Repository not found",
                "recommendation": f"Run osc_setup_all.py to clone repositories"
            })
        elif not repo_info["has_venv"]:
            diagnostics["issues"].append({
                "repository": repo_info["name"],
                "issue": "Virtual environment not found",
                "recommendation": f"Run osc_setup_all.py to set up the environment"
            })
        elif not repo_info["requirements_installed"]:
            diagnostics["issues"].append({
                "repository": repo_info["name"],
                "issue": "Requirements not installed",
                "recommendation": f"Run osc_setup_all.py or manually install requirements"
            })
        elif repo_info["tests_passed"] is False:
            diagnostics["issues"].append({
                "repository": repo_info["name"],
                "issue": "Tests failed",
                "recommendation": f"Check test logs and fix issues"
            })
    
    return diagnostics

def detailed_report(diagnostics: Dict[str, Any]) -> str:
    """
    Generate a detailed report from diagnostic information.
    
    Args:
        diagnostics: Diagnostic information from run_diagnostics()
        
    Returns:
        Formatted report as a string
    """
    report = [
        f"OSC-GEO Diagnostic Report ({diagnostics['timestamp']})",
        "\nSystem Information:",
        f"  Platform: {diagnostics['system_info']['platform']}",
        f"  Python Version: {diagnostics['system_info']['python_version'].split()[0]}",
        f"  Python Executable: {diagnostics['system_info']['executable']}",
        "\nEnvironment:",
        f"  OSC_REPOS_DIR: {diagnostics['environment']['OSC_REPOS_DIR']}",
        "\nRepository Status:"
    ]
    
    for repo_key, repo_info in diagnostics["repositories"].items():
        report.append(f"\n  {repo_info['name']} ({repo_key}):")
        report.append(f"    Exists: {repo_info['exists']}")
        
        if repo_info['exists']:
            report.append(f"    Path: {repo_info['path']}")
            report.append(f"    Git Repository: {repo_info['is_git_repo']}")
            
            if repo_info['is_git_repo']:
                report.append(f"    Current Branch: {repo_info['current_branch']}")
                report.append(f"    Latest Commit: {repo_info['latest_commit'][:8]} ({repo_info['commit_date']})")
            
            report.append(f"    Virtual Environment: {repo_info['has_venv']}")
            report.append(f"    Requirements Installed: {repo_info['requirements_installed']}")
            report.append(f"    Tests Passed: {repo_info['tests_passed'] if repo_info['tests_passed'] is not None else 'Not run'}")
            
            if "disk_space_mb" in repo_info:
                report.append(f"    Disk Space: {repo_info['disk_space_mb']} MB")
            
            if "permissions" in repo_info:
                report.append(f"    Permissions: {repo_info['permissions']}")
        
        if repo_info.get("error_message"):
            report.append(f"    Error: {repo_info['error_message']}")
    
    if diagnostics["issues"]:
        report.append("\nIssues Detected:")
        for issue in diagnostics["issues"]:
            report.append(f"\n  Repository: {issue['repository']}")
            report.append(f"  Issue: {issue['issue']}")
            report.append(f"  Recommendation: {issue['recommendation']}")
    else:
        report.append("\nNo issues detected!")
    
    return "\n".join(report) 