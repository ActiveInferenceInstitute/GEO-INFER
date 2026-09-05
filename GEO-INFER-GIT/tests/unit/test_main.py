"""Regression tests for the module entry point (geo_infer_git.main)."""

import git
import pytest
from pathlib import Path

from geo_infer_git.main import create_gitignore_entry
from geo_infer_git.utils.config_loader import (
    CloneConfig,
    load_clone_config,
)


class TestCloneConfigFlow:
    """The documented entry point must drive CloneConfig via attributes."""

    def test_load_clone_config_returns_dataclass(self):
        config = load_clone_config()
        assert isinstance(config, CloneConfig)
        # Attribute surface consumed by main()
        assert hasattr(config, "output_dir")
        assert hasattr(config, "github_token")
        assert hasattr(config, "concurrency_enabled")
        assert hasattr(config, "report_format")

    def test_config_is_not_subscriptable(self):
        """Regression: main() used to subscript CloneConfig like a dict.

        CloneConfig exposes configuration through attributes only; dict-style
        access must raise TypeError so misuse fails loudly instead of
        silently working in tests.
        """
        config = load_clone_config()
        with pytest.raises(TypeError):
            config["general"]  # type: ignore[index]

    def test_attribute_overrides_match_main_flow(self, tmp_path, monkeypatch):
        """Apply the same overrides main() performs and clone from the result."""
        monkeypatch.chdir(tmp_path)
        config = load_clone_config()
        config.output_dir = str(tmp_path / "cloned")
        config.concurrency_enabled = False
        config.max_workers = 2

        # RepoCloner consumes the mutated CloneConfig directly
        from geo_infer_git.core.repo_cloner import RepoCloner

        cloner = RepoCloner(config)
        try:
            assert cloner.output_dir == Path(config.output_dir)
            assert (tmp_path / "cloned").exists()
        finally:
            cloner.close()


class TestCreateGitignoreEntry:
    def test_writes_relative_entry_inside_repo(self, tmp_path):
        repository_path = tmp_path / "host-repo"
        git.Repo.init(repository_path)
        output_dir = repository_path / "cloned_repositories"
        output_dir.mkdir()

        create_gitignore_entry(str(output_dir))

        gitignore = (repository_path / ".gitignore").read_text(encoding="utf-8")
        assert "cloned_repositories" in gitignore
        # Entry must be repo-relative, never an absolute path
        assert str(tmp_path) not in gitignore

    def test_no_writes_outside_repo(self, tmp_path):
        """An output dir outside any repository must not create files."""
        outside = tmp_path / "outside"
        outside.mkdir()

        create_gitignore_entry(str(outside))

        assert not (outside / ".gitignore").exists()
        assert not (outside.parent / ".gitignore").exists()

    def test_appends_to_existing_gitignore_once(self, tmp_path):
        repository_path = tmp_path / "host-repo"
        git.Repo.init(repository_path)
        (repository_path / ".gitignore").write_text("*.pyc\n", encoding="utf-8")
        output_dir = repository_path / "cloned_repositories"
        output_dir.mkdir()

        create_gitignore_entry(str(output_dir))
        create_gitignore_entry(str(output_dir))

        content = (repository_path / ".gitignore").read_text(encoding="utf-8")
        assert content.count("cloned_repositories") == 1