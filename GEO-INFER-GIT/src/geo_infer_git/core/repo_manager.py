#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Repository Manager for GEO-INFER-GIT

This module provides functionality for managing multiple Git repositories,
including cloning, synchronizing, and monitoring repository status.
"""

import os
import sys
import time
import yaml
import logging
import concurrent.futures
from typing import Dict, List, Optional, Union, Tuple
from pathlib import Path
import subprocess
import shutil
import git
from tqdm import tqdm

# Configure logger
logger = logging.getLogger("geo_infer_git.repo_manager")

class RepoManager:
    """
    Repository Manager for handling operations on multiple Git repositories.
    
    This class provides functionality for:
    - Cloning repositories from multiple sources
    - Synchronizing repositories
    - Checking repository health
    - Managing branches across repositories
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the Repository Manager with configuration.
        
        Args:
            config_path: Path to the configuration file (YAML)
        """
        self.config = self._load_config(config_path)
        self.base_dir = self._get_base_dir()
        self.repos = {}  # Will store repo name -> repo object mappings
        
    def _load_config(self, config_path: Optional[str] = None) -> Dict:
        """
        Load configuration from file or use defaults.
        
        Args:
            config_path: Path to the configuration file
            
        Returns:
            Configuration dictionary
        """
        default_config = {
            "repositories": {
                "base_directory": "./repos",
                "default_branch": "main",
                "clone_depth": 1,
                "auth_method": "https"
            },
            "operations": {
                "clone": {
                    "parallel": True,
                    "max_workers": 4
                }
            }
        }
        
        if not config_path:
            logger.info("Using default configuration")
            return default_config
        
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                logger.info(f"Loaded configuration from {config_path}")
                return config
        except Exception as e:
            logger.error(f"Failed to load configuration from {config_path}: {e}")
            logger.info("Using default configuration")
            return default_config
    
    def _get_base_dir(self) -> Path:
        """
        Get and create (if needed) the base directory for repositories.
        
        Returns:
            Path object for the base directory
        """
        base_dir = Path(self.config.get('repositories', {}).get('base_directory', './repos'))
        
        # Create directory if it doesn't exist
        if not base_dir.exists():
            try:
                base_dir.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created base directory at {base_dir}")
            except Exception as e:
                logger.error(f"Failed to create base directory {base_dir}: {e}")
                raise
                
        return base_dir
    
    def clone_repositories(self, repo_list: List[Dict], parallel: bool = None) -> Dict:
        """
        Clone multiple repositories.
        
        Args:
            repo_list: List of repository configurations
                Each item should contain at minimum:
                    - url: Repository URL
                    - name: Name for the repository (optional, derived from URL if not provided)
            parallel: Whether to clone in parallel (overrides config)
            
        Returns:
            Dictionary mapping repository names to success status
        """
        if parallel is None:
            parallel = self.config.get('operations', {}).get('clone', {}).get('parallel', True)
            
        max_workers = self.config.get('operations', {}).get('clone', {}).get('max_workers', 4)
        results = {}
        
        if parallel and len(repo_list) > 1:
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_repo = {
                    executor.submit(self._clone_single_repo, repo): repo 
                    for repo in repo_list
                }
                
                for future in tqdm(concurrent.futures.as_completed(future_to_repo), 
                                  total=len(repo_list),
                                  desc="Cloning repositories"):
                    repo = future_to_repo[future]
                    repo_name = repo.get('name') or self._get_repo_name_from_url(repo['url'])
                    try:
                        success = future.result()
                        results[repo_name] = success
                    except Exception as e:
                        logger.error(f"Exception while cloning {repo_name}: {e}")
                        results[repo_name] = False
        else:
            for repo in tqdm(repo_list, desc="Cloning repositories"):
                repo_name = repo.get('name') or self._get_repo_name_from_url(repo['url'])
                try:
                    success = self._clone_single_repo(repo)
                    results[repo_name] = success
                except Exception as e:
                    logger.error(f"Exception while cloning {repo_name}: {e}")
                    results[repo_name] = False
                    
        return results
    
    def _clone_single_repo(self, repo_config: Dict) -> bool:
        """
        Clone a single repository.
        
        Args:
            repo_config: Repository configuration dictionary
            
        Returns:
            True if successful, False otherwise
        """
        url = repo_config['url']
        repo_name = repo_config.get('name') or self._get_repo_name_from_url(url)
        branch = repo_config.get('branch') or self.config.get('repositories', {}).get('default_branch', 'main')
        depth = repo_config.get('depth') or self.config.get('repositories', {}).get('clone_depth', 1)
        
        target_dir = self.base_dir / repo_name
        
        # Check if repository already exists
        if target_dir.exists():
            logger.info(f"Repository {repo_name} already exists at {target_dir}")
            return True
            
        try:
            logger.info(f"Cloning {url} to {target_dir}")
            
            # Determine authentication method
            auth_method = repo_config.get('auth_method') or self.config.get('repositories', {}).get('auth_method', 'https')
            
            # Clone options
            clone_opts = {
                'branch': branch,
                'depth': depth,
            }
            
            if auth_method == 'ssh':
                # For SSH auth, we rely on SSH agent or keys in ~/.ssh
                pass
            elif auth_method == 'https_token':
                # For HTTPS with token
                token = os.environ.get('GIT_TOKEN')
                if token and 'github.com' in url:
                    # Modify URL to include token for GitHub
                    url = url.replace('https://', f'https://{token}@')
            
            # Perform the clone
            repo = git.Repo.clone_from(url, target_dir, **clone_opts)
            self.repos[repo_name] = repo
            logger.info(f"Successfully cloned {repo_name}")
            return True
            
        except git.GitCommandError as e:
            logger.error(f"Git error while cloning {repo_name}: {e}")
            # Clean up partial clone
            if target_dir.exists():
                shutil.rmtree(target_dir)
            return False
        except Exception as e:
            logger.error(f"Unexpected error while cloning {repo_name}: {e}")
            if target_dir.exists():
                shutil.rmtree(target_dir)
            return False
    
    def _get_repo_name_from_url(self, url: str) -> str:
        """
        Extract repository name from URL.
        
        Args:
            url: Repository URL
            
        Returns:
            Repository name
        """
        # Remove .git extension if present
        if url.endswith('.git'):
            url = url[:-4]
            
        # Get the last part of the URL
        return url.split('/')[-1]
    
    def sync_repositories(self, repo_names: Optional[List[str]] = None) -> Dict:
        """
        Synchronize repositories by pulling latest changes.
        
        Args:
            repo_names: List of repository names to sync (all if None)
            
        Returns:
            Dictionary mapping repository names to sync status
        """
        results = {}
        all_repos = self._get_all_repo_paths()
        
        repos_to_sync = []
        if repo_names:
            for name in repo_names:
                if name in all_repos:
                    repos_to_sync.append((name, all_repos[name]))
                else:
                    logger.warning(f"Repository {name} not found")
                    results[name] = False
        else:
            repos_to_sync = list(all_repos.items())
            
        for name, path in tqdm(repos_to_sync, desc="Syncing repositories"):
            try:
                repo = git.Repo(path)
                current_branch = repo.active_branch.name
                
                # Fetch
                logger.info(f"Fetching updates for {name}")
                for remote in repo.remotes:
                    remote.fetch()
                
                # Pull
                logger.info(f"Pulling updates for {name} on branch {current_branch}")
                repo.git.pull('origin', current_branch)
                results[name] = True
            except git.GitCommandError as e:
                logger.error(f"Git error while syncing {name}: {e}")
                results[name] = False
            except Exception as e:
                logger.error(f"Unexpected error while syncing {name}: {e}")
                results[name] = False
                
        return results
    
    def _get_all_repo_paths(self) -> Dict[str, Path]:
        """
        Get paths for all repositories in the base directory.
        
        Returns:
            Dictionary mapping repository names to paths
        """
        repos = {}
        for item in self.base_dir.iterdir():
            if item.is_dir() and (item / '.git').exists():
                repos[item.name] = item
                
        return repos
    
    def check_repo_status(self, repo_names: Optional[List[str]] = None) -> Dict:
        """
        Check status of repositories (changes, branch, etc.).
        
        Args:
            repo_names: List of repository names to check (all if None)
            
        Returns:
            Dictionary with repository status information
        """
        results = {}
        all_repos = self._get_all_repo_paths()
        
        repos_to_check = []
        if repo_names:
            for name in repo_names:
                if name in all_repos:
                    repos_to_check.append((name, all_repos[name]))
                else:
                    logger.warning(f"Repository {name} not found")
                    results[name] = {"error": "Repository not found"}
        else:
            repos_to_check = list(all_repos.items())
            
        for name, path in repos_to_check:
            try:
                repo = git.Repo(path)
                status = {
                    "branch": repo.active_branch.name,
                    "is_dirty": repo.is_dirty(),
                    "untracked_files": repo.untracked_files,
                    "commits_behind": 0,
                    "commits_ahead": 0,
                    "remotes": [r.name for r in repo.remotes]
                }
                
                # Check commits ahead/behind
                if repo.remotes:
                    try:
                        remote = repo.remotes.origin
                        remote.fetch()
                        commits_behind = len(list(repo.iter_commits(
                            f"{repo.active_branch.name}..origin/{repo.active_branch.name}")))
                        commits_ahead = len(list(repo.iter_commits(
                            f"origin/{repo.active_branch.name}..{repo.active_branch.name}")))
                        
                        status["commits_behind"] = commits_behind
                        status["commits_ahead"] = commits_ahead
                    except git.GitCommandError:
                        # Remote branch might not exist
                        status["remote_tracking"] = False
                    
                results[name] = status
            except Exception as e:
                logger.error(f"Error checking status for {name}: {e}")
                results[name] = {"error": str(e)}
                
        return results
    
    def create_branch(self, branch_name: str, repo_names: Optional[List[str]] = None) -> Dict:
        """
        Create a new branch in repositories.
        
        Args:
            branch_name: Name of the branch to create
            repo_names: List of repository names to create branch in (all if None)
            
        Returns:
            Dictionary mapping repository names to branch creation status
        """
        results = {}
        all_repos = self._get_all_repo_paths()
        
        repos_for_branch = []
        if repo_names:
            for name in repo_names:
                if name in all_repos:
                    repos_for_branch.append((name, all_repos[name]))
                else:
                    logger.warning(f"Repository {name} not found")
                    results[name] = False
        else:
            repos_for_branch = list(all_repos.items())
            
        for name, path in tqdm(repos_for_branch, desc=f"Creating branch {branch_name}"):
            try:
                repo = git.Repo(path)
                
                # Check if branch already exists
                if branch_name in [ref.name for ref in repo.references]:
                    logger.info(f"Branch {branch_name} already exists in {name}")
                    results[name] = True
                    continue
                
                # Create new branch from current HEAD
                new_branch = repo.create_head(branch_name)
                logger.info(f"Created branch {branch_name} in {name}")
                results[name] = True
            except Exception as e:
                logger.error(f"Error creating branch in {name}: {e}")
                results[name] = False
                
        return results
    
    def checkout_branch(self, branch_name: str, repo_names: Optional[List[str]] = None) -> Dict:
        """
        Checkout a branch in repositories.
        
        Args:
            branch_name: Name of the branch to checkout
            repo_names: List of repository names to checkout branch in (all if None)
            
        Returns:
            Dictionary mapping repository names to checkout status
        """
        results = {}
        all_repos = self._get_all_repo_paths()
        
        repos_for_checkout = []
        if repo_names:
            for name in repo_names:
                if name in all_repos:
                    repos_for_checkout.append((name, all_repos[name]))
                else:
                    logger.warning(f"Repository {name} not found")
                    results[name] = False
        else:
            repos_for_checkout = list(all_repos.items())
            
        for name, path in tqdm(repos_for_checkout, desc=f"Checking out branch {branch_name}"):
            try:
                repo = git.Repo(path)
                
                # Check if working tree is clean
                if repo.is_dirty():
                    logger.warning(f"Repository {name} has uncommitted changes, skipping checkout")
                    results[name] = False
                    continue
                    
                # Check if branch exists
                if branch_name not in [ref.name for ref in repo.references]:
                    # Check if it exists in remote
                    for remote in repo.remotes:
                        remote.fetch()
                        remote_branch = f"{remote.name}/{branch_name}"
                        if remote_branch in [ref.name for ref in repo.references]:
                            # Create local branch tracking remote
                            repo.git.checkout('-b', branch_name, remote_branch)
                            logger.info(f"Created and checked out branch {branch_name} from {remote_branch} in {name}")
                            results[name] = True
                            break
                    else:
                        logger.warning(f"Branch {branch_name} does not exist in {name}, skipping")
                        results[name] = False
                        continue
                else:
                    # Branch exists locally, checkout
                    repo.git.checkout(branch_name)
                    logger.info(f"Checked out branch {branch_name} in {name}")
                    results[name] = True
            except Exception as e:
                logger.error(f"Error checking out branch in {name}: {e}")
                results[name] = False
                
        return results
    
    def batch_operation(self, operation: str, *args, **kwargs) -> Dict:
        """
        Perform a Git operation across multiple repositories.
        
        Args:
            operation: Operation name (commit, push, pull, fetch, etc.)
            *args, **kwargs: Arguments to pass to the operation function
            
        Returns:
            Dictionary with operation results
        """
        op_map = {
            "clone": self.clone_repositories,
            "sync": self.sync_repositories,
            "status": self.check_repo_status,
            "create_branch": self.create_branch,
            "checkout": self.checkout_branch,
        }
        
        if operation not in op_map:
            logger.error(f"Unknown operation: {operation}")
            return {"error": f"Unknown operation: {operation}"}
            
        logger.info(f"Performing batch operation: {operation}")
        return op_map[operation](*args, **kwargs)


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    # Create a repo manager
    manager = RepoManager()
    
    # Example repositories to clone
    repos = [
        {"url": "https://github.com/user/repo1", "name": "repo1"},
        {"url": "https://github.com/user/repo2", "name": "repo2"}
    ]
    
    # Clone repositories
    results = manager.clone_repositories(repos)
    print(f"Clone results: {results}")
    
    # Check status
    status = manager.check_repo_status()
    print(f"Status: {status}") 