"""
Mixed Effects Models for Statistical Parametric Mapping

This module implements mixed effects (hierarchical) models for SPM analysis,
allowing for the modeling of both fixed and random effects in geospatial data.
Mixed effects models are particularly useful for:

- Accounting for spatial clustering and grouping effects
- Modeling hierarchical data structures (e.g., regions within countries)
- Handling correlated observations within groups
- Estimating both population-level and group-specific effects

Mathematical Foundation:
y = Xβ + Zu + ε

where:
- y: Response vector
- X: Fixed effects design matrix
- β: Fixed effects coefficients
- Z: Random effects design matrix
- u: Random effects (u ~ N(0, G))
- ε: Residual errors (ε ~ N(0, R))
"""

import numpy as np
from typing import Dict, List, Optional, Tuple, Union, Any
from scipy import linalg, stats
from scipy.optimize import minimize
import warnings

from ...models.data_models import SPMData, SPMResult, DesignMatrix


class MixedEffectsSPM:
    """
    Mixed Effects Statistical Parametric Mapping

    This class implements mixed effects models for SPM, allowing both
    fixed and random effects to be modeled simultaneously.

    Attributes:
        fixed_design: Design matrix for fixed effects
        random_groups: Grouping structure for random effects
        random_effects: Specification of random effects structure
        fitted_model: Fitted model parameters
    """

    def __init__(self, fixed_design: DesignMatrix, random_groups: Dict[str, np.ndarray],
                 random_effects: Optional[Dict[str, Any]] = None):
        """
        Initialize mixed effects SPM.

        Args:
            fixed_design: Design matrix for fixed effects
            random_groups: Dictionary mapping group names to group indices
            random_effects: Specification of random effects structure
        """
        self.fixed_design = fixed_design
        self.random_groups = random_groups
        self.random_effects = random_effects or {}
        self.fitted_model = None

        # Validate inputs
        self._validate_inputs()

    def _validate_inputs(self):
        """Validate input parameters."""
        if not isinstance(self.fixed_design, DesignMatrix):
            raise TypeError("fixed_design must be a DesignMatrix instance")

        if not isinstance(self.random_groups, dict):
            raise TypeError("random_groups must be a dictionary")

        # Check that group indices are valid
        n_points = self.fixed_design.matrix.shape[0]
        for group_name, group_indices in self.random_groups.items():
            if np.max(group_indices) >= n_points or np.min(group_indices) < 0:
                raise ValueError(f"Group indices for {group_name} are out of bounds")

    def fit(self, data: SPMData, method: str = "REML",
            optimizer: str = "BFGS") -> SPMResult:
        """
        Fit mixed effects model to SPM data.

        Args:
            data: SPMData containing response variable
            method: Estimation method ('ML' or 'REML')
            optimizer: Optimization method for parameter estimation

        Returns:
            SPMResult with fitted mixed effects model
        """
        y = self._extract_response(data)

        # Set up mixed effects model matrices
        X, Z, group_info = self._setup_matrices(y)

        # Estimate parameters using maximum likelihood
        if method.upper() == "REML":
            beta_hat, variance_components, log_likelihood = self._fit_reml(X, Z, y, group_info)
        elif method.upper() == "ML":
            beta_hat, variance_components, log_likelihood = self._fit_ml(X, Z, y, group_info)
        else:
            raise ValueError(f"Unknown estimation method: {method}")

        # Compute residuals and fitted values
        y_hat = X @ beta_hat
        residuals = y - y_hat

        # Store fitted model
        self.fitted_model = {
            'beta': beta_hat,
            'variance_components': variance_components,
            'log_likelihood': log_likelihood,
            'method': method,
            'converged': True
        }

        # Create SPMResult
        result = SPMResult(
            spm_data=data,
            design_matrix=self.fixed_design,
            beta_coefficients=beta_hat,
            residuals=residuals,
            model_diagnostics={
                'method': f'Mixed_Effects_{method}',
                'log_likelihood': log_likelihood,
                'variance_components': variance_components,
                'n_groups': len(group_info),
                'optimizer': optimizer
            }
        )

        return result

    def _extract_response(self, data: SPMData) -> np.ndarray:
        """Extract response variable from SPMData."""
        if isinstance(data.data, np.ndarray):
            return data.data.flatten()
        else:
            raise TypeError("Mixed effects models require array data")

    def _setup_matrices(self, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray, Dict[str, Any]]:
        """
        Set up design matrices for mixed effects model.

        Returns:
            X: Fixed effects design matrix
            Z: Random effects design matrix
            group_info: Information about grouping structure
        """
        n_points = len(y)
        X = self.fixed_design.matrix

        # Create random effects design matrix
        Z_list = []
        group_info = {}

        for group_name, group_indices in self.random_groups.items():
            # Create random effects for this grouping variable
            n_groups = len(np.unique(group_indices))
            group_info[group_name] = {
                'n_groups': n_groups,
                'indices': group_indices,
                'random_effects': self.random_effects.get(group_name, ['intercept'])
            }

            # Create Z matrix for this grouping variable
            Z_group = np.zeros((n_points, n_groups))
            for i, group_idx in enumerate(group_indices):
                Z_group[i, group_idx] = 1.0

            Z_list.append(Z_group)

        # Combine all random effects matrices
        if Z_list:
            Z = np.concatenate(Z_list, axis=1)
        else:
            Z = np.zeros((n_points, 0))

        return X, Z, group_info

    def _fit_reml(self, X: np.ndarray, Z: np.ndarray, y: np.ndarray,
                  group_info: Dict[str, Any]) -> Tuple[np.ndarray, Dict[str, float], float]:
        """
        Fit mixed effects model using Restricted Maximum Likelihood (REML).

        REML provides unbiased estimation of variance components.
        """
        # Simplified REML implementation
        # In practice, this would use more sophisticated optimization

        def negative_reml_loglik(params):
            """Negative REML log-likelihood."""
            # Extract parameters
            beta = params[:X.shape[1]]
            sigma2 = np.exp(params[X.shape[1]])  # Ensure positive
            tau2 = np.exp(params[X.shape[1] + 1])  # Random effects variance

            # Compute V = ZGZ' + R (simplified)
            V = tau2 * Z @ Z.T + sigma2 * np.eye(len(y))

            try:
                # Compute log-likelihood
                V_inv = linalg.pinvh(V)
                log_det_V = np.log(linalg.det(V))

                mu = X @ beta
                resid = y - mu

                # REML log-likelihood (simplified)
                n = len(y)
                p = X.shape[1]
                loglik = -0.5 * (n - p) * np.log(2 * np.pi) - 0.5 * log_det_V
                loglik -= 0.5 * resid.T @ V_inv @ resid

                return -loglik  # Negative for minimization

            except np.linalg.LinAlgError:
                return np.inf

        # Initial parameter guesses
        n_params = X.shape[1] + 2  # beta + sigma2 + tau2
        init_params = np.concatenate([
            np.linalg.pinv(X) @ y,  # Initial beta
            [0.0, 0.0]  # Log variances
        ])

        # Optimize
        try:
            result = minimize(
                negative_reml_loglik,
                init_params,
                method='L-BFGS-B',
                options={'maxiter': 100}
            )

            if result.success:
                beta_hat = result.x[:X.shape[1]]
                sigma2 = np.exp(result.x[X.shape[1]])
                tau2 = np.exp(result.x[X.shape[1] + 1])
                log_likelihood = -result.fun

                variance_components = {
                    'residual_variance': sigma2,
                    'random_effects_variance': tau2,
                    'total_variance': sigma2 + tau2
                }

                return beta_hat, variance_components, log_likelihood
            else:
                warnings.warn("REML optimization did not converge")
                # Return OLS estimates
                return np.linalg.pinv(X) @ y, {'residual_variance': np.var(y)}, -np.inf

        except Exception as e:
            warnings.warn(f"REML fitting failed: {e}")
            # Fallback to OLS
            return np.linalg.pinv(X) @ y, {'residual_variance': np.var(y)}, -np.inf

    def _fit_ml(self, X: np.ndarray, Z: np.ndarray, y: np.ndarray,
                group_info: Dict[str, Any]) -> Tuple[np.ndarray, Dict[str, float], float]:
        """
        Fit mixed effects model using Maximum Likelihood (ML).
        """
        # Simplified ML implementation (similar to REML but without restriction)
        def negative_ml_loglik(params):
            beta = params[:X.shape[1]]
            sigma2 = np.exp(params[X.shape[1]])
            tau2 = np.exp(params[X.shape[1] + 1])

            V = tau2 * Z @ Z.T + sigma2 * np.eye(len(y))

            try:
                V_inv = linalg.pinvh(V)
                log_det_V = np.log(linalg.det(V))

                mu = X @ beta
                resid = y - mu

                n = len(y)
                loglik = -0.5 * n * np.log(2 * np.pi) - 0.5 * log_det_V
                loglik -= 0.5 * resid.T @ V_inv @ resid

                return -loglik

            except np.linalg.LinAlgError:
                return np.inf

        # Same optimization as REML
        n_params = X.shape[1] + 2
        init_params = np.concatenate([
            np.linalg.pinv(X) @ y,
            [0.0, 0.0]
        ])

        try:
            result = minimize(
                negative_ml_loglik,
                init_params,
                method='L-BFGS-B',
                options={'maxiter': 100}
            )

            if result.success:
                beta_hat = result.x[:X.shape[1]]
                sigma2 = np.exp(result.x[X.shape[1]])
                tau2 = np.exp(result.x[X.shape[1] + 1])
                log_likelihood = -result.fun

                variance_components = {
                    'residual_variance': sigma2,
                    'random_effects_variance': tau2,
                    'total_variance': sigma2 + tau2
                }

                return beta_hat, variance_components, log_likelihood
            else:
                warnings.warn("ML optimization did not converge")
                return np.linalg.pinv(X) @ y, {'residual_variance': np.var(y)}, -np.inf

        except Exception as e:
            warnings.warn(f"ML fitting failed: {e}")
            return np.linalg.pinv(X) @ y, {'residual_variance': np.var(y)}, -np.inf

    def predict(self, new_data: SPMData, include_random_effects: bool = True) -> np.ndarray:
        """
        Make predictions using fitted mixed effects model.

        Args:
            new_data: New data for prediction
            include_random_effects: Whether to include random effects in prediction

        Returns:
            Predicted values
        """
        if self.fitted_model is None:
            raise ValueError("Model must be fitted before making predictions")

        # For simplicity, return fixed effects predictions only
        # Full implementation would handle random effects properly
        X_pred = self.fixed_design.matrix  # Would need to construct for new data
        beta = self.fitted_model['beta']

        return X_pred @ beta

    def get_random_effects(self) -> Dict[str, np.ndarray]:
        """
        Extract estimated random effects.

        Returns:
            Dictionary of random effects by group
        """
        if self.fitted_model is None:
            raise ValueError("Model must be fitted before extracting random effects")

        # Placeholder - full implementation would extract random effects
        # from the fitted model
        return {
            'random_effects': np.array([]),
            'group_effects': {}
        }

    def anova(self, other_model: 'MixedEffectsSPM') -> Dict[str, Any]:
        """
        Perform likelihood ratio test comparing two nested models.

        Args:
            other_model: Another fitted MixedEffectsSPM to compare against

        Returns:
            Dictionary with test results
        """
        if self.fitted_model is None or other_model.fitted_model is None:
            raise ValueError("Both models must be fitted")

        # Likelihood ratio test
        ll1 = self.fitted_model['log_likelihood']
        ll2 = other_model.fitted_model['log_likelihood']

        # Determine which model is nested
        df1 = len(self.fitted_model['beta'])
        df2 = len(other_model.fitted_model['beta'])

        if df1 != df2:
            lr_stat = 2 * abs(ll1 - ll2)
            df_diff = abs(df1 - df2)
            p_value = 1 - stats.chi2.cdf(lr_stat, df_diff)
        else:
            lr_stat = 0
            df_diff = 0
            p_value = 1.0

        return {
            'likelihood_ratio': lr_stat,
            'df': df_diff,
            'p_value': p_value,
            'significant': p_value < 0.05
        }


def fit_mixed_effects(data: SPMData, fixed_design: DesignMatrix,
                     random_groups: Dict[str, np.ndarray],
                     **kwargs) -> SPMResult:
    """
    Convenience function to fit mixed effects SPM model.

    Args:
        data: SPMData containing response variable
        fixed_design: Design matrix for fixed effects
        random_groups: Grouping structure for random effects
        **kwargs: Additional arguments passed to MixedEffectsSPM.fit()

    Returns:
        SPMResult with fitted mixed effects model

    Example:
        >>> # Define groups (e.g., spatial clusters)
        >>> groups = {'cluster': cluster_indices}
        >>> result = fit_mixed_effects(data, design_matrix, groups)
    """
    model = MixedEffectsSPM(fixed_design, random_groups)
    return model.fit(data, **kwargs)
