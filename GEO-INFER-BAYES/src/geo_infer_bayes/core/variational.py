"""
Variational Inference implementation for Bayesian inference.
"""

import numpy as np
import xarray as xr
import time
from typing import Dict, Any, Optional, Union, List, Tuple, Callable
from tqdm import tqdm


class VariationalInference:
    """
    Variational Inference (VI) for scalable Bayesian approximation.
    
    This class implements variational inference methods to approximate
    posterior distributions by optimizing a simpler distribution.
    
    Parameters
    ----------
    model : BayesianModel
        The model to perform inference on
    learning_rate : float, default=0.01
        Learning rate for optimization
    n_iterations : int, default=10000
        Maximum number of optimization iterations
    convergence_tol : float, default=1e-6
        Convergence tolerance for ELBO
    n_mc_samples : int, default=10
        Number of Monte Carlo samples for gradient estimation
    vi_method : str, default='meanfield'
        Variational inference method: 'meanfield' or 'fullrank'
    random_seed : int, optional
        Random seed for reproducibility
    """
    
    def __init__(
        self,
        model,
        learning_rate: float = 0.01,
        n_iterations: int = 10000,
        convergence_tol: float = 1e-6,
        n_mc_samples: int = 10,
        vi_method: str = 'meanfield',
        random_seed: Optional[int] = None
    ):
        self.model = model
        self.learning_rate = learning_rate
        self.n_iterations = n_iterations
        self.convergence_tol = convergence_tol
        self.n_mc_samples = n_mc_samples
        self.vi_method = vi_method.lower()
        
        if random_seed is not None:
            np.random.seed(random_seed)
            
        if self.vi_method not in ['meanfield', 'fullrank']:
            raise ValueError(f"Unsupported VI method: {self.vi_method}. "
                           f"Choose from: 'meanfield', 'fullrank'")
    
    def run(
        self,
        data: Any,
        progress_bar: bool = True,
        **kwargs
    ) -> Union[Dict[str, np.ndarray], xr.Dataset]:
        """
        Run variational inference for the model.
        
        Parameters
        ----------
        data : any
            Data for inference
        progress_bar : bool, default=True
            Whether to show a progress bar
        **kwargs : dict
            Additional arguments for inference
            
        Returns
        -------
        dict or Dataset
            Approximate posterior samples
        """
        param_names = list(self.model.parameters.keys())
        n_params = len(param_names)
        
        # Initialize variational parameters
        var_params = self._initialize_variational_parameters(param_names)
        
        # Set up progress bar
        iterator = range(self.n_iterations)
        if progress_bar:
            iterator = tqdm(iterator, desc="Variational inference")
        
        # Track ELBO for convergence monitoring
        elbo_history = []
        best_elbo = -np.inf
        best_params = var_params.copy()
        
        # Optimization loop
        for i in iterator:
            # Compute ELBO and gradients
            elbo, grads = self._compute_elbo_and_gradients(var_params, data)
            
            # Update variational parameters using gradients
            self._update_variational_parameters(var_params, grads)
            
            # Track progress
            elbo_history.append(elbo)
            
            # Check if this is the best seen so far
            if elbo > best_elbo:
                best_elbo = elbo
                best_params = var_params.copy()
            
            # Check for convergence
            if i > 100 and abs(elbo_history[-1] - elbo_history[-100]) < self.convergence_tol:
                if progress_bar:
                    print(f"Converged after {i} iterations")
                break
            
            # Update progress bar
            if progress_bar and i % 100 == 0:
                iterator.set_postfix(ELBO=elbo)
        
        # Generate samples from the approximate posterior
        samples = self._generate_samples(best_params, n_samples=kwargs.get('n_samples', 1000))
        
        return samples
    
    def _initialize_variational_parameters(
        self,
        param_names: List[str]
    ) -> Dict[str, Dict[str, np.ndarray]]:
        """
        Initialize variational distribution parameters.
        
        For mean-field Gaussian approximation, we need a mean and 
        log-standard deviation for each parameter.
        For full-rank, we would need additional covariance terms.
        """
        var_params = {}
        
        for param in param_names:
            param_info = self.model.parameters[param]
            var_params[param] = {}
            
            # Initialize mean based on prior
            if param_info['prior'] == 'log_normal':
                mu = param_info['hyperparams']['mu']
                sigma = param_info['hyperparams']['sigma']
                # Initialize in log space
                var_params[param]['mean'] = mu
            elif param_info['prior'] == 'normal':
                mu = param_info['hyperparams']['mu']
                var_params[param]['mean'] = mu
            elif param_info['prior'] == 'uniform':
                low = param_info['hyperparams']['low']
                high = param_info['hyperparams']['high']
                var_params[param]['mean'] = (low + high) / 2
            else:
                var_params[param]['mean'] = 0.0
            
            # Initialize log-std based on prior
            if param_info['prior'] == 'log_normal' or param_info['prior'] == 'normal':
                sigma = param_info['hyperparams'].get('sigma', 1.0)
                var_params[param]['log_std'] = np.log(sigma)
            else:
                var_params[param]['log_std'] = 0.0  # log(1.0)
            
            # For full-rank approximation, initialize covariance matrix
            if self.vi_method == 'fullrank':
                # We would add covariance parameters here
                # This is just a placeholder
                var_params[param]['cov_factor'] = np.zeros((1, 1))
        
        return var_params
    
    def _compute_elbo_and_gradients(
        self,
        var_params: Dict[str, Dict[str, np.ndarray]],
        data: Any
    ) -> Tuple[float, Dict[str, Dict[str, np.ndarray]]]:
        """
        Compute the Evidence Lower Bound (ELBO) and its gradients.
        
        The ELBO is the objective function in variational inference,
        which we want to maximize. It's a lower bound on the model evidence.
        """
        param_names = list(var_params.keys())
        
        # Initialize gradients
        grads = {param: {'mean': 0.0, 'log_std': 0.0} for param in param_names}
        if self.vi_method == 'fullrank':
            for param in param_names:
                grads[param]['cov_factor'] = np.zeros_like(var_params[param]['cov_factor'])
        
        # Compute ELBO via Monte Carlo sampling
        elbo = 0.0
        for _ in range(self.n_mc_samples):
            # Sample from the variational distribution
            sample = self._sample_variational_distribution(var_params)
            
            # Compute log probability of the model
            log_prob_model = self.model.log_posterior(sample, data)
            
            # Compute log probability of the variational distribution
            log_prob_q = self._log_prob_variational(sample, var_params)
            
            # Accumulate ELBO
            elbo += log_prob_model - log_prob_q
            
            # Compute gradients using score function estimator (REINFORCE)
            # or reparameterization trick (preferred for continuous parameters)
            for param in param_names:
                # Compute gradient for mean
                grads[param]['mean'] += (log_prob_model - log_prob_q) * \
                                       self._compute_mean_gradient(sample, var_params, param)
                
                # Compute gradient for log-std
                grads[param]['log_std'] += (log_prob_model - log_prob_q) * \
                                         self._compute_log_std_gradient(sample, var_params, param)
                
                # Additional gradients for full-rank approximation
                if self.vi_method == 'fullrank':
                    # We would compute covariance gradients here
                    pass
        
        # Average over Monte Carlo samples
        elbo /= self.n_mc_samples
        for param in param_names:
            grads[param]['mean'] /= self.n_mc_samples
            grads[param]['log_std'] /= self.n_mc_samples
            if self.vi_method == 'fullrank':
                grads[param]['cov_factor'] /= self.n_mc_samples
        
        return elbo, grads
    
    def _sample_variational_distribution(
        self,
        var_params: Dict[str, Dict[str, np.ndarray]]
    ) -> Dict[str, float]:
        """
        Sample from the variational distribution.
        
        For a mean-field Gaussian approximation, we sample each parameter
        independently from its variational distribution.
        """
        sample = {}
        
        for param, param_dist in var_params.items():
            mean = param_dist['mean']
            std = np.exp(param_dist['log_std'])
            
            # Sample from a standard normal and then transform
            z = np.random.normal(0, 1)
            sample[param] = mean + z * std
            
            # Handle constraints for different parameter types
            param_info = self.model.parameters[param]
            
            # For log-normal parameters, work in log space
            if param_info['prior'] == 'log_normal':
                sample[param] = np.exp(sample[param])
            
            # For uniform parameters, clip to the bounds
            elif param_info['prior'] == 'uniform':
                low = param_info['hyperparams']['low']
                high = param_info['hyperparams']['high']
                sample[param] = np.clip(sample[param], low, high)
        
        return sample
    
    def _log_prob_variational(
        self,
        sample: Dict[str, float],
        var_params: Dict[str, Dict[str, np.ndarray]]
    ) -> float:
        """
        Compute the log probability of a sample under the variational distribution.
        """
        log_prob = 0.0
        
        for param, value in sample.items():
            mean = var_params[param]['mean']
            std = np.exp(var_params[param]['log_std'])
            
            # Handle log-normal parameters
            if self.model.parameters[param]['prior'] == 'log_normal':
                # Convert to log space
                log_value = np.log(value)
                # Gaussian log-pdf
                log_prob += -0.5 * ((log_value - mean) / std) ** 2 - np.log(std) - 0.5 * np.log(2 * np.pi)
                # Jacobian adjustment for log transform
                log_prob += -np.log(value)
            else:
                # Regular Gaussian log-pdf
                log_prob += -0.5 * ((value - mean) / std) ** 2 - np.log(std) - 0.5 * np.log(2 * np.pi)
        
        return log_prob
    
    def _compute_mean_gradient(
        self,
        sample: Dict[str, float],
        var_params: Dict[str, Dict[str, np.ndarray]],
        param: str
    ) -> float:
        """
        Compute the gradient of the log density with respect to the mean parameter.
        """
        std = np.exp(var_params[param]['log_std'])
        
        # For log-normal parameters, handle in log space
        if self.model.parameters[param]['prior'] == 'log_normal':
            log_value = np.log(sample[param])
            return (log_value - var_params[param]['mean']) / (std ** 2)
        else:
            return (sample[param] - var_params[param]['mean']) / (std ** 2)
    
    def _compute_log_std_gradient(
        self,
        sample: Dict[str, float],
        var_params: Dict[str, Dict[str, np.ndarray]],
        param: str
    ) -> float:
        """
        Compute the gradient of the log density with respect to log standard deviation.
        """
        mean = var_params[param]['mean']
        std = np.exp(var_params[param]['log_std'])
        
        # For log-normal parameters, handle in log space
        if self.model.parameters[param]['prior'] == 'log_normal':
            log_value = np.log(sample[param])
            return ((log_value - mean) ** 2 / std**2 - 1.0) * std
        else:
            return ((sample[param] - mean) ** 2 / std**2 - 1.0) * std
    
    def _update_variational_parameters(
        self,
        var_params: Dict[str, Dict[str, np.ndarray]],
        grads: Dict[str, Dict[str, np.ndarray]]
    ) -> None:
        """
        Update variational parameters using computed gradients.
        
        We use simple gradient ascent here, but more sophisticated optimizers
        like Adam or RMSprop could be implemented for better performance.
        """
        for param in var_params:
            # Update mean
            var_params[param]['mean'] += self.learning_rate * grads[param]['mean']
            
            # Update log_std
            var_params[param]['log_std'] += self.learning_rate * grads[param]['log_std']
            
            # Constrain log_std for numerical stability
            var_params[param]['log_std'] = np.clip(var_params[param]['log_std'], -10, 2)
            
            # Update covariance for full-rank approximation
            if self.vi_method == 'fullrank' and 'cov_factor' in var_params[param]:
                var_params[param]['cov_factor'] += self.learning_rate * grads[param]['cov_factor']
    
    def _generate_samples(
        self,
        var_params: Dict[str, Dict[str, np.ndarray]],
        n_samples: int = 1000
    ) -> Dict[str, np.ndarray]:
        """
        Generate samples from the approximate posterior for inference.
        """
        samples = {param: np.zeros(n_samples) for param in var_params}
        
        for i in range(n_samples):
            sample = self._sample_variational_distribution(var_params)
            for param, value in sample.items():
                samples[param][i] = value
        
        return samples
    
    def update(
        self,
        new_data: Any,
        previous_samples: Union[Dict[str, np.ndarray], xr.Dataset],
        **kwargs
    ) -> Union[Dict[str, np.ndarray], xr.Dataset]:
        """
        Update the approximate posterior with new data.
        
        Parameters
        ----------
        new_data : any
            New data for updating
        previous_samples : dict or Dataset
            Previous posterior samples
        **kwargs : dict
            Additional arguments for inference
            
        Returns
        -------
        dict or Dataset
            Updated posterior samples
        """
        # Initialize variational parameters from previous posterior
        param_names = list(self.model.parameters.keys())
        var_params = self._initialize_variational_parameters(param_names)
        
        # Compute mean and std from previous samples
        for param in param_names:
            if isinstance(previous_samples, dict):
                samples = previous_samples[param]
            else:
                samples = previous_samples[param].values
                
            # Use samples to initialize variational parameters    
            if self.model.parameters[param]['prior'] == 'log_normal':
                # For log-normal, work in log space
                log_samples = np.log(samples)
                var_params[param]['mean'] = np.mean(log_samples)
                var_params[param]['log_std'] = np.log(np.std(log_samples) + 1e-10)
            else:
                var_params[param]['mean'] = np.mean(samples)
                var_params[param]['log_std'] = np.log(np.std(samples) + 1e-10)
        
        # Run inference with the new data and warm-started parameters
        return self.run(
            data=new_data,
            **kwargs
        ) 