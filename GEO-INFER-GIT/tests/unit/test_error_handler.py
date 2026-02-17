"""Tests for GIT error handling utilities."""
import pytest

from geo_infer_git.utils.error_handler import (
    ValidationError,
    ErrorCategory,
    ErrorSeverity,
)


class TestErrorModels:
    def test_error_category_values(self):
        assert ErrorCategory.CONFIGURATION is not None
        assert ErrorCategory.NETWORK is not None

    def test_error_severity_values(self):
        assert ErrorSeverity.LOW is not None
        assert ErrorSeverity.CRITICAL is not None

    def test_validation_error_creation(self):
        error = ValidationError("Invalid config format")
        assert "Invalid config format" in str(error)
        assert isinstance(error, Exception)

    def test_validation_error_with_details(self):
        error = ValidationError(
            "Missing required field: url",
        )
        assert "url" in str(error)
