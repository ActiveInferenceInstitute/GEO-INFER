"""Tests for BIO validation utilities."""

import pytest
from geo_infer_bio.utils.validation import DataValidator


class TestDataValidator:
    """Tests for the data validator."""

    def test_initialization(self) -> None:
        validator = DataValidator()
        assert validator is not None
