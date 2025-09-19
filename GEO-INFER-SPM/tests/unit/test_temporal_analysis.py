"""
Unit tests for temporal analysis functionality
"""

import numpy as np
import pytest

from geo_infer_spm.core.temporal_analysis import TemporalAnalyzer


class TestTemporalAnalyzer:
    """Test TemporalAnalyzer class functionality."""

    def setup_method(self):
        """Set up test data."""
        np.random.seed(42)
        self.n_timepoints = 100
        self.time_points = np.arange(self.n_timepoints)

        # Create test time series data
        self.time_series = np.random.randn(self.n_timepoints)

        self.analyzer = TemporalAnalyzer(self.time_points, self.time_series)

    def test_initialization(self):
        """Test TemporalAnalyzer initialization."""
        assert len(self.analyzer.time_points) == self.n_timepoints
        assert self.analyzer.time_series.shape == (self.n_timepoints,)

        # Test sorting
        unsorted_times = np.array([3, 1, 4, 1, 5])
        unsorted_data = np.array([1, 2, 3, 4, 5])
        analyzer_sorted = TemporalAnalyzer(unsorted_times, unsorted_data)

        assert np.all(np.diff(analyzer_sorted.time_points) >= 0)  # Should be sorted

    def test_linear_trend_detection(self):
        """Test linear trend detection."""
        # Create data with known linear trend
        slope = 0.02
        intercept = 5.0
        trend_data = slope * self.time_points + intercept + 0.1 * np.random.randn(self.n_timepoints)

        analyzer = TemporalAnalyzer(self.time_points, trend_data)
        results = analyzer.detect_trends(trend_data.reshape(1, -1))

        trend = results['trends'][0]
        assert 'slope' in trend
        assert 'p_value' in trend
        assert trend['significant'] == True
        assert abs(trend['slope'] - slope) < 0.005  # Should recover true slope

    def test_mann_kendall_trend(self):
        """Test Mann-Kendall trend detection."""
        # Create monotonic increasing trend
        trend_data = np.sort(np.random.randn(self.n_timepoints)) + 0.01 * self.time_points

        analyzer = TemporalAnalyzer(self.time_points, trend_data)
        results = analyzer.detect_trends(trend_data.reshape(1, -1), method='mann_kendall')

        trend = results['trends'][0]
        assert trend['significant'] == True
        assert trend['direction'] == 'increasing'

    def test_no_trend_detection(self):
        """Test trend detection on random data (no trend)."""
        random_data = np.random.randn(self.n_timepoints)

        analyzer = TemporalAnalyzer(self.time_points, random_data)
        results = analyzer.detect_trends(random_data.reshape(1, -1))

        trend = results['trends'][0]
        assert trend['significant'] == False

    def test_seasonal_decomposition_fallback(self):
        """Test seasonal decomposition fallback when statsmodels unavailable."""
        # Create seasonal data
        seasonal_data = 10 + 3 * np.sin(2 * np.pi * self.time_points / 12) + np.random.randn(self.n_timepoints)

        analyzer = TemporalAnalyzer(self.time_points, seasonal_data)

        # This should work even without statsmodels (uses fallback)
        try:
            result = analyzer.seasonal_decomposition(seasonal_data, period=12)
            assert 'trend' in result
            assert 'seasonal' in result
            assert 'residual' in result
        except ImportError:
            pytest.skip("Statsmodels not available for seasonal decomposition")

    def test_sliding_window_analysis(self):
        """Test sliding window analysis."""
        # Create data with changing patterns
        data = np.zeros(self.n_timepoints)
        data[:30] = 1.0   # First 30 points: mean = 1
        data[30:70] = 3.0 # Next 40 points: mean = 3
        data[70:] = 2.0   # Last 30 points: mean = 2

        analyzer = TemporalAnalyzer(self.time_points, data)

        result = analyzer.sliding_window_analysis(
            data, window_size=20, step_size=10,
            analysis_func=lambda x: {'mean': np.mean(x), 'std': np.std(x)}
        )

        assert 'window_results' in result
        assert len(result['window_results']) > 0

        # Check that means change over time
        means = [r['mean'] for r in result['window_results']]
        assert means[-1] != means[0]  # Should detect change

    def test_temporal_basis_functions(self):
        """Test temporal basis function generation."""
        analyzer = TemporalAnalyzer(self.time_points)

        # Test Fourier basis
        fourier_basis = analyzer.temporal_basis_functions(n_basis=6, basis_type='fourier')
        assert fourier_basis.shape == (self.n_timepoints, 6)

        # Test polynomial basis
        poly_basis = analyzer.temporal_basis_functions(n_basis=4, basis_type='polynomial')
        assert poly_basis.shape == (self.n_timepoints, 4)

        # Test B-spline basis (may fallback)
        bspline_basis = analyzer.temporal_basis_functions(n_basis=5, basis_type='bspline')
        assert bspline_basis.shape[0] == self.n_timepoints

    def test_arima_model_fallback(self):
        """Test ARIMA modeling fallback when statsmodels unavailable."""
        # Create AR(1) process data
        ar_data = np.zeros(self.n_timepoints)
        phi = 0.7
        for i in range(1, self.n_timepoints):
            ar_data[i] = phi * ar_data[i-1] + np.random.randn()

        analyzer = TemporalAnalyzer(self.time_points, ar_data)

        # This should either work or raise ImportError
        try:
            result = analyzer.fit_arima_model(ar_data, order=(1, 0, 0))
            assert 'models' in result or 'success' in result
        except ImportError:
            pytest.skip("Statsmodels not available for ARIMA modeling")


