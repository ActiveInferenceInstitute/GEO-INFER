"""Tests for BIO validation utilities."""

from __future__ import annotations

import pytest
from geo_infer_bio.utils.validation import DataValidator


class TestDataValidator:
    """Tests for the data validator."""

    def test_initialization(self) -> None:
        validator = DataValidator()
        assert validator is not None

    def test_validate_spatial_coordinates_valid(self) -> None:
        validator = DataValidator()
        assert validator.validate_spatial_coordinates(latitude=45.0, longitude=-122.0) is True

    def test_validate_spatial_coordinates_invalid_lat(self) -> None:
        validator = DataValidator()
        assert validator.validate_spatial_coordinates(latitude=100.0, longitude=0.0) is False

    def test_validate_sequence_dna(self) -> None:
        validator = DataValidator()
        assert validator.validate_sequence("ATCG") is True

    def test_validate_sequence_invalid(self) -> None:
        validator = DataValidator()
        assert validator.validate_sequence("123XYZ") is False

    def test_validate_gc_content_valid(self) -> None:
        validator = DataValidator()
        assert validator.validate_gc_content(50.0, 100) is True

    def test_validate_gc_content_out_of_range(self) -> None:
        validator = DataValidator()
        assert validator.validate_gc_content(150.0, 100) is False

    def test_validate_gc_content_zero_length(self) -> None:
        validator = DataValidator()
        assert validator.validate_gc_content(50.0, 0) is False

    def test_validate_coding_region_valid(self) -> None:
        validator = DataValidator()
        assert validator.validate_coding_region(0, 199, 200, 100) is True

    def test_validate_coding_region_too_short(self) -> None:
        validator = DataValidator()
        assert validator.validate_coding_region(0, 49, 200, 100) is False

    def test_validate_motif_dna(self) -> None:
        validator = DataValidator()
        assert validator.validate_motif("ATC", "DNA") is True

    def test_validate_motif_rna(self) -> None:
        validator = DataValidator()
        # DataValidator treats RNA with the same charset as DNA (A, T, C, G)
        assert validator.validate_motif("ATC", "RNA") is True

    def test_validate_motif_invalid(self) -> None:
        validator = DataValidator()
        assert validator.validate_motif("XYZ", "DNA") is False