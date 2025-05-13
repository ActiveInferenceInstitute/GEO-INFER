"""
Hamiltonian Monte Carlo implementation for Bayesian inference.
"""

import numpy as np
import xarray as xr
from typing import Dict, Any, Optional, Union, List, Tuple, Callable
from tqdm import tqdm


class HMC:
    """
    Hamiltonian Monte Carlo (HMC) for Bayesian inference.
    
    This class implements HMC sampling for Bayesian models with enhanced
    efficiency for high-dimensional parameter spaces.
    
    Parameters
    ----------
    model : BayesianModel
        The model to perform inference on
    n_chains : int, default=4
        Number of Markov chains to run
    step_size : float, default=0.01
        Initial step size for leapfrog integration
    n_steps : int, default=50
        Number of steps in leapfrog integration
    adapt_step_size : bool, default=True
        Whether to adapt the step size during warmup
    max_tree_depth : int, default=10
        Maximum depth for NUTS (No-U-Turn Sampler)
    target_accept : float, default=0.8
        Target acceptance rate
    random_seed : int, optional
        Random seed for reproducibility
    """
    
    def __init__(
        self,
        model,
        n_chains: int = 4,
        step_size: float = 0.01,
        n_steps: int = 50,
        adapt_step_size: bool = True,
        max_tree_depth: int = 10,
        target_accept: float = 0.8,
        random_seed: Optional[int] = None
    ):
        self.model = model
        self.n_chains = n_chains
        self.step_size = step_size
        self.n_steps = n_steps
        self.adapt_step_size = adapt_step_size
        self.max_tree_depth = max_tree_depth
        self.target_accept = target_accept
        
        if random_seed is not None:
            np.random.seed(random_seed)
    
    def run(
        self,
        data: Any,
        n_samples: int = 1000,
        n_warmup: int = 500,
        thin: int = 1,
        init_strategy: str = 'random',
        use_nuts: bool = True,
        progress_bar: bool = True,
        **kwargs
    ) -> Union[Dict[str, np.ndarray], xr.Dataset]:
        """
        Run HMC sampling for the model.
        
        Parameters
        ----------
        data : any
            Data for inference
        n_samples : int, default=1000
            Number of samples to generate
        n_warmup : int, default=500
            Number of warmup/burn-in steps
        thin : int, default=1
            Thinning rate for samples
        init_strategy : str, default='random'
            Initialization strategy: 'random', 'prior', or 'map'
        use_nuts : bool, default=True
            Whether to use No-U-Turn Sampler (NUTS)
        progress_bar : bool, default=True
            Whether to show a progress bar
        **kwargs : dict
            Additional arguments for sampling
            
        Returns
        -------
        dict or Dataset
            Posterior samples
        """
        # Initialize chains
        chains = self._initialize_chains(data, init_strategy, **kwargs)
        
        # Prepare storage for samples
        param_names = list(self.model.parameters.keys())
        n_params = len(param_names)
        
        # Allocate sample storage - shape: (n_chains, n_samples, n_params)
        samples = np.zeros((self.n_chains, n_samples, n_params))
        
        # Acceptance tracking
        acceptance_rate = np.zeros(self.n_chains)
        
        # Current log probabilities and parameters for each chain
        current_params = chains
        current_log_prob = np.zeros(self.n_chains)
        current_grad = [None] * self.n_chains
        
        for c in range(self.n_chains):
            theta = current_params[c]
            current_log_prob[c], current_grad[c] = self._compute_log_posterior_grad(theta, data)
        
        # Momentum distribution - standard normal
        momentum_dist = lambda size: np.random.normal(0, 1, size=size)
        
        # Adapt step size during warmup
        step_sizes = [self.step_size] * self.n_chains
        
        # Run sampling
        total_iterations = n_warmup + n_samples * thin
        iterator = range(total_iterations)
        if progress_bar:
            iterator = tqdm(iterator, desc="HMC sampling")
            
        for i in iterator:
            # Adapt step size during warmup
            if i < n_warmup and self.adapt_step_size and i % 50 == 0 and i > 0:
                for c in range(self.n_chains):
                    accept_rate = acceptance_rate[c] / (i + 1)
                    if accept_rate < self.target_accept - 0.1:
                        step_sizes[c] *= 0.9
                    elif accept_rate > self.target_accept + 0.1:
                        step_sizes[c] *= 1.1
            
            # Update each chain
            for c in range(self.n_chains):
                # Get current state
                theta = current_params[c]
                log_prob = current_log_prob[c]
                grad = current_grad[c]
                
                # Initialize momentum
                momentum = momentum_dist(len(param_names))
                current_K = 0.5 * np.sum(momentum**2)
                
                # Store initial state
                initial_theta = theta.copy()
                initial_momentum = momentum.copy()
                initial_log_prob = log_prob
                initial_grad = grad.copy()
                
                # Leapfrog integration
                if use_nuts:
                    # No-U-Turn Sampler (NUTS)
                    new_theta, new_momentum, new_log_prob, new_grad, accepted = self._nuts_step(
                        theta, momentum, log_prob, grad, 
                        step_sizes[c], data
                    )
                else:
                    # Standard HMC with fixed trajectory
                    new_theta, new_momentum, new_log_prob, new_grad, accepted = self._hmc_step(
                        theta, momentum, log_prob, grad,
                        step_sizes[c], self.n_steps, data
                    )
                
                # Update state if accepted
                if accepted:
                    current_params[c] = new_theta
                    current_log_prob[c] = new_log_prob
                    current_grad[c] = new_grad
                    acceptance_rate[c] += 1
            
            # Store samples after warmup, respecting thinning
            if i >= n_warmup and (i - n_warmup) % thin == 0:
                sample_idx = (i - n_warmup) // thin
                for c in range(self.n_chains):
                    for p, param in enumerate(param_names):
                        samples[c, sample_idx, p] = current_params[c][param]
        
        # Combine chains and convert to dictionary
        combined_samples = {}
        for p, param in enumerate(param_names):
            # Reshape to (n_chains * n_samples,)
            combined_samples[param] = samples[:, :, p].reshape(-1)
        
        # Report diagnostics
        if progress_bar:
            for c in range(self.n_chains):
                print(f"Chain {c+1} acceptance rate: {acceptance_rate[c] / total_iterations:.2f}")
        
        return combined_samples
    
    def _hmc_step(
        self,
        theta: Dict[str, float],
        momentum: np.ndarray,
        log_prob: float,
        grad: np.ndarray,
        step_size: float,
        n_steps: int,
        data: Any
    ) -> Tuple[Dict[str, float], np.ndarray, float, np.ndarray, bool]:
        """Perform a single HMC step with leapfrog integration."""
        # Make a copy of the initial state
        current_theta = theta.copy()
        current_momentum = momentum.copy()
        current_log_prob = log_prob
        current_grad = grad.copy()
        
        # Half step for momentum
        current_momentum += step_size * current_grad / 2
        
        # Full steps for position and momentum
        for _ in range(n_steps):
            # Full step for position
            self._update_position(current_theta, current_momentum, step_size)
            
            # Recompute gradient at new position
            current_log_prob, current_grad = self._compute_log_posterior_grad(current_theta, data)
            
            # Full step for momentum
            current_momentum += step_size * current_grad
        
        # Half step for momentum
        current_momentum += step_size * current_grad / 2
        
        # Negate momentum for reversibility
        current_momentum = -current_momentum
        
        # Compute Hamiltonian (energy)
        current_K = 0.5 * np.sum(current_momentum**2)
        initial_K = 0.5 * np.sum(momentum**2)
        
        initial_U = -log_prob
        current_U = -current_log_prob
        
        # Compute acceptance probability
        delta_H = current_U + current_K - (initial_U + initial_K)
        accept_prob = min(1, np.exp(-delta_H))
        
        # Accept or reject
        if np.random.uniform() < accept_prob:
            return current_theta, current_momentum, current_log_prob, current_grad, True
        else:
            return theta, momentum, log_prob, grad, False
    
    def _nuts_step(
        self,
        theta: Dict[str, float],
        momentum: np.ndarray,
        log_prob: float,
        grad: np.ndarray,
        step_size: float,
        data: Any
    ) -> Tuple[Dict[str, float], np.ndarray, float, np.ndarray, bool]:
        """
        No-U-Turn Sampler (NUTS) step.
        
        This is a simplified implementation of the No-U-Turn Sampler,
        based on Algorithm 3 of the NUTS paper by Hoffman & Gelman (2014).
        """
        # For simplicity, we'll delegate to a standard HMC step for now
        # In a full implementation, this would use the NUTS algorithm
        # with dynamic trajectory length based on the U-turn criterion
        return self._hmc_step(
            theta, momentum, log_prob, grad, 
            step_size, self.n_steps, data
        )
    
    def _update_position(
        self,
        theta: Dict[str, float],
        momentum: np.ndarray,
        step_size: float
    ) -> None:
        """Update position (parameters) using momentum."""
        param_names = list(theta.keys())
        for i, param in enumerate(param_names):
            theta[param] += step_size * momentum[i]
    
    def _compute_log_posterior_grad(
        self,
        theta: Dict[str, float],
        data: Any
    ) -> Tuple[float, np.ndarray]:
        """
        Compute log posterior and its gradient.
        
        For simplicity, we'll use numerical differentiation.
        In practice, analytical gradients should be provided by the model
        for efficiency.
        """
        # Compute log posterior
        log_posterior = self.model.log_posterior(theta, data)
        
        # Compute gradient using finite differences
        param_names = list(theta.keys())
        grad = np.zeros(len(param_names))
        
        h = 1e-6  # Step size for finite differences
        for i, param in enumerate(param_names):
            theta_plus = theta.copy()
            theta_plus[param] += h
            
            log_posterior_plus = self.model.log_posterior(theta_plus, data)
            
            # Forward difference approximation
            grad[i] = (log_posterior_plus - log_posterior) / h
        
        return log_posterior, grad
    
    def _initialize_chains(
        self,
        data: Any,
        init_strategy: str,
        **kwargs
    ) -> List[Dict[str, float]]:
        """Initialize the Markov chains."""
        param_names = list(self.model.parameters.keys())
        chains = []
        
        if init_strategy == 'custom' and 'custom_init' in kwargs:
            return kwargs['custom_init']
        
        for c in range(self.n_chains):
            chain = {}
            for param in param_names:
                param_info = self.model.parameters[param]
                
                if init_strategy == 'random':
                    # Random initialization based on prior type
                    if param_info['prior'] == 'log_normal':
                        mu = param_info['hyperparams']['mu']
                        sigma = param_info['hyperparams']['sigma']
                        chain[param] = np.exp(np.random.normal(mu, sigma))
                    elif param_info['prior'] == 'normal':
                        mu = param_info['hyperparams']['mu']
                        sigma = param_info['hyperparams']['sigma']
                        chain[param] = np.random.normal(mu, sigma)
                    elif param_info['prior'] == 'uniform':
                        low = param_info['hyperparams']['low']
                        high = param_info['hyperparams']['high']
                        chain[param] = np.random.uniform(low, high)
                    else:
                        # Default to standard normal
                        chain[param] = np.random.normal(0, 1)
                
                elif init_strategy == 'prior':
                    # Sample directly from prior
                    if param_info['prior'] == 'log_normal':
                        mu = param_info['hyperparams']['mu']
                        sigma = param_info['hyperparams']['sigma']
                        chain[param] = np.exp(np.random.normal(mu, sigma))
                    elif param_info['prior'] == 'normal':
                        mu = param_info['hyperparams']['mu']
                        sigma = param_info['hyperparams']['sigma']
                        chain[param] = np.random.normal(mu, sigma)
                    elif param_info['prior'] == 'uniform':
                        low = param_info['hyperparams']['low']
                        high = param_info['hyperparams']['high']
                        chain[param] = np.random.uniform(low, high)
                
                elif init_strategy == 'map':
                    # Todo: implement MAP estimation for initialization
                    # For now, fall back to prior-based initialization
                    if param_info['prior'] == 'log_normal':
                        mu = param_info['hyperparams']['mu']
                        sigma = param_info['hyperparams']['sigma']
                        chain[param] = np.exp(mu)  # Mode of log-normal
                    elif param_info['prior'] == 'normal':
                        mu = param_info['hyperparams']['mu']
                        chain[param] = mu  # Mode of normal
                    elif param_info['prior'] == 'uniform':
                        low = param_info['hyperparams']['low']
                        high = param_info['hyperparams']['high']
                        chain[param] = (low + high) / 2  # Center of uniform
            
            chains.append(chain)
        
        return chains
    
    def update(
        self,
        new_data: Any,
        previous_samples: Union[Dict[str, np.ndarray], xr.Dataset],
        n_samples: int = 500,
        **kwargs
    ) -> Union[Dict[str, np.ndarray], xr.Dataset]:
        """
        Update previous samples with new data.
        
        Parameters
        ----------
        new_data : any
            New data for updating
        previous_samples : dict or Dataset
            Previous posterior samples
        n_samples : int, default=500
            Number of new samples to generate
        **kwargs : dict
            Additional arguments for sampling
            
        Returns
        -------
        dict or Dataset
            Updated posterior samples
        """
        # Convert previous samples to initialization points for chains
        param_names = list(self.model.parameters.keys())
        
        # Get a random subset of previous samples to initialize chains
        if isinstance(previous_samples, dict):
            n_prev = len(previous_samples[param_names[0]])
            indices = np.random.choice(n_prev, self.n_chains, replace=False)
            chains = []
            for idx in indices:
                chain = {}
                for param in param_names:
                    chain[param] = previous_samples[param][idx]
                chains.append(chain)
        else:
            # Handle xarray Dataset
            n_prev = len(previous_samples[param_names[0]])
            indices = np.random.choice(n_prev, self.n_chains, replace=False)
            chains = []
            for idx in indices:
                chain = {}
                for param in param_names:
                    chain[param] = previous_samples[param].values[idx]
                chains.append(chain)
        
        # Run sampling with new data, using previous samples as initialization
        return self.run(
            data=new_data,
            n_samples=n_samples,
            n_warmup=n_samples // 2,  # Shorter warmup for updates
            init_strategy='custom',
            custom_init=chains,
            **kwargs
        ) 