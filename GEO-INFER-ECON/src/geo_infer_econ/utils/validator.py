"""
Model validation utilities for economic analysis.
"""

from typing import Dict, Any, List, Optional, Union, Callable
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.model_selection import cross_val_score
from sklearn.metrics import mean_squared_error, r2_score
import logging

class ModelValidator:
    """
    Utility class for validating economic models and results.
    
    Provides methods for statistical testing, model diagnostics, and validation.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the ModelValidator.
        
        Args:
            config: Optional configuration for validation
        """
        self.logger = logging.getLogger(__name__)
        self.config = config or {}
        
    def validate_regression_assumptions(self, 
                                      residuals: np.ndarray,
                                      fitted_values: np.ndarray,
                                      X: Optional[np.ndarray] = None) -> Dict[str, Any]:
        """
        Validate regression model assumptions.
        
        Args:
            residuals: Model residuals
            fitted_values: Fitted values from the model
            X: Optional design matrix for additional tests
            
        Returns:
            Dictionary with validation results
        """
        validation_results = {
            'normality': self._test_normality(residuals),
            'homoscedasticity': self._test_homoscedasticity(residuals, fitted_values),
            'autocorrelation': self._test_autocorrelation(residuals),
            'linearity': self._test_linearity(residuals, fitted_values)
        }
        
        if X is not None:
            validation_results['multicollinearity'] = self._test_multicollinearity(X)
            
        return validation_results
        
    def _test_normality(self, residuals: np.ndarray) -> Dict[str, Any]:
        """Test normality of residuals using Shapiro-Wilk and Jarque-Bera tests."""
        try:
            # Shapiro-Wilk test (for smaller samples)
            if len(residuals) <= 5000:
                shapiro_stat, shapiro_p = stats.shapiro(residuals)
            else:
                shapiro_stat, shapiro_p = None, None
                
            # Jarque-Bera test
            jb_stat, jb_p = stats.jarque_bera(residuals)
            
            return {
                'shapiro_statistic': shapiro_stat,
                'shapiro_p_value': shapiro_p,
                'jarque_bera_statistic': jb_stat,
                'jarque_bera_p_value': jb_p,
                'normal': jb_p > 0.05,
                'interpretation': 'Residuals appear normally distributed' if jb_p > 0.05 else 'Residuals deviate from normality'
            }
            
        except Exception as e:
            self.logger.error(f"Normality test failed: {str(e)}")
            return {'error': str(e)}
            
    def _test_homoscedasticity(self, residuals: np.ndarray, fitted_values: np.ndarray) -> Dict[str, Any]:
        """Test homoscedasticity using Breusch-Pagan test."""
        try:
            # Breusch-Pagan test
            n = len(residuals)
            squared_residuals = residuals ** 2
            
            # Simple regression of squared residuals on fitted values
            X = np.column_stack([np.ones(n), fitted_values])
            beta = np.linalg.lstsq(X, squared_residuals, rcond=None)[0]
            predicted = X @ beta
            
            # Test statistic
            rss = np.sum((squared_residuals - predicted) ** 2)
            explained_ss = np.sum((predicted - np.mean(squared_residuals)) ** 2)
            
            bp_stat = (n * explained_ss) / np.sum(squared_residuals ** 2)
            bp_p = 1 - stats.chi2.cdf(bp_stat, 1)
            
            return {
                'breusch_pagan_statistic': bp_stat,
                'breusch_pagan_p_value': bp_p,
                'homoscedastic': bp_p > 0.05,
                'interpretation': 'Homoscedasticity assumption satisfied' if bp_p > 0.05 else 'Heteroscedasticity detected'
            }
            
        except Exception as e:
            self.logger.error(f"Homoscedasticity test failed: {str(e)}")
            return {'error': str(e)}
            
    def _test_autocorrelation(self, residuals: np.ndarray) -> Dict[str, Any]:
        """Test for autocorrelation using Durbin-Watson test."""
        try:
            # Durbin-Watson test
            diff_residuals = np.diff(residuals)
            dw_stat = np.sum(diff_residuals ** 2) / np.sum(residuals ** 2)
            
            # Simple interpretation (more sophisticated critical values would be needed)
            no_autocorr = 1.5 < dw_stat < 2.5
            
            return {
                'durbin_watson_statistic': dw_stat,
                'no_autocorrelation': no_autocorr,
                'interpretation': 'No significant autocorrelation' if no_autocorr else 'Autocorrelation detected'
            }
            
        except Exception as e:
            self.logger.error(f"Autocorrelation test failed: {str(e)}")
            return {'error': str(e)}
            
    def _test_linearity(self, residuals: np.ndarray, fitted_values: np.ndarray) -> Dict[str, Any]:
        """Test linearity assumption using RESET test."""
        try:
            # Simple linearity test using correlation
            corr_coef = np.corrcoef(residuals, fitted_values)[0, 1]
            
            # Test if correlation is significantly different from zero
            n = len(residuals)
            t_stat = corr_coef * np.sqrt((n - 2) / (1 - corr_coef**2))
            p_value = 2 * (1 - stats.t.cdf(np.abs(t_stat), n - 2))
            
            return {
                'correlation_residuals_fitted': corr_coef,
                't_statistic': t_stat,
                'p_value': p_value,
                'linear': p_value > 0.05,
                'interpretation': 'Linearity assumption satisfied' if p_value > 0.05 else 'Nonlinearity detected'
            }
            
        except Exception as e:
            self.logger.error(f"Linearity test failed: {str(e)}")
            return {'error': str(e)}
            
    def _test_multicollinearity(self, X: np.ndarray) -> Dict[str, Any]:
        """Test for multicollinearity using condition number and VIF."""
        try:
            # Condition number
            cond_number = np.linalg.cond(X)
            
            # Simple VIF calculation (would need more sophisticated implementation)
            # For now, just return condition number
            high_multicollinearity = cond_number > 30
            
            return {
                'condition_number': cond_number,
                'high_multicollinearity': high_multicollinearity,
                'interpretation': 'Multicollinearity concern' if high_multicollinearity else 'Multicollinearity acceptable'
            }
            
        except Exception as e:
            self.logger.error(f"Multicollinearity test failed: {str(e)}")
            return {'error': str(e)}
            
    def cross_validate_model(self, 
                           model: Any,
                           X: np.ndarray, 
                           y: np.ndarray,
                           cv_folds: int = 5,
                           scoring: str = 'neg_mean_squared_error') -> Dict[str, Any]:
        """
        Perform cross-validation for model performance assessment.
        
        Args:
            model: Sklearn-compatible model
            X: Feature matrix
            y: Target variable
            cv_folds: Number of cross-validation folds
            scoring: Scoring metric
            
        Returns:
            Cross-validation results
        """
        try:
            cv_scores = cross_val_score(model, X, y, cv=cv_folds, scoring=scoring)
            
            return {
                'cv_scores': cv_scores,
                'mean_cv_score': np.mean(cv_scores),
                'std_cv_score': np.std(cv_scores),
                'scoring_metric': scoring,
                'interpretation': f'Mean CV score: {np.mean(cv_scores):.4f} ± {np.std(cv_scores):.4f}'
            }
            
        except Exception as e:
            self.logger.error(f"Cross-validation failed: {str(e)}")
            return {'error': str(e)}
            
    def validate_economic_model_results(self, 
                                      predictions: np.ndarray,
                                      actual: np.ndarray,
                                      model_type: str = 'regression') -> Dict[str, Any]:
        """
        Validate economic model results against known outcomes.
        
        Args:
            predictions: Model predictions
            actual: Actual observed values
            model_type: Type of model ('regression', 'classification')
            
        Returns:
            Validation metrics
        """
        try:
            if model_type == 'regression':
                mse = mean_squared_error(actual, predictions)
                rmse = np.sqrt(mse)
                r2 = r2_score(actual, predictions)
                
                # Mean Absolute Percentage Error
                mape = np.mean(np.abs((actual - predictions) / actual)) * 100
                
                return {
                    'mse': mse,
                    'rmse': rmse,
                    'r_squared': r2,
                    'mape': mape,
                    'interpretation': f'Model explains {r2:.2%} of variance with RMSE of {rmse:.4f}'
                }
                
            else:
                # Placeholder for classification metrics
                return {'error': 'Classification validation not yet implemented'}
                
        except Exception as e:
            self.logger.error(f"Results validation failed: {str(e)}")
            return {'error': str(e)} 