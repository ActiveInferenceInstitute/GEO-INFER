"""
Numerical Methods Module

This module provides specialized numerical algorithms for solving mathematical
problems arising in geospatial contexts, including interpolation, optimization,
and solving differential equations.
"""

import numpy as np
from typing import Union, List, Tuple, Dict, Optional, Any, Callable
from dataclasses import dataclass
from scipy.optimize import minimize_scalar, root_scalar
from scipy.integrate import solve_ivp, quad
import logging

logger = logging.getLogger(__name__)

@dataclass
class InterpolationResult:
    """Container for interpolation results."""
    values: np.ndarray
    method: str
    parameters: Dict[str, Any]
    error_estimate: Optional[np.ndarray] = None

@dataclass
class OptimizationResult:
    """Container for optimization results."""
    x: np.ndarray
    fun: float
    success: bool
    method: str
    nfev: int
    message: str

@dataclass
class ODEsolution:
    """Container for ODE solution."""
    t: np.ndarray
    y: np.ndarray
    success: bool
    method: str
    message: str

class SpatialInterpolator:
    """Advanced spatial interpolation methods."""

    def __init__(self, method: str = 'kriging'):
        """
        Initialize spatial interpolator.

        Args:
            method: Interpolation method ('kriging', 'spline', 'rbf')
        """
        self.method = method
        self.trained = False
        self.training_points = None
        self.training_values = None
        self.parameters = {}

    def fit(self, points: np.ndarray, values: np.ndarray, **kwargs) -> 'SpatialInterpolator':
        """
        Fit the interpolator to training data.

        Args:
            points: Training point coordinates (n_points, 2)
            values: Training values (n_points,)
            **kwargs: Method-specific parameters

        Returns:
            Self for method chaining
        """
        self.training_points = points.copy()
        self.training_values = values.copy()
        self.parameters.update(kwargs)

        if self.method == 'kriging':
            self._fit_kriging()
        elif self.method == 'spline':
            self._fit_spline()
        elif self.method == 'rbf':
            self._fit_rbf()

        self.trained = True
        return self

    def predict(self, query_points: np.ndarray) -> np.ndarray:
        """
        Predict values at query points.

        Args:
            query_points: Points to interpolate (n_points, 2)

        Returns:
            Interpolated values
        """
        if not self.trained:
            raise ValueError("Interpolator must be fitted before prediction")

        if self.method == 'kriging':
            return self._predict_kriging(query_points)
        elif self.method == 'spline':
            return self._predict_spline(query_points)
        elif self.method == 'rbf':
            return self._predict_rbf(query_points)

    def _fit_kriging(self):
        """Fit Kriging model."""
        # Calculate distances between all training points
        n_points = len(self.training_points)
        distances = np.zeros((n_points, n_points))

        for i in range(n_points):
            for j in range(n_points):
                distances[i, j] = np.sqrt(np.sum((self.training_points[i] - self.training_points[j])**2))

        # Use spherical variogram model by default
        sill = np.var(self.training_values)
        range_param = np.max(distances) * 0.3
        nugget = sill * 0.1

        self.parameters.update({
            'sill': sill,
            'range': range_param,
            'nugget': nugget,
            'distances': distances
        })

    def _predict_kriging(self, query_points: np.ndarray) -> np.ndarray:
        """Predict using Kriging."""
        predictions = []

        for query_point in query_points:
            # Calculate distances from query point to training points
            distances = np.sqrt(np.sum((self.training_points - query_point)**2, axis=1))

            # Calculate variogram values
            variogram_values = self._spherical_variogram(distances)

            # Simple Kriging weights (simplified)
            weights = 1.0 / (variogram_values + 1e-10)
            weights = weights / np.sum(weights)

            # Calculate prediction
            prediction = np.sum(weights * self.training_values)
            predictions.append(prediction)

        return np.array(predictions)

    def _spherical_variogram(self, h: np.ndarray) -> np.ndarray:
        """Spherical variogram model."""
        sill = self.parameters['sill']
        range_param = self.parameters['range']
        nugget = self.parameters['nugget']

        result = np.zeros_like(h)
        mask = h <= range_param
        result[mask] = nugget + (sill - nugget) * (1.5 * h[mask]/range_param - 0.5 * (h[mask]/range_param)**3)
        result[~mask] = sill

        return result

    def _fit_spline(self):
        """Fit spline interpolation model."""
        # For now, use simple linear interpolation between points
        self.parameters['fitted'] = True

    def _predict_spline(self, query_points: np.ndarray) -> np.ndarray:
        """Predict using spline interpolation."""
        # Simplified spline interpolation using nearest neighbors
        predictions = []

        for query_point in query_points:
            distances = np.sqrt(np.sum((self.training_points - query_point)**2, axis=1))
            nearest_idx = np.argmin(distances)
            predictions.append(self.training_values[nearest_idx])

        return np.array(predictions)

    def _fit_rbf(self):
        """Fit Radial Basis Function interpolation."""
        # RBF parameters
        epsilon = self.parameters.get('epsilon', 1.0)
        function = self.parameters.get('function', 'multiquadric')

        self.parameters.update({
            'epsilon': epsilon,
            'function': function
        })

    def _predict_rbf(self, query_points: np.ndarray) -> np.ndarray:
        """Predict using RBF interpolation."""
        predictions = []

        for query_point in query_points:
            # Calculate RBF values for all training points
            rbf_values = []
            for train_point in self.training_points:
                r = np.sqrt(np.sum((query_point - train_point)**2))
                rbf_val = self._rbf_function(r, self.parameters['epsilon'], self.parameters['function'])
                rbf_values.append(rbf_val)

            # Simple weighted average (simplified RBF interpolation)
            weights = np.array(rbf_values)
            weights = weights / np.sum(weights)
            prediction = np.sum(weights * self.training_values)
            predictions.append(prediction)

        return np.array(predictions)

    def _rbf_function(self, r: float, epsilon: float, function: str) -> float:
        """Radial basis function."""
        if function == 'multiquadric':
            return np.sqrt(1 + (epsilon * r)**2)
        elif function == 'inverse_multiquadric':
            return 1.0 / np.sqrt(1 + (epsilon * r)**2)
        elif function == 'gaussian':
            return np.exp(-(epsilon * r)**2)
        elif function == 'thin_plate':
            return r**2 * np.log(r + 1e-10)
        else:
            return np.exp(-r)  # Default exponential

