"""Tests for BIO visualization utilities."""

import pytest
from geo_infer_bio.utils.visualization import BioVisualizer


class TestBioVisualizer:
    """Tests for the bio visualizer."""

    def test_initialization(self) -> None:
        viz = BioVisualizer()
        assert viz is not None
