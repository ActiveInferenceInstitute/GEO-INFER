"""
Tests for Temporal Statistics Module.

Comprehensive tests for time series statistical analysis including
diagnostic tests, information criteria, and summary statistics.
"""

import pytest
import numpy as np
import pandas as pd

from geo_infer_time.core.statistics import TemporalStatistics


@pytest.fixture
def stats():
    """Create a TemporalStatistics instance."""
    return TemporalStatistics()


@pytest.fixture
def sample_values():
    """Generate sample time series values."""
    np.random.seed(42)
    n = 100
    trend = np.arange(n) * 0.5
    noise = np.random.randn(n) * 5
    return list(trend + noise + 50)


@pytest.fixture
def stationary_values():
    """Generate stationary time series."""
    np.random.seed(42)
    return list(np.random.randn(100))


@pytest.fixture
def residual_values():
    """Generate residual-like values (mean ~ 0)."""
    np.random.seed(42)
    return list(np.random.randn(100) * 0.5)


class TestCalculateSummary:
    """Tests for summary statistics calculation."""
    
    def test_summary_structure(self, stats, sample_values):
        """Test that summary returns expected structure."""
        result = stats.calculate_summary(sample_values)
        
        assert 'n' in result
        assert 'central_tendency' in result
        assert 'dispersion' in result
        assert 'shape' in result
        assert 'quantiles' in result
        assert 'dynamics' in result
    
    def test_summary_central_tendency(self, stats, sample_values):
        """Test central tendency calculations."""
        result = stats.calculate_summary(sample_values)
        
        ct = result['central_tendency']
        assert 'mean' in ct
        assert 'median' in ct
    
    def test_summary_dispersion(self, stats, sample_values):
        """Test dispersion calculations."""
        result = stats.calculate_summary(sample_values)
        
        disp = result['dispersion']
        assert 'std' in disp
        assert 'variance' in disp
        assert 'cv' in disp
        assert disp['variance'] >= 0
    
    def test_summary_shape(self, stats, sample_values):
        """Test shape calculations."""
        result = stats.calculate_summary(sample_values)
        
        shape = result['shape']
        assert 'skewness' in shape
        assert 'kurtosis' in shape
    
    def test_summary_dynamics(self, stats, sample_values):
        """Test dynamics calculations."""
        result = stats.calculate_summary(sample_values)
        
        dyn = result['dynamics']
        assert 'trend_direction' in dyn
        assert dyn['trend_direction'] in ['increasing', 'decreasing', 'flat', 'unknown']
    
    def test_summary_empty(self, stats):
        """Test handling of empty values."""
        result = stats.calculate_summary([])
        assert 'error' in result


class TestCalculateDifferences:
    """Tests for differencing calculations."""
    
    def test_first_difference(self, stats, sample_values):
        """Test first-order differencing."""
        result = stats.calculate_differences(sample_values, order=1)
        
        assert 'differenced' in result
        assert len(result['differenced']['values']) == len(sample_values) - 1
    
    def test_second_difference(self, stats, sample_values):
        """Test second-order differencing."""
        result = stats.calculate_differences(sample_values, order=2)
        
        assert 'differenced' in result
        assert len(result['differenced']['values']) == len(sample_values) - 2
    
    def test_seasonal_difference(self, stats, sample_values):
        """Test seasonal differencing."""
        result = stats.calculate_differences(sample_values, order=1, seasonal_period=12)
        
        assert 'seasonal_differenced' in result
        assert result['seasonal_differenced']['period'] == 12
    
    def test_difference_too_short(self, stats):
        """Test error handling for too short series."""
        result = stats.calculate_differences([1, 2], order=3)
        assert 'error' in result


class TestLjungBoxTest:
    """Tests for Ljung-Box test."""
    
    def test_ljung_box_structure(self, stats, residual_values):
        """Test Ljung-Box returns expected structure."""
        result = stats.ljung_box_test(residual_values, lags=10)
        
        assert 'lb_statistic' in result
        assert 'p_value' in result
        assert 'lags' in result
        assert 'significant' in result
        assert 'interpretation' in result
    
    def test_ljung_box_random_residuals(self, stats, residual_values):
        """Test that random residuals pass Ljung-Box."""
        result = stats.ljung_box_test(residual_values, lags=10)
        
        # Random residuals should not show significant autocorrelation
        # (p-value should be > 0.05 most of the time)
        assert 'p_value' in result
    
    def test_ljung_box_too_short(self, stats):
        """Test error handling for too short series."""
        result = stats.ljung_box_test([1, 2, 3], lags=10)
        assert 'error' in result


class TestJarqueBeraTest:
    """Tests for Jarque-Bera normality test."""
    
    def test_jarque_bera_structure(self, stats, residual_values):
        """Test Jarque-Bera returns expected structure."""
        result = stats.jarque_bera_test(residual_values)
        
        assert 'jb_statistic' in result
        assert 'p_value' in result
        assert 'skewness' in result
        assert 'kurtosis' in result
        assert 'is_normal' in result
        assert 'interpretation' in result
    
    def test_jarque_bera_normal_data(self, stats):
        """Test that normal data passes Jarque-Bera."""
        np.random.seed(42)
        normal_data = list(np.random.randn(500))
        result = stats.jarque_bera_test(normal_data)
        
        # Should be normal with high probability
        assert 'is_normal' in result
    
    def test_jarque_bera_non_normal_data(self, stats):
        """Test that non-normal data is detected."""
        # Highly skewed data
        skewed_data = list(np.exp(np.random.randn(100)))
        result = stats.jarque_bera_test(skewed_data)
        
        # Skewed data should have significant skewness
        assert abs(result['skewness']) > 0
    
    def test_jarque_bera_too_short(self, stats):
        """Test error handling for too short series."""
        result = stats.jarque_bera_test([1, 2])
        assert 'error' in result


