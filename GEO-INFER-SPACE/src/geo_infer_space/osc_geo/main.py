"""
Main module for OSC-GEO.

This module provides high-level functions for working with OS Climate geospatial tools.
"""

import logging
import os
from typing import Dict, List, Optional, Tuple, Union

from .core.repos import clone_osc_repos, OSC_REPOS
from .core.h3grid import H3GridManager
from .core.loader import H3DataLoader

logger = logging.getLogger(__name__)

def setup_osc_geo(
    output_dir: Optional[str] = None,
    github_token: Optional[str] = None
) -> Dict[str, bool]:
    """
    Set up the OSC-GEO module by cloning required repositories.
    
    Args:
        output_dir: Directory to clone repositories into.
        github_token: GitHub API token for authentication.
        
    Returns:
        Dictionary mapping repository names to clone success status.
    """
    logger.info("Setting up OSC-GEO module")
    
    # Clone OS Climate repositories
    clone_results = clone_osc_repos(
        output_dir=output_dir,
        token=github_token
    )
    
    # Check if all repositories were cloned successfully
    all_success = all(clone_results.values())
    
    if all_success:
        logger.info("All OS Climate repositories cloned successfully")
    else:
        failed_repos = [repo for repo, success in clone_results.items() if not success]
        logger.warning(f"Failed to clone repositories: {', '.join(failed_repos)}")
    
    return clone_results

def get_repo_list() -> List[Dict[str, str]]:
    """
    Get a list of OS Climate repositories used by OSC-GEO.
    
    Returns:
        List of repository information dictionaries.
    """
    return [
        {
            "key": key,
            "owner": info["owner"],
            "repo": info["repo"],
            "branch": info.get("branch", "main"),
            "description": info.get("description", "")
        }
        for key, info in OSC_REPOS.items()
    ]

def create_h3_grid_manager(
    repo_base_dir: Optional[str] = None,
    server_port: int = 8000,
    auto_start: bool = False
) -> H3GridManager:
    """
    Create an H3 grid manager instance.
    
    Args:
        repo_base_dir: Base directory for cloned repositories.
        server_port: Port for the H3 grid service.
        auto_start: Whether to automatically start the service.
        
    Returns:
        H3GridManager instance.
    """
    return H3GridManager(
        repo_base_dir=repo_base_dir,
        server_port=server_port,
        auto_start=auto_start
    )

def create_h3_data_loader(
    repo_base_dir: Optional[str] = None
) -> H3DataLoader:
    """
    Create an H3 data loader instance.
    
    Args:
        repo_base_dir: Base directory for cloned repositories.
        
    Returns:
        H3DataLoader instance.
    """
    return H3DataLoader(repo_base_dir=repo_base_dir)

def load_data_to_h3_grid(
    input_file: str,
    output_file: str,
    resolution: int = 8,
    loader: Optional[H3DataLoader] = None,
    repo_base_dir: Optional[str] = None,
    **kwargs
) -> bool:
    """
    Load geospatial data into an H3 grid system.
    
    Args:
        input_file: Path to input file.
        output_file: Path to output file.
        resolution: H3 resolution (0-15).
        loader: H3DataLoader instance. If None, a new instance is created.
        repo_base_dir: Base directory for cloned repositories.
        **kwargs: Additional arguments to pass to the loader.
        
    Returns:
        True if the data was loaded successfully, False otherwise.
    """
    if loader is None:
        loader = create_h3_data_loader(repo_base_dir)
    
    return loader.load_data(
        input_file=input_file,
        output_file=output_file,
        resolution=resolution,
        **kwargs
    ) 