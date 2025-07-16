"""
Dynamic Causal Modeling for Active Inference.
"""
from typing import Dict, List, Optional, Callable, Any
import numpy as np
from scipy.integrate import odeint

from geo_infer_act.utils.math import gaussian_log_likelihood


class DynamicCausalModel:
    """
    Dynamic Causal Model for continuous-time active inference.
    
    This class implements dynamic causal modeling using stochastic
    differential equations for continuous-time inference.
    """
    
    def __init__(self, 
                 state_dim: int,
                 input_dim: int,
                 output_dim: int,
                 dt: float = 0.01):
        """
        Initialize the dynamic causal model.
        
        Args:
            state_dim: Dimension of hidden states
            input_dim: Dimension of inputs
            output_dim: Dimension of outputs
            dt: Time step for integration
        """
        self.state_dim = state_dim
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.dt = dt
        
        # Model parameters
        self.A = np.eye(state_dim) * -0.1  # State dynamics matrix
        self.B = np.random.randn(state_dim, input_dim) * 0.1  # Input matrix
        self.C = np.random.randn(output_dim, state_dim) * 0.1  # Output matrix
        
        # Noise parameters
        self.Q = np.eye(state_dim) * 0.01  # State noise
        self.R = np.eye(output_dim) * 0.01  # Observation noise
        
        # Current state
        self.state = np.zeros(state_dim)
        
    def state_equation(self, state: np.ndarray, t: float, 
                      inputs: np.ndarray) -> np.ndarray:
        """
        State evolution equation: dx/dt = f(x, u, t).
        
        Args:
            state: Current state vector
            t: Current time
            inputs: Input vector
            
        Returns:
            State derivative
        """
        # Linear dynamics: dx/dt = A*x + B*u
        dxdt = self.A @ state + self.B @ inputs
        
        return dxdt
    
    def observation_equation(self, state: np.ndarray) -> np.ndarray:
        """
        Observation equation: y = g(x) + noise.
        
        Args:
            state: Current state vector
            
        Returns:
            Observation vector
        """
        # Linear observation: y = C*x
        observation = self.C @ state
        
        # Add noise
        noise = np.random.multivariate_normal(
            np.zeros(self.output_dim), self.R
        )
        
        return observation + noise
    
    def integrate_dynamics(self, 
                          initial_state: np.ndarray,
                          inputs: np.ndarray,
                          time_points: np.ndarray) -> np.ndarray:
        """
        Integrate the system dynamics over time.
        
        Args:
            initial_state: Initial state vector
            inputs: Input sequence (n_timesteps x input_dim)
            time_points: Time points for integration
            
        Returns:
            State trajectory (n_timesteps x state_dim)
        """
        n_timesteps = len(time_points)
        state_trajectory = np.zeros((n_timesteps, self.state_dim))
        
        current_state = initial_state.copy()
        state_trajectory[0] = current_state
        
        for i in range(1, n_timesteps):
            dt = time_points[i] - time_points[i-1]
            current_input = inputs[i-1] if i-1 < len(inputs) else np.zeros(self.input_dim)
            
            # Simple Euler integration
            dxdt = self.state_equation(current_state, time_points[i-1], current_input)
            current_state = current_state + dt * dxdt
            
            # Add process noise
            noise = np.random.multivariate_normal(
                np.zeros(self.state_dim), self.Q * dt
            )
            current_state += noise
            
            state_trajectory[i] = current_state
            
        return state_trajectory
    
    def generate_observations(self, state_trajectory: np.ndarray) -> np.ndarray:
        """
        Generate observations from state trajectory.
        
        Args:
            state_trajectory: State trajectory
            
        Returns:
            Observation trajectory
        """
        n_timesteps = state_trajectory.shape[0]
        observations = np.zeros((n_timesteps, self.output_dim))
        
        for i in range(n_timesteps):
            observations[i] = self.observation_equation(state_trajectory[i])
            
        return observations
    
    def estimate_parameters(self,
                           observations: np.ndarray,
                           inputs: np.ndarray,
                           time_points: np.ndarray,
                           initial_state: Optional[np.ndarray] = None) -> Dict[str, np.ndarray]:
        """
        Estimate model parameters from data.
        
        Args:
            observations: Observation sequence
            inputs: Input sequence
            time_points: Time points
            initial_state: Initial state estimate
            
        Returns:
            Estimated parameters
        """
        if initial_state is None:
            initial_state = np.zeros(self.state_dim)
            
        # Simplified parameter estimation using least squares
        # In practice, would use more sophisticated methods like EM algorithm
        
        # Estimate state trajectory using Kalman smoother (simplified)
        estimated_states = self._estimate_states(observations, inputs, time_points, initial_state)
        
        # Estimate A and B matrices from state dynamics
        X = estimated_states[:-1]  # Current states
        X_next = estimated_states[1:]  # Next states
        U = inputs[:len(X)] if len(inputs) > 1 else np.zeros((len(X), self.input_dim))
        
        # Solve: X_next = X*A.T + U*B.T
        if len(X) > 0:
            XU = np.hstack([X, U])
            AB = np.linalg.lstsq(XU, X_next, rcond=None)[0]
            
            estimated_A = AB[:self.state_dim].T
            estimated_B = AB[self.state_dim:].T if self.input_dim > 0 else self.B
        else:
            estimated_A = self.A
            estimated_B = self.B
        
        # Estimate C matrix from observations
        if len(estimated_states) > 0:
            estimated_C = np.linalg.lstsq(estimated_states, observations, rcond=None)[0].T
        else:
            estimated_C = self.C
            
        return {
            'A': estimated_A,
            'B': estimated_B,
            'C': estimated_C,
            'estimated_states': estimated_states
        }
    
    def _estimate_states(self,
                        observations: np.ndarray,
                        inputs: np.ndarray,
                        time_points: np.ndarray,
                        initial_state: np.ndarray) -> np.ndarray:
        """
        Estimate state trajectory using simplified Kalman filter.
        
        Args:
            observations: Observation sequence
            inputs: Input sequence
            time_points: Time points
            initial_state: Initial state
            
        Returns:
            Estimated state trajectory
        """
        n_timesteps = len(observations)
        states = np.zeros((n_timesteps, self.state_dim))
        
        # Initialize
        current_state = initial_state.copy()
        current_cov = np.eye(self.state_dim)
        
        states[0] = current_state
        
        for i in range(1, n_timesteps):
            dt = time_points[i] - time_points[i-1] if i < len(time_points) else self.dt
            current_input = inputs[i-1] if i-1 < len(inputs) else np.zeros(self.input_dim)
            
            # Prediction step
            pred_state = current_state + dt * self.state_equation(current_state, time_points[i-1], current_input)
            pred_cov = current_cov + self.Q * dt
            
            # Update step
            innovation = observations[i] - self.C @ pred_state
            innovation_cov = self.C @ pred_cov @ self.C.T + self.R
            kalman_gain = pred_cov @ self.C.T @ np.linalg.inv(innovation_cov)
            
            current_state = pred_state + kalman_gain @ innovation
            current_cov = (np.eye(self.state_dim) - kalman_gain @ self.C) @ pred_cov
            
            states[i] = current_state
            
        return states
    
    def set_parameters(self, A: np.ndarray, B: np.ndarray, C: np.ndarray):
        """Set model parameters."""
        self.A = A
        self.B = B
        self.C = C
    
    def set_noise_parameters(self, Q: np.ndarray, R: np.ndarray):
        """Set noise parameters."""
        self.Q = Q
        self.R = R 