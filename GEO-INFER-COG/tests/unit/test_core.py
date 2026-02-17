"""
Unit tests for GEO-INFER-COG core functionality.
"""

import pytest
import numpy as np

from geo_infer_cog import __version__
from geo_infer_cog.core.cognitive_engine import CognitiveProcessingEngine, CognitiveState


class TestCogModule:
    """Test basic module functionality."""

    def test_module_import(self) -> None:
        """Test that the module can be imported."""
        import geo_infer_cog
        assert geo_infer_cog is not None

    def test_module_version(self) -> None:
        """Test that module has a version."""
        assert __version__ is not None
        assert isinstance(__version__, str)

    def test_cognitive_state_creation(self) -> None:
        """Test CognitiveState creation."""
        state = CognitiveState()
        assert state.cognitive_load == 0.0
        assert state.uncertainty_level == 0.0
        assert isinstance(state.attention_focus, dict)
        assert isinstance(state.working_memory, dict)

    def test_cognitive_state_update_attention(self) -> None:
        """Test attention update functionality."""
        state = CognitiveState()
        focus_areas = {"area1": 0.8, "area2": 0.5}
        state.update_attention(focus_areas)
        # update_attention normalizes weights so they sum to 1.0
        total = sum(focus_areas.values())
        expected = {k: v / total for k, v in focus_areas.items()}
        assert state.attention_focus == expected

    def test_cognitive_engine_initialization(self) -> None:
        """Test CognitiveProcessingEngine initialization."""
        engine = CognitiveProcessingEngine()
        assert engine is not None
        assert hasattr(engine, 'process_spatial_input')

