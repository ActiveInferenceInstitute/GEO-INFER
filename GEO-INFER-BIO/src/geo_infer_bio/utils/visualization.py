"""
Visualization utilities for GEO-INFER-BIO.
"""
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import geopandas as gpd
from typing import Optional
from pathlib import Path


class BioVisualizer:
    """A class for visualizing biological data with spatial context."""

    def __init__(self):
        """Initialize the BioVisualizer."""
        plt.style.use("seaborn")
        sns.set_palette("husl")

    def plot_spatial_distribution(
        self,
        data: pd.DataFrame,
        output_path: Optional[str] = None,
        title: str = "Spatial Distribution",
    ) -> None:
        """
        Plot spatial distribution of biological features.

        Args:
            data: DataFrame containing spatial data
            output_path: Optional path to save the plot
            title: Plot title
        """
        gdf = gpd.GeoDataFrame(
            data,
            geometry=gpd.points_from_xy(data.longitude, data.latitude),
            crs="EPSG:4326",
        )

        fig, ax = plt.subplots(figsize=(12, 8))
        gdf.plot(ax=ax, markersize=100)
        ax.set_title(title)
        ax.set_xlabel("Longitude")
        ax.set_ylabel("Latitude")

        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close()

    def plot_gc_distribution(
        self,
        data: pd.DataFrame,
        output_path: Optional[str] = None,
    ) -> None:
        """
        Plot GC content distribution.

        Args:
            data: DataFrame containing GC content data
            output_path: Optional path to save the plot
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))

        # Histogram
        sns.histplot(data=data, x="gc_content", ax=ax1)
        ax1.set_title("GC Content Distribution")
        ax1.set_xlabel("GC Content (%)")
        ax1.set_ylabel("Count")

        # Spatial plot
        gdf = gpd.GeoDataFrame(
            data,
            geometry=gpd.points_from_xy(data.longitude, data.latitude),
            crs="EPSG:4326",
        )
        gdf.plot(column="gc_content", ax=ax2, legend=True)
        ax2.set_title("Spatial GC Content Distribution")
        ax2.set_xlabel("Longitude")
        ax2.set_ylabel("Latitude")

        plt.tight_layout()
        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close()

    def plot_motif_density(
        self,
        data: pd.DataFrame,
        output_path: Optional[str] = None,
    ) -> None:
        """
        Plot motif density distribution.

        Args:
            data: DataFrame containing motif density data
            output_path: Optional path to save the plot
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))

        # Bar plot
        sns.barplot(data=data, x="sequence_id", y="motif_count", ax=ax1)
        ax1.set_title("Motif Density by Sequence")
        ax1.set_xlabel("Sequence ID")
        ax1.set_ylabel("Motif Count")
        ax1.tick_params(axis="x", rotation=45)

        # Spatial plot
        gdf = gpd.GeoDataFrame(
            data,
            geometry=gpd.points_from_xy(data.longitude, data.latitude),
            crs="EPSG:4326",
        )
        gdf.plot(column="motif_count", ax=ax2, legend=True)
        ax2.set_title("Spatial Motif Density")
        ax2.set_xlabel("Longitude")
        ax2.set_ylabel("Latitude")

        plt.tight_layout()
        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close()

    def plot_coding_potential(
        self,
        data: pd.DataFrame,
        output_path: Optional[str] = None,
    ) -> None:
        """
        Plot coding potential distribution.

        Args:
            data: DataFrame containing coding potential data
            output_path: Optional path to save the plot
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))

        # Bar plot
        sns.barplot(data=data, x="sequence_id", y="coding_regions", ax=ax1)
        ax1.set_title("Coding Regions by Sequence")
        ax1.set_xlabel("Sequence ID")
        ax1.set_ylabel("Number of Coding Regions")
        ax1.tick_params(axis="x", rotation=45)

        # Spatial plot
        gdf = gpd.GeoDataFrame(
            data,
            geometry=gpd.points_from_xy(data.longitude, data.latitude),
            crs="EPSG:4326",
        )
        gdf.plot(column="coding_regions", ax=ax2, legend=True)
        ax2.set_title("Spatial Coding Potential")
        ax2.set_xlabel("Longitude")
        ax2.set_ylabel("Latitude")

        plt.tight_layout()
        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close()

    def plot_sequence_alignment(
        self,
        alignment,
        output_path: Optional[str] = None,
    ) -> None:
        """
        Plot sequence alignment.

        Args:
            alignment: MultipleSeqAlignment object
            output_path: Optional path to save the plot
        """
        fig, ax = plt.subplots(figsize=(15, 8))
        sns.heatmap(
            pd.DataFrame(alignment),
            ax=ax,
            cmap="YlOrRd",
            cbar_kws={"label": "Nucleotide"},
        )
        ax.set_title("Sequence Alignment")
        ax.set_xlabel("Position")
        ax.set_ylabel("Sequence ID")

        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close() 