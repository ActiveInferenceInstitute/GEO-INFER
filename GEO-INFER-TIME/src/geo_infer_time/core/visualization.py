"""
Temporal Visualization Module for GEO-INFER-TIME.

Provides visualization methods for time series analysis including plots
for decomposition, forecasts, anomalies, and diagnostics.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple, Union
from pathlib import Path
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# Check for matplotlib
try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    logger.warning("matplotlib not available. Visualization disabled.")


class TemporalVisualization:
    """
    Visualization engine for temporal analysis.
    
    Provides methods for creating various time series plots including
    line plots, decomposition panels, forecast visualizations, and more.
    """

    def __init__(self, style: str = 'seaborn-v0_8-whitegrid', figsize: Tuple[int, int] = (12, 6)):
        """
        Initialize visualization engine.
        
        Args:
            style: Matplotlib style to use
            figsize: Default figure size (width, height)
        """
        self.figsize = figsize
        if HAS_MATPLOTLIB:
            try:
                plt.style.use(style)
            except Exception:
                try:
                    plt.style.use('seaborn-whitegrid')
                except Exception:
                    pass  # Use default style

    def plot_timeseries(
        self,
        values: List[float],
        timestamps: Optional[List] = None,
        title: str = "Time Series",
        ylabel: str = "Value",
        xlabel: str = "Time",
        color: str = "#2E86AB",
        show_grid: bool = True,
        save_path: Optional[Path] = None
    ) -> Optional[Any]:
        """
        Create a basic time series plot.
        
        Args:
            values: Time series values
            timestamps: Optional timestamps (index otherwise)
            title: Plot title
            ylabel: Y-axis label
            xlabel: X-axis label
            color: Line color
            show_grid: Whether to show grid
            save_path: Optional path to save figure
            
        Returns:
            Matplotlib figure or None if not available
        """
        if not HAS_MATPLOTLIB:
            return {'error': 'matplotlib not available'}
        
        fig, ax = plt.subplots(figsize=self.figsize)
        
        x = timestamps if timestamps is not None else range(len(values))
        ax.plot(x, values, color=color, linewidth=1.5)
        
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel(xlabel, fontsize=11)
        ax.set_ylabel(ylabel, fontsize=11)
        
        if show_grid:
            ax.grid(True, alpha=0.3)
        
        if timestamps is not None and len(timestamps) > 0:
            if hasattr(timestamps[0], 'strftime'):
                fig.autofmt_xdate()
        
        plt.tight_layout()
        
        if save_path:
            fig.savefig(save_path, dpi=150, bbox_inches='tight')
            logger.info(f"Saved plot to {save_path}")
        
        return fig

    def plot_decomposition(
        self,
        trend: List[float],
        seasonal: List[float],
        residual: List[float],
        original: Optional[List[float]] = None,
        timestamps: Optional[List] = None,
        title: str = "Time Series Decomposition",
        save_path: Optional[Path] = None
    ) -> Optional[Any]:
        """
        Create a decomposition plot with trend, seasonal, and residual panels.
        
        Args:
            trend: Trend component
            seasonal: Seasonal component
            residual: Residual component
            original: Optional original series
            timestamps: Optional timestamps
            title: Plot title
            save_path: Optional path to save figure
            
        Returns:
            Matplotlib figure
        """
        if not HAS_MATPLOTLIB:
            return {'error': 'matplotlib not available'}
        
        n_panels = 4 if original is not None else 3
        fig, axes = plt.subplots(n_panels, 1, figsize=(self.figsize[0], self.figsize[1] * 1.5))
        
        components = []
        labels = []
        colors = []
        
        if original is not None:
            components.append(original)
            labels.append('Original')
            colors.append('#2E86AB')
        
        components.extend([trend, seasonal, residual])
        labels.extend(['Trend', 'Seasonal', 'Residual'])
        colors.extend(['#E94F37', '#4DAA57', '#7B68EE'])
        
        for ax, data, label, color in zip(axes, components, labels, colors):
            x = timestamps if timestamps is not None else range(len(data))
            ax.plot(x, data, color=color, linewidth=1.2)
            ax.set_ylabel(label, fontsize=10)
            ax.grid(True, alpha=0.3)
        
        axes[0].set_title(title, fontsize=14, fontweight='bold')
        axes[-1].set_xlabel('Time', fontsize=11)
        
        plt.tight_layout()
        
        if save_path:
            fig.savefig(save_path, dpi=150, bbox_inches='tight')
        
        return fig

    def plot_forecast(
        self,
        historical: List[float],
        forecast: List[float],
        confidence_lower: Optional[List[float]] = None,
        confidence_upper: Optional[List[float]] = None,
        timestamps_historical: Optional[List] = None,
        timestamps_forecast: Optional[List] = None,
        title: str = "Time Series Forecast",
        save_path: Optional[Path] = None
    ) -> Optional[Any]:
        """
        Create a forecast plot with confidence intervals.
        
        Args:
            historical: Historical values
            forecast: Forecasted values
            confidence_lower: Lower confidence bound
            confidence_upper: Upper confidence bound
            timestamps_historical: Timestamps for historical data
            timestamps_forecast: Timestamps for forecast
            title: Plot title
            save_path: Optional path to save figure
            
        Returns:
            Matplotlib figure
        """
        if not HAS_MATPLOTLIB:
            return {'error': 'matplotlib not available'}
        
        fig, ax = plt.subplots(figsize=self.figsize)
        
        # Historical data
        n_hist = len(historical)
        x_hist = timestamps_historical if timestamps_historical is not None else range(n_hist)
        ax.plot(x_hist, historical, color='#2E86AB', linewidth=1.5, label='Historical')
        
        # Forecast
        if timestamps_forecast is not None:
            x_forecast = timestamps_forecast
        else:
            x_forecast = range(n_hist, n_hist + len(forecast))
        
        ax.plot(x_forecast, forecast, color='#E94F37', linewidth=2, 
                linestyle='--', label='Forecast')
        
        # Confidence intervals
        if confidence_lower is not None and confidence_upper is not None:
            ax.fill_between(x_forecast, confidence_lower, confidence_upper,
                          color='#E94F37', alpha=0.2, label='95% CI')
        
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel('Time', fontsize=11)
        ax.set_ylabel('Value', fontsize=11)
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
        
        # Vertical line at forecast start
        if len(x_hist) > 0 and len(x_forecast) > 0:
            ax.axvline(x=x_hist[-1] if hasattr(x_hist[-1], '__add__') else n_hist - 1,
                      color='gray', linestyle=':', alpha=0.7)
        
        plt.tight_layout()
        
        if save_path:
            fig.savefig(save_path, dpi=150, bbox_inches='tight')
        
        return fig

    def plot_acf_pacf(
        self,
        acf_values: List[float],
        pacf_values: Optional[List[float]] = None,
        confidence_bound: float = 0.0,
        title: str = "Autocorrelation Analysis",
        save_path: Optional[Path] = None
    ) -> Optional[Any]:
        """
        Create ACF and PACF plots.
        
        Args:
            acf_values: Autocorrelation function values
            pacf_values: Partial autocorrelation function values
            confidence_bound: Significance bound (e.g., 1.96/sqrt(n))
            title: Plot title
            save_path: Optional path to save figure
            
        Returns:
            Matplotlib figure
        """
        if not HAS_MATPLOTLIB:
            return {'error': 'matplotlib not available'}
        
        n_panels = 2 if pacf_values is not None else 1
        fig, axes = plt.subplots(n_panels, 1, figsize=(self.figsize[0], self.figsize[1]))
        
        if n_panels == 1:
            axes = [axes]
        
        # ACF
        lags = range(len(acf_values))
        axes[0].bar(lags, acf_values, color='#2E86AB', width=0.3)
        axes[0].axhline(y=0, color='black', linewidth=0.5)
        if confidence_bound > 0:
            axes[0].axhline(y=confidence_bound, color='red', linestyle='--', alpha=0.7)
            axes[0].axhline(y=-confidence_bound, color='red', linestyle='--', alpha=0.7)
        axes[0].set_ylabel('ACF', fontsize=10)
        axes[0].set_title(title, fontsize=14, fontweight='bold')
        axes[0].grid(True, alpha=0.3)
        
        # PACF
        if pacf_values is not None:
            axes[1].bar(range(len(pacf_values)), pacf_values, color='#4DAA57', width=0.3)
            axes[1].axhline(y=0, color='black', linewidth=0.5)
            if confidence_bound > 0:
                axes[1].axhline(y=confidence_bound, color='red', linestyle='--', alpha=0.7)
                axes[1].axhline(y=-confidence_bound, color='red', linestyle='--', alpha=0.7)
            axes[1].set_ylabel('PACF', fontsize=10)
            axes[1].grid(True, alpha=0.3)
        
        axes[-1].set_xlabel('Lag', fontsize=11)
        
        plt.tight_layout()
        
        if save_path:
            fig.savefig(save_path, dpi=150, bbox_inches='tight')
        
        return fig

    def plot_anomalies(
        self,
        values: List[float],
        anomaly_indices: List[int],
        timestamps: Optional[List] = None,
        title: str = "Anomaly Detection",
        save_path: Optional[Path] = None
    ) -> Optional[Any]:
        """
        Create a plot highlighting anomalies.
        
        Args:
            values: Time series values
            anomaly_indices: Indices of detected anomalies
            timestamps: Optional timestamps
            title: Plot title
            save_path: Optional path to save figure
            
        Returns:
            Matplotlib figure
        """
        if not HAS_MATPLOTLIB:
            return {'error': 'matplotlib not available'}
        
        fig, ax = plt.subplots(figsize=self.figsize)
        
        x = timestamps if timestamps is not None else range(len(values))
        values_arr = np.array(values)
        
        # Plot main series
        ax.plot(x, values_arr, color='#2E86AB', linewidth=1.2, label='Values')
        
        # Highlight anomalies
        if anomaly_indices:
            anomaly_x = [x[i] for i in anomaly_indices if i < len(x)]
            anomaly_y = [values_arr[i] for i in anomaly_indices if i < len(values_arr)]
            ax.scatter(anomaly_x, anomaly_y, color='#E94F37', s=100, 
                      zorder=5, label=f'Anomalies ({len(anomaly_indices)})',
                      edgecolors='white', linewidths=2)
        
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel('Time', fontsize=11)
        ax.set_ylabel('Value', fontsize=11)
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            fig.savefig(save_path, dpi=150, bbox_inches='tight')
        
        return fig

    def plot_rolling_statistics(
        self,
        values: List[float],
        rolling_mean: List[float],
        rolling_std: Optional[List[float]] = None,
        timestamps: Optional[List] = None,
        window: int = 0,
        title: str = "Rolling Statistics",
        save_path: Optional[Path] = None
    ) -> Optional[Any]:
        """
        Create a plot with rolling mean and standard deviation bands.
        
        Args:
            values: Original time series values
            rolling_mean: Rolling mean values
            rolling_std: Rolling standard deviation (for bands)
            timestamps: Optional timestamps
            window: Window size (for title)
            title: Plot title
            save_path: Optional path to save figure
            
        Returns:
            Matplotlib figure
        """
        if not HAS_MATPLOTLIB:
            return {'error': 'matplotlib not available'}
        
        fig, ax = plt.subplots(figsize=self.figsize)
        
        x = timestamps if timestamps is not None else range(len(values))
        
        # Original series
        ax.plot(x, values, color='#2E86AB', alpha=0.5, linewidth=1, label='Original')
        
        # Rolling mean
        # Adjust x length for rolling values
        x_rolling = x[-len(rolling_mean):]
        ax.plot(x_rolling, rolling_mean, color='#E94F37', linewidth=2, label='Rolling Mean')
        
        # Standard deviation bands
        if rolling_std is not None:
            rolling_mean_arr = np.array(rolling_mean)
            rolling_std_arr = np.array(rolling_std)
            ax.fill_between(x_rolling, 
                          rolling_mean_arr - 2 * rolling_std_arr,
                          rolling_mean_arr + 2 * rolling_std_arr,
                          color='#E94F37', alpha=0.2, label='±2 Std Dev')
        
        title_text = f"{title}" if window == 0 else f"{title} (window={window})"
        ax.set_title(title_text, fontsize=14, fontweight='bold')
        ax.set_xlabel('Time', fontsize=11)
        ax.set_ylabel('Value', fontsize=11)
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            fig.savefig(save_path, dpi=150, bbox_inches='tight')
        
        return fig

    def plot_seasonality(
        self,
        values: List[float],
        period: int,
        timestamps: Optional[List] = None,
        title: str = "Seasonal Subseries",
        save_path: Optional[Path] = None
    ) -> Optional[Any]:
        """
        Create seasonal subseries plot.
        
        Args:
            values: Time series values
            period: Seasonal period (e.g., 12 for monthly, 7 for weekly)
            timestamps: Optional timestamps
            title: Plot title
            save_path: Optional path to save figure
            
        Returns:
            Matplotlib figure
        """
        if not HAS_MATPLOTLIB:
            return {'error': 'matplotlib not available'}
        
        n = len(values)
        values_arr = np.array(values)
        
        fig, ax = plt.subplots(figsize=self.figsize)
        
        colors = plt.cm.tab10(np.linspace(0, 1, period))
        
        for season in range(period):
            season_values = values_arr[season::period]
            season_indices = np.arange(len(season_values))
            ax.plot(season_indices, season_values, 'o-', 
                   color=colors[season], alpha=0.7, markersize=4,
                   label=f'Season {season + 1}')
        
        ax.set_title(f"{title} (period={period})", fontsize=14, fontweight='bold')
        ax.set_xlabel('Cycle', fontsize=11)
        ax.set_ylabel('Value', fontsize=11)
        ax.legend(loc='best', ncol=min(4, period), fontsize=8)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            fig.savefig(save_path, dpi=150, bbox_inches='tight')
        
        return fig

    def create_dashboard(
        self,
        values: List[float],
        timestamps: Optional[List] = None,
        decomposition: Optional[Dict[str, List[float]]] = None,
        forecast: Optional[Dict[str, Any]] = None,
        anomalies: Optional[List[int]] = None,
        title: str = "Time Series Dashboard",
        save_path: Optional[Path] = None
    ) -> Optional[Any]:
        """
        Create a comprehensive multi-panel dashboard.
        
        Args:
            values: Time series values
            timestamps: Optional timestamps
            decomposition: Optional decomposition dict with 'trend', 'seasonal', 'residual'
            forecast: Optional forecast dict with 'values', 'lower', 'upper'
            anomalies: Optional list of anomaly indices
            title: Dashboard title
            save_path: Optional path to save figure
            
        Returns:
            Matplotlib figure
        """
        if not HAS_MATPLOTLIB:
            return {'error': 'matplotlib not available'}
        
        # Determine layout
        n_rows = 2
        n_cols = 2
        
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(self.figsize[0] * 1.5, self.figsize[1] * 1.5))
        fig.suptitle(title, fontsize=16, fontweight='bold', y=1.02)
        
        x = timestamps if timestamps is not None else range(len(values))
        values_arr = np.array(values)
        
        # Panel 1: Original series with anomalies
        ax1 = axes[0, 0]
        ax1.plot(x, values_arr, color='#2E86AB', linewidth=1.2)
        if anomalies:
            anomaly_x = [x[i] for i in anomalies if i < len(x)]
            anomaly_y = [values_arr[i] for i in anomalies if i < len(values_arr)]
            ax1.scatter(anomaly_x, anomaly_y, color='#E94F37', s=50, zorder=5)
        ax1.set_title('Time Series' + (f' ({len(anomalies)} anomalies)' if anomalies else ''), fontsize=11)
        ax1.set_xlabel('Time')
        ax1.set_ylabel('Value')
        ax1.grid(True, alpha=0.3)
        
        # Panel 2: Decomposition or Distribution
        ax2 = axes[0, 1]
        if decomposition and 'trend' in decomposition:
            ax2.plot(decomposition['trend'], color='#E94F37', label='Trend')
            if 'seasonal' in decomposition:
                ax2.plot(decomposition['seasonal'], color='#4DAA57', alpha=0.5, label='Seasonal')
            ax2.set_title('Decomposition', fontsize=11)
            ax2.legend(fontsize=8)
        else:
            ax2.hist(values_arr, bins=30, color='#2E86AB', edgecolor='white', alpha=0.7)
            ax2.axvline(np.mean(values_arr), color='#E94F37', linestyle='--', label='Mean')
            ax2.axvline(np.median(values_arr), color='#4DAA57', linestyle='--', label='Median')
            ax2.set_title('Distribution', fontsize=11)
            ax2.legend(fontsize=8)
        ax2.grid(True, alpha=0.3)
        
        # Panel 3: Rolling statistics
        ax3 = axes[1, 0]
        window = min(20, len(values_arr) // 5)
        if window > 1:
            rolling_mean = pd.Series(values_arr).rolling(window=window).mean()
            rolling_std = pd.Series(values_arr).rolling(window=window).std()
            ax3.plot(x, values_arr, color='#2E86AB', alpha=0.3, linewidth=1)
            ax3.plot(x, rolling_mean, color='#E94F37', linewidth=2, label='Rolling Mean')
            ax3.fill_between(x, 
                           rolling_mean - 2*rolling_std,
                           rolling_mean + 2*rolling_std,
                           color='#E94F37', alpha=0.2)
            ax3.set_title(f'Rolling Statistics (window={window})', fontsize=11)
        else:
            ax3.plot(x, values_arr, color='#2E86AB')
            ax3.set_title('Time Series', fontsize=11)
        ax3.set_xlabel('Time')
        ax3.set_ylabel('Value')
        ax3.grid(True, alpha=0.3)
        
        # Panel 4: Forecast or ACF
        ax4 = axes[1, 1]
        if forecast and 'values' in forecast:
            n_hist = len(values_arr)
            ax4.plot(range(n_hist), values_arr, color='#2E86AB', label='Historical')
            forecast_x = range(n_hist, n_hist + len(forecast['values']))
            ax4.plot(forecast_x, forecast['values'], color='#E94F37', 
                    linestyle='--', linewidth=2, label='Forecast')
            if 'lower' in forecast and 'upper' in forecast:
                ax4.fill_between(forecast_x, forecast['lower'], forecast['upper'],
                               color='#E94F37', alpha=0.2)
            ax4.set_title('Forecast', fontsize=11)
            ax4.legend(fontsize=8)
        else:
            # ACF plot
            from statsmodels.tsa.stattools import acf
            acf_values = acf(values_arr, nlags=min(40, len(values_arr)//2), fft=True)
            ax4.bar(range(len(acf_values)), acf_values, color='#2E86AB', width=0.3)
            ax4.axhline(y=0, color='black', linewidth=0.5)
            conf = 1.96 / np.sqrt(len(values_arr))
            ax4.axhline(y=conf, color='red', linestyle='--', alpha=0.7)
            ax4.axhline(y=-conf, color='red', linestyle='--', alpha=0.7)
            ax4.set_title('Autocorrelation', fontsize=11)
        ax4.set_xlabel('Lag' if forecast is None else 'Time')
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            fig.savefig(save_path, dpi=150, bbox_inches='tight')
        
        return fig
