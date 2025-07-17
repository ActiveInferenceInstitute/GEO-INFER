"""
Mathematical utilities for active inference models.

This module provides mathematical functions for computing
information-theoretic quantities, probability distributions,
and Active Inference specific calculations.
"""
import numpy as np
from typing import Union, Optional, Tuple, List, Dict
from scipy import stats
from scipy.signal import find_peaks
from sklearn.metrics import mutual_info_score
import warnings


def softmax(x: np.ndarray, temperature: float = 1.0, axis: int = -1) -> np.ndarray:
    """
    Compute softmax transformation of input array.
    
    Args:
        x: Input array
        temperature: Temperature parameter (higher = more uniform)
        axis: Axis along which to compute softmax
        
    Returns:
        Softmax-transformed array
    """
    # Subtract max for numerical stability
    x_stable = x - np.max(x, axis=axis, keepdims=True)
    
    # Apply temperature scaling
    x_scaled = x_stable / temperature
    
    # Compute softmax
    exp_x = np.exp(x_scaled)
    return exp_x / np.sum(exp_x, axis=axis, keepdims=True)


def normalize_distribution(x: np.ndarray, axis: int = -1) -> np.ndarray:
    """
    Normalize array to form a probability distribution.
    
    Args:
        x: Input array
        axis: Axis along which to normalize
        
    Returns:
        Normalized probability distribution
    """
    # Ensure non-negative values
    x_pos = np.maximum(x, 0)
    
    # Normalize
    sum_x = np.sum(x_pos, axis=axis, keepdims=True)
    
    # Handle zero sum case
    sum_x = np.where(sum_x == 0, 1, sum_x)
    
    return x_pos / sum_x


def kl_divergence(p: np.ndarray, q: np.ndarray, epsilon: float = 1e-10) -> float:
    """
    Compute Kullback-Leibler divergence between two probability distributions.
    
    Args:
        p: First probability distribution
        q: Second probability distribution
        epsilon: Small value to avoid log(0)
        
    Returns:
        KL divergence D(p||q)
    """
    # Ensure both are valid probability distributions
    p = np.asarray(p)
    q = np.asarray(q)
    
    # Add small epsilon to avoid log(0)
    p_safe = p + epsilon
    q_safe = q + epsilon
    
    # Normalize to ensure they sum to 1
    p_safe = p_safe / np.sum(p_safe)
    q_safe = q_safe / np.sum(q_safe)
    
    # Compute KL divergence
    return np.sum(p_safe * np.log(p_safe / q_safe))


def entropy(p: np.ndarray, base: Union[float, str] = 'e') -> float:
    """
    Compute entropy of a probability distribution.
    
    Args:
        p: Probability distribution
        base: Logarithm base ('e', 2, 10, or float)
        
    Returns:
        Entropy value
    """
    p = np.asarray(p)
    
    # Filter out zero probabilities
    p_nonzero = p[p > 0]
    
    if len(p_nonzero) == 0:
        return 0.0
    
    # Compute entropy
    if base == 'e':
        log_func = np.log
    elif base == 2:
        log_func = np.log2
    elif base == 10:
        log_func = np.log10
    else:
        log_func = lambda x: np.log(x) / np.log(base)
    
    return -np.sum(p_nonzero * log_func(p_nonzero))


def mutual_information(joint: np.ndarray) -> float:
    """
    Compute mutual information from joint probability distribution.
    
    Args:
        joint: Joint probability distribution (2D array)
        
    Returns:
        Mutual information value
    """
    joint = np.asarray(joint)
    
    # Marginal distributions
    p_x = np.sum(joint, axis=1)
    p_y = np.sum(joint, axis=0)
    
    # Mutual information
    mi = 0.0
    for i in range(joint.shape[0]):
        for j in range(joint.shape[1]):
            if joint[i, j] > 0 and p_x[i] > 0 and p_y[j] > 0:
                mi += joint[i, j] * np.log(joint[i, j] / (p_x[i] * p_y[j]))
    
    return mi


def precision_weighted_error(mean: np.ndarray, 
                           target: np.ndarray,
                           precision: np.ndarray) -> float:
    """
    Compute precision-weighted prediction error.
    
    Args:
        mean: Predicted mean
        target: Target values
        precision: Precision matrix
        
    Returns:
        Precision-weighted error
    """
    error = target - mean
    
    if precision.ndim == 0 or (precision.ndim == 1 and len(precision) == 1):
        # Scalar precision
        return float(precision * np.sum(error ** 2))
    elif precision.ndim == 1:
        # Diagonal precision
        return float(np.sum(precision * error ** 2))
    else:
        # Full precision matrix
        return float(error.T @ precision @ error)


