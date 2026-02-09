# Agent
: api

## Scope
 This directory contains api components for the module. It provides 18 classes and 5 functions.

## Classes
 and Functions

### RepositoryRequest
 Request model for repository operations.

**Methods**:
- `validate_platform(cls, v)`:

### RepositoryResponse
 Response model for repository information.

### CloneRequest
 Request model for repository cloning.

### CloneResponse
 Response model for clone operations.

### SyncRequest
 Request model for repository synchronization.

### SyncResponse
 Response model for sync operations.

### BranchRequest
 Request model for branch operations.

### BranchResponse
 Response model for branch information.

### MergeRequest
 Request model for merge operations.

### MergeResponse
 Response model for merge operations.

### CommitRequest
 Request model for commit operations.

### CommitResponse
 Response model for commit information.

### WorkflowRequest
 Request model for workflow operations.

### WorkflowResponse
 Response model for workflow information.

### IntegrationRequest
 Request model for platform integration.

### IntegrationResponse
 Response model for integration information.

### HealthResponse
 Response model for health checks.

### SystemStatusResponse
 Response model for system status.

### get_repo_manager
 `get_repo_manager() -> RepoManager` Get repository manager instance.

### get_github_api
 `get_github_api() -> GitHubAPI` Get GitHub API instance.

### get_logger
 `get_logger()` Get logger instance.

### initialize_api
 `initialize_api(config_path: Optional[str])` Initialize the API with configuration.

### run_api
 `run_api(host: str, port: int, config_path: Optional[str])` Run the FastAPI server.

## Capabilities

- **18 classes** for core functionality
- **5 functions** for utility operations

## Integration

- **Location**: `GEO-INFER-GIT/src/geo_infer_git/api`
- **Type**: Directory Node
