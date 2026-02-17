"""Tests for behavioral economics module."""

import numpy as np
import pytest
from geo_infer_econ.microeconomics.behavioral_economics import (
    ProspectTheory,
    BehavioralParameters,
)


class TestProspectTheory:
    """Tests for prospect theory implementation."""

    def setup_method(self) -> None:
        self.pt = ProspectTheory(
            BehavioralParameters(risk_aversion=0.88, loss_aversion=2.25)
        )

    def test_value_function_gains(self) -> None:
        outcomes = np.array([10.0, 20.0, 50.0])
        values = self.pt.value_function(outcomes, reference_point=0.0)
        assert all(v > 0 for v in values)
        # Diminishing sensitivity: value function concave in gains
        assert values[1] / values[0] < 2.0

    def test_value_function_losses(self) -> None:
        outcomes = np.array([-10.0, -20.0])
        values = self.pt.value_function(outcomes, reference_point=0.0)
        assert all(v < 0 for v in values)

    def test_loss_aversion(self) -> None:
        """Loss of $X hurts more than gain of $X feels good."""
        gain_val = self.pt.value_function(np.array([10.0]))[0]
        loss_val = self.pt.value_function(np.array([-10.0]))[0]
        assert abs(loss_val) > abs(gain_val)

    def test_reference_dependence(self) -> None:
        """Different reference points change gain/loss framing."""
        outcomes = np.array([15.0])
        v_gain = self.pt.value_function(outcomes, reference_point=0.0)
        v_loss = self.pt.value_function(outcomes, reference_point=20.0)
        assert v_gain[0] > 0  # 15 is a gain relative to 0
        assert v_loss[0] < 0  # 15 is a loss relative to 20

    def test_probability_weighting_overweights_small(self) -> None:
        probs = np.array([0.01, 0.5, 0.99])
        weighted = self.pt.probability_weighting(probs)
        # Overweight small probabilities
        assert weighted[0] > probs[0]
        # Underweight large probabilities
        assert weighted[2] < probs[2]

    def test_probability_weighting_preserves_order(self) -> None:
        probs = np.array([0.1, 0.3, 0.7, 0.9])
        weighted = self.pt.probability_weighting(probs)
        for i in range(len(weighted) - 1):
            assert weighted[i] <= weighted[i + 1]


class TestBehavioralParameters:
    """Tests for behavioral parameter defaults."""

    def test_default_parameters(self) -> None:
        params = BehavioralParameters()
        assert params.loss_aversion == 2.25
        assert params.risk_aversion == 0.5
        assert 0 < params.time_discount_rate < 1

    def test_custom_parameters(self) -> None:
        params = BehavioralParameters(
            risk_aversion=0.9, loss_aversion=3.0, present_bias=0.7
        )
        assert params.risk_aversion == 0.9
        assert params.loss_aversion == 3.0
        assert params.present_bias == 0.7
