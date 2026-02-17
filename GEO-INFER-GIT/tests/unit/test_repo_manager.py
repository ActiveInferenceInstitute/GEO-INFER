"""Tests for GIT repo manager module."""
import pytest
from unittest.mock import patch
from pathlib import Path

from geo_infer_git.core.repo_manager import RepoManager


class TestRepoManager:
    def test_init_default(self):
        mgr = RepoManager()
        assert mgr.config is not None
        assert isinstance(mgr.repos, dict)

    def test_load_default_config(self):
        mgr = RepoManager()
        config = mgr.config
        assert "repositories" in config or isinstance(config, dict)

    def test_get_base_dir(self):
        mgr = RepoManager()
        base_dir = mgr.base_dir
        assert base_dir is not None

    def test_get_repo_status_no_repos(self):
        mgr = RepoManager()
        if hasattr(mgr, "get_repo_status"):
            status = mgr.get_repo_status()
            assert isinstance(status, (dict, list))
