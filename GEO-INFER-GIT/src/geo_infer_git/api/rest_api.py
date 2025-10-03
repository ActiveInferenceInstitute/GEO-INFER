#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
REST API implementation for GEO-INFER-GIT.

This module provides a FastAPI-based REST API that implements the endpoints
defined in the OpenAPI schema for repository management operations.
"""

import os
import json
import time
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
import uvicorn

from ..core.repo_manager import RepoManager
from ..core.github_api import GitHubAPI
from ..utils.config_loader import ConfigLoader, CloneConfig
from ..utils.logging_utils import setup_logging, get_logger
from ..utils.error_handler import handle_error, GeoInferGitError

# Create FastAPI app
app = FastAPI(
    title="GEO-INFER-GIT API",
    description="Version control integration and repository management system for the GEO-INFER framework",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
repo_manager = None
github_api = None
config_loader = None
logger = None

# Pydantic models for request/response
class RepositoryRequest(BaseModel):
    """Request model for repository operations."""

    clone_url: str = Field(..., description="Repository clone URL")
    name: Optional[str] = Field(None, description="Custom name for the repository")
    description: Optional[str] = Field(None, description="Repository description")
    platform: str = Field("github", description="Git platform (github, gitlab, bitbucket)")
    credentials: Optional[Dict[str, Any]] = Field(None, description="Authentication credentials")
    auto_sync: bool = Field(True, description="Enable automatic synchronization")
    sync_interval: int = Field(3600, description="Sync interval in seconds")

    @validator('platform')
    def validate_platform(cls, v):
        if v not in ['github', 'gitlab', 'bitbucket', 'local']:
            raise ValueError('Platform must be one of: github, gitlab, bitbucket, local')
        return v

class RepositoryResponse(BaseModel):
    """Response model for repository information."""

    id: str
    name: str
    full_name: str
    description: Optional[str]
    platform: str
    clone_url: str
    ssh_url: Optional[str]
    default_branch: str
    language: Optional[str]
    size: int
    branch_count: int
    commit_count: int
    status: str
    last_sync: Optional[datetime]
    created_at: datetime
    updated_at: datetime

class CloneRequest(BaseModel):
    """Request model for repository cloning."""

    branch: Optional[str] = Field(None, description="Branch to clone")
    depth: int = Field(1, description="Clone depth")
    recursive: bool = Field(False, description="Clone submodules recursively")
    lfs: bool = Field(True, description="Include Git LFS files")

class CloneResponse(BaseModel):
    """Response model for clone operations."""

    job_id: str
    status: str
    progress: float
    estimated_completion: Optional[datetime]

class SyncRequest(BaseModel):
    """Request model for repository synchronization."""

    force: bool = Field(False, description="Force synchronization")
    prune: bool = Field(True, description="Prune deleted branches")
    branches: Optional[List[str]] = Field(None, description="Specific branches to sync")

class SyncResponse(BaseModel):
    """Response model for sync operations."""

    job_id: str
    status: str
    changes_detected: bool
    started_at: datetime

class BranchRequest(BaseModel):
    """Request model for branch operations."""

    name: str = Field(..., description="Branch name")
    base: str = Field(..., description="Base branch")
    protected: bool = Field(False, description="Whether branch is protected")

class BranchResponse(BaseModel):
    """Response model for branch information."""

    name: str
    commit_sha: str
    commit_message: str
    author: str
    created_at: datetime
    updated_at: datetime
    protected: bool
    ahead: int
    behind: int
    repository_id: str

class MergeRequest(BaseModel):
    """Request model for merge operations."""

    target_branch: str = Field(..., description="Target branch for merge")
    message: Optional[str] = Field(None, description="Merge commit message")
    strategy: str = Field("merge", description="Merge strategy")
    delete_source: bool = Field(False, description="Delete source branch after merge")

class MergeResponse(BaseModel):
    """Response model for merge operations."""

    merge_commit_sha: Optional[str]
    merged: bool
    message: str
    conflicts: List[str]

class CommitRequest(BaseModel):
    """Request model for commit operations."""

    message: str = Field(..., description="Commit message")
    description: Optional[str] = Field(None, description="Commit description")
    branch: Optional[str] = Field(None, description="Branch to commit to")
    author: Optional[Dict[str, str]] = Field(None, description="Commit author info")
    changes: List[Dict[str, Any]] = Field(..., description="File changes")

class CommitResponse(BaseModel):
    """Response model for commit information."""

    sha: str
    message: str
    author: Dict[str, str]
    committer: Dict[str, str]
    timestamp: datetime
    tree_sha: str
    parent_shas: List[str]
    files_changed: int
    insertions: int
    deletions: int
    repository_id: str
    url: str

class WorkflowRequest(BaseModel):
    """Request model for workflow operations."""

    name: str = Field(..., description="Workflow name")
    description: Optional[str] = Field(None, description="Workflow description")
    type: str = Field(..., description="Workflow type")
    repository_id: str = Field(..., description="Repository ID")
    trigger: Dict[str, Any] = Field(..., description="Workflow trigger configuration")
    definition: Dict[str, Any] = Field(..., description="Workflow definition")
    enabled: bool = Field(True, description="Whether workflow is enabled")

class WorkflowResponse(BaseModel):
    """Response model for workflow information."""

    id: str
    name: str
    description: Optional[str]
    type: str
    repository_id: str
    status: str
    trigger: Dict[str, Any]
    definition: Dict[str, Any]
    enabled: bool
    created_at: datetime
    updated_at: datetime

class IntegrationRequest(BaseModel):
    """Request model for platform integration."""

    name: str = Field(..., description="Integration name")
    platform: str = Field(..., description="Platform type")
    endpoint: str = Field(..., description="Platform API endpoint")
    credentials: Dict[str, Any] = Field(..., description="Authentication credentials")
    configuration: Optional[Dict[str, Any]] = Field(None, description="Integration configuration")

class IntegrationResponse(BaseModel):
    """Response model for integration information."""

    id: str
    name: str
    platform: str
    endpoint: str
    status: str
    last_sync: Optional[datetime]
    repository_count: int
    created_at: datetime

class HealthResponse(BaseModel):
    """Response model for health checks."""

    status: str
    timestamp: datetime
    components: Dict[str, Dict[str, Any]]

class SystemStatusResponse(BaseModel):
    """Response model for system status."""

    version: str
    uptime: int
    repository_count: int
    active_workflows: int
    storage_usage: Dict[str, Any]
    git_version: str

# Dependency functions
def get_repo_manager() -> RepoManager:
    """Get repository manager instance."""
    if repo_manager is None:
        raise HTTPException(status_code=500, detail="Repository manager not initialized")
    return repo_manager

def get_github_api() -> GitHubAPI:
    """Get GitHub API instance."""
    if github_api is None:
        raise HTTPException(status_code=500, detail="GitHub API not initialized")
    return github_api

def get_logger():
    """Get logger instance."""
    if logger is None:
        raise HTTPException(status_code=500, detail="Logger not initialized")
    return logger

# API Endpoints

@app.get("/health", response_model=HealthResponse, tags=["system"])
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        components={
            "repository_manager": {"status": "up" if repo_manager else "down"},
            "github_api": {"status": "up" if github_api else "down"},
            "database": {"status": "up"}
        }
    )

@app.get("/repositories", response_model=Dict[str, Any], tags=["repositories"])
async def list_repositories(
    status_filter: Optional[str] = None,
    platform: Optional[str] = None,
    organization: Optional[str] = None,
    language: Optional[str] = None,
    manager: RepoManager = Depends(get_repo_manager)
):
    """List managed repositories with optional filtering."""
    try:
        # Get all repositories
        all_repos = manager._get_all_repo_paths()

        # Apply filters
        filtered_repos = {}
        for name, path in all_repos.items():
            include_repo = True

            # Status filter (simplified - would need more sophisticated status tracking)
            if status_filter:
                if status_filter == "active" and not (path / '.git').exists():
                    include_repo = False
                elif status_filter == "error":
                    # Would need error tracking
                    pass

            if include_repo:
                filtered_repos[name] = {
                    "path": str(path),
                    "exists": path.exists(),
                    "is_git": (path / '.git').exists()
                }

        return {
            "repositories": filtered_repos,
            "total": len(filtered_repos)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing repositories: {str(e)}")

@app.post("/repositories", response_model=RepositoryResponse, tags=["repositories"])
async def add_repository(
    request: RepositoryRequest,
    background_tasks: BackgroundTasks,
    manager: RepoManager = Depends(get_repo_manager)
):
    """Add a new repository to the management system."""
    try:
        # Validate repository URL
        if request.platform == "github" and not request.clone_url.startswith("https://github.com/"):
            raise HTTPException(status_code=400, detail="Invalid GitHub repository URL")

        # Create repository entry
        repo_id = f"{request.platform}_{request.name or 'unknown'}"
        repo_data = {
            "id": repo_id,
            "name": request.name or "unknown",
            "full_name": request.clone_url.split('/')[-2] + "/" + request.clone_url.split('/')[-1].replace('.git', ''),
            "description": request.description,
            "platform": request.platform,
            "clone_url": request.clone_url,
            "status": "pending",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        # Start clone operation in background
        background_tasks.add_task(clone_repository_background, repo_data, request)

        return RepositoryResponse(**repo_data)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding repository: {str(e)}")

@app.get("/repositories/{repo_id}", response_model=RepositoryResponse, tags=["repositories"])
async def get_repository(
    repo_id: str,
    manager: RepoManager = Depends(get_repo_manager)
):
    """Get detailed information about a specific repository."""
    try:
        # This would need more sophisticated repository tracking
        raise HTTPException(status_code=404, detail=f"Repository {repo_id} not found")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting repository: {str(e)}")

@app.post("/repositories/{repo_id}/clone", response_model=CloneResponse, tags=["repositories"])
async def clone_repository(
    repo_id: str,
    request: CloneRequest,
    background_tasks: BackgroundTasks,
    manager: RepoManager = Depends(get_repo_manager)
):
    """Clone a repository."""
    try:
        # Generate job ID
        job_id = f"clone_{repo_id}_{int(time.time())}"

        # Start clone operation in background
        background_tasks.add_task(clone_repository_background, repo_id, request)

        return CloneResponse(
            job_id=job_id,
            status="queued",
            progress=0.0,
            estimated_completion=datetime.utcnow()  # Would need better estimation
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting clone: {str(e)}")

@app.post("/repositories/{repo_id}/sync", response_model=SyncResponse, tags=["repositories"])
async def sync_repository(
    repo_id: str,
    request: SyncRequest,
    background_tasks: BackgroundTasks,
    manager: RepoManager = Depends(get_repo_manager)
):
    """Synchronize a repository."""
    try:
        # Generate job ID
        job_id = f"sync_{repo_id}_{int(time.time())}"

        # Start sync operation in background
        background_tasks.add_task(sync_repository_background, repo_id, request)

        return SyncResponse(
            job_id=job_id,
            status="queued",
            changes_detected=False,  # Would be determined during sync
            started_at=datetime.utcnow()
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting sync: {str(e)}")

@app.get("/repositories/{repo_id}/branches", response_model=Dict[str, Any], tags=["branches"])
async def list_branches(
    repo_id: str,
    status_filter: Optional[str] = None,
    protected: Optional[bool] = None,
    manager: RepoManager = Depends(get_repo_manager)
):
    """List branches for a repository."""
    try:
        # This would need integration with actual Git repositories
        return {
            "branches": [],
            "total": 0
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing branches: {str(e)}")

@app.post("/repositories/{repo_id}/branches", response_model=BranchResponse, tags=["branches"])
async def create_branch(
    repo_id: str,
    request: BranchRequest,
    manager: RepoManager = Depends(get_repo_manager)
):
    """Create a new branch."""
    try:
        # This would need integration with actual Git repositories
        raise HTTPException(status_code=501, detail="Branch creation not yet implemented")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating branch: {str(e)}")

@app.post("/repositories/{repo_id}/branches/{branch_name}/merge", response_model=MergeResponse, tags=["branches"])
async def merge_branch(
    repo_id: str,
    branch_name: str,
    request: MergeRequest,
    manager: RepoManager = Depends(get_repo_manager)
):
    """Merge a branch."""
    try:
        # This would need integration with actual Git repositories
        raise HTTPException(status_code=501, detail="Branch merging not yet implemented")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error merging branch: {str(e)}")

@app.get("/system/status", response_model=SystemStatusResponse, tags=["system"])
async def get_system_status():
    """Get comprehensive system status."""
    try:
        import git

        return SystemStatusResponse(
            version="1.0.0",
            uptime=int(time.time()),  # Would need proper uptime tracking
            repository_count=0,  # Would need repository tracking
            active_workflows=0,  # Would need workflow tracking
            storage_usage={},  # Would need storage tracking
            git_version=git.__version__
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting system status: {str(e)}")

# Background task functions
async def clone_repository_background(repo_id: str, clone_request: Union[RepositoryRequest, CloneRequest]):
    """Background task for repository cloning."""
    try:
        # This would implement actual cloning logic
        logger.info(f"Starting background clone for {repo_id}")
        # Implementation would use RepoManager and RepoCloner
    except Exception as e:
        logger.error(f"Background clone failed for {repo_id}: {e}")

async def sync_repository_background(repo_id: str, sync_request: SyncRequest):
    """Background task for repository synchronization."""
    try:
        # This would implement actual sync logic
        logger.info(f"Starting background sync for {repo_id}")
        # Implementation would use RepoManager
    except Exception as e:
        logger.error(f"Background sync failed for {repo_id}: {e}")

# Initialization function
def initialize_api(config_path: Optional[str] = None):
    """Initialize the API with configuration."""
    global repo_manager, github_api, config_loader, logger

    # Load configuration
    config_loader = ConfigLoader(config_path)

    # Load clone configuration
    clone_config = config_loader.load_clone_config()

    # Initialize components
    repo_manager = RepoManager()
    github_api = GitHubAPI(
        token=clone_config.github_token,
        api_url=clone_config.github_api_url,
        wait_on_rate_limit=clone_config.github_wait_on_rate_limit,
        max_retries=clone_config.github_max_retries,
        retry_delay=clone_config.github_retry_delay
    )

    # Setup logging
    logger = setup_logging({
        'level': clone_config.log_level,
        'format': clone_config.log_format,
        'file': f"{clone_config.output_dir}/api.log"
    })

def run_api(host: str = "0.0.0.0", port: int = 8000, config_path: Optional[str] = None):
    """Run the FastAPI server."""
    initialize_api(config_path)

    uvicorn.run(
        "geo_infer_git.api.rest_api:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    run_api()
