"""
Markov Chain Monte Carlo implementation for Bayesian inference.
"""

import numpy as np
import xarray as xr
from typing import Dict, Any, Optional, Union, List, Tuple, Callable
from tqdm import tqdm


class MCMC:
    """
    Markov Chain Monte Carlo (MCMC) for Bayesian inference.
    
    This class implements MCMC sampling for Bayesian models, with
    specific enhancements for spatial models.
    
    Parameters
    ----------
    model : BayesianModel
        The model to perform inference on
    n_chains : int, default=4
        Number of Markov chains to run
    step_size : float, default=0.1
        Initial step size for proposals
    adapt_step_size : bool, default=True
        Whether to adapt the step size during warmup
    max_steps : int, default=1000
        Maximum number of steps in one parameter update
    random_seed : int, optional
        Random seed for reproducibility
    """
    
    def __init__(
        self,
        model,
        n_chains: int = 4,
        step_size: float = 0.1,
        adapt_step_size: bool = True,
        max_steps: int = 1000,
        random_seed: Optional[int] = None
    ):
        self.model = model
        self.n_chains = n_chains
        self.step_size = step_size
        self.adapt_step_size = adapt_step_size
        self.max_steps = max_steps
        
        if random_seed is not None:
            np.random.seed(random_seed)
    
    def run(
        self,
        data: Any,
        n_samples: int = 1000,
        n_warmup: int = 500,
        thin: int = 1,
        init_strategy: str = 'random',
        progress_bar: bool = True,
        **kwargs
    ) -> Union[Dict[str, np.ndarray], xr.Dataset]:
        """
        Run MCMC sampling for the model.
        
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
        
        # Current log probabilities for each chain
        current_log_prob = np.zeros(self.n_chains)
        for c in range(self.n_chains):
            current_log_prob[c] = self._log_posterior(chains[c], data)
        
        # Run sampling
        total_iterations = n_warmup + n_samples * thin
        iterator = range(total_iterations)
        if progress_bar:
            iterator = tqdm(iterator, desc="MCMC sampling")
            
        for i in iterator:
            # Adapt step size during warmup
            if i < n_warmup and self.adapt_step_size and i % 50 == 0 and i > 0:
                for c in range(self.n_chains):
                    if acceptance_rate[c] / (i + 1) < 0.2:
                        self.step_size *= 0.8
                    elif acceptance_rate[c] / (i + 1) > 0.5:
                        self.step_size *= 1.2
            
            # Update each chain
            for c in range(self.n_chains):
                # Propose new state
                proposed_theta, log_proposal_ratio = self._propose(chains[c])
                
                # Compute acceptance probability
                proposed_log_prob = self._log_posterior(proposed_theta, data)
                log_accept_prob = proposed_log_prob - current_log_prob[c] + log_proposal_ratio
                
                # Accept or reject
                if np.log(np.random.uniform()) < log_accept_prob:
                    chains[c] = proposed_theta
                    current_log_prob[c] = proposed_log_prob
                    acceptance_rate[c] += 1
            
            # Store samples after warmup, respecting thinning
            if i >= n_warmup and (i - n_warmup) % thin == 0:
                sample_idx = (i - n_warmup) // thin
                for c in range(self.n_chains):
                    for p, param in enumerate(param_names):
                        samples[c, sample_idx, p] = chains[c][param]
        
        # Combine chains and convert to dictionary
        combined_samples = {}
        for p, param in enumerate(param_names):
            # Reshape to (n_chains * n_samples,)
            combined_samples[param] = samples[:, :, p].reshape(-1)
        
        # Report diagnostics
        if progress_bar:
            for c in range(self.n_chains):
                print(f"Chain {c+1} acceptance rate: {acceptance_rate[c] / total_iterations:.2f}")
        
        # Convert samples to desired format (add coordinates for xarray if needed)
        return combined_samples
    
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
    
    def _propose(
        self,
        current_theta: Dict[str, float]
    ) -> Tuple[Dict[str, float], float]:
        """
        Generate a proposal for MCMC.
        
        Parameters
        ----------
        current_theta : dict
            Current parameter values
            
        Returns
        -------
        proposed_theta : dict
            Proposed parameter values
        log_proposal_ratio : float
            Log of the proposal ratio for asymmetric proposals
        """
        proposed_theta = {}
        log_proposal_ratio = 0.0
        
        for param, value in current_theta.items():
            param_info = self.model.parameters[param]
            
            # Adjust proposal based on prior
            if param_info['prior'] == 'log_normal':
                # For log-normal, propose in log space
                log_param = np.log(value)
                proposed_log = log_param + np.random.normal(0, self.step_size)
                proposed_theta[param] = np.exp(proposed_log)
                
                # Proposal ratio is 1.0 (symmetric in log space)
                
            elif param_info['prior'] == 'uniform':
                # For uniform, use truncated normal proposals
                low = param_info['hyperparams']['low']
                high = param_info['hyperparams']['high']
                
                # Keep trying until we get a valid proposal
                steps = 0
                proposed_value = value
                while (proposed_value <= low or proposed_value >= high) and steps < self.max_steps:
                    proposed_value = value + np.random.normal(0, self.step_size)
                    steps += 1
                
                # If still invalid, reflect off boundaries
                if proposed_value <= low:
                    proposed_value = low + (low - proposed_value)
                elif proposed_value >= high:
                    proposed_value = high - (proposed_value - high)
                
                # Cap at boundaries
                proposed_value = max(low, min(high, proposed_value))
                proposed_theta[param] = proposed_value
                
                # Proposal ratio is 1.0 (symmetric)
                
            else:
                # Default to normal proposal
                proposed_theta[param] = value + np.random.normal(0, self.step_size)
                # Proposal ratio is 1.0 (symmetric)
        
        return proposed_theta, log_proposal_ratio
    
    def _log_posterior(self, theta: Dict[str, float], data: Any) -> float:
        """Compute log posterior for a set of parameters."""
        try:
            return self.model.log_posterior(theta, data)
        except Exception:
            # Return negative infinity for invalid parameters
            return -np.inf