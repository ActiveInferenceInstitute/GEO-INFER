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