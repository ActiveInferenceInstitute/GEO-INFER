# Agent
: core ## Scope
 This directory contains core components for the module. It provides 22 classes and 2 functions. ## Classes
 and Functions ### SubmoduleInf
o
 Information about a Git submodule. ### MergeConflic
t
 Information about a merge conflict. ### CherryPickOperatio
n
 Information about a cherry-pick operation. ### RebaseOperatio
n
 Information about a rebase operation. ### SubmoduleManage
r
 submodule management for Git repositories. **Methods**: - `initialize_submodules(recursive: bool) -> Dict[str, bool]`: Initialize all submodules in the repository. - `update_submodules(recursive: bool) -> Dict[str, bool]`: Update all submodules to their latest commits. - `sync_submodules(recursive: bool) -> Dict[str, bool]`: Synchronize submodules with their remote repositories. - `get_submodule_status() -> Dict[str, Dict[str, Any]]`: Get status of all submodules. ### CherryPickManage
r
 cherry-picking functionality for selective commit application. **Methods**: - `cherry_pick_commit(commit_sha: str, strategy: str) -> CherryPickOperation`: Cherry-pick a specific commit. - `cherry_pick_range(start_sha: str, end_sha: str, stop_on_conflict: bool) -> List[CherryPickOperation]`: Cherry-pick a range of commits. - `resolve_conflicts(operation_index: int, resolution_strategy: str) -> bool`: Resolve conflicts in a cherry-pick operation. ### RebaseManage
r
 rebasing functionality for history manipulation. **Methods**: - `start_interactive_rebase(base_commit: str, target_branch: str) -> RebaseOperation`: Start an interactive rebase operation. - `continue_rebase() -> bool`: Continue an ongoing rebase operation. - `abort_rebase() -> bool`: Abort the current rebase operation. ### AdvancedGitOperation
s
 Git operations manager. **Methods**: - `execute_workflow(workflow_config: Dict[str, Any]) -> Dict[str, Any]`: Execute a complex Git workflow. - `get_repository_health() -> Dict[str, Any]`: Get repository health information. ### GitHubRepositor
y
 GitHub repository information. **Methods**: - `from_api_response(cls, data: Dict[str, Any]) -> 'GitHubRepository'`: Create repository object from GitHub API response. ### RateLimi
t
 GitHub API rate limit information. **Methods**: - `reset_datetime() -> float`: Get reset time as datetime. ### GitHubAP
I
 GitHub API client for repository operations. **Methods**: - `get_rate_limit() -> RateLimit`: Get current rate limit status. - `get_user_repositories(username: str, include_repos: List[str], exclude_repos: List[str], max_repos: int) -> List[GitHubRepository]`: Get repositories for a specific user. - `get_organization_repositories(org_name: str, include_repos: List[str], exclude_repos: List[str], max_repos: int) -> List[GitHubRepository]`: Get repositories for a specific organization. - `get_repository(owner: str, repo: str) -> GitHubRepository`: Get information about a specific repository. - `search_repositories(query: str, language: str, stars: str, forks: str, size: str, followers: str, license: str, sort: str, order: str, per_page: int, max_results: int) -> List[GitHubRepository]`: Search for repositories using GitHub's search API. - `filter_repositories(repositories: List[GitHubRepository], min_stars: int, max_size: int, languages: List[str], exclude_forks: bool, exclude_archived: bool, has_topics: List[str]) -> List[GitHubRepository]`: Filter repositories based on various criteria. - `get_repository_languages(owner: str, repo: str) -> Dict[str, int]`: Get programming languages used in a repository. - `get_repository_topics(owner: str, repo: str) -> List[str]`: Get topics for a repository. - `check_repository_exists(owner: str, repo: str) -> bool`: Check if a repository exists. - `get_repository_contributors(owner: str, repo: str, max_contributors: int) -> List[Dict[str, Any]]`: Get top contributors for a repository. - `close() -> None`: Close the HTTP session. ### GitLabRepositor
y
 GitLab repository information. **Methods**: - `from_api_response(cls, data: Dict[str, Any]) -> 'GitLabRepository'`: Create repository object from GitLab API response. ### BitbucketRepositor
y
 Bitbucket repository information. **Methods**: - `from_api_response(cls, data: Dict[str, Any]) -> 'BitbucketRepository'`: Create repository object from Bitbucket API response. ### LocalRepositor
y
 Local Git repository information. **Methods**: - `from_path(cls, path: Path) -> 'LocalRepository'`: Create repository object from local path. ### PlatformAP
