"""
Approximate Bayesian Computation implementation for Bayesian inference.

This module provides Approximate Bayesian Computation (ABC) methods for
Bayesian inference when likelihood functions are intractable.
"""

import numpy as np
from typing import Dict, Any, Optional, Union, List, Callable


class ApproximateBayesianComputation:
    """
    Approximate Bayesian Computation (ABC) for Bayesian inference.

    This class implements ABC methods for models where the likelihood
    function is intractable or computationally expensive.
    """

    def __init__(
        self,
        model,
        distance_metric: str = "euclidean",
        tolerance: float = 0.1,
        n_samples: int = 10000,
        random_seed: Optional[int] = None,
    ):
        """
        Initialize the ABC sampler.

        Args:
            model: The model to perform inference on
            distance_metric: Distance metric for comparing simulated and observed data
            tolerance: Tolerance for accepting samples
            n_samples: Number of ABC samples to generate
            random_seed: Random seed for reproducibility
        """
        self.model = model
        self.distance_metric = distance_metric.lower()
        self.tolerance = tolerance
        self.n_samples = n_samples

        if random_seed is not None:
            np.random.seed(random_seed)

    def run(
        self,
        observed_data: Any,
        simulator: Optional[Callable] = None,
        progress_bar: bool = True,
        **kwargs,
    ) -> Union[Dict[str, np.ndarray], Any]:
        """
        Run ABC sampling for the model.

        Args:
            observed_data: Observed data for inference
            simulator: Function that produces model data for a parameter draw
            progress_bar: Whether to show progress
            **kwargs: Additional arguments

        Returns:
            Posterior samples
        """
        if simulator is None:
            raise ValueError(
                "ABC requires an explicit simulator callable for the configured model"
            )

        samples = []
        accepted_count = 0

        # Generate samples until we have enough accepted samples
        total_attempts = 0
        max_attempts = self.n_samples * 10  # Safety limit

        while accepted_count < self.n_samples and total_attempts < max_attempts:
            # Sample from prior
            theta = self._sample_from_prior()

            # Simulate data
            simulated_data = simulator(theta)

            # Compute distance
            distance = self._compute_distance(simulated_data, observed_data)

            # Accept if distance is below tolerance
            if distance < self.tolerance:
                samples.append(theta)
                accepted_count += 1

            total_attempts += 1

        if accepted_count < self.n_samples:
            print(
                f"Warning: Only {accepted_count} samples accepted out of {self.n_samples} requested"
            )

        # Convert to the expected format
        return self._convert_samples_to_dict(samples)

    def _sample_from_prior(self) -> Dict[str, float]:
        """Sample parameter values from the prior distribution."""
        theta = {}

        for param, param_info in self.model.parameters.items():
            if param_info["prior"] == "log_normal":
                mu = param_info["hyperparams"]["mu"]
                sigma = param_info["hyperparams"]["sigma"]
                theta[param] = np.exp(np.random.normal(mu, sigma))
            elif param_info["prior"] == "normal":
                mu = param_info["hyperparams"]["mu"]
                sigma = param_info["hyperparams"]["sigma"]
                theta[param] = np.random.normal(mu, sigma)
            elif param_info["prior"] == "uniform":
                low = param_info["hyperparams"]["low"]
                high = param_info["hyperparams"]["high"]
                theta[param] = np.random.uniform(low, high)
            else:
                theta[param] = np.random.normal(0, 1)

        return theta

    def _compute_distance(self, simulated: np.ndarray, observed: np.ndarray) -> float:
        """Compute distance between simulated and observed data."""
        if self.distance_metric == "euclidean":
            return np.sqrt(np.sum((simulated - observed) ** 2))
        elif self.distance_metric == "manhattan":
            return np.sum(np.abs(simulated - observed))
        elif self.distance_metric == "mahalanobis":
            # Simplified Mahalanobis distance
            diff = simulated - observed
            cov = np.cov(np.column_stack([simulated, observed]))
            if cov.shape[0] >= 2:
                inv_cov = np.linalg.inv(cov)
                return np.sqrt(diff.T @ inv_cov @ diff)
            else:
                return np.sqrt(np.sum(diff**2))
        else:
            raise ValueError(f"Unknown distance metric: {self.distance_metric}")

    def _convert_samples_to_dict(
        self, samples: List[Dict[str, float]]
    ) -> Dict[str, np.ndarray]:
        """Convert list of parameter dictionaries to the expected format."""
        if not samples:
            return {}

        # Get all parameter names
        param_names = samples[0].keys()

        result = {}
        for param in param_names:
            result[param] = np.array([sample[param] for sample in samples])

        return result

    def update(
        self,
        new_data: Any,
        previous_samples: Union[Dict[str, np.ndarray], Any],
        **kwargs,
    ) -> Union[Dict[str, np.ndarray], Any]:
        """
        Update ABC samples with new data.

        Args:
            new_data: New data for updating
            previous_samples: Previous ABC samples
            **kwargs: Additional arguments

        Returns:
            Updated samples
        """
        # For ABC, we can run the algorithm again with the new data
        # and potentially use previous samples to inform the prior
        return self.run(new_data, **kwargs)