class SpatialOptimizer:
    """Optimization methods for spatial problems."""

    def __init__(self, method: str = 'gradient_descent'):
        """
        Initialize spatial optimizer.

        Args:
            method: Optimization method
        """
        self.method = method
        self.objective_function = None
        self.constraints = []

    def minimize(self,
                objective: Callable,
                bounds: List[Tuple[float, float]],
                initial_guess: Optional[np.ndarray] = None,
                **kwargs) -> OptimizationResult:
        """
        Minimize objective function.

        Args:
            objective: Objective function to minimize
            bounds: Parameter bounds
            initial_guess: Initial parameter values
            **kwargs: Method-specific parameters

        Returns:
            Optimization result
        """
        self.objective_function = objective

        if initial_guess is None:
            initial_guess = np.array([(b[0] + b[1]) / 2 for b in bounds])

        if self.method == 'gradient_descent':
            return self._gradient_descent(objective, bounds, initial_guess, **kwargs)
        elif self.method == 'newton':
            return self._newton_method(objective, bounds, initial_guess, **kwargs)
        elif self.method == 'simulated_annealing':
            return self._simulated_annealing(objective, bounds, initial_guess, **kwargs)
        else:
            raise ValueError(f"Unknown optimization method: {self.method}")

    def _gradient_descent(self,
                         objective: Callable,
                         bounds: List[Tuple[float, float]],
                         x0: np.ndarray,
                         max_iter: int = 1000,
                         learning_rate: float = 0.01,
                         tolerance: float = 1e-6) -> OptimizationResult:
        """Gradient descent optimization."""
        x = x0.copy()
        n_evaluations = 0

        for iteration in range(max_iter):
            # Evaluate objective and gradient
            f_val = objective(x)
            gradient = self._numerical_gradient(objective, x)
            n_evaluations += len(x) + 1

            # Update parameters
            x_new = x - learning_rate * gradient

            # Apply bounds
            x_new = np.clip(x_new, [b[0] for b in bounds], [b[1] for b in bounds])

            # Check convergence
            if np.linalg.norm(x_new - x) < tolerance:
                return OptimizationResult(
                    x=x_new,
                    fun=objective(x_new),
                    success=True,
                    method='gradient_descent',
                    nfev=n_evaluations,
                    message=f'Converged after {iteration} iterations'
                )

            x = x_new

        return OptimizationResult(
            x=x,
            fun=objective(x),
            success=False,
            method='gradient_descent',
            nfev=n_evaluations,
            message='Maximum iterations reached'
        )

    def _newton_method(self,
                      objective: Callable,
                      bounds: List[Tuple[float, float]],
                      x0: np.ndarray,
                      max_iter: int = 100) -> OptimizationResult:
        """Newton's method optimization."""
        x = x0.copy()
        n_evaluations = 0

        for iteration in range(max_iter):
            # Evaluate objective, gradient, and Hessian
            f_val = objective(x)
            gradient = self._numerical_gradient(objective, x)
            hessian = self._numerical_hessian(objective, x)
            n_evaluations += len(x)**2 + len(x) + 1

            # Solve for Newton step
            try:
                step = np.linalg.solve(hessian, gradient)
            except np.linalg.LinAlgError:
                # Hessian is singular, use gradient descent step
                step = gradient

            # Update parameters
            x_new = x - step

            # Apply bounds
            x_new = np.clip(x_new, [b[0] for b in bounds], [b[1] for b in bounds])

            # Check convergence
            if np.linalg.norm(x_new - x) < 1e-6:
                return OptimizationResult(
                    x=x_new,
                    fun=objective(x_new),
                    success=True,
                    method='newton',
                    nfev=n_evaluations,
                    message=f'Converged after {iteration} iterations'
                )

            x = x_new

        return OptimizationResult(
            x=x,
            fun=objective(x),
            success=False,
            method='newton',
            nfev=n_evaluations,
            message='Maximum iterations reached'
        )

    def _simulated_annealing(self,
                           objective: Callable,
                           bounds: List[Tuple[float, float]],
                           x0: np.ndarray,
                           max_iter: int = 1000,
                           initial_temp: float = 100.0,
                           cooling_rate: float = 0.95) -> OptimizationResult:
        """Simulated annealing optimization."""
        x = x0.copy()
        current_energy = objective(x)
        best_x = x.copy()
        best_energy = current_energy
        temperature = initial_temp
        n_evaluations = 1

        for iteration in range(max_iter):
            # Generate candidate solution
            candidate = x + np.random.normal(0, temperature/10, size=len(x))

            # Apply bounds
            candidate = np.clip(candidate, [b[0] for b in bounds], [b[1] for b in bounds])

            # Evaluate candidate
            candidate_energy = objective(candidate)
            n_evaluations += 1

            # Accept or reject candidate
            delta_energy = candidate_energy - current_energy

            if delta_energy < 0 or np.random.random() < np.exp(-delta_energy / temperature):
                x = candidate
                current_energy = candidate_energy

                # Update best solution
                if current_energy < best_energy:
                    best_x = x.copy()
                    best_energy = current_energy

            # Cool down
            temperature *= cooling_rate

        return OptimizationResult(
            x=best_x,
            fun=best_energy,
            success=True,
            method='simulated_annealing',
            nfev=n_evaluations,
            message=f'Completed {max_iter} iterations'
        )

    def _numerical_gradient(self,
                          objective: Callable,
                          x: np.ndarray,
                          epsilon: float = 1e-7) -> np.ndarray:
        """Calculate numerical gradient."""
        gradient = np.zeros_like(x)

        for i in range(len(x)):
            x_plus = x.copy()
            x_minus = x.copy()
            x_plus[i] += epsilon
            x_minus[i] -= epsilon

            gradient[i] = (objective(x_plus) - objective(x_minus)) / (2 * epsilon)

        return gradient

    def _numerical_hessian(self,
                         objective: Callable,
                         x: np.ndarray,
                         epsilon: float = 1e-7) -> np.ndarray:
        """Calculate numerical Hessian matrix."""
        n = len(x)
        hessian = np.zeros((n, n))

        for i in range(n):
            for j in range(n):
                x_pp = x.copy()
                x_pm = x.copy()
                x_mp = x.copy()
                x_mm = x.copy()

                x_pp[i] += epsilon
                x_pp[j] += epsilon
                x_pm[i] += epsilon
                x_pm[j] -= epsilon
                x_mp[i] -= epsilon
                x_mp[j] += epsilon
                x_mm[i] -= epsilon
                x_mm[j] -= epsilon

                hessian[i, j] = (objective(x_pp) - objective(x_pm) -
                               objective(x_mp) + objective(x_mm)) / (4 * epsilon**2)

        return hessian

