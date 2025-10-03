"""
Sequential Monte Carlo implementation for Bayesian inference.

This module provides Sequential Monte Carlo (SMC) methods for
Bayesian inference, particularly useful for sequential data.
"""

import numpy as np
from typing import Dict, Any, Optional, Union, List, Tuple, Callable


class SequentialMonteCarlo:
    """
    Sequential Monte Carlo (SMC) for Bayesian inference.

    This class implements SMC sampling for Bayesian models,
    particularly useful for sequential data and online learning.
    """

    def __init__(
        self,
        model,
        n_particles: int = 1000,
        resampling_threshold: float = 0.5,
        random_seed: Optional[int] = None
    ):
        """
        Initialize the SMC sampler.

        Args:
            model: The model to perform inference on
            n_particles: Number of particles for SMC
            resampling_threshold: ESS threshold for resampling
            random_seed: Random seed for reproducibility
        """
        self.model = model
        self.n_particles = n_particles
        self.resampling_threshold = resampling_threshold

        if random_seed is not None:
            np.random.seed(random_seed)

    def run(
        self,
        data: Any,
        n_steps: int = 100,
        progress_bar: bool = True,
        **kwargs
    ) -> Union[Dict[str, np.ndarray], Any]:
        """
        Run SMC sampling for the model.

        Args:
            data: Data for inference
            n_steps: Number of SMC steps
            progress_bar: Whether to show progress
            **kwargs: Additional arguments

        Returns:
            Posterior samples or SMC results
        """
        # Initialize particles
        particles = self._initialize_particles()

        # Run SMC steps
        for step in range(n_steps):
            # Resample if effective sample size is too low
            if self._effective_sample_size(particles) < self.resampling_threshold * self.n_particles:
                particles = self._resample_particles(particles)

            # Move particles
            particles = self._move_particles(particles, data, step)

        # Extract samples from final particles
        samples = self._extract_samples(particles)

        return samples

    def _initialize_particles(self) -> List[Dict[str, float]]:
        """Initialize SMC particles."""
        particles = []

        for _ in range(self.n_particles):
            particle = {}

            for param, param_info in self.model.parameters.items():
                if param_info['prior'] == 'log_normal':
                    mu = param_info['hyperparams']['mu']
                    sigma = param_info['hyperparams']['sigma']
                    particle[param] = np.exp(np.random.normal(mu, sigma))
                elif param_info['prior'] == 'normal':
                    mu = param_info['hyperparams']['mu']
                    sigma = param_info['hyperparams']['sigma']
                    particle[param] = np.random.normal(mu, sigma)
                elif param_info['prior'] == 'uniform':
                    low = param_info['hyperparams']['low']
                    high = param_info['hyperparams']['high']
                    particle[param] = np.random.uniform(low, high)
                else:
                    particle[param] = np.random.normal(0, 1)

            particles.append(particle)

        return particles

    def _effective_sample_size(self, particles: List[Dict[str, float]]) -> float:
        """Compute effective sample size."""
        # Simplified ESS calculation
        weights = [p.get('weight', 1.0) for p in particles]
        weights = np.array(weights)
        weights = weights / np.sum(weights)  # Normalize

        return 1.0 / np.sum(weights**2)

    def _resample_particles(self, particles: List[Dict[str, float]]) -> List[Dict[str, float]]:
        """Resample particles based on their weights."""
        weights = np.array([p.get('weight', 1.0) for p in particles])
        weights = weights / np.sum(weights)

        # Resample indices
        indices = np.random.choice(len(particles), size=len(particles), p=weights, replace=True)

        # Create new particles
        new_particles = []
        for idx in indices:
            new_particle = particles[idx].copy()
            new_particle['weight'] = 1.0 / len(particles)  # Equal weights after resampling
            new_particles.append(new_particle)

        return new_particles

    def _move_particles(
        self,
        particles: List[Dict[str, float]],
        data: Any,
        step: int
    ) -> List[Dict[str, float]]:
        """Move particles using MCMC steps."""
        new_particles = []

        for particle in particles:
            # Propose new particle
            proposed = self._propose_particle(particle)

            # Compute acceptance probability
            log_accept_prob = self._compute_acceptance_probability(particle, proposed, data)

            # Accept or reject
            if np.log(np.random.uniform()) < log_accept_prob:
                new_particles.append(proposed)
            else:
                new_particles.append(particle)

        return new_particles

    def _propose_particle(self, particle: Dict[str, float]) -> Dict[str, float]:
        """Propose a new particle."""
        proposed = particle.copy()

        for param in particle:
            if param != 'weight':
                # Simple random walk proposal
                proposed[param] = particle[param] + np.random.normal(0, 0.1)

        return proposed

    def _compute_acceptance_probability(
        self,
        current: Dict[str, float],
        proposed: Dict[str, float],
        data: Any
    ) -> float:
        """Compute acceptance probability for particle move."""
        # Compute log posterior for current and proposed
        current_log_post = self.model.log_posterior(current, data)
        proposed_log_post = self.model.log_posterior(proposed, data)

        # Proposal ratio (symmetric)
        log_proposal_ratio = 0.0

        # Acceptance probability
        log_accept_prob = proposed_log_post - current_log_post + log_proposal_ratio

        return min(0, log_accept_prob)  # Metropolis acceptance

    def _extract_samples(self, particles: List[Dict[str, float]]) -> Dict[str, np.ndarray]:
        """Extract samples from final particles."""
        samples = {}

        # Get all parameter names
        param_names = set()
        for particle in particles:
            param_names.update(particle.keys())
        param_names.discard('weight')  # Remove weight if present

        # Extract samples for each parameter
        for param in param_names:
            samples[param] = np.array([p[param] for p in particles])

        return samples

    def update(
        self,
        new_data: Any,
        previous_samples: Union[Dict[str, np.ndarray], Any],
        **kwargs
    ) -> Union[Dict[str, np.ndarray], Any]:
        """
        Update particles with new data.

        Args:
            new_data: New data for updating
            previous_samples: Previous SMC samples
            **kwargs: Additional arguments

        Returns:
            Updated samples
        """
        # Initialize particles from previous samples
        particles = []
        for i in range(min(self.n_particles, len(previous_samples[list(previous_samples.keys())[0]]))):
            particle = {}
            for param, values in previous_samples.items():
                particle[param] = values[i]
            particle['weight'] = 1.0 / self.n_particles
            particles.append(particle)

        # Run SMC on new data
        return self.run(new_data, **kwargs)
