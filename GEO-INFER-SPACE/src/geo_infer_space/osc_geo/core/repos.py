"""
Repository management module for OSC-GEO.

This module provides functionality to clone OS Climate geospatial repositories
directly using git commands.
"""

import os
import logging
import subprocess
from typing import Dict, List, Optional, Tuple, Union

logger = logging.getLogger(__name__)

# OS Climate repository URLs
OSC_REPOS = {
    "h3grid-srv": {
        "owner": "os-climate",
        "repo": "osc-geo-h3grid-srv",
        "branch": "main",
        "description": "H3 grid service for geospatial applications"
    },
    "h3loader-cli": {
        "owner": "os-climate",
        "repo": "osc-geo-h3loader-cli",
        "branch": "main",
        "description": "Command-line tool for loading data into H3 grid systems"
    }
}

def clone_repo(
    owner: str,
    repo: str,
    output_dir: str,
    branch: Optional[str] = None,
    depth: int = 1,
    github_token: Optional[str] = None
) -> bool:
    """
    Clone a single repository using git.
    
    Args:
        owner: Repository owner (username or organization)
        repo: Repository name
        output_dir: Directory to clone into
        branch: Optional branch to clone
        depth: Git clone depth
        github_token: GitHub API token
        
    Returns:
        True if cloning was successful, False otherwise
    """
    # Build target directory
    target_dir = os.path.join(output_dir, owner, repo)
    
    # Check if repository already exists
    if os.path.exists(target_dir):
        logger.info(f"Repository {owner}/{repo} already exists at {target_dir}, updating")
        try:
            # Pull latest changes
            subprocess.run(
                ["git", "pull"],
                cwd=target_dir,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            logger.info(f"Successfully updated {owner}/{repo}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to update repository {owner}/{repo}: {e}")
            return False
    
    # Build clone URL
    clone_url = f"https://github.com/{owner}/{repo}.git"
    if github_token:
        clone_url = f"https://{github_token}@github.com/{owner}/{repo}.git"
    
    # Build clone command
    cmd = ["git", "clone"]
    
    # Add branch if specified
    if branch:
        cmd.extend(["--branch", branch])
    
    # Add depth limit to make cloning faster
    cmd.extend(["--depth", str(depth)])
    
    # Add URL and target directory
    cmd.extend([clone_url, target_dir])
    
    # Clone repository
    try:
        logger.info(f"Cloning {owner}/{repo} to {target_dir}")
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False  # Don't raise an exception on non-zero exit
        )
        
        if result.returncode == 0:
            logger.info(f"Successfully cloned {owner}/{repo} to {target_dir}")
            return True
        else:
            error = result.stderr.decode().strip()
            logger.error(f"Failed to clone repository {owner}/{repo}: {error}")
            return False
    except Exception as e:
        logger.error(f"Error cloning repository {owner}/{repo}: {e}")
        return False

def clone_osc_repos(
    output_dir: Optional[str] = None,
    repos: Optional[List[str]] = None,
    token: Optional[str] = None
) -> Dict[str, bool]:
    """
    Clone OS Climate geospatial repositories.
    
    Args:
        output_dir: Directory to clone repositories into.
        repos: List of repository keys to clone. If None, clones all repositories.
        token: GitHub API token.
        
    Returns:
        Dictionary mapping repository names to clone success status.
    """
    # Use default output directory if not specified
    if not output_dir:
        output_dir = os.environ.get("OSC_REPOS_DIR", "./ext/os-climate")
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Determine which repos to clone
    repos_to_clone = {}
    if repos is None:
        repos_to_clone = OSC_REPOS
    else:
        for repo_key in repos:
            if repo_key in OSC_REPOS:
                repos_to_clone[repo_key] = OSC_REPOS[repo_key]
            else:
                logger.warning(f"Unknown repository key: {repo_key}")
    
    if not repos_to_clone:
        logger.warning("No repositories to clone")
        return {}
    
    # Clone repositories
    results = {}
    for repo_key, repo_info in repos_to_clone.items():
        owner = repo_info["owner"]
        repo = repo_info["repo"]
        branch = repo_info.get("branch")
        
        logger.info(f"Cloning {owner}/{repo}...")
        success = clone_repo(
            owner=owner,
            repo=repo,
            output_dir=output_dir,
            branch=branch,
            github_token=token
        )
        
        if success:
            logger.info(f"Successfully cloned {owner}/{repo}")
        else:
            logger.error(f"Failed to clone {owner}/{repo}")
        
        results[repo_key] = success
    
    return results

def get_repo_path(
    repo_key: str,
    base_dir: Optional[str] = None
) -> Optional[str]:
    """
    Get the path to a cloned OS Climate repository.
    
    Args:
        repo_key: Repository key (e.g., "h3grid-srv")
        base_dir: Base directory for cloned repositories. If None, uses the
            environment variable OSC_REPOS_DIR or a default value.
            
    Returns:
        Path to the repository if found, None otherwise.
    """
    if repo_key not in OSC_REPOS:
        logger.warning(f"Unknown repository key: {repo_key}")
        return None
    
    # Determine base directory
    if not base_dir:
        base_dir = os.environ.get("OSC_REPOS_DIR", "./ext/os-climate")
    
    repo_info = OSC_REPOS[repo_key]
    owner = repo_info["owner"]
    repo = repo_info["repo"]
    
    repo_path = os.path.join(base_dir, owner, repo)
    
    if os.path.exists(repo_path):
        return repo_path
    else:
        logger.warning(f"Repository path not found: {repo_path}")
        return None 