"""
Free energy calculation for active inference models.

This module implements variational free energy calculations for different
types of active inference models, including categorical and Gaussian models.
"""

from typing import Dict, Any, Optional, Union
import logging

import numpy as np

from geo_infer_act.core.types import FreeEnergyBreakdown
from geo_infer_act.utils.math import softmax

logger = logging.getLogger(__name__)

EPSILON = 1e-12


def _coerce_probability_vector(
    values: Union[np.ndarray, list, tuple],
    target_length: Optional[int] = None,
    *,
    use_softmax: bool = False,
) -> np.ndarray:
    """Return a finite normalized probability vector with optional alignment."""
    vector = np.asarray(values, dtype=float).reshape(-1)

    if target_length is not None and len(vector) != target_length:
        if len(vector) < target_length:
            vector = np.pad(vector, (0, target_length - len(vector)), mode="constant")
        else:
            vector = vector[:target_length]

    if use_softmax:
        vector = softmax(vector)
    else:
        vector = np.nan_to_num(vector, nan=0.0, posinf=0.0, neginf=0.0)
        vector = np.clip(vector, EPSILON, None)
        total = float(np.sum(vector))
        if total <= EPSILON:
            vector = np.ones_like(vector, dtype=float) / max(len(vector), 1)
        else:
            vector = vector / total

    return np.clip(vector, EPSILON, 1.0)


