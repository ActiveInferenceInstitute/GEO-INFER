"""
Results visualization utilities for economic analysis.
"""

from typing import Dict, Any, List, Optional, Union, Tuple
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import geopandas as gpd
import numpy as np
from pathlib import Path
import logging

class ResultsVisualizer:
    """
    Utility class for visualizing economic analysis results.
    
    Provides methods for creating charts, maps, and interactive visualizations.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the ResultsVisualizer.
        
        Args:
            config: Optional configuration for visualization
        """
        self.logger = logging.getLogger(__name__)
        self.config = config or {}
        
        # Set style
        plt.style.use(self.config.get('style', 'seaborn-v0_8'))
        sns.set_palette(self.config.get('palette', 'husl'))
        
    def plot_economic_indicators(self, 
                                data: pd.DataFrame,
                                indicators: List[str],
                                title: str = "Economic Indicators",
                                save_path: Optional[Path] = None) -> plt.Figure:
        """
        Plot economic indicators over time or across regions.
        
        Args:
            data: DataFrame with economic indicators
            indicators: List of indicators to plot
            title: Chart title
            save_path: Optional path to save the chart
            
        Returns:
            Matplotlib figure object
        """
        fig, axes = plt.subplots(len(indicators), 1, figsize=(12, 6*len(indicators)))
        if len(indicators) == 1:
            axes = [axes]
            
        for i, indicator in enumerate(indicators):
            if indicator in data.columns:
                data[indicator].plot(ax=axes[i], title=f"{indicator}")
                axes[i].set_ylabel(indicator)
                axes[i].grid(True, alpha=0.3)
                
        plt.suptitle(title, fontsize=16)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"Economic indicators chart saved to {save_path}")
            
        return fig
        
    def create_choropleth_map(self,
                             gdf: gpd.GeoDataFrame,
                             value_column: str,
                             title: str = "Choropleth Map",
                             cmap: str = 'viridis',
                             save_path: Optional[Path] = None) -> plt.Figure:
        """
        Create a choropleth map for spatial economic data.
        
        Args:
            gdf: GeoDataFrame with spatial data
            value_column: Column to visualize
            title: Map title
            cmap: Colormap name
            save_path: Optional path to save the map
            
        Returns:
            Matplotlib figure object
        """
        fig, ax = plt.subplots(1, 1, figsize=(12, 8))
        
        gdf.plot(column=value_column, 
                ax=ax, 
                cmap=cmap, 
                legend=True,
                legend_kwds={'shrink': 0.6})
        
        ax.set_title(title, fontsize=16)
        ax.axis('off')
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"Choropleth map saved to {save_path}")
            
        return fig
        
    def plot_policy_comparison(self,
                              comparison_data: Dict[str, Dict[str, float]],
                              metrics: List[str],
                              title: str = "Policy Comparison",
                              save_path: Optional[Path] = None) -> plt.Figure:
        """
        Create a comparison chart for policy scenarios.
        
        Args:
            comparison_data: Dictionary with scenario data
            metrics: List of metrics to compare
            title: Chart title
            save_path: Optional path to save the chart
            
        Returns:
            Matplotlib figure object
        """
        # Convert to DataFrame for easier plotting
        df_data = []
        for scenario, data in comparison_data.items():
            for metric in metrics:
                if metric in data:
                    df_data.append({
                        'Scenario': scenario,
                        'Metric': metric,
                        'Value': data[metric]
                    })
                    
        df = pd.DataFrame(df_data)
        
        fig, ax = plt.subplots(1, 1, figsize=(12, 6))
        
        sns.barplot(data=df, x='Metric', y='Value', hue='Scenario', ax=ax)
        ax.set_title(title, fontsize=16)
        ax.set_ylabel('Impact Value')
        plt.xticks(rotation=45)
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"Policy comparison chart saved to {save_path}")
            
        return fig
        
    def plot_distributional_effects(self,
                                   effects: Dict[str, float],
                                   title: str = "Distributional Effects",
                                   save_path: Optional[Path] = None) -> plt.Figure:
        """
        Plot distributional effects across income quintiles or regions.

        Args:
            effects: Dictionary with distributional effects
            title: Chart title
            save_path: Optional path to save the chart

        Returns:
            Matplotlib figure object
        """
        categories = list(effects.keys())
        values = list(effects.values())

        fig, ax = plt.subplots(1, 1, figsize=(10, 6))

        bars = ax.bar(categories, values)

        # Color bars based on positive/negative values
        for bar, value in zip(bars, values):
            if value >= 0:
                bar.set_color('green')
            else:
                bar.set_color('red')

        ax.set_title(title, fontsize=16)
        ax.set_ylabel('Effect Size')
        ax.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        ax.grid(True, alpha=0.3)

        plt.xticks(rotation=45)
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"Distributional effects chart saved to {save_path}")

        return fig

    def create_spatial_heatmap(self, data: pd.DataFrame, value_column: str,
                              title: str = "Spatial Heatmap",
                              save_path: Optional[Path] = None) -> plt.Figure:
        """
        Create a spatial heatmap visualization.

        Args:
            data: DataFrame with spatial data
            value_column: Column to visualize
            title: Chart title
            save_path: Optional path to save the chart

        Returns:
            Matplotlib figure object
        """
        fig, ax = plt.subplots(1, 1, figsize=(12, 8))

        # Create heatmap
        if 'latitude' in data.columns and 'longitude' in data.columns:
            # Scatter plot with color intensity
            scatter = ax.scatter(data['longitude'], data['latitude'],
                               c=data[value_column], cmap='viridis', s=50, alpha=0.7)
            plt.colorbar(scatter, ax=ax, label=value_column)
        else:
            # Regular heatmap if no spatial coordinates
            heatmap_data = data.pivot_table(index=data.index, values=value_column)
            sns.heatmap(heatmap_data, ax=ax, cmap='viridis', annot=True, fmt='.2f')
            ax.set_title(title)

        ax.set_title(title, fontsize=16)
        ax.set_xlabel('Longitude' if 'longitude' in data.columns else 'X')
        ax.set_ylabel('Latitude' if 'latitude' in data.columns else 'Y')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"Spatial heatmap saved to {save_path}")

        return fig

    def plot_time_series_decomposition(self, time_series: pd.Series,
                                     decomposition_type: str = 'additive',
                                     title: str = "Time Series Decomposition",
                                     save_path: Optional[Path] = None) -> plt.Figure:
        """
        Plot time series decomposition (trend, seasonal, residual).

        Args:
            time_series: Time series data
            decomposition_type: Type of decomposition ('additive', 'multiplicative')
            title: Chart title
            save_path: Optional path to save the chart

        Returns:
            Matplotlib figure object
        """
        from statsmodels.tsa.seasonal import seasonal_decompose

        try:
            # Perform decomposition
            decomposition = seasonal_decompose(time_series, model=decomposition_type)

            # Create subplots
            fig, axes = plt.subplots(4, 1, figsize=(12, 10))

            # Original series
            axes[0].plot(time_series.index, time_series.values)
            axes[0].set_title('Original Series')
            axes[0].grid(True, alpha=0.3)

            # Trend
            axes[1].plot(time_series.index, decomposition.trend)
            axes[1].set_title('Trend')
            axes[1].grid(True, alpha=0.3)

            # Seasonal
            axes[2].plot(time_series.index, decomposition.seasonal)
            axes[2].set_title('Seasonal')
            axes[2].grid(True, alpha=0.3)

            # Residual
            axes[3].plot(time_series.index, decomposition.resid)
            axes[3].set_title('Residual')
            axes[3].grid(True, alpha=0.3)

            plt.suptitle(title, fontsize=16)
            plt.tight_layout()

            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                self.logger.info(f"Time series decomposition saved to {save_path}")

            return fig

        except Exception as e:
            self.logger.error(f"Time series decomposition failed: {str(e)}")
            # Return simple time series plot as fallback
            fig, ax = plt.subplots(1, 1, figsize=(12, 6))
            time_series.plot(ax=ax, title=title)
            return fig

    def create_model_diagnostics_plot(self, model_results: Dict[str, Any],
                                    title: str = "Model Diagnostics",
                                    save_path: Optional[Path] = None) -> plt.Figure:
        """
        Create comprehensive model diagnostics visualization.

        Args:
            model_results: Dictionary with model results and diagnostics
            title: Chart title
            save_path: Optional path to save the chart

        Returns:
            Matplotlib figure object
        """
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))

        # Residuals plot
        if 'residuals' in model_results:
            residuals = model_results['residuals']
            axes[0, 0].plot(residuals, 'o', alpha=0.5)
            axes[0, 0].axhline(y=0, color='red', linestyle='--')
            axes[0, 0].set_title('Residuals')
            axes[0, 0].grid(True, alpha=0.3)

        # Q-Q plot for normality
        if 'residuals' in model_results:
            residuals = model_results['residuals']
            from scipy import stats
            (osm, osr), (slope, intercept, r) = stats.probplot(residuals, dist='norm')
            axes[0, 1].scatter(osm, osr, alpha=0.5)
            axes[0, 1].plot(osm, slope * osm + intercept, 'r--')
            axes[0, 1].set_title('Q-Q Plot')
            axes[0, 1].grid(True, alpha=0.3)

        # Residuals vs Fitted values
        if 'fitted_values' in model_results and 'residuals' in model_results:
            fitted = model_results['fitted_values']
            residuals = model_results['residuals']
            axes[1, 0].scatter(fitted, residuals, alpha=0.5)
            axes[1, 0].axhline(y=0, color='red', linestyle='--')
            axes[1, 0].set_xlabel('Fitted Values')
            axes[1, 0].set_ylabel('Residuals')
            axes[1, 0].set_title('Residuals vs Fitted')
            axes[1, 0].grid(True, alpha=0.3)

        # Model performance metrics
        axes[1, 1].text(0.1, 0.8, f"R²: {model_results.get('r_squared', 'N/A'):.3f}")
        axes[1, 1].text(0.1, 0.6, f"RMSE: {model_results.get('rmse', 'N/A'):.3f}")
        axes[1, 1].text(0.1, 0.4, f"MAE: {model_results.get('mae', 'N/A'):.3f}")
        axes[1, 1].text(0.1, 0.2, f"MAPE: {model_results.get('mape', 'N/A'):.2f}%")
        axes[1, 1].set_title('Model Metrics')
        axes[1, 1].set_xlim(0, 1)
        axes[1, 1].set_ylim(0, 1)
        axes[1, 1].axis('off')

        plt.suptitle(title, fontsize=16)
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"Model diagnostics plot saved to {save_path}")

        return fig

    def plot_spatial_autocorrelation(self, data: gpd.GeoDataFrame, variable: str,
                                   spatial_weights: np.ndarray,
                                   title: str = "Spatial Autocorrelation",
                                   save_path: Optional[Path] = None) -> plt.Figure:
        """
        Plot spatial autocorrelation analysis including Moran's I scatterplot.

        Args:
            data: GeoDataFrame with spatial data
            variable: Variable to analyze
            spatial_weights: Spatial weights matrix
            title: Chart title
            save_path: Optional path to save the chart

        Returns:
            Matplotlib figure object
        """
        fig, axes = plt.subplots(1, 2, figsize=(15, 6))

        # Extract values and spatial lag
        values = data[variable].values
        wy_values = spatial_weights @ values

        # Moran's I scatterplot
        axes[0].scatter(values, wy_values, alpha=0.7)
        axes[0].axhline(y=np.mean(wy_values), color='red', linestyle='--', alpha=0.7)
        axes[0].axvline(x=np.mean(values), color='red', linestyle='--', alpha=0.7)
        axes[0].set_xlabel(f'{variable}')
        axes[0].set_ylabel(f'Spatial Lag of {variable}')
        axes[0].set_title("Moran's I Scatterplot")
        axes[0].grid(True, alpha=0.3)

        # Local indicators of spatial association (LISA) map
        # Calculate local Moran's I
        n = len(values)
        local_morans = values * wy_values / (values.T @ values / n)

        # Simple classification for visualization
        lisa_classes = np.zeros(n)
        lisa_classes[(values > np.mean(values)) & (local_morans > np.mean(local_morans))] = 1  # High-High
        lisa_classes[(values < np.mean(values)) & (local_morans < np.mean(local_morans))] = 2  # Low-Low
        lisa_classes[(values > np.mean(values)) & (local_morans < np.mean(local_morans))] = 3  # High-Low
        lisa_classes[(values < np.mean(values)) & (local_morans > np.mean(local_morans))] = 4  # Low-High

        # Plot LISA clusters on map
        data.plot(column=lisa_classes, ax=axes[1], cmap='Set1',
                 legend=True, categorical=True)
        axes[1].set_title("LISA Clusters")
        axes[1].set_xlabel("Longitude")
        axes[1].set_ylabel("Latitude")

        plt.suptitle(title, fontsize=16)
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"Spatial autocorrelation plot saved to {save_path}")

        return fig

    def create_interactive_dashboard(self, data_dict: Dict[str, Any],
                                   dashboard_type: str = 'economic_overview',
                                   output_path: Optional[Path] = None) -> str:
        """
        Create interactive dashboard (simplified - would use Plotly/Dash in practice).

        Args:
            data_dict: Dictionary with dashboard data
            dashboard_type: Type of dashboard
            output_path: Optional path to save HTML

        Returns:
            HTML string for interactive dashboard
        """
        # This is a simplified implementation
        # In practice, would use Plotly, Dash, or similar for interactive dashboards

        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>GEO-INFER-ECON Dashboard</title>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .dashboard {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
                .chart {{ border: 1px solid #ddd; padding: 15px; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <h1>GEO-INFER-ECON Interactive Dashboard</h1>
            <div class="dashboard">
                <div class="chart">
                    <h3>Economic Indicators</h3>
                    <div id="economic-chart" style="height: 400px;"></div>
                </div>
                <div class="chart">
                    <h3>Spatial Analysis</h3>
                    <div id="spatial-chart" style="height: 400px;"></div>
                </div>
            </div>
            <script>
                // Baseline for interactive charts
                // In practice, would create actual Plotly charts
                console.log('Dashboard data:', {data});
            </script>
        </body>
        </html>
        """

        # In a real implementation, would populate with actual data
        return html_template.format(data=data_dict) 