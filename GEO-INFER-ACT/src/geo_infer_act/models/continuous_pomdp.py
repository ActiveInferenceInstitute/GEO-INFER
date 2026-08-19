"""
Continuous POMDP Active Inference and Gaussian Filter Engine for GEO-INFER-ACT.

Bridges discrete categorical active inference with continuous state-space
generalized predictive coding and Kalman/Laplace filter dynamics.
"""

from __future__ import annotations

import logging
from typing import Dict, Any, Optional, Tuple, List, Union
import numpy as np

logger = logging.getLogger(__name__)


class ContinuousPOMDPActiveInference:
    r"""
    Continuous-state Active Inference model with Laplace approximation / Kalman-Bucy filter.
    
    Implements continuous state transitions $\dot{x} = f(x, a) + w$, linear/nonlinear
    observation mapping $y = g(x) + v$, and variational free energy minimization
    over continuous trajectory predictions and policy controls.
    """

    def __init__(
        self,
        state_dim: int = 2,
        obs_dim: int = 2,
        action_dim: int = 2,
        dt: float = 0.1,
        process_noise_cov: Optional[np.ndarray] = None,
        obs_noise_cov: Optional[np.ndarray] = None,
        prior_mean: Optional[np.ndarray] = None,
        prior_cov: Optional[np.ndarray] = None,
        target_prior: Optional[np.ndarray] = None,
        random_seed: Optional[int] = None,
    ):
        self.state_dim = state_dim
        self.obs_dim = obs_dim
        self.action_dim = action_dim
        self.dt = dt
        self.rng = np.random.default_rng(random_seed)

        # Transition dynamics matrices: dx/dt = A x + B u
        self.A = np.zeros((state_dim, state_dim))
        np.fill_diagonal(self.A, -0.1)  # stable decay by default
        self.B = np.eye(state_dim, action_dim)

        # Observation mapping: y = C x
        self.C = np.eye(obs_dim, state_dim)

        # Covariances
        self.Q = process_noise_cov if process_noise_cov is not None else np.eye(state_dim) * 0.05
        self.R = obs_noise_cov if obs_noise_cov is not None else np.eye(obs_dim) * 0.05

        # Belief states (mean and covariance)
        self.mu = np.zeros(state_dim) if prior_mean is None else np.asarray(prior_mean, dtype=float).copy()
        self.sigma = np.eye(state_dim) if prior_cov is None else np.asarray(prior_cov, dtype=float).copy()

        # Desired/preferred continuous observations
        self.target_prior = np.zeros(obs_dim) if target_prior is None else np.asarray(target_prior, dtype=float).copy()

        self.history: List[Dict[str, Any]] = []

    def set_system_matrices(
        self,
        A: Optional[np.ndarray] = None,
        B: Optional[np.ndarray] = None,
        C: Optional[np.ndarray] = None,
    ) -> None:
        """Set continuous transition, control, and measurement matrices."""
        if A is not None:
            self.A = np.asarray(A, dtype=float)
        if B is not None:
            self.B = np.asarray(B, dtype=float)
        if C is not None:
            self.C = np.asarray(C, dtype=float)

    def predict(self, action: Optional[np.ndarray] = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        Continuous prior propagation step (Euler discretization of continuous dynamics).
        """
        u = np.zeros(self.action_dim) if action is None else np.asarray(action, dtype=float)
        # mu_dot = A * mu + B * u
        mu_dot = self.A @ self.mu + self.B @ u
        mu_pred = self.mu + self.dt * mu_dot

        # Covariance update via discrete Riccati-style approximation:
        # F = I + dt * A
        F = np.eye(self.state_dim) + self.dt * self.A
        sigma_pred = F @ self.sigma @ F.T + self.dt * self.Q
        return mu_pred, sigma_pred

    def update_beliefs(
        self, observation: np.ndarray, action: Optional[np.ndarray] = None
    ) -> Tuple[np.ndarray, np.ndarray, float]:
        """
        Bayesian belief update on receiving continuous measurement.
        
        Returns:
            (updated_mean, updated_covariance, free_energy)
        """
        y = np.asarray(observation, dtype=float)
        mu_pred, sigma_pred = self.predict(action)

        # Innovation / prediction error
        y_pred = self.C @ mu_pred
        eps = y - y_pred

        # Innovation covariance S = C * sigma_pred * C.T + R
        S = self.C @ sigma_pred @ self.C.T + self.R
        K = sigma_pred @ self.C.T @ np.linalg.inv(S)

        # Posterior update
        self.mu = mu_pred + K @ eps
        I_KC = np.eye(self.state_dim) - K @ self.C
        self.sigma = I_KC @ sigma_pred @ I_KC.T + K @ self.R @ K.T

        # Variational Free Energy: F = 0.5 * (eps.T @ S^-1 @ eps + log|S| + c)
        sign, logdet = np.linalg.slogdet(S)
        vfe = 0.5 * float(eps.T @ np.linalg.inv(S) @ eps + logdet + self.obs_dim * np.log(2 * np.pi))

        record = {
            "observation": y.tolist(),
            "belief_mean": self.mu.copy().tolist(),
            "belief_cov_diag": np.diag(self.sigma).tolist(),
            "free_energy": vfe,
        }
        self.history.append(record)
        return self.mu.copy(), self.sigma.copy(), vfe

    def select_action(self, horizon: int = 5) -> np.ndarray:
        """
        Select continuous control action minimizing Expected Free Energy (EFE).
        """
        # Linear Quadratic Regulator / Path Integral style continuous action optimization
        # Minimize predicted distance to target preference: (C * mu_future - target)^2 + control_effort
        best_action = np.zeros(self.action_dim)
        best_efe = float("inf")

        candidate_actions = [
            np.zeros(self.action_dim),
            np.ones(self.action_dim) * 0.5,
            -np.ones(self.action_dim) * 0.5,
            np.ones(self.action_dim) * 1.0,
            -np.ones(self.action_dim) * 1.0,
        ]

        for cand in candidate_actions:
            mu_h = self.mu.copy()
            total_efe = 0.0
            for step in range(horizon):
                mu_dot = self.A @ mu_h + self.B @ cand
                mu_h += self.dt * mu_dot
                y_proj = self.C @ mu_h
                # Pragmatic value + control penalty
                cost = np.sum((y_proj - self.target_prior) ** 2) + 0.01 * np.sum(cand ** 2)
                total_efe += cost

            if total_efe < best_efe:
                best_efe = total_efe
                best_action = cand

        return best_action