class TestTemporalTrendDetection:
    """Test comprehensive trend detection methods."""

    def setup_method(self):
        """Set up trend test data."""
        np.random.seed(42)
        self.n_points = 50
        self.time = np.arange(self.n_points)

    def test_linear_trend_recovery(self):
        """Test accurate recovery of linear trend parameters."""
        true_slope = 0.05
        true_intercept = 2.0
        noise_level = 0.1

        # Generate data with known trend
        trend = true_slope * self.time + true_intercept
        data = trend + noise_level * np.random.randn(self.n_points)

        analyzer = TemporalAnalyzer(self.time, data)
        results = analyzer.detect_trends(data.reshape(1, -1))

        estimated_slope = results['trends'][0]['slope']
        estimated_intercept = results['trends'][0]['intercept']

        # Should recover parameters within reasonable bounds
        assert abs(estimated_slope - true_slope) < 0.01
        assert abs(estimated_intercept - true_intercept) < 0.5

    def test_trend_significance(self):
        """Test trend significance detection."""
        # Strong trend
        strong_trend = 0.1 * self.time + np.random.randn(self.n_points) * 0.1
        analyzer = TemporalAnalyzer(self.time, strong_trend)
        results = analyzer.detect_trends(strong_trend.reshape(1, -1))
        assert results['trends'][0]['significant'] == True

        # Weak trend
        weak_trend = 0.01 * self.time + np.random.randn(self.n_points) * 0.5
        analyzer = TemporalAnalyzer(self.time, weak_trend)
        results = analyzer.detect_trends(weak_trend.reshape(1, -1))
        assert results['trends'][0]['significant'] == False

    def test_seasonal_pattern_detection(self):
        """Test detection of seasonal patterns."""
        # Create seasonal data
        seasonal_data = 10 + 5 * np.sin(2 * np.pi * self.time / 12) + np.random.randn(self.n_points)

        analyzer = TemporalAnalyzer(self.time, seasonal_data)

        try:
            decomposition = analyzer.seasonal_decomposition(seasonal_data, period=12)
            assert 'seasonal' in decomposition

            # Seasonal component should have the same period
            seasonal_amplitude = np.std(decomposition['seasonal'])
            assert seasonal_amplitude > 2.0  # Should detect strong seasonal pattern

        except ImportError:
            pytest.skip("Seasonal decomposition requires statsmodels")

    def test_change_point_detection_unavailable(self):
        """Test change point detection (requires external library)."""
        # Create data with change point
        data = np.zeros(self.n_points)
        data[:25] = 1.0
        data[25:] = 3.0

        analyzer = TemporalAnalyzer(self.time, data)

        # This should either work or raise ImportError for ruptures
        try:
            result = analyzer.change_point_detection(data)
            assert 'change_points' in result
        except ImportError:
            pytest.skip("Change point detection requires ruptures library")