def gaussian_log_likelihood(x: np.ndarray,
                          mean: np.ndarray,
                          precision: np.ndarray) -> float:
    """
    Compute log likelihood of Gaussian distribution.
    
    Args:
        x: Observed values
        mean: Mean of distribution
        precision: Precision matrix (inverse covariance)
        
    Returns:
        Log likelihood
    """
    x = np.asarray(x)
    mean = np.asarray(mean)
    precision = np.asarray(precision)
    
    # Residual
    residual = x - mean
    
    # Dimensionality
    d = len(x)
    
    if precision.ndim == 0 or (precision.ndim == 1 and len(precision) == 1):
        # Scalar precision
        log_det_precision = d * np.log(precision)
        quadratic_form = precision * np.sum(residual ** 2)
    elif precision.ndim == 1:
        # Diagonal precision
        log_det_precision = np.sum(np.log(precision))
        quadratic_form = np.sum(precision * residual ** 2)
    else:
        # Full precision matrix
        try:
            log_det_precision = np.log(np.linalg.det(precision))
            quadratic_form = residual.T @ precision @ residual
        except np.linalg.LinAlgError:
            # Fallback for singular matrices
            log_det_precision = np.sum(np.log(np.diag(precision)))
            quadratic_form = np.sum(np.diag(precision) * residual ** 2)
    
    # Log likelihood
    log_likelihood = 0.5 * (log_det_precision - d * np.log(2 * np.pi) - quadratic_form)
    
    return float(log_likelihood)


def categorical_log_likelihood(observations: np.ndarray,
                             probabilities: np.ndarray) -> float:
    """
    Compute log likelihood for categorical distribution.
    
    Args:
        observations: Observed counts or one-hot encoded observations
        probabilities: Category probabilities
        
    Returns:
        Log likelihood
    """
    observations = np.asarray(observations)
    probabilities = np.asarray(probabilities)
    
    # Ensure probabilities are valid
    probabilities = probabilities + 1e-10
    probabilities = probabilities / np.sum(probabilities)
    
    # Compute log likelihood
    return float(np.sum(observations * np.log(probabilities)))


def dirichlet_kl_divergence(alpha1: np.ndarray, alpha2: np.ndarray) -> float:
    """
    Compute KL divergence between two Dirichlet distributions.
    
    Args:
        alpha1: Parameters of first Dirichlet distribution
        alpha2: Parameters of second Dirichlet distribution
        
    Returns:
        KL divergence
    """
    from scipy.special import gammaln, digamma
    
    alpha1 = np.asarray(alpha1)
    alpha2 = np.asarray(alpha2)
    
    # Sum of parameters
    sum_alpha1 = np.sum(alpha1)
    sum_alpha2 = np.sum(alpha2)
    
    # KL divergence formula for Dirichlet distributions
    kl = (gammaln(sum_alpha1) - gammaln(sum_alpha2) +
          np.sum(gammaln(alpha2) - gammaln(alpha1)) +
          np.sum((alpha1 - alpha2) * (digamma(alpha1) - digamma(sum_alpha1))))
    
    return float(kl)


def sample_categorical(probabilities: np.ndarray, 
                     n_samples: int = 1,
                     random_state: Optional[int] = None) -> np.ndarray:
    """
    Sample from categorical distribution.
    
    Args:
        probabilities: Category probabilities
        n_samples: Number of samples
        random_state: Random seed
        
    Returns:
        Sampled indices
    """
    if random_state is not None:
        np.random.seed(random_state)
    
    probabilities = np.asarray(probabilities)
    probabilities = probabilities / np.sum(probabilities)
    
    return np.random.choice(len(probabilities), size=n_samples, p=probabilities)


def compute_free_energy_categorical(beliefs: np.ndarray,
                                  observations: np.ndarray,
                                  prior: Optional[np.ndarray] = None) -> float:
    """
    Compute variational free energy for categorical models.
    
    Args:
        beliefs: Current belief distribution
        observations: Observed data
        prior: Prior distribution (uniform if None)
        
    Returns:
        Free energy value
    """
    beliefs = np.asarray(beliefs)
    observations = np.asarray(observations)
    
    if prior is None:
        prior = np.ones_like(beliefs) / len(beliefs)
    
    # Accuracy term (expected log likelihood)
    accuracy = np.sum(beliefs * np.log(observations + 1e-10))
    
    # Complexity term (KL divergence from prior)
    complexity = kl_divergence(beliefs, prior)
    
    # Free energy = Complexity - Accuracy
    return complexity - accuracy


