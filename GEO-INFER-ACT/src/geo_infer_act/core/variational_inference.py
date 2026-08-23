"""
Variational inference for active inference models.

This module implements variational inference algorithms for belief updating
in active inference models, including mean-field and structured approximations.
"""

import numpy as np
from typing import Callable, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class VariationalInference:
    """
    Variational inference engine for active inference models.

    Implements various variational inference algorithms for efficient
    belief updating in probabilistic models.
    """

    def __init__(
        self,
        max_iterations: int = 100,
        tolerance: float = 1e-6,
        random_seed: Optional[int] = None,
    ):
        """
        Initialize the variational inference engine.

        Args:
            max_iterations: Maximum number of iterations for iterative algorithms
            tolerance: Convergence tolerance
            random_seed: Optional seed for reproducible sampling updates
        """
        if (
            isinstance(max_iterations, bool)
            or int(max_iterations) != max_iterations
            or max_iterations <= 0
        ):
            raise ValueError("max_iterations must be a positive integer")
        if not np.isfinite(tolerance) or tolerance <= 0:
            raise ValueError("tolerance must be finite and strictly positive")
        self.max_iterations = int(max_iterations)
        self.tolerance = float(tolerance)
        self.rng = np.random.default_rng(random_seed)

    def mean_field_update(
        self,
        prior: Dict[str, np.ndarray],
        likelihood: Dict[str, np.ndarray],
        observations: np.ndarray,
    ) -> Dict[str, np.ndarray]:
        """
        Perform mean-field variational inference update.

        Args:
            prior: Prior distribution parameters
            likelihood: Likelihood function parameters
            observations: Observed data

        Returns:
            Updated posterior parameters
        """
        if not isinstance(prior, dict) or not isinstance(likelihood, dict):
            raise ValueError("prior and likelihood must be mappings")
        observations = np.asarray(observations, dtype=float).reshape(-1)
        if observations.size == 0 or not np.all(np.isfinite(observations)):
            raise ValueError("observations must be a non-empty finite vector")
        # Mean-field update for conjugate categorical and Gaussian cases.
        if "concentration" in prior:
            # Dirichlet-categorical conjugate update
            concentration = np.asarray(prior["concentration"], dtype=float).reshape(-1)
            if concentration.shape != observations.shape:
                raise ValueError(
                    "Dirichlet concentration and observations must have the same shape"
                )
            if not np.all(np.isfinite(concentration)) or np.any(concentration <= 0):
                raise ValueError("Dirichlet concentration must be finite and positive")
            if np.any(observations < 0):
                raise ValueError("Dirichlet observations must be non-negative")
            posterior_concentration = concentration + observations

            # Normalize to get mean parameters
            posterior_mean = posterior_concentration / np.sum(posterior_concentration)

            return {
                "concentration": posterior_concentration,
                "mean": posterior_mean,
                "precision": 1.0 / (posterior_mean * (1 - posterior_mean) + 1e-8),
            }

        elif "mean" in prior and "precision" in prior:
            # Gaussian update
            prior_mean = np.asarray(prior["mean"], dtype=float).reshape(-1)
            prior_precision = np.asarray(prior["precision"], dtype=float)
            if prior_precision.shape != (prior_mean.size, prior_mean.size):
                raise ValueError(
                    "prior precision must be square with one row per state"
                )

            # Likelihood precision (assumed known)
            obs_precision = np.asarray(
                likelihood.get("precision", np.eye(len(observations))), dtype=float
            )
            if (
                prior_mean.shape != observations.shape
                or obs_precision.shape != prior_precision.shape
            ):
                raise ValueError(
                    "Gaussian prior, likelihood, and observations must have matching dimensions"
                )
            for name, matrix in (
                ("prior precision", prior_precision),
                ("observation precision", obs_precision),
            ):
                if not np.all(np.isfinite(matrix)) or not np.allclose(matrix, matrix.T):
                    raise ValueError(f"{name} must be finite and symmetric")
                try:
                    np.linalg.cholesky(matrix)
                except np.linalg.LinAlgError as exc:
                    raise ValueError(f"{name} must be positive definite") from exc

            # Posterior parameters
            posterior_precision = prior_precision + obs_precision
            posterior_mean = np.linalg.solve(
                posterior_precision,
                prior_precision @ prior_mean + obs_precision @ observations,
            )

            return {
                "mean": posterior_mean,
                "precision": posterior_precision,
                "covariance": np.linalg.solve(
                    posterior_precision, np.eye(posterior_precision.shape[0])
                ),
            }

        else:
            # Default update
            return prior.copy()

    def mean_field_update_categorical(
        self, prior: np.ndarray, likelihood: np.ndarray, observations: np.ndarray
    ) -> np.ndarray:
        """Update categorical mean-field beliefs from a Dirichlet prior."""
        return self.mean_field_update(
            {"concentration": prior}, {"likelihood_matrix": likelihood}, observations
        )["mean"]

    def mean_field_update_gaussian(
        self, mean: np.ndarray, cov: np.ndarray, obs: np.ndarray
    ) -> np.ndarray:
        """Update Gaussian mean-field beliefs and return the posterior mean."""
        mean = np.asarray(mean, dtype=float).reshape(-1)
        cov = np.asarray(cov, dtype=float)
        if cov.shape != (mean.size, mean.size):
            raise ValueError("covariance must be square with one row per mean value")
        precision = np.linalg.solve(cov, np.eye(mean.size))
        return self.mean_field_update(
            {"mean": mean, "precision": precision},
            {"precision": np.eye(len(obs)) * 10},
            obs,
        )["mean"]

    def structured_update(
        self,
        factor_graph: Dict[str, Any],
        observations: Dict[str, np.ndarray],
        method: str = "belief_propagation",
    ) -> Dict[str, np.ndarray]:
        """
        Perform structured variational inference with factor graphs.

        Args:
            factor_graph: Factor graph representation
            observations: Observed variables
            method: Inference method ('belief_propagation', 'mean_field')

        Returns:
            Updated beliefs for all variables
        """
        if method == "belief_propagation":
            return self._belief_propagation(factor_graph, observations)
        elif method == "mean_field":
            return self._structured_mean_field(factor_graph, observations)
        else:
            raise ValueError(f"Unknown inference method: {method}")

    def _belief_propagation(
        self, factor_graph: Dict[str, Any], observations: Dict[str, np.ndarray]
    ) -> Dict[str, np.ndarray]:
        """
        Implement belief propagation algorithm.

        Args:
            factor_graph: Factor graph structure
            observations: Observed variables

        Returns:
            Marginal beliefs for all variables
        """
        variables = factor_graph.get("variables", {})
        if not isinstance(variables, dict):
            raise ValueError("factor_graph['variables'] must be a mapping")
        unknown_observations = set(observations) - set(variables)
        if unknown_observations:
            raise ValueError(
                "observations reference unknown variables: "
                + ", ".join(sorted(unknown_observations))
            )

        dimensions = {
            name: self._variable_dimension(name, info)
            for name, info in variables.items()
        }
        clamped: Dict[str, np.ndarray] = {}
        unary = {}
        for var_name, dimension in dimensions.items():
            info = variables[var_name]
            prior = (
                info.get("prior", np.ones(dimension))
                if isinstance(info, dict)
                else np.ones(dimension)
            )
            unary[var_name] = self._normalize_message(prior, dimension)
            if var_name in observations:
                observed = np.asarray(observations[var_name], dtype=float).reshape(-1)
                clamped[var_name] = self._normalize_message(observed, dimension)

        factors = self._parse_factors(factor_graph.get("factors", {}), dimensions)
        factor_to_var: Dict[tuple[str, str], np.ndarray] = {}
        var_to_factor: Dict[tuple[str, str], np.ndarray] = {}
        for factor_name, factor_vars, _ in factors:
            for variable in factor_vars:
                factor_to_var[(factor_name, variable)] = (
                    np.ones(dimensions[variable]) / dimensions[variable]
                )
                var_to_factor[(variable, factor_name)] = clamped.get(
                    variable, unary[variable]
                ).copy()

        beliefs = {name: clamped.get(name, unary[name]).copy() for name in dimensions}
        for iteration in range(self.max_iterations):
            old_beliefs = {name: value.copy() for name, value in beliefs.items()}

            # Factor-to-variable messages marginalize the factor potential
            # over all other variables using their current incoming messages.
            for factor_name, factor_vars, potential in factors:
                for target in factor_vars:
                    message = potential.copy()
                    for axis, variable in reversed(list(enumerate(factor_vars))):
                        if variable == target:
                            continue
                        incoming = var_to_factor[(variable, factor_name)]
                        shape = [1] * message.ndim
                        shape[axis] = dimensions[variable]
                        message = message * incoming.reshape(shape)
                        message = np.sum(message, axis=axis)
                    factor_to_var[(factor_name, target)] = self._normalize_message(
                        message, dimensions[target]
                    )

            for variable, dimension in dimensions.items():
                if variable in clamped:
                    beliefs[variable] = clamped[variable].copy()
                    continue
                belief = unary[variable].copy()
                for factor_name, factor_vars, _ in factors:
                    if variable in factor_vars:
                        belief *= factor_to_var[(factor_name, variable)]
                beliefs[variable] = self._normalize_message(belief, dimension)
                for factor_name, factor_vars, _ in factors:
                    if variable not in factor_vars:
                        continue
                    message = unary[variable].copy()
                    for other_factor_name, other_factor_vars, _ in factors:
                        if (
                            variable in other_factor_vars
                            and other_factor_name != factor_name
                        ):
                            message *= factor_to_var[(other_factor_name, variable)]
                    var_to_factor[(variable, factor_name)] = self._normalize_message(
                        message, dimension
                    )

            if all(
                np.max(np.abs(beliefs[name] - old_beliefs[name])) <= self.tolerance
                for name in beliefs
            ):
                logger.debug(
                    "Belief propagation converged in %s iterations", iteration + 1
                )
                break

        # Preserve observed arrays exactly for the longstanding clamping API;
        # only latent-variable marginals are normalized outputs.
        return {
            name: (
                np.asarray(observations[name]).copy()
                if name in observations
                else beliefs[name]
            )
            for name in dimensions
        }

    @staticmethod
    def _variable_dimension(name: str, info: Any) -> int:
        """Validate and return a factor-graph variable's state dimension."""
        if not isinstance(info, dict):
            raise ValueError(f"variable '{name}' must be described by a mapping")
        dimension = info.get("dimension", 2)
        if isinstance(dimension, bool) or int(dimension) != dimension or dimension <= 0:
            raise ValueError(
                f"variable '{name}' must have a positive integer dimension"
            )
        return int(dimension)

    @staticmethod
    def _normalize_message(values: Any, dimension: int) -> np.ndarray:
        """Normalize a finite non-negative message to a categorical vector."""
        message = np.asarray(values, dtype=float).reshape(-1)
        if message.shape != (dimension,):
            raise ValueError(f"factor message must have shape ({dimension},)")
        if not np.all(np.isfinite(message)) or np.any(message < 0):
            raise ValueError("factor messages must be finite and non-negative")
        total = float(np.sum(message))
        if total <= 0:
            return np.ones(dimension, dtype=float) / dimension
        return message / total

    @classmethod
    def _parse_factors(
        cls, factor_spec: Any, dimensions: Dict[str, int]
    ) -> list[tuple[str, list[str], np.ndarray]]:
        """Parse common categorical factor-table representations."""
        if factor_spec is None:
            return []
        entries = (
            list(factor_spec.items())
            if isinstance(factor_spec, dict)
            else list(enumerate(factor_spec))
        )
        parsed = []
        for raw_name, raw_factor in entries:
            if not isinstance(raw_factor, dict):
                raise ValueError(
                    "each factor must be a mapping with variables and potential"
                )
            factor_name = str(raw_name)
            factor_vars = raw_factor.get("variables", raw_factor.get("scope"))
            if not isinstance(factor_vars, (list, tuple)) or not factor_vars:
                raise ValueError(
                    f"factor '{factor_name}' must define a non-empty variables list"
                )
            factor_vars = [str(variable) for variable in factor_vars]
            if len(set(factor_vars)) != len(factor_vars) or any(
                variable not in dimensions for variable in factor_vars
            ):
                raise ValueError(
                    f"factor '{factor_name}' references an unknown or duplicate variable"
                )
            raw_potential = raw_factor.get(
                "potential", raw_factor.get("values", raw_factor.get("table"))
            )
            if raw_potential is None:
                raise ValueError(
                    f"factor '{factor_name}' must define a potential table"
                )
            potential = np.asarray(raw_potential, dtype=float)
            expected_shape = tuple(dimensions[variable] for variable in factor_vars)
            if potential.shape != expected_shape:
                raise ValueError(
                    f"factor '{factor_name}' potential must have shape {expected_shape}"
                )
            if raw_factor.get("log_potential", False):
                if not np.all(np.isfinite(potential)):
                    raise ValueError("log-potential values must be finite")
                potential = np.exp(potential - np.max(potential))
            elif not np.all(np.isfinite(potential)) or np.any(potential < 0):
                raise ValueError("factor potentials must be finite and non-negative")
            if not np.any(potential > 0):
                raise ValueError(f"factor '{factor_name}' has no positive support")
            parsed.append((factor_name, factor_vars, potential))
        return parsed

    def _structured_mean_field(
        self, factor_graph: Dict[str, Any], observations: Dict[str, np.ndarray]
    ) -> Dict[str, np.ndarray]:
        """
        Implement structured mean-field variational inference.

        Args:
            factor_graph: Factor graph structure
            observations: Observed variables

        Returns:
            Variational posterior approximations
        """
        variables = factor_graph.get("variables", {})
        unknown_observations = set(observations) - set(variables)
        if unknown_observations:
            raise ValueError(
                "observations reference unknown variables: "
                + ", ".join(sorted(unknown_observations))
            )
        dimensions = {
            name: self._variable_dimension(name, info)
            for name, info in variables.items()
        }
        factors = self._parse_factors(factor_graph.get("factors", {}), dimensions)
        q_params = {}
        for var_name, dimension in dimensions.items():
            if var_name in observations:
                # Preserve clamped values in the public result.
                q_params[var_name] = np.asarray(observations[var_name]).copy()
            else:
                prior = variables[var_name].get("prior", np.ones(dimension))
                q_params[var_name] = self._normalize_message(prior, dimension)

        # Coordinate ascent updates
        for iteration in range(self.max_iterations):
            old_params = {k: v.copy() for k, v in q_params.items()}

            for var_name, dimension in dimensions.items():
                if var_name in observations:
                    continue
                log_belief = np.log(
                    self._normalize_message(
                        variables[var_name].get("prior", np.ones(dimension)),
                        dimension,
                    )
                    + 1e-12
                )
                for _, factor_vars, potential in factors:
                    if var_name not in factor_vars:
                        continue
                    expected_log_potential = np.log(np.maximum(potential, 1e-300))
                    for axis, other in reversed(list(enumerate(factor_vars))):
                        if other == var_name:
                            continue
                        other_q = self._normalize_message(
                            q_params[other], dimensions[other]
                        )
                        shape = [1] * expected_log_potential.ndim
                        shape[axis] = dimensions[other]
                        expected_log_potential = np.sum(
                            expected_log_potential * other_q.reshape(shape), axis=axis
                        )
                    log_belief += expected_log_potential
                shifted = log_belief - np.max(log_belief)
                q_params[var_name] = np.exp(shifted)
                q_params[var_name] = self._normalize_message(
                    q_params[var_name], dimension
                )

            # Check convergence
            converged = True
            for var_name in q_params:
                if var_name in observations:
                    continue
                if (
                    np.max(np.abs(q_params[var_name] - old_params[var_name]))
                    > self.tolerance
                ):
                    converged = False
                    break

            if converged:
                logger.debug(
                    f"Structured mean-field converged in {iteration + 1} iterations"
                )
                break

        return q_params

    def importance_sampling_update(
        self,
        prior: Dict[str, np.ndarray],
        likelihood_fn: Callable[[np.ndarray, np.ndarray], float],
        observations: np.ndarray,
        n_samples: int = 1000,
    ) -> Dict[str, np.ndarray]:
        """
        Perform importance sampling for posterior approximation.

        Args:
            prior: Prior distribution parameters
            likelihood_fn: Likelihood function
            observations: Observed data
            n_samples: Number of importance samples

        Returns:
            Approximate posterior statistics
        """
        # Generate samples from prior
        if "mean" in prior and "covariance" in prior:
            # Gaussian prior
            samples = self.rng.multivariate_normal(
                prior["mean"], prior["covariance"], n_samples
            )
        else:
            # Standard normal proposal when only a dimension is supplied.
            dim = len(prior.get("mean", [0, 0]))
            samples = self.rng.normal(size=(n_samples, dim))

        # Compute importance weights
        weights = np.array([likelihood_fn(sample, observations) for sample in samples])
        weights = weights / (np.sum(weights) + 1e-8)

        # Compute weighted statistics
        posterior_mean = np.sum(samples * weights[:, np.newaxis], axis=0)

        # Weighted covariance
        centered_samples = samples - posterior_mean
        posterior_cov = np.sum(
            weights[:, np.newaxis, np.newaxis]
            * centered_samples[:, :, np.newaxis]
            * centered_samples[:, np.newaxis, :],
            axis=0,
        )

        return {
            "mean": posterior_mean,
            "covariance": posterior_cov,
            "precision": np.linalg.inv(
                posterior_cov + 1e-6 * np.eye(posterior_cov.shape[0])
            ),
            "samples": samples,
            "weights": weights,
        }

    def compute_elbo(
        self,
        posterior: Dict[str, np.ndarray],
        prior: Dict[str, np.ndarray],
        likelihood: Dict[str, np.ndarray],
        observations: np.ndarray,
    ) -> float:
        """
        Compute Evidence Lower BOund (ELBO).

        Args:
            posterior: Posterior distribution parameters
            prior: Prior distribution parameters
            likelihood: Likelihood parameters
            observations: Observed data

        Returns:
            ELBO value
        """
        # Expected log likelihood term
        if "mean" in posterior:
            # Gaussian case
            residual = observations - posterior["mean"]
            precision = likelihood.get("precision", np.eye(len(observations)))
            exp_log_lik = -0.5 * residual.T @ precision @ residual
        else:
            # Categorical case.
            exp_log_lik = np.sum(
                posterior.get("mean", posterior.get("concentration", observations))
                * np.log(observations + 1e-8)
            )

        # KL divergence term
        if "mean" in posterior and "mean" in prior:
            # Gaussian KL divergence
            post_mean = posterior["mean"]
            post_prec = posterior.get("precision", np.eye(len(post_mean)))
            prior_mean = prior["mean"]
            prior_prec = prior.get("precision", np.eye(len(prior_mean)))

            try:
                kl_div = 0.5 * (
                    np.trace(np.linalg.solve(prior_prec, post_prec))
                    + (post_mean - prior_mean).T @ prior_prec @ (post_mean - prior_mean)
                    - len(post_mean)
                    + np.log(np.linalg.det(prior_prec) / np.linalg.det(post_prec))
                )
            except np.linalg.LinAlgError:
                kl_div = 0.5 * np.sum((post_mean - prior_mean) ** 2)
        else:
            # Categorical KL divergence.
            post_probs = posterior.get(
                "mean", np.ones(len(observations)) / len(observations)
            )
            prior_probs = prior.get("mean", np.ones_like(post_probs) / len(post_probs))
            kl_div = np.sum(
                post_probs * np.log(post_probs / (prior_probs + 1e-8) + 1e-8)
            )

        elbo = exp_log_lik - kl_div
        return float(elbo)
