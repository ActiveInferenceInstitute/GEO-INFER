"""Tests for GIT validation utilities."""
import pytest

from geo_infer_git.utils.validation import (
    ConfigValidator,
    RepositoryValidator,
    InputValidator,
)


class TestConfigValidator:
    def test_init(self):
        validator = ConfigValidator()
        assert validator.schemas is not None

    def test_validate_clone_config_valid(self):
        validator = ConfigValidator()
        config = {
            "general": {"output_dir": "/tmp/repos"},
            "github": {"max_retries": 3, "wait_on_rate_limit": True},
            "concurrency": {"enabled": True, "max_workers": 4},
        }
        errors = validator.validate_config(config, "clone_config")
        assert isinstance(errors, list)

    def test_validate_target_repositories(self):
        validator = ConfigValidator()
        config = {
            "repositories": [
                {"owner": "test-org", "repo": "test-repo", "branch": "main"},
            ]
        }
        errors = validator.validate_config(config, "target_repositories")
        assert isinstance(errors, list)


class TestRepositoryValidator:
    def test_init(self):
        validator = RepositoryValidator()
        assert validator.required_fields == ["name", "url"]

    def test_validate_repository_data_valid(self):
        validator = RepositoryValidator()
        data = {
            "name": "test-repo",
            "url": "https://github.com/owner/repo.git",
            "branch": "main",
        }
        errors = validator.validate_repository_data(data)
        assert isinstance(errors, list)

    def test_validate_repository_data_missing_name(self):
        validator = RepositoryValidator()
        data = {"url": "https://github.com/owner/repo.git"}
        errors = validator.validate_repository_data(data)
        # Should contain at least one error about missing name
        assert isinstance(errors, list)


class TestInputValidator:
    def test_init(self):
        validator = InputValidator()
        assert hasattr(validator, "validation_errors")

    def test_validate_positive_integer_valid(self):
        validator = InputValidator()
        errors = validator.validate_positive_integer(5, "count")
        assert len(errors) == 0

    def test_validate_positive_integer_invalid(self):
        validator = InputValidator()
        errors = validator.validate_positive_integer(-1, "count")
        assert len(errors) > 0

    def test_validate_positive_integer_zero(self):
        validator = InputValidator()
        errors = validator.validate_positive_integer(0, "count")
        assert len(errors) > 0

    def test_validate_positive_integer_non_integer(self):
        validator = InputValidator()
        errors = validator.validate_positive_integer("not_a_number", "count")
        assert len(errors) > 0
