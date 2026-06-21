"""Tests for GIT REST API repository status handling."""

import asyncio

import pytest
from fastapi import HTTPException

from geo_infer_git.api.rest_api import list_repositories


class _RepoManager:
    def __init__(self, repositories):
        self._repositories = repositories

    def _get_all_repo_paths(self):
        return self._repositories


def test_list_repositories_error_filter_reports_missing_and_non_git(tmp_path):
    """Test error status includes missing paths and non-git directories."""
    active_repo = tmp_path / "active"
    active_repo.mkdir()
    (active_repo / ".git").mkdir()
    non_git_repo = tmp_path / "non_git"
    non_git_repo.mkdir()
    missing_repo = tmp_path / "missing"

    result = asyncio.run(
        list_repositories(
            status_filter="error",
            manager=_RepoManager(
                {
                    "active": active_repo,
                    "non_git": non_git_repo,
                    "missing": missing_repo,
                }
            ),
        )
    )

    assert set(result["repositories"]) == {"non_git", "missing"}
    assert result["repositories"]["non_git"]["exists"] is True
    assert result["repositories"]["non_git"]["is_git"] is False
    assert result["repositories"]["missing"]["exists"] is False


def test_list_repositories_rejects_unknown_status_filter(tmp_path):
    """Test unsupported status filters return a client error."""
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(
            list_repositories(
                status_filter="unknown",
                manager=_RepoManager({"repo": tmp_path / "repo"}),
            )
        )

    assert exc_info.value.status_code == 400
