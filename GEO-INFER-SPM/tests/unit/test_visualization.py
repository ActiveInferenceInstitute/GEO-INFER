"""
Unit tests for visualization functionality
"""

import numpy as np
import pytest

from geo_infer_spm.models.data_models import SPMData, SPMResult, ContrastResult, DesignMatrix


class TestVisualizationImports:
    """Test visualization module imports and availability."""

    def test_maps_import(self):
        """Test maps module import."""
        try:
            from geo_infer_spm.visualization import maps
            assert hasattr(maps, 'create_statistical_map')
            assert hasattr(maps, 'plot_spm_results')
        except ImportError:
            pytest.skip("Visualization dependencies not available")

    def test_diagnostics_import(self):
        """Test diagnostics module import."""
        try:
            from geo_infer_spm.visualization import diagnostics
            assert hasattr(diagnostics, 'plot_model_diagnostics')
            assert hasattr(diagnostics, 'plot_contrast_results')
        except ImportError:
            pytest.skip("Visualization dependencies not available")

    def test_interactive_import(self):
        """Test interactive module import."""
        try:
            from geo_infer_spm.visualization import interactive
            assert hasattr(interactive, 'create_interactive_map')
            assert hasattr(interactive, 'create_dashboard')
        except ImportError:
            pytest.skip("Visualization dependencies not available")


class TestStatisticalMapVisualization:
    """Test statistical map creation."""

    def setup_method(self):
        """Set up test data."""
        np.random.seed(42)
        n_points = 50

        # Create mock SPM result
        coordinates = np.column_stack([
            np.random.uniform(-180, 180, n_points),
            np.random.uniform(-90, 90, n_points)
        ])

        X = np.random.randn(n_points, 2)
        beta = np.array([1.0, -0.5])
        y = X @ beta + 0.1 * np.random.randn(n_points)

        spm_data = SPMData(data=y, coordinates=coordinates, crs='EPSG:4326')
        design_matrix = DesignMatrix(matrix=X, names=['int', 'slope'])

        self.spm_result = SPMResult(
            spm_data=spm_data,
            design_matrix=design_matrix,
            beta_coefficients=beta,
            residuals=y - X @ beta,
            model_diagnostics={'r_squared': 0.9}
        )

        # Create mock contrast result
        self.contrast_result = ContrastResult(
            contrast_vector=np.array([0, 1]),
            t_statistic=np.random.randn(n_points),
            effect_size=np.random.randn(n_points),
            standard_error=np.ones(n_points),
            p_values=np.random.rand(n_points),
            significance_mask=np.random.rand(n_points) < 0.1
        )

    def test_create_statistical_map_data_structure(self):
        """Test statistical map data structure creation."""
        try:
            from geo_infer_spm.visualization.maps import create_statistical_map

            viz_data = create_statistical_map(self.spm_result, contrast_idx=0)

            # Check required fields
            required_fields = ['coordinates', 'stat_values', 'threshold', 'colormap', 'title']
            for field in required_fields:
                assert field in viz_data

            assert len(viz_data['coordinates']) == 50
            assert len(viz_data['stat_values']) == 50

        except ImportError:
            pytest.skip("Matplotlib not available")

    def test_statistical_map_with_contrast(self):
        """Test statistical map with specific contrast."""
        try:
            from geo_infer_spm.visualization.maps import create_statistical_map

            # Add contrast to result
            self.spm_result.contrasts = [self.contrast_result]

            viz_data = create_statistical_map(
                self.spm_result,
                contrast_idx=0,
                threshold=0.05,
                colormap='viridis'
            )

            assert viz_data['threshold'] == 0.05
            assert viz_data['colormap'] == 'viridis'
            assert 'significance_mask' in viz_data

        except ImportError:
            pytest.skip("Matplotlib not available")

    def test_plot_spm_results_dispatch(self):
        """Test SPM results plotting dispatch."""
        try:
            from geo_infer_spm.visualization.maps import plot_spm_results

            # Test stat_map type
            result = plot_spm_results(self.spm_result, plot_type='stat_map')
            assert isinstance(result, dict)

            # Test beta_map type
            result = plot_spm_results(self.spm_result, plot_type='beta_map')
            assert isinstance(result, dict)

        except ImportError:
            pytest.skip("Matplotlib not available")