I
 Protocol for Git platform API clients. **Methods**: - `get_user_repositories(username: str, **kwargs) -> List[Any]`: Get repositories for a user. - `get_repository(owner: str, repo: str) -> Any`: Get information about a specific repository. - `check_credentials() -> bool`: Check if credentials are valid. ### GitLabAP
I
 GitLab API client for repository operations. **Methods**: - `get_user_repositories(username: str, include_repos: List[str], exclude_repos: List[str], max_repos: int) -> List[GitLabRepository]`: Get repositories for a GitLab user. - `get_repository(owner: str, repo: str) -> GitLabRepository`: Get information about a specific GitLab repository. - `check_credentials() -> bool`: Check if GitLab credentials are valid. ### BitbucketAP
I
 Bitbucket API client for repository operations. **Methods**: - `get_user_repositories(username: str, include_repos: List[str], exclude_repos: List[str], max_repos: int) -> List[BitbucketRepository]`: Get repositories for a Bitbucket user. - `get_repository(owner: str, repo: str) -> BitbucketRepository`: Get information about a specific Bitbucket repository. - `check_credentials() -> bool`: Check if Bitbucket credentials are valid. ### LocalGitAP
I
 Local Git repository API for managing local repositories. **Methods**: - `discover_repositories(max_depth: int) -> List[LocalRepository]`: Discover Git repositories in base paths. - `get_repository(path: str) -> LocalRepository`: Get information about a local repository. - `check_repository(path: str) -> bool`: Check if a path contains a valid Git repository. ### MultiPlatformAP
I
 Unified API client for multiple Git platforms. **Methods**: - `get_user_repositories(platform: str, username: str, **kwargs) -> List[Any]`: Get repositories for a user across platforms. - `get_repository(platform: str, owner: str, repo: str) -> Any`: Get repository information across platforms. - `check_credentials(platform: str) -> bool`: Check if credentials are valid for a platform. - `get_supported_platforms() -> List[str]`: Get list of supported platforms. ### CloneProgres
s
 Track cloning progress and statistics. **Methods**: - `increment_completed()`: Increment completed repository count. - `increment_failed()`: Increment failed repository count. - `increment_skipped()`: Increment skipped repository count. - `elapsed_time() -> float`: Get elapsed time since start. - `success_rate() -> float`: Get success rate as percentage. - `get_stats() -> Dict[str, Any]`: Get current statistics. ### RepoClone
r
 Repository cloner with parallel execution and progress tracking. **Methods**: - `clone_repository(owner: str, repo: str, branch: str) -> bool`: Clone a single repository. - `clone_repositories_for_user(username: str, repositories: List[GitHubRepository]) -> Tuple[int, int]`: Clone repositories for a specific user. - `clone_multiple_repositories(repositories: List[Tuple[str, str, str]]) -> Dict[str, bool]`: Clone multiple repositories in parallel. - `get_disk_usage() -> Dict[str, Any]`: Get disk usage information for the output directory. - `cleanup_failed_clones() -> int`: Clean up any partially cloned repositories. - `get_clone_stats() -> Dict[str, Any]`: Get cloning statistics and progress. - `reset_progress() -> None`: Reset progress tracking. - `close() -> None`: Clean up resources. - `estimate_clone_time(repo_count: int, avg_repo_size: int) -> Dict[str, Any]`: Estimate cloning time based on repository count and average size. ### RepoManage
r
 Repository Manager for handling operations on multiple Git repositories. **Methods**: - `clone_repositories(repo_list: List[Dict], parallel: bool) -> Dict`: Clone multiple repositories. - `sync_repositories(repo_names: Optional[List[str]]) -> Dict`: Synchronize repositories by pulling latest changes. - `check_repo_status(repo_names: Optional[List[str]]) -> Dict`: Check status of repositories (changes, branch, etc.). - `create_branch(branch_name: str, repo_names: Optional[List[str]]) -> Dict`: Create a branch in repositories. - `checkout_branch(branch_name: str, repo_names: Optional[List[str]]) -> Dict`: Checkout a branch in repositories. - `batch_operation(operation: str, *args, **kwargs) -> Dict`: Perform a Git operation across multiple repositories. ### create_advanced_git_operation
s
 `create_advanced_git_operations(repo_path: Union[str, Path]) -> AdvancedGitOperations` Create an AdvancedGitOperations instance for a repository. ### create_platform_ap
i
 `create_platform_api(config: Dict[str, Any]) -> MultiPlatformAPI` Create a multi-platform API client from configuration. ## Capabilities
 - **22 classes** for core functionality - **2 functions** for utility operations ## Integration
 - **Location**: `GEO-INFER-GIT/src/geo_infer_git/core` - **Type**: Directory Node 