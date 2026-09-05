"""Tests for GIT repo manager module."""

import git
import pytest

from geo_infer_git.core.repo_manager import RepoManager


class TestRepoManager:
    def test_init_default(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        mgr = RepoManager()
        assert mgr.config is not None
        assert isinstance(mgr.repos, dict)

    def test_init_does_not_create_base_dir(self, tmp_path, monkeypatch):
        """Constructing RepoManager must not create ./repos in the CWD."""
        monkeypatch.chdir(tmp_path)
        mgr = RepoManager()
        assert not (tmp_path / "repos").exists()
        assert mgr.base_dir is not None

    def test_base_dir_created_on_first_clone(self, tmp_path, monkeypatch):
        """The base directory appears on the first write operation."""
        monkeypatch.chdir(tmp_path)
        mgr = RepoManager()
        results = mgr.clone_repositories([{"url": "not-a-valid-url", "name": "x"}])
        assert results == {"x": False}
        assert (tmp_path / "repos").exists()

    def test_get_base_dir(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        mgr = RepoManager()
        base_dir = mgr.base_dir
        assert base_dir is not None

    def test_load_default_config(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        mgr = RepoManager()
        config = mgr.config
        assert isinstance(config, dict)
        assert "repositories" in config

    def test_check_repo_status_no_repos(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        mgr = RepoManager()
        status = mgr.check_repo_status()
        assert isinstance(status, dict)

    def test_branch_lifecycle_uses_real_git_repository(self, tmp_path):
        """Branch operations report and mutate an actual local worktree."""
        repository_path = tmp_path / "demo"
        repository = git.Repo.init(repository_path)
        with repository.config_writer() as writer:
            writer.set_value("user", "name", "GEO-INFER Test")
            writer.set_value("user", "email", "tests@geo-infer.local")
        (repository_path / "README.md").write_text("base\n", encoding="utf-8")
        repository.index.add(["README.md"])
        repository.index.commit("initial commit")
        base_branch = repository.active_branch.name

        manager = RepoManager()
        manager.base_dir = tmp_path
        created = manager.create_branch_for_repository(
            "demo", "feature", base_branch, protected=True
        )

        assert created["name"] == "feature"
        assert created["protected"] is True
        assert {branch["name"] for branch in manager.list_branches("demo")} == {
            base_branch,
            "feature",
        }

        repository.git.checkout("feature")
        (repository_path / "README.md").write_text("feature\n", encoding="utf-8")
        repository.index.add(["README.md"])
        repository.index.commit("feature change")
        merged = manager.merge_branch("demo", "feature", base_branch)

        assert merged["merged"] is True
        assert repository.active_branch.name == "feature"
        repository.git.checkout(base_branch)
        assert (repository_path / "README.md").read_text(
            encoding="utf-8"
        ) == "feature\n"