class TestModelDiagnosticsVisualization:
    """Test model diagnostics plotting."""

    def setup_method(self):
        """Set up test data."""
        np.random.seed(42)
        n_points = 30

        coordinates = np.column_stack([
            np.random.uniform(-180, 180, n_points),
            np.random.uniform(-90, 90, n_points)
        ])

        X = np.random.randn(n_points, 2)
        beta = np.array([1.0, -0.5])
        y = X @ beta + 0.1 * np.random.randn(n_points)

        spm_data = SPMData(data=y, coordinates=coordinates, crs='EPSG:4326')
        design_matrix = DesignMatrix(matrix=X, names=['int', 'slope'])

        self.spm_result = SPMResult(
            spm_data=spm_data,
            design_matrix=design_matrix,
            beta_coefficients=beta,
            residuals=y - X @ beta,
            model_diagnostics={'r_squared': 0.9, 'f_statistic': 45.2}
        )

    def test_plot_model_diagnostics(self):
        """Test comprehensive model diagnostics plotting."""
        try:
            from geo_infer_spm.visualization.diagnostics import plot_model_diagnostics

            diagnostics = plot_model_diagnostics(self.spm_result)

            assert isinstance(diagnostics, dict)
            assert 'diagnostic_statistics' in diagnostics

            # Check that key statistics are computed
            stats = diagnostics['diagnostic_statistics']
            required_stats = ['n_observations', 'n_parameters', 'residual_mean', 'residual_std']
            for stat in required_stats:
                assert stat in stats

        except ImportError:
            pytest.skip("Matplotlib not available")

    def test_plot_contrast_results(self):
        """Test contrast results plotting."""
        try:
            from geo_infer_spm.visualization.diagnostics import plot_contrast_results

            contrast_result = ContrastResult(
                contrast_vector=np.array([0, 1]),
                t_statistic=np.random.randn(30),
                effect_size=np.random.randn(30),
                standard_error=np.ones(30),
                p_values=np.random.rand(30),
                significance_mask=np.random.rand(30) < 0.1
            )

            result = plot_contrast_results(contrast_result)

            assert isinstance(result, dict)
            assert 'n_significant' in result
            assert 'correction_method' in result

        except ImportError:
            pytest.skip("Matplotlib not available")

    def test_diagnostic_helper_functions(self):
        """Test diagnostic helper functions."""
        try:
            from geo_infer_spm.visualization.diagnostics import (
                _compute_diagnostic_stats,
                _plot_qq_residuals,
                _plot_residuals_vs_fitted
            )

            # Test diagnostic stats computation
            stats = _compute_diagnostic_stats(self.spm_result)

            assert isinstance(stats, dict)
            assert 'residual_mean' in stats
            assert 'residual_std' in stats

        except ImportError:
            pytest.skip("Matplotlib not available")


class TestInteractiveVisualization:
    """Test interactive visualization functions."""

    def setup_method(self):
        """Set up test data."""
        np.random.seed(42)
        n_points = 25

        coordinates = np.column_stack([
            np.random.uniform(-180, 180, n_points),
            np.random.uniform(-90, 90, n_points)
        ])

        X = np.random.randn(n_points, 2)
        beta = np.array([1.0, -0.5])
        y = X @ beta + 0.1 * np.random.randn(n_points)

        spm_data = SPMData(data=y, coordinates=coordinates, crs='EPSG:4326')
        design_matrix = DesignMatrix(matrix=X, names=['int', 'slope'])

        self.spm_result = SPMResult(
            spm_data=spm_data,
            design_matrix=design_matrix,
            beta_coefficients=beta,
            residuals=y - X @ beta,
            model_diagnostics={'r_squared': 0.9}
        )

    def test_create_interactive_map(self):
        """Test interactive map creation."""
        try:
            from geo_infer_spm.visualization.interactive import create_interactive_map

            # Test scattergeo map type
            interactive_map = create_interactive_map(
                self.spm_result,
                contrast_idx=0,
                map_type='scattergeo'
            )

            # Should return plotly figure or None
            assert interactive_map is None or hasattr(interactive_map, 'show')

        except ImportError:
            pytest.skip("Plotly not available")

    def test_create_dashboard(self):
        """Test dashboard creation."""
        try:
            from geo_infer_spm.visualization.interactive import create_dashboard

            dashboard = create_dashboard(self.spm_result, include_diagnostics=True)

            # Should return plotly figure or None
            assert dashboard is None or hasattr(dashboard, 'show')

        except ImportError:
            pytest.skip("Plotly not available")

    def test_create_time_series_explorer(self):
        """Test time series explorer creation."""
        try:
            from geo_infer_spm.visualization.interactive import create_time_series_explorer

            # Add temporal data
            time_data = np.arange(25)
            self.spm_result.spm_data.time = time_data

            explorer = create_time_series_explorer(self.spm_result)

            # Should return plotly figure or None
            assert explorer is None or hasattr(explorer, 'show')

        except ImportError:
            pytest.skip("Plotly not available")


