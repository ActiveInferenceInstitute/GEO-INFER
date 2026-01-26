# core
 ## Overview
 This directory contains core components. It includes 5 Python modules. ## Components
 ### advanced_gi
t
.py Git operations for GEO-INFER-GIT. **Classes**: `SubmoduleInfo`, `MergeConflict`, `CherryPickOperation`, `RebaseOperation`, `SubmoduleManager`, `CherryPickManager`, `RebaseManager`, `AdvancedGitOperations` **Functions**: `create_advanced_git_operations` ### github_ap
i
.py GitHub API client for GEO-INFER-GIT. **Classes**: `GitHubRepository`, `RateLimit`, `GitHubAPI` ### multi_platform_ap
i
.py Multi-platform Git API client for GEO-INFER-GIT. **Classes**: `GitLabRepository`, `BitbucketRepository`, `LocalRepository`, `PlatformAPI`, `GitLabAPI`, `BitbucketAPI`, `LocalGitAPI`, `MultiPlatformAPI` **Functions**: `create_platform_api` ### repo_clone
r
.py Repository cloning functionality for GEO-INFER-GIT. **Classes**: `CloneProgress`, `RepoCloner` ### repo_manage
r
.py Repository Manager for GEO-INFER-GIT **Classes**: `RepoManager` ## Usage
 See individual component documentation for usage examples. ## Integration
 This directory integrates with other module components and may be used by higher-level modules. 