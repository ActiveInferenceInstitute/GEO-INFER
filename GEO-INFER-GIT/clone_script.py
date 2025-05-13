#!/usr/bin/env python3
"""
Standalone script to clone GitHub repositories from the configured lists.
This script does not rely on module imports and can be run directly.
"""

import os
import sys
import subprocess
import logging
import yaml
import requests
from concurrent.futures import ThreadPoolExecutor
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Configuration
CONFIG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config')
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cloned_repositories')

def load_yaml_config(file_path):
    """Load a YAML configuration file."""
    try:
        with open(file_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Error loading config file {file_path}: {e}")
        return {}

def get_github_repo_info(owner, repo):
    """Get information about a GitHub repository."""
    url = f"https://api.github.com/repos/{owner}/{repo}"
    try:
        response = requests.get(url, headers={'Accept': 'application/vnd.github.v3+json'})
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Error fetching info for {owner}/{repo}: {e}")
        return {}

def clone_repository(owner, repo, branch=None):
    """Clone a single repository."""
    # Construct clone URL
    clone_url = f"https://github.com/{owner}/{repo}.git"
    
    # Prepare target directory
    target_dir = os.path.join(OUTPUT_DIR, owner, repo)
    
    # Check if directory exists
    if os.path.exists(target_dir):
        logger.info(f"Repository {owner}/{repo} already exists, skipping")
        return True
    
    # Create parent directory if needed
    os.makedirs(os.path.dirname(target_dir), exist_ok=True)
    
    # Prepare git command
    git_cmd = ["git", "clone"]
    
    # Add depth argument to speed up cloning
    git_cmd.extend(["--depth", "1"])
    
    # Add branch argument if specified
    if branch:
        git_cmd.extend(["--single-branch", "--branch", branch])
    
    # Add repository URL and target directory
    git_cmd.extend([clone_url, target_dir])
    
    # Execute git clone command
    try:
        logger.info(f"Cloning {owner}/{repo} to {target_dir}")
        result = subprocess.run(
            git_cmd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        logger.info(f"Successfully cloned {owner}/{repo}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error cloning repository {owner}/{repo}: {e.stderr}")
        # Clean up if directory was created
        if os.path.exists(target_dir):
            import shutil
            shutil.rmtree(target_dir)
        return False
    except Exception as e:
        logger.error(f"Unexpected error cloning {owner}/{repo}: {e}")
        return False

def main():
    """Main function to clone repositories from configuration."""
    # Create output directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Load target repositories
    repos_file = os.path.join(CONFIG_DIR, 'target_repos.yaml')
    repos_config = load_yaml_config(repos_file)
    
    # Load target users
    users_file = os.path.join(CONFIG_DIR, 'target_users.yaml')
    users_config = load_yaml_config(users_file)
    
    # Statistics
    total_repos = 0
    success_repos = 0
    
    # Clone specific repositories
    if repos_config and 'repositories' in repos_config:
        repos = repos_config['repositories']
        logger.info(f"Cloning {len(repos)} specific repositories")
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = []
            
            for repo_info in repos:
                owner = repo_info.get('owner')
                repo = repo_info.get('repo')
                branch = repo_info.get('branch')
                
                if not owner or not repo:
                    logger.warning(f"Skipping invalid repository configuration: {repo_info}")
                    continue
                
                futures.append(executor.submit(clone_repository, owner, repo, branch))
                total_repos += 1
            
            for future in futures:
                if future.result():
                    success_repos += 1
    
    # Clone repositories from users
    if users_config and 'users' in users_config:
        users = users_config['users']
        logger.info(f"Processing {len(users)} users")
        
        for user_info in users:
            username = user_info.get('username')
            
            if not username:
                logger.warning(f"Skipping user with no username: {user_info}")
                continue
            
            # Get user repositories from GitHub API
            url = f"https://api.github.com/users/{username}/repos?sort=updated&per_page=100"
            
            try:
                logger.info(f"Fetching repositories for user {username}")
                response = requests.get(url, headers={'Accept': 'application/vnd.github.v3+json'})
                response.raise_for_status()
                user_repos = response.json()
                
                # Apply include/exclude filters
                include_repos = user_info.get('include_repos', [])
                exclude_repos = user_info.get('exclude_repos', [])
                max_repos = user_info.get('max_repos', 10)
                
                filtered_repos = []
                for repo in user_repos:
                    repo_name = repo.get('name')
                    
                    # Skip if no name
                    if not repo_name:
                        continue
                    
                    # Check include list if provided
                    if include_repos:
                        if repo_name not in include_repos:
                            continue
                    
                    # Check exclude list if provided
                    if exclude_repos:
                        if any(match_wildcard(repo_name, pattern) for pattern in exclude_repos):
                            continue
                    
                    filtered_repos.append(repo)
                    
                    # Stop if we've reached the maximum
                    if len(filtered_repos) >= max_repos:
                        break
                
                logger.info(f"Found {len(filtered_repos)} repositories for user {username}")
                
                # Clone repositories
                with ThreadPoolExecutor(max_workers=4) as executor:
                    futures = []
                    
                    for repo in filtered_repos:
                        repo_name = repo.get('name')
                        futures.append(executor.submit(clone_repository, username, repo_name))
                        total_repos += 1
                    
                    for future in futures:
                        if future.result():
                            success_repos += 1
                
            except Exception as e:
                logger.error(f"Error processing user {username}: {e}")
    
    # Print summary
    logger.info(f"Cloning complete: {success_repos}/{total_repos} repositories cloned successfully")

def match_wildcard(name, pattern):
    """Match a repository name against a wildcard pattern."""
    if pattern.startswith("*") and pattern.endswith("*"):
        return pattern[1:-1] in name
    elif pattern.startswith("*"):
        return name.endswith(pattern[1:])
    elif pattern.endswith("*"):
        return name.startswith(pattern[:-1])
    else:
        return name == pattern

if __name__ == "__main__":
    main() 