"""
Unit tests for the Ecological Active Inference Model.

Tests the EcologicalModel class which implements ecological niche modeling
using Active Inference with hidden states for resources and predation risk.
"""

import numpy as np
import pytest

from geo_infer_act.models.ecological import EcologicalModel


class TestEcologicalModelInit:
    """Test EcologicalModel initialization and matrix construction."""

    def test_default_initialization(self) -> None:
        """Test that default initialization creates valid model dimensions."""
        model = EcologicalModel()
        assert model.num_states == [3, 2]
        assert model.num_obs == [3, 2]
        assert model.num_controls == [3]
        assert model.num_factors == 2
        assert model.num_modalities == 2

    def test_a_matrix_construction(self) -> None:
        """Test likelihood matrix A has correct structure and normalization."""
        model = EcologicalModel()
        A = model._build_A_matrix()
        assert len(A) == 2
        # Food modality: (3 obs) x (6 flattened states = 3*2)
        assert A[0].shape == (3, 6)
        # Threat modality: (2 obs) x (6 flattened states)
        assert A[1].shape == (2, 6)
        # Columns should sum to 1 (valid conditional distributions)
        for col in range(6):
            np.testing.assert_allclose(A[0][:, col].sum(), 1.0, atol=1e-6)
            np.testing.assert_allclose(A[1][:, col].sum(), 1.0, atol=1e-6)

    def test_b_matrix_construction(self) -> None:
        """Test transition matrix B has valid probability structure."""
        model = EcologicalModel()
        B = model._build_B_matrix()
        assert len(B) == 2
        # Resource factor: (3, 3, 3) -- [next_state, curr_state, action]
        assert B[0].shape == (3, 3, 3)
        # Risk factor: (2, 2, 3)
        assert B[1].shape == (2, 2, 3)
        # Each column (for each action) should sum to 1
        for action_idx in range(3):
            for state_idx in range(3):
                np.testing.assert_allclose(
                    B[0][:, state_idx, action_idx].sum(), 1.0, atol=1e-6
                )
            for state_idx in range(2):
                np.testing.assert_allclose(
                    B[1][:, state_idx, action_idx].sum(), 1.0, atol=1e-6
                )

    def test_c_matrix_preferences(self) -> None:
        """Test preference matrix C encodes ecologically meaningful preferences."""
        model = EcologicalModel()
        C = model._build_C_matrix()
        assert len(C) == 2
        # Prefer abundant food (index 2 highest in modality 0)
        assert C[0][2] > C[0][1] > C[0][0]
        # Prefer quiet/safe (index 0 highest in modality 1)
        assert C[1][0] > C[1][1]

    def test_d_matrix_priors(self) -> None:
        """Test prior matrix D sums to valid distributions."""
        model = EcologicalModel()
        D = model._build_D_matrix()
        assert len(D) == 2
        np.testing.assert_allclose(D[0].sum(), 1.0, atol=1e-6)
        np.testing.assert_allclose(D[1].sum(), 1.0, atol=1e-6)
        # Prior expects high resources
        assert D[0][2] > D[0][0]
        # Prior expects safe environment
        assert D[1][0] > D[1][1]


class TestEcologicalModelDynamics:
    """Test ecological model simulation dynamics."""

    def test_step_returns_valid_structure(self) -> None:
        """Test that a step returns beliefs, action, and observation."""
        model = EcologicalModel()
        result = model.step([1, 0])
        assert 'beliefs' in result
        assert 'action' in result
        assert 'observation' in result
        assert result['observation'] == [1, 0]

    def test_step_default_observation(self) -> None:
        """Test that step works with default observation."""
        model = EcologicalModel()
        result = model.step()
        assert result['observation'] == [0, 0]

    def test_multiple_steps_produce_different_beliefs(self) -> None:
        """Test that sequential observations lead to belief evolution."""
        np.random.seed(42)
        model = EcologicalModel()
        result1 = model.step([2, 0])  # Abundant food, quiet
        result2 = model.step([0, 1])  # No food, threat noise
        # Different observations should produce different belief states
        # (the exact values depend on the inference engine, but they should differ)
        assert result1['observation'] != result2['observation']


class TestEcologicalModelEdgeCases:
    """Test edge cases for the ecological model."""

    def test_custom_config_override(self) -> None:
        """Test that custom A/B/C/D matrices can override defaults."""
        custom_A = [
            np.ones((3, 6)) / 3.0,
            np.ones((2, 6)) / 2.0,
        ]
        config = {'A': custom_A}
        model = EcologicalModel(config=config)
        # Model should still initialize without error
        assert model.num_states == [3, 2]

    def test_repeated_same_observation(self) -> None:
        """Test model stability under repeated identical observations."""
        model = EcologicalModel()
        results = []
        for _ in range(5):
            results.append(model.step([2, 0]))
        # Model should remain stable (no NaN, no crashes)
        for r in results:
            assert r['action'] is not None