class ODESolver:
    """ODE solver for spatial-temporal models."""

    def __init__(self, method: str = 'rk45'):
        """
        Initialize ODE solver.

        Args:
            method: Integration method ('rk45', 'rk23', 'dop853', etc.)
        """
        self.method = method

    def solve(self,
             ode_function: Callable,
             t_span: Tuple[float, float],
             y0: np.ndarray,
             t_eval: Optional[np.ndarray] = None,
             **kwargs) -> ODEsolution:
        """
        Solve ODE system.

        Args:
            ode_function: ODE function dy/dt = f(t, y)
            t_span: Time span (t_start, t_end)
            y0: Initial conditions
            t_eval: Times at which to evaluate solution
            **kwargs: Additional solver options

        Returns:
            ODE solution
        """
        try:
            result = solve_ivp(
                ode_function,
                t_span,
                y0,
                method=self.method,
                t_eval=t_eval,
                **kwargs
            )

            return ODEsolution(
                t=result.t,
                y=result.y,
                success=result.success,
                method=self.method,
                message=result.message
            )

        except Exception as e:
            logger.error(f"ODE solving failed: {e}")
            return ODEsolution(
                t=np.array([]),
                y=np.array([]),
                success=False,
                method=self.method,
                message=str(e)
            )

class PDEsolver:
    """PDE solver for spatial-temporal problems."""

    def __init__(self, method: str = 'finite_difference'):
        """
        Initialize PDE solver.

        Args:
            method: Solution method
        """
        self.method = method

    def solve_diffusion(self,
                       initial_condition: np.ndarray,
                       diffusion_coefficient: float,
                       time_steps: int,
                       dt: float,
                       dx: float) -> np.ndarray:
        """
        Solve 1D diffusion equation using finite differences.

        Args:
            initial_condition: Initial concentration/temperature profile
            diffusion_coefficient: Diffusion coefficient
            time_steps: Number of time steps
            dt: Time step size
            dx: Spatial step size

        Returns:
            Solution at each time step
        """
        n_points = len(initial_condition)
        solution = np.zeros((time_steps + 1, n_points))
        solution[0] = initial_condition

        # Stability check
        stability_param = diffusion_coefficient * dt / dx**2
        if stability_param > 0.5:
            logger.warning(f"Stability condition violated: {stability_param} > 0.5")

        for t in range(time_steps):
            for i in range(1, n_points - 1):
                # Finite difference scheme
                solution[t + 1, i] = (solution[t, i] +
                                    stability_param * (solution[t, i + 1] - 2 * solution[t, i] + solution[t, i - 1]))

            # Boundary conditions (fixed ends)
            solution[t + 1, 0] = solution[t, 0]
            solution[t + 1, -1] = solution[t, -1]

        return solution

    def solve_wave_equation(self,
                           initial_displacement: np.ndarray,
                           initial_velocity: np.ndarray,
                           wave_speed: float,
                           time_steps: int,
                           dt: float,
                           dx: float) -> Tuple[np.ndarray, np.ndarray]:
        """
        Solve 1D wave equation using finite differences.

        Args:
            initial_displacement: Initial displacement
            initial_velocity: Initial velocity
            wave_speed: Wave propagation speed
            time_steps: Number of time steps
            dt: Time step size
            dx: Spatial step size

        Returns:
            Tuple of (displacement, velocity) at each time step
        """
        n_points = len(initial_displacement)
        displacement = np.zeros((time_steps + 1, n_points))
        velocity = np.zeros((time_steps + 1, n_points))

        displacement[0] = initial_displacement
        velocity[0] = initial_velocity

        # Stability check
        stability_param = wave_speed * dt / dx
        if stability_param > 1.0:
            logger.warning(f"Stability condition violated: {stability_param} > 1.0")

        for t in range(time_steps):
            for i in range(1, n_points - 1):
                # Update velocity
                velocity[t + 1, i] = (velocity[t, i] +
                                    stability_param**2 * (displacement[t, i + 1] -
                                                        2 * displacement[t, i] +
                                                        displacement[t, i - 1]))

                # Update displacement
                displacement[t + 1, i] = (displacement[t, i] + dt * velocity[t + 1, i])

            # Boundary conditions
            displacement[t + 1, 0] = 0
            displacement[t + 1, -1] = 0
            velocity[t + 1, 0] = 0
            velocity[t + 1, -1] = 0

        return displacement, velocity