class TestVisualizationDataStructures:
    """Test visualization data structure creation."""

    def test_statistical_map_data_format(self):
        """Test statistical map data format."""
        try:
            from geo_infer_spm.visualization.maps import create_statistical_map

            # Create minimal SPM result
            coordinates = np.random.rand(10, 2) * 100
            spm_data = SPMData(data=np.random.randn(10), coordinates=coordinates, crs='EPSG:4326')

            X = np.random.randn(10, 1)
            design_matrix = DesignMatrix(matrix=X, names=['intercept'])

            spm_result = SPMResult(
                spm_data=spm_data,
                design_matrix=design_matrix,
                beta_coefficients=np.array([0.5]),
                residuals=np.random.randn(10),
                model_diagnostics={}
            )

            viz_data = create_statistical_map(spm_result, contrast_idx=0)

            # Validate data structure
            assert isinstance(viz_data['coordinates'], list)
            assert isinstance(viz_data['stat_values'], list)
            assert isinstance(viz_data['title'], str)
            assert len(viz_data['coordinates']) == len(viz_data['stat_values'])

        except ImportError:
            pytest.skip("Matplotlib not available")

    def test_visualization_error_handling(self):
        """Test error handling in visualization functions."""
        try:
            from geo_infer_spm.visualization.maps import create_statistical_map

            # Test with invalid contrast index
            coordinates = np.random.rand(5, 2) * 100
            spm_data = SPMData(data=np.random.randn(5), coordinates=coordinates, crs='EPSG:4326')

            X = np.random.randn(5, 1)
            design_matrix = DesignMatrix(matrix=X, names=['intercept'])

            spm_result = SPMResult(
                spm_data=spm_data,
                design_matrix=design_matrix,
                beta_coefficients=np.array([0.5]),
                residuals=np.random.randn(5),
                model_diagnostics={}
            )

            # Should raise error for invalid contrast index
            with pytest.raises(ValueError, match="Contrast index.*out of range"):
                create_statistical_map(spm_result, contrast_idx=5)

        except ImportError:
            pytest.skip("Matplotlib not available")


class TestVisualizationWithoutDependencies:
    """Test visualization behavior when dependencies are unavailable."""

    def test_visualization_graceful_failure(self):
        """Test that visualization functions fail gracefully without dependencies."""
        # This test simulates the case where matplotlib/plotly are not available
        # by temporarily hiding the modules

        # Mock unavailable matplotlib
        import sys
        original_modules = sys.modules.copy()

        try:
            # Remove matplotlib from sys.modules if it exists
            modules_to_remove = ['matplotlib', 'matplotlib.pyplot', 'plotly', 'plotly.graph_objects']
            for module in modules_to_remove:
                if module in sys.modules:
                    del sys.modules[module]

            # Try to import visualization functions
            try:
                from geo_infer_spm.visualization.maps import create_statistical_map
                # If we get here, the import worked but matplotlib is not available
                # Create a dummy SPM result to test
                coordinates = np.random.rand(5, 2) * 100
                spm_data = SPMData(data=np.random.randn(5), coordinates=coordinates, crs='EPSG:4326')
                X = np.random.randn(5, 1)
                design_matrix = DesignMatrix(matrix=X, names=['intercept'])
                spm_result = SPMResult(
                    spm_data=spm_data,
                    design_matrix=design_matrix,
                    beta_coefficients=np.array([0.5]),
                    residuals=np.random.randn(5),
                    model_diagnostics={}
                )

                # This should return data dict without matplotlib figure
                result = create_statistical_map(spm_result, contrast_idx=0)
                assert isinstance(result, dict)
                assert 'coordinates' in result
                assert 'stat_values' in result

            except ImportError:
                # This is expected if visualization dependencies are not available
                pytest.skip("Visualization dependencies not available")

        finally:
            # Restore original modules
            sys.modules.update(original_modules)