def compute_expected_free_energy(beliefs: np.ndarray,
                               preferences: np.ndarray,
                               exploration_bonus: float = 0.1) -> float:
    """
    Compute expected free energy for policy evaluation.
    
    Args:
        beliefs: Current belief distribution
        preferences: Prior preferences
        exploration_bonus: Exploration bonus weight
        
    Returns:
        Expected free energy
    """
    beliefs = np.asarray(beliefs)
    preferences = np.asarray(preferences)
    
    # Epistemic value (information gain)
    epistemic_value = entropy(beliefs)
    
    # Pragmatic value (preference satisfaction)
    pragmatic_value = -np.sum(beliefs * np.log(preferences + 1e-10))
    
    # Expected free energy
    expected_free_energy = pragmatic_value - exploration_bonus * epistemic_value
    
    return float(expected_free_energy)


def numerical_gradient(func, x: np.ndarray, h: float = 1e-5) -> np.ndarray:
    """
    Compute numerical gradient using finite differences.
    
    Args:
        func: Function to differentiate
        x: Point at which to compute gradient
        h: Step size
        
    Returns:
        Gradient vector
    """
    x = np.asarray(x)
    grad = np.zeros_like(x)
    
    for i in range(len(x)):
        x_plus = x.copy()
        x_minus = x.copy()
        x_plus[i] += h
        x_minus[i] -= h
        
        grad[i] = (func(x_plus) - func(x_minus)) / (2 * h)
    
    return grad


def stable_log_sum_exp(x: np.ndarray, axis: int = -1) -> np.ndarray:
    """
    Compute log(sum(exp(x))) in a numerically stable way.
    
    Args:
        x: Input array
        axis: Axis along which to compute
        
    Returns:
        Stable log-sum-exp
    """
    x_max = np.max(x, axis=axis, keepdims=True)
    return x_max + np.log(np.sum(np.exp(x - x_max), axis=axis, keepdims=True))


def matrix_log_det(matrix: np.ndarray) -> float:
    """
    Compute log determinant of a matrix safely.
    
    Args:
        matrix: Input matrix
        
    Returns:
        Log determinant
    """
    try:
        return float(np.log(np.linalg.det(matrix)))
    except:
        # Fallback using eigenvalues
        eigenvals = np.linalg.eigvals(matrix)
        eigenvals = eigenvals[eigenvals > 0]  # Only positive eigenvalues
        return float(np.sum(np.log(eigenvals))) if len(eigenvals) > 0 else -np.inf


# Additional analysis functions for pattern detection

def detect_stationarity(data: np.ndarray, window_size: int = 10) -> Dict[str, float]:
    """
    Detect stationarity in time series data.
    
    Args:
        data: Time series data
        window_size: Window size for analysis
        
    Returns:
        Dictionary with stationarity metrics
    """
    data = np.asarray(data)
    
    if len(data) < 2 * window_size:
        return {'is_stationary': False, 'stationarity_score': 0.0}
    
    # Compute rolling statistics
    n_windows = len(data) - window_size + 1
    rolling_means = []
    rolling_vars = []
    
    for i in range(n_windows):
        window = data[i:i+window_size]
        rolling_means.append(np.mean(window))
        rolling_vars.append(np.var(window))
    
    # Compute variation in rolling statistics
    mean_variation = np.var(rolling_means) / (np.mean(rolling_means)**2 + 1e-8)
    var_variation = np.var(rolling_vars) / (np.mean(rolling_vars) + 1e-8)
    
    # Simple stationarity score (lower is more stationary)
    stationarity_score = 1.0 / (1.0 + mean_variation + var_variation)
    is_stationary = mean_variation < 0.1 and var_variation < 0.1
    
    return {
        'is_stationary': is_stationary,
        'stationarity_score': float(stationarity_score),
        'mean_variation': float(mean_variation),
        'variance_variation': float(var_variation)
    }