def numerical_integration(func: Callable,
                         a: float,
                         b: float,
                         method: str = 'trapezoidal',
                         n_points: int = 1000) -> float:
    """
    Numerical integration using various methods.

    Args:
        func: Function to integrate
        a: Lower limit
        b: Upper limit
        method: Integration method ('trapezoidal', 'simpson', 'romberg')
        n_points: Number of integration points

    Returns:
        Approximate integral value
    """
    if method == 'trapezoidal':
        x = np.linspace(a, b, n_points)
        y = np.array([func(xi) for xi in x])
        return np.trapz(y, x)

    elif method == 'simpson':
        x = np.linspace(a, b, n_points)
        y = np.array([func(xi) for xi in x])
        return np.trapz(y, x)  # Simplified - should use Simpson's rule

    elif method == 'romberg':
        # Simplified Romberg integration
        return quad(func, a, b)[0]

    else:
        raise ValueError(f"Unknown integration method: {method}")

def find_root(func: Callable,
             bracket: Tuple[float, float],
             method: str = 'brentq',
             **kwargs) -> float:
    """
    Find root of a function.

    Args:
        func: Function for which to find root
        bracket: Initial bracket containing the root
        method: Root finding method
        **kwargs: Additional method parameters

    Returns:
        Root value
    """
    try:
        result = root_scalar(func, bracket=bracket, method=method, **kwargs)
        return result.root
    except Exception as e:
        logger.error(f"Root finding failed: {e}")
        return np.nan

def minimize_scalar_function(func: Callable,
                           bounds: Tuple[float, float],
                           method: str = 'bounded',
                           **kwargs) -> float:
    """
    Minimize a scalar function.

    Args:
        func: Function to minimize
        bounds: Parameter bounds
        method: Minimization method
        **kwargs: Additional method parameters

    Returns:
        Optimal parameter value
    """
    try:
        result = minimize_scalar(func, bounds=bounds, method=method, **kwargs)
        return result.x
    except Exception as e:
        logger.error(f"Scalar minimization failed: {e}")
        return np.nan

__all__ = [
    "InterpolationResult",
    "OptimizationResult",
    "ODEsolution",
    "SpatialInterpolator",
    "SpatialOptimizer",
    "ODESolver",
    "PDEsolver",
    "numerical_integration",
    "find_root",
    "minimize_scalar_function"
]
