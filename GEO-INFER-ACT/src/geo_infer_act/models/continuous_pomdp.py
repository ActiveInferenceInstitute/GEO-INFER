"""
Continuous POMDP Active Inference and Gaussian Filter Engine for GEO-INFER-ACT.

Bridges discrete categorical active inference with continuous state-space
generalized predictive coding and Kalman/Laplace filter dynamics.
"""

from __future__ import annotations

import logging
from typing import Dict, Any, Optional, Tuple, List, Union, cast
import numpy as np

from geo_infer_act.core.types import FreeEnergyBreakdown

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

    # ------------------------------------------------------------------
    # Laplace / Kalman-Bucy filtering diagnostics
    # ------------------------------------------------------------------
    def _innovation_covariance(self, action: Optional[np.ndarray] = None) -> np.ndarray:
        """Return the innovation covariance S = C sigma_pred C^T + R."""
        _, sigma_pred = self.predict(action)
        return cast(
            np.ndarray, self.C @ sigma_pred @ self.C.T + self.R
        )

    def _adaptive_precision(self, action: Optional[np.ndarray] = None) -> float:
        """
        Laplace-scaled precision schedule.  Agrees with the inverse
        trace of the innovation covariance so that high innovation
        (surprising observations) downweights the current posterior's
        confidence during action evaluation.
        """
        S = self._innovation_covariance(action)
        trace = float(np.trace(S))
        if not np.isfinite(trace) or trace <= 1e-12:
            return 1.0
        return float(np.clip(1.0 / trace, 1e-3, 1e3))

    def compute_variational_free_energy(
        self,
        observation: Optional[np.ndarray] = None,
        action: Optional[np.ndarray] = None,
    ) -> FreeEnergyBreakdown:
        """
        Laplace-approximated variational free energy for the current belief.

        Decomposes F into an *accuracy* term (precision-weighted squared
        innovation) and a *complexity* term (KL from the predictive prior to
        the posterior).  Both are evaluated in a numerically stable way using
        the Joseph-form covariance handed back by ``update_beliefs``.
        """
        y = (
            self.mu
            if observation is None
            else np.asarray(observation, dtype=float).reshape(-1)
        )
        mu_pred, sigma_pred = self.predict(action)
        y_pred = self.C @ mu_pred
        eps = y - y_pred
        S = self.C @ sigma_pred @ self.C.T + self.R
        sign_logdet, logdet = np.linalg.slogdet(S)
        if sign_logdet <= 0:
            logdet = float(np.log(max(float(np.trace(S)), 1e-12)))
        acc = 0.5 * float(eps.T @ np.linalg.solve(S, eps) + logdet + self.obs_dim * np.log(2 * np.pi))
        _, logdet_prior = np.linalg.slogdet(self.sigma)
        _, logdet_post = np.linalg.slogdet(self.sigma)
        # Complexity: half the expected divergence from the predicted prior.
        complexity = 0.5 * float(
            np.trace(np.linalg.solve(sigma_pred + np.eye(self.state_dim) * 1e-9, self.sigma))
            + (self.mu - mu_pred).T @ sigma_pred @ (self.mu - mu_pred)
            - self.state_dim
            + logdet_prior
            - logdet_post
        )
        fe = float(complexity + acc)
        return FreeEnergyBreakdown(
            free_energy=fe,
            accuracy=acc,
            complexity=complexity,
            entropy=float(np.trace(self.sigma)),
            metadata={
                "model_type": "gaussian_laplace",
                "adaptive_precision": self._adaptive_precision(action),
                "innovation_trace": float(np.trace(S)),
            },
        )

    def compute_expected_free_energy(
        self,
        action: np.ndarray,
        horizon: int = 1,
        return_breakdown: bool = False,
        epistemic_weight: float = 1.0,
        preference_prior: Optional[np.ndarray] = None,
    ) -> Union[float, FreeEnergyBreakdown]:
        """
        Expected free energy for a continuous control action under a Laplace
        filter.

        G(pi) = -Epistemic value - Pragmatic value with simultaneous
        decomposition:

        - **Pragmatic cost** is the expected squared error between the
          projected observation trajectory and the preferred target
          (goal-seeking; minimized by approaching ``target_prior``).  It is
          exposed as ``pragmatic_value`` in the breakdown.
        - **Epistemic gain** is the expected information gain measured by
          the trajectory-average log-determinant of the innovation covariance
          (uncertainty resolution; strongest when sensing would disambiguate
          hidden states).
        - **Risk** folds in the control effort, favouring parsimonious
          commands.

        Returns a ``FreeEnergyBreakdown`` when requested; the scalar combined
        EFE otherwise.
        """
        target = (
            self.target_prior
            if preference_prior is None
            else np.asarray(preference_prior, dtype=float).reshape(-1)
        )
        u = np.asarray(action, dtype=float)
        mu_h = self.mu.copy()
        cov_h = self.sigma.copy()
        pragmatic = 0.0
        epistemic = 0.0
        F = np.eye(self.state_dim) + self.dt * self.A
        for _ in range(max(int(horizon), 1)):
            mu_dot = self.A @ mu_h + self.B @ u
            mu_h = mu_h + self.dt * mu_dot
            cov_h = F @ cov_h @ F.T + self.dt * self.Q
            y_proj = self.C @ mu_h
            # Pragmatic cost: summed squared error to the target (lower is
            # better; drives goal-seeking).
            pragmatic += float(np.sum((y_proj - target) ** 2))
            # Epistemic gain: log-determinant of the innovation covariance
            # (higher innovation means more uncertainty resolved by sensing).
            S_h = self.C @ cov_h @ self.C.T + self.R
            sign, ld = np.linalg.slogdet(S_h)
            if sign > 0 and np.isfinite(ld):
                epistemic += 0.5 * float(ld)
        control = 0.01 * float(np.sum(u**2))
        pragmatic_value = float(pragmatic)
        epistemic_value = float(epistemic)
        # Minimise pragmatic cost and control effort while rewarding epistemic
        # (information-gain) value via the subtractive epistemic term.
        expected_free_energy = float(
            pragmatic - epistemic_weight * epistemic + control
        )
        if return_breakdown:
            return FreeEnergyBreakdown(
                free_energy=expected_free_energy,
                pragmatic_value=pragmatic_value,
                epistemic_value=epistemic_value,
                risk=control,
                entropy=float(np.trace(self.sigma)),
                metadata={
                    "action": u.tolist(),
                    "epistemic_weight": float(epistemic_weight),
                    "adaptive_precision": self._adaptive_precision(),
                },
            )
        return expected_free_energy

    def select_action(self, horizon: int = 5) -> np.ndarray:
        """
        Select continuous control action minimizing Expected Free Energy (EFE).
        """
        # Use the decomposed epistemic + pragmatic EFE to prefer actions that
        # both approach the target and reduce hidden-state uncertainty.
        scoreboard = self.evaluate_actions(horizon=horizon)
        return cast(np.ndarray, scoreboard["best_action"])

    def evaluate_actions(
        self,
        horizon: int = 1,
        candidate_actions: Optional[List[np.ndarray]] = None,
        epistemic_weight: float = 1.0,
    ) -> Dict[str, Any]:
        """
        Score a set of continuous control actions by expected free energy,
        returning the per-action decomposition plus the arg-minimum action.

        Returns a dictionary with keys:
            ``candidates``, ``efe_scores``, ``pragmatic_values``,
            ``epistemic_values``, ``best_index``, ``best_action``,
            ``best_efe`` and ``metadata`` (pure Python floats for logging).
        """
        if candidate_actions is None:
            candidates: List[np.ndarray] = [
                np.zeros(self.action_dim),
                np.ones(self.action_dim) * 0.5,
                -np.ones(self.action_dim) * 0.5,
                np.ones(self.action_dim) * 1.0,
                -np.ones(self.action_dim) * 1.0,
            ]
        else:
            candidates = [
                np.asarray(action, dtype=float).reshape(-1) for action in candidate_actions
            ]
        efe_scores: List[float] = []
        pragmatic_values: List[float] = []
        epistemic_values: List[float] = []
        for cand in candidates:
            # Normalise candidate length to action_dim for broadcasting safety.
            if cand.size != self.action_dim:
                cand = np.resize(cand, self.action_dim)
            breakdown = cast(
                FreeEnergyBreakdown,
                self.compute_expected_free_energy(
                    cand,
                    horizon=horizon,
                    return_breakdown=True,
                    epistemic_weight=epistemic_weight,
                ),
            )
            efe_scores.append(breakdown.free_energy)
            pragmatic_values.append(breakdown.pragmatic_value)
            epistemic_values.append(breakdown.epistemic_value)
        best_index = int(np.argmin(efe_scores))
        return {
            "candidates": [candidate.tolist() for candidate in candidates],
            "efe_scores": efe_scores,
            "pragmatic_values": pragmatic_values,
            "epistemic_values": epistemic_values,
            "best_index": best_index,
            "best_action": candidates[best_index],
            "best_efe": float(efe_scores[best_index]),
            "breakdowns": {
                "pragmatic": pragmatic_values,
                "epistemic": epistemic_values,
                "efe": efe_scores,
            },
        }