def detect_periodicity(data: np.ndarray, min_period: int = 2) -> Dict[str, Union[bool, float, int]]:
    """
    Detect periodic patterns in data.
    
    Args:
        data: Time series data
        min_period: Minimum period to consider
        
    Returns:
        Dictionary with periodicity information
    """
    data = np.asarray(data)
    
    if len(data) < 2 * min_period:
        return {'is_periodic': False, 'period': 0, 'strength': 0.0}
    
    # Autocorrelation analysis
    max_lag = min(len(data) // 2, 50)  # Limit for computational efficiency
    autocorr = []
    
    for lag in range(1, max_lag):
        if lag < len(data):
            corr = np.corrcoef(data[:-lag], data[lag:])[0, 1]
            autocorr.append(corr if not np.isnan(corr) else 0.0)
        else:
            autocorr.append(0.0)
    
    autocorr = np.array(autocorr)
    
    # Find peaks in autocorrelation
    if len(autocorr) > min_period:
        peaks, _ = find_peaks(autocorr[min_period-1:], height=0.3)
        
        if len(peaks) > 0:
            # Most prominent peak
            best_peak_idx = np.argmax(autocorr[min_period-1:][peaks])
            period = peaks[best_peak_idx] + min_period
            strength = autocorr[min_period-1:][peaks[best_peak_idx]]
            
            return {
                'is_periodic': True,
                'period': int(period),
                'strength': float(strength),
                'autocorr_peaks': peaks + min_period
            }
    
    return {'is_periodic': False, 'period': 0, 'strength': 0.0}


def assess_complexity(data: np.ndarray) -> Dict[str, float]:
    """
    Assess complexity of data using multiple metrics.
    
    Args:
        data: Input data array
        
    Returns:
        Dictionary with complexity metrics
    """
    data = np.asarray(data)
    
    if data.ndim > 1:
        # For multi-dimensional data, analyze each dimension
        complexities = []
        for dim in range(data.shape[1]):
            dim_complexity = assess_complexity(data[:, dim])
            complexities.append(dim_complexity['overall_complexity'])
        return {'overall_complexity': float(np.mean(complexities))}
    
    if len(data) < 3:
        return {'overall_complexity': 0.0}
    
    # 1. Entropy-based complexity
    # Discretize data for entropy calculation
    try:
        hist, _ = np.histogram(data, bins=min(10, len(data)//2))
        hist = hist + 1  # Add pseudocount
        probs = hist / np.sum(hist)
        entropy_complexity = entropy(probs) / np.log(len(probs))
    except:
        entropy_complexity = 0.0
    
    # 2. Variation complexity
    variation_complexity = np.std(data) / (np.mean(np.abs(data)) + 1e-8)
    variation_complexity = min(1.0, variation_complexity)
    
    # 3. Autocorrelation complexity
    if len(data) > 1:
        try:
            autocorr = np.corrcoef(data[:-1], data[1:])[0, 1]
            autocorr_complexity = 1.0 - abs(autocorr) if not np.isnan(autocorr) else 0.5
        except:
            autocorr_complexity = 0.5
    else:
        autocorr_complexity = 0.0
    
    # 4. Trend complexity
    if len(data) > 2:
        try:
            trend_coef = np.polyfit(range(len(data)), data, 1)[0]
            trend_complexity = min(1.0, abs(trend_coef) / (np.std(data) + 1e-8))
        except:
            trend_complexity = 0.0
    else:
        trend_complexity = 0.0
    
    # Overall complexity (weighted average)
    weights = [0.3, 0.3, 0.2, 0.2]
    components = [entropy_complexity, variation_complexity, autocorr_complexity, trend_complexity]
    overall_complexity = sum(w * c for w, c in zip(weights, components))
    
    return {
        'overall_complexity': float(overall_complexity),
        'entropy_complexity': float(entropy_complexity),
        'variation_complexity': float(variation_complexity),
        'autocorr_complexity': float(autocorr_complexity),
        'trend_complexity': float(trend_complexity)
    }


def compute_prediction_accuracy(predictions: np.ndarray, targets: np.ndarray) -> Dict[str, float]:
    """
    Compute various prediction accuracy metrics.
    
    Args:
        predictions: Predicted values
        targets: Target values
        
    Returns:
        Dictionary with accuracy metrics
    """
    predictions = np.asarray(predictions)
    targets = np.asarray(targets)
    
    if len(predictions) != len(targets):
        raise ValueError("Predictions and targets must have same length")
    
    # Mean Squared Error
    mse = np.mean((predictions - targets) ** 2)
    
    # Mean Absolute Error
    mae = np.mean(np.abs(predictions - targets))
    
    # R-squared (coefficient of determination)
    ss_res = np.sum((targets - predictions) ** 2)
    ss_tot = np.sum((targets - np.mean(targets)) ** 2)
    r2 = 1 - (ss_res / (ss_tot + 1e-8))
    
    # Root Mean Squared Error
    rmse = np.sqrt(mse)
    
    # Mean Absolute Percentage Error
    mape = np.mean(np.abs((targets - predictions) / (targets + 1e-8))) * 100
    
    # Correlation coefficient
    try:
        correlation = np.corrcoef(predictions, targets)[0, 1]
        if np.isnan(correlation):
            correlation = 0.0
    except:
        correlation = 0.0
    
    return {
        'mse': float(mse),
        'mae': float(mae),
        'rmse': float(rmse),
        'r2': float(r2),
        'mape': float(mape),
        'correlation': float(correlation)
    }


def compute_information_gain(prior_entropy: float, posterior_entropy: float) -> float:
    """
    Compute information gain from prior to posterior.
    
    Args:
        prior_entropy: Entropy before observation
        posterior_entropy: Entropy after observation
        
    Returns:
        Information gain (reduction in entropy)
    """
    return float(max(0.0, prior_entropy - posterior_entropy))


def compute_surprise(observation: np.ndarray, predicted_distribution: np.ndarray, sigma: float = 0.1) -> float:
    """
    Compute surprise of an observation given predicted distribution.
    
    Args:
        observation: Observed outcome (can be one-hot, index, or continuous)
        predicted_distribution: Predicted probability distribution
        sigma: Standard deviation for continuous observations (default: 0.1)
        
    Returns:
        Surprise value (negative log probability)
    """
    observation = np.asarray(observation)
    predicted_distribution = np.asarray(predicted_distribution)
    
    # Ensure valid distribution
    predicted_distribution = predicted_distribution + 1e-10
    predicted_distribution = predicted_distribution / np.sum(predicted_distribution)
    
    # For one-hot encoded observations (categorical)
    if (observation.ndim == 1 and 
        len(observation) == len(predicted_distribution) and 
        np.allclose(np.sum(observation), 1.0)):
        prob = np.sum(observation * predicted_distribution)
        return float(-np.log(prob + 1e-10))
    
    # For single index observation
    elif observation.ndim == 0 or (observation.ndim == 1 and len(observation) == 1):
        idx = int(observation.item() if hasattr(observation, 'item') else observation)
        if 0 <= idx < len(predicted_distribution):
            prob = predicted_distribution[idx]
            return float(-np.log(prob + 1e-10))
        else:
            return float(10.0)  # High surprise for invalid index
    
    # For continuous/multi-dimensional observations
    else:
        # Compute surprise based on distance from mean prediction
        mean_pred = np.mean(predicted_distribution)
        obs_mean = np.mean(observation)
        
        # Gaussian surprise approximation
        diff = (obs_mean - mean_pred) ** 2
        surprise = diff / (2 * sigma**2) + 0.5 * np.log(2 * np.pi * sigma**2)
        
        return float(max(0.0, surprise))


def assess_convergence(sequence: np.ndarray, window_size: int = 10, threshold: float = 1e-3) -> Dict[str, Union[bool, float, int]]:
    """
    Assess convergence of a sequence.
    
    Args:
        sequence: Input sequence
        window_size: Window size for convergence check
        threshold: Convergence threshold
        
    Returns:
        Dictionary with convergence information
    """
    sequence = np.asarray(sequence)
    
    if len(sequence) < window_size:
        return {'converged': False, 'convergence_step': -1, 'final_variance': np.var(sequence)}
    
    # Check convergence using moving variance
    for i in range(window_size, len(sequence)):
        window = sequence[i-window_size:i]
        variance = np.var(window)
        
        if variance < threshold:
            return {
                'converged': True,
                'convergence_step': i,
                'final_variance': float(variance),
                'convergence_rate': float(1.0 / (i + 1))
            }
    
    return {
        'converged': False,
        'convergence_step': -1,
        'final_variance': float(np.var(sequence[-window_size:])),
        'convergence_rate': 0.0
    } 

def sample_dirichlet(alpha: np.ndarray) -> np.ndarray:
    """Sample from Dirichlet distribution."""
    return np.random.dirichlet(alpha) 


def precision_weighted_error(prediction_error: np.ndarray, precision: np.ndarray) -> np.ndarray:
    """Compute precision-weighted prediction error."""
    return prediction_error * precision 