class TestTemporalBasisFunctions:
    """Test temporal basis function generation."""

    def setup_method(self):
        """Set up basis function test data."""
        self.time_points = np.linspace(0, 10, 100)
        self.analyzer = TemporalAnalyzer(self.time_points)

    def test_fourier_basis_properties(self):
        """Test Fourier basis function properties."""
        basis = self.analyzer.temporal_basis_functions(n_basis=8, basis_type='fourier')

        # First column should be constant (intercept)
        assert np.allclose(basis[:, 0], 1.0)

        # Sine and cosine pairs should be orthogonal
        for i in range(1, basis.shape[1], 2):
            sine_comp = basis[:, i]
            cosine_comp = basis[:, i+1] if i+1 < basis.shape[1] else np.zeros_like(sine_comp)

            # Check orthogonality (approximately)
            dot_product = np.abs(np.dot(sine_comp, cosine_comp))
            assert dot_product < 0.1

    def test_polynomial_basis_orthogonality(self):
        """Test polynomial basis orthogonality."""
        basis = self.analyzer.temporal_basis_functions(n_basis=4, basis_type='polynomial')

        # Check that higher order polynomials are orthogonal to lower ones
        for i in range(basis.shape[1]):
            for j in range(i+1, basis.shape[1]):
                dot_product = abs(np.dot(basis[:, i], basis[:, j]))
                # Should be approximately orthogonal (small dot product)
                assert dot_product < len(self.time_points) * 0.1

    def test_basis_normalization(self):
        """Test that basis functions are properly scaled."""
        for basis_type in ['fourier', 'polynomial', 'bspline']:
            basis = self.analyzer.temporal_basis_functions(n_basis=5, basis_type=basis_type)

            # Each column should have reasonable scale
            for col in range(basis.shape[1]):
                col_std = np.std(basis[:, col])
                assert 0.1 < col_std < 10.0  # Reasonable scale

    def test_invalid_basis_type(self):
        """Test error handling for invalid basis types."""
        with pytest.raises(ValueError, match="Unknown basis type"):
            self.analyzer.temporal_basis_functions(basis_type='invalid')


class TestTemporalAnalysisEdgeCases:
    """Test edge cases in temporal analysis."""

    def test_single_timepoint(self):
        """Test with single time point."""
        time_points = np.array([0.0])
        data = np.array([1.0])

        analyzer = TemporalAnalyzer(time_points, data)
        assert len(analyzer.time_points) == 1
        assert analyzer.time_series.shape == (1,)

    def test_unsorted_time_points(self):
        """Test automatic sorting of time points."""
        time_points = np.array([5, 2, 8, 1, 9])
        data = np.array([1, 2, 3, 4, 5])

        analyzer = TemporalAnalyzer(time_points, data)

        # Should be sorted
        assert np.array_equal(analyzer.time_points, np.array([1, 2, 5, 8, 9]))
        assert np.array_equal(analyzer.time_series, np.array([4, 2, 1, 3, 5]))

    def test_missing_time_series(self):
        """Test analyzer without time series data."""
        time_points = np.arange(10)
        analyzer = TemporalAnalyzer(time_points)

        assert analyzer.time_series is None

        # Should still work for basis functions
        basis = analyzer.temporal_basis_functions(n_basis=3)
        assert basis.shape == (10, 3)

    def test_irregular_time_spacing(self):
        """Test with irregular time spacing."""
        time_points = np.array([0, 0.5, 1.7, 3.2, 6.1, 10.0])
        data = np.random.randn(6)

        analyzer = TemporalAnalyzer(time_points, data)

        # Should handle irregular spacing
        trends = analyzer.detect_trends(data.reshape(1, -1))
        assert len(trends['trends']) == 1

    def test_duplicate_time_points(self):
        """Test handling of duplicate time points."""
        time_points = np.array([1, 2, 2, 3, 4])
        data = np.array([1, 2, 2.1, 3, 4])

        analyzer = TemporalAnalyzer(time_points, data)

        # Should handle duplicates gracefully
        assert len(analyzer.time_points) == 5
        trends = analyzer.detect_trends(data.reshape(1, -1))
        assert trends is not None