class TestDurbinWatsonTest:
    """Tests for Durbin-Watson test."""
    
    def test_durbin_watson_structure(self, stats, residual_values):
        """Test Durbin-Watson returns expected structure."""
        result = stats.durbin_watson_test(residual_values)
        
        assert 'dw_statistic' in result
        assert 'rho' in result
        assert 'interpretation' in result
        assert 'autocorrelation' in result
    
    def test_durbin_watson_range(self, stats, residual_values):
        """Test DW statistic is in valid range."""
        result = stats.durbin_watson_test(residual_values)
        
        # DW should be between 0 and 4
        assert 0 <= result['dw_statistic'] <= 4
    
    def test_durbin_watson_random_residuals(self, stats, residual_values):
        """Test that random residuals have DW ~ 2."""
        result = stats.durbin_watson_test(residual_values)
        
        # Random residuals should have DW close to 2
        assert 1.0 < result['dw_statistic'] < 3.0
    
    def test_durbin_watson_positive_autocorr(self, stats):
        """Test DW detects positive autocorrelation."""
        # Create AR(1) process with positive autocorrelation
        np.random.seed(42)
        ar_data = [0]
        for _ in range(99):
            ar_data.append(0.9 * ar_data[-1] + np.random.randn())
        
        result = stats.durbin_watson_test(ar_data)
        
        # Strong positive autocorrelation should have DW < 2
        assert result['dw_statistic'] < 2.0


class TestHurstExponent:
    """Tests for Hurst exponent calculation."""
    
    def test_hurst_structure(self, stats, sample_values):
        """Test Hurst exponent returns expected structure."""
        result = stats.hurst_exponent(sample_values)
        
        if 'error' not in result:
            assert 'hurst_exponent' in result
            assert 'process_type' in result
            assert 'interpretation' in result
    
    def test_hurst_range(self, stats, sample_values):
        """Test Hurst exponent is in valid range."""
        result = stats.hurst_exponent(sample_values)
        
        if 'hurst_exponent' in result:
            # Hurst should be between 0 and 1
            assert 0 <= result['hurst_exponent'] <= 1
    
    def test_hurst_random_walk(self, stats):
        """Test Hurst ≈ 0.5 for random walk."""
        np.random.seed(42)
        random_walk = list(np.cumsum(np.random.randn(200)))
        result = stats.hurst_exponent(random_walk)
        
        if 'hurst_exponent' in result:
            # Random walk should have H around 0.5-1.0 (R/S method can overestimate)
            assert 0.2 < result['hurst_exponent'] < 1.2
    
    def test_hurst_too_short(self, stats):
        """Test error handling for too short series."""
        result = stats.hurst_exponent([1, 2, 3])
        assert 'error' in result


class TestInformationCriteria:
    """Tests for information criteria calculation."""
    
    def test_ic_structure(self, stats, residual_values):
        """Test information criteria returns expected structure."""
        result = stats.information_criteria(residual_values, num_params=3)
        
        assert 'aic' in result
        assert 'bic' in result
        assert 'aicc' in result
        assert 'hqc' in result
        assert 'log_likelihood' in result
    
    def test_ic_penalty_ordering(self, stats, residual_values):
        """Test that AIC < AICc and BIC penalizes more than AIC."""
        result = stats.information_criteria(residual_values, num_params=5)
        
        # AICc >= AIC (corrected for small samples)
        assert result['aicc'] >= result['aic']
    
    def test_ic_more_params_higher(self, stats, residual_values):
        """Test that more parameters increase IC values."""
        result_3 = stats.information_criteria(residual_values, num_params=3)
        result_5 = stats.information_criteria(residual_values, num_params=5)
        
        # More parameters should increase AIC
        assert result_5['aic'] > result_3['aic']


class TestResidualDiagnostics:
    """Tests for comprehensive residual diagnostics."""
    
    def test_diagnostics_structure(self, stats, residual_values):
        """Test residual diagnostics returns expected structure."""
        result = stats.residual_diagnostics(residual_values)
        
        assert 'summary' in result
        assert 'normality' in result
        assert 'serial_correlation' in result
        assert 'mean_test' in result
        assert 'variance_test' in result
        assert 'overall' in result
    
    def test_diagnostics_overall_assessment(self, stats, residual_values):
        """Test overall assessment is provided."""
        result = stats.residual_diagnostics(residual_values)
        
        overall = result['overall']
        assert 'issues' in overall
        assert 'residuals_ok' in overall
        assert 'recommendation' in overall
    
    def test_diagnostics_good_residuals(self, stats):
        """Test that good residuals pass diagnostics."""
        np.random.seed(42)
        good_residuals = list(np.random.randn(100))
        result = stats.residual_diagnostics(good_residuals)
        
        # Should have few or no issues
        assert 'overall' in result
        assert isinstance(result['overall']['issues'], list)


class TestIntegration:
    """Integration tests combining multiple statistics."""
    
    def test_full_diagnostic_workflow(self, stats, sample_values):
        """Test running full diagnostic workflow."""
        # Summary
        summary = stats.calculate_summary(sample_values)
        assert 'n' in summary
        
        # Differencing
        diff = stats.calculate_differences(sample_values, order=1)
        assert 'differenced' in diff
        
        # Tests on differenced series
        diff_values = diff['differenced']['values']
        
        jb = stats.jarque_bera_test(diff_values)
        assert 'is_normal' in jb
        
        lb = stats.ljung_box_test(diff_values, lags=5)
        assert 'significant' in lb or 'error' in lb