class FreeEnergyCalculator:
    """
    Calculator for variational free energy in active inference models.

    The free energy serves as a cost function that agents minimize through
    perception (belief updating) and action (policy selection).
    """

    def __init__(self) -> None:
        """Initialize the free energy calculator with default configuration."""
        self.last_computed_energy: float = 0.0
        self.computation_count: int = 0

    def compute_categorical_free_energy(
        self,
        beliefs: np.ndarray,
        observations: np.ndarray,
        preferences: Optional[np.ndarray] = None,
        return_breakdown: bool = False,
    ) -> Union[float, FreeEnergyBreakdown]:
        """
        Compute variational free energy for categorical models.

        The free energy F is decomposed into accuracy (expected log-likelihood)
        and complexity (KL divergence from prior):

        F[q(s), o] = E_q[log q(s)] - E_q[log p(o,s)]
                   = D_KL[q(s)||p(s)] - E_q[log p(o|s)]
                   = Complexity - Accuracy

        Where:
        - q(s) is the variational posterior (beliefs)
        - p(s) is the prior
        - p(o|s) is the likelihood of observations given states
        - D_KL is the Kullback-Leibler divergence

        Mathematical Foundation:
        The free energy provides an upper bound on the negative log evidence:
        -log p(o) ≤ F[q(s), o]

        Minimizing free energy simultaneously:
        1. Maximizes model evidence (Occam's principle)
        2. Minimizes prediction error (Darwinian imperative)

        Args:
            beliefs: Current variational posterior q(s) over hidden states
            observations: Observed data vector o
            preferences: Prior preferences C (log prior probabilities)

        Returns:
            Free energy value F[q(s), o], or a decomposed result object when
            ``return_breakdown`` is true.

        References:
            - Friston, K. (2010). The free-energy principle: a unified brain theory?
            - Parr, T., Pezzulo, G., & Friston, K. (2022). Active Inference
        """
        beliefs = np.asarray(beliefs)
        if beliefs.dtype == object:
            try:
                beliefs = np.stack([np.asarray(b) for b in beliefs.flat]).astype(float)
            except Exception:
                beliefs = np.asarray(beliefs, dtype=float)
        else:
            beliefs = beliefs.astype(float)
        beliefs = _coerce_probability_vector(beliefs)

        entropy = float(-np.sum(beliefs * np.log(beliefs + EPSILON)))

        if preferences is not None:
            prior = _coerce_probability_vector(preferences, len(beliefs))
        else:
            prior = np.ones_like(beliefs) / len(beliefs)
        complexity = float(
            np.sum(beliefs * (np.log(beliefs + EPSILON) - np.log(prior + EPSILON)))
        )

        obs_prob = _coerce_probability_vector(
            observations, len(beliefs), use_softmax=True
        )
        accuracy = float(np.sum(beliefs * np.log(obs_prob + EPSILON)))

        free_energy = float(complexity - accuracy)
        self.last_computed_energy = free_energy
        self.computation_count += 1

        if return_breakdown:
            return FreeEnergyBreakdown(
                free_energy=free_energy,
                accuracy=accuracy,
                complexity=complexity,
                entropy=entropy,
                metadata={"model_type": "categorical"},
            )
        return free_energy

    def compute_gaussian_free_energy(
        self,
        mean: np.ndarray,
        precision: np.ndarray,
        observations: np.ndarray,
        prior_mean: Optional[np.ndarray] = None,
        prior_precision: Optional[np.ndarray] = None,
    ) -> float:
        """
        Compute free energy for Gaussian models.

        Args:
            mean: Current belief mean
            precision: Current belief precision matrix
            observations: Observed data
            prior_mean: Prior mean
            prior_precision: Prior precision matrix

        Returns:
            Free energy value
        """
        # Set defaults
        if prior_mean is None:
            prior_mean = np.zeros_like(mean)
        if prior_precision is None:
            prior_precision = np.eye(len(mean))

        # Complexity term (KL divergence from prior)
        try:
            complexity = 0.5 * (
                np.trace(np.linalg.solve(prior_precision, precision))
                + (mean - prior_mean).T @ prior_precision @ (mean - prior_mean)
                - len(mean)
                + np.log(np.linalg.det(prior_precision) / np.linalg.det(precision))
            )
        except np.linalg.LinAlgError:
            # Fallback calculation
            complexity = 0.5 * np.trace(precision)

        # Accuracy term (negative log likelihood)
        residual = observations - mean
        accuracy = 0.5 * residual.T @ precision @ residual

        free_energy = float(complexity + accuracy)
        self.last_computed_energy = free_energy
        self.computation_count += 1

        return free_energy

    def compute_expected_free_energy(
        self,
        beliefs: np.ndarray,
        policy: Dict[str, Any],
        preferences: Optional[np.ndarray] = None,
        return_breakdown: bool = False,
    ) -> Union[float, FreeEnergyBreakdown]:
        """
        Compute expected free energy for policy evaluation.

        Args:
            beliefs: Current beliefs
            policy: Policy to evaluate. Supported diagnostic keys include
                ``expected_free_energy`` for externally supplied scores,
                ``predicted_beliefs`` or ``expected_observation`` for
                policy-conditioned predictive distributions,
                ``exploration_bonus``, ``risk_preference``, and ``ambiguity``.
            preferences: Prior preferences

        Returns:
            Expected free energy value, or a decomposed result object when
            ``return_breakdown`` is true.
        """
        if isinstance(policy, dict) and "expected_free_energy" in policy:
            expected_free_energy = float(policy["expected_free_energy"])
            if return_breakdown:
                return FreeEnergyBreakdown(
                    free_energy=expected_free_energy,
                    metadata={"policy_supplied_expected_free_energy": True},
                )
            return expected_free_energy

        beliefs = _coerce_probability_vector(beliefs)
        if "predicted_beliefs" in policy:
            predictive = _coerce_probability_vector(
                policy["predicted_beliefs"], len(beliefs)
            )
        elif "expected_observation" in policy:
            predictive = _coerce_probability_vector(
                policy["expected_observation"], len(beliefs)
            )
        else:
            predictive = beliefs

        entropy = float(-np.sum(predictive * np.log(predictive + EPSILON)))
        epistemic_value = entropy

        if preferences is not None:
            preferences = _coerce_probability_vector(preferences, len(beliefs))
            pragmatic_value = float(-np.sum(predictive * np.log(preferences + EPSILON)))
        else:
            pragmatic_value = 0.0

        exploration_bonus = float(policy.get("exploration_bonus", 0.1))
        risk_preference = float(policy.get("risk_preference", 0.0))
        temporal_discount = float(policy.get("temporal_discount", 1.0))
        ambiguity = float(policy.get("ambiguity", 0.0))

        risk = float(risk_preference * np.var(predictive))
        expected_free_energy = float(
            temporal_discount * pragmatic_value
            - exploration_bonus * epistemic_value
            + risk
            + ambiguity
        )

        self.last_computed_energy = expected_free_energy
        self.computation_count += 1

        if return_breakdown:
            return FreeEnergyBreakdown(
                free_energy=expected_free_energy,
                entropy=entropy,
                pragmatic_value=pragmatic_value,
                epistemic_value=epistemic_value,
                risk=risk,
                ambiguity=ambiguity,
                metadata={
                    "model_type": "expected_policy",
                    "predictive_beliefs": predictive.copy(),
                    "temporal_discount": temporal_discount,
                    "exploration_bonus": exploration_bonus,
                },
            )
        return expected_free_energy

    def compute(
        self,
        beliefs: Union[np.ndarray, Dict],
        observations: Optional[np.ndarray] = None,
        preferences: Optional[np.ndarray] = None,
        model_type: str = "categorical",
    ) -> float:
        """General free energy compute dispatching."""
        if model_type == "categorical":
            if isinstance(beliefs, dict):
                beliefs = beliefs.get("states", beliefs.get("mean"))
            obs = (
                observations
                if observations is not None
                else np.ones_like(beliefs) / len(beliefs)
            )
            return self.compute_categorical_free_energy(beliefs, obs, preferences)
        elif model_type == "gaussian":
            mean = beliefs.get("mean", beliefs)
            precision = beliefs.get("precision", np.eye(len(mean)))
            obs = observations if observations is not None else np.zeros_like(mean)
            prior_mean = (
                preferences.get("mean") if isinstance(preferences, dict) else None
            )
            prior_prec = (
                preferences.get("precision") if isinstance(preferences, dict) else None
            )
            return self.compute_gaussian_free_energy(
                mean, precision, obs, prior_mean, prior_prec
            )
        else:
            raise ValueError(f"Unsupported model type: {model_type}")
