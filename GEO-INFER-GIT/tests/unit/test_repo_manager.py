"""Tests for GIT repo manager module."""

import git

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
