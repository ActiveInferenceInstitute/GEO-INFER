"""
GeoArt module for artistic visualization of geospatial data.
"""

import os
from typing import Dict, List, Optional, Tuple, Union

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

from geo_infer_art.core.aesthetics import ColorPalette
from geo_infer_art.utils.validators import validate_file_path, validate_geospatial_data


class GeoArt:
    """
    A class for creating artistic visualizations of geospatial data.
    
    The GeoArt class provides methods for loading, transforming, and
    visualizing geospatial data with artistic elements and aesthetic
    considerations.
    
    Attributes:
        data: The geospatial data as a GeoDataFrame or raster array
        metadata: Additional information about the data
        crs: Coordinate reference system of the data
    """
    
    def __init__(
        self, 
        data: Optional[Union[gpd.GeoDataFrame, np.ndarray]] = None, 
        metadata: Optional[Dict] = None,
        crs: Optional[str] = "EPSG:4326"
    ):
        """
        Initialize a GeoArt object.
        
        Args:
            data: Geospatial data as a GeoDataFrame or numpy array (for raster)
            metadata: Additional information about the data
            crs: Coordinate reference system identifier
        """
        self.data = data
        self.metadata = metadata or {}
        self.crs = crs
        self._figure = None
        self._ax = None
    
    @classmethod
    def load_geojson(cls, file_path: str) -> 'GeoArt':
        """
        Load geospatial data from a GeoJSON file.
        
        Args:
            file_path: Path to the GeoJSON file
            
        Returns:
            A new GeoArt object with the loaded data
        
        Raises:
            FileNotFoundError: If the file does not exist
            ValueError: If the file is not a valid GeoJSON
        """
        validate_file_path(file_path, ['.geojson', '.json'])
        
        try:
            data = gpd.read_file(file_path)
            metadata = {
                "source": file_path,
                "type": "vector",
                "features": len(data),
                "attributes": list(data.columns),
            }
            return cls(data=data, metadata=metadata, crs=data.crs)
        except Exception as e:
            raise ValueError(f"Failed to load GeoJSON: {str(e)}") from e
    
    @classmethod
    def load_raster(cls, file_path: str) -> 'GeoArt':
        """
        Load geospatial data from a raster file (e.g., GeoTIFF).
        
        Args:
            file_path: Path to the raster file
            
        Returns:
            A new GeoArt object with the loaded data
            
        Raises:
            FileNotFoundError: If the file does not exist
            ValueError: If the file is not a valid raster
        """
        import rasterio
        
        validate_file_path(file_path, ['.tif', '.tiff', '.jpg', '.png'])
        
        try:
            with rasterio.open(file_path) as src:
                data = src.read()
                metadata = {
                    "source": file_path,
                    "type": "raster",
                    "shape": data.shape,
                    "bounds": src.bounds,
                    "transform": src.transform,
                }
                return cls(data=data, metadata=metadata, crs=src.crs.to_string())
        except Exception as e:
            raise ValueError(f"Failed to load raster: {str(e)}") from e
    
    def apply_style(
        self,
        style: str = "default",
        color_palette: Optional[Union[str, ColorPalette]] = None,
        line_width: float = 1.0,
        alpha: float = 0.8,
        background_color: str = "white",
    ) -> 'GeoArt':
        """
        Apply an artistic style to the geospatial data.
        
        Args:
            style: Name of the style to apply
            color_palette: Color palette name or ColorPalette object
            line_width: Width of lines for vector data
            alpha: Transparency level (0.0 to 1.0)
            background_color: Background color of the visualization
            
        Returns:
            Self for method chaining
            
        Raises:
            ValueError: If the data is not loaded or the style is invalid
        """
        if self.data is None:
            raise ValueError("No data loaded. Load data first.")
        
        validate_geospatial_data(self.data)
        
        # Handle color palette
        if isinstance(color_palette, str):
            palette = ColorPalette.get_palette(color_palette)
        elif isinstance(color_palette, ColorPalette):
            palette = color_palette
        elif color_palette is None:
            # Default palettes for different styles
            style_palettes = {
                "default": "viridis",
                "watercolor": "pastel",
                "topographic": "earth",
                "neon": "bright",
                "minimal": "grayscale",
                "blueprint": "blue",
            }
            palette_name = style_palettes.get(style, "viridis")
            palette = ColorPalette.get_palette(palette_name)
        else:
            raise ValueError(f"Unsupported color_palette type: {type(color_palette)}")
        
        # Create figure and apply style
        fig, ax = plt.subplots(figsize=(10, 8), facecolor=background_color)
        
        if isinstance(self.data, gpd.GeoDataFrame):
            # Vector data visualization
            self.data.plot(
                ax=ax,
                cmap=palette.cmap,
                linewidth=line_width,
                alpha=alpha,
            )
        else:
            # Raster data visualization
            if self.data.ndim == 3 and self.data.shape[0] == 3:
                # RGB image
                rgb = np.dstack([self.data[0], self.data[1], self.data[2]])
                ax.imshow(rgb)
            else:
                # Single band or other raster
                ax.imshow(self.data, cmap=palette.cmap, alpha=alpha)
        
        # Apply style-specific settings
        if style == "watercolor":
            ax.patch.set_alpha(0.3)
            ax.grid(False)
        elif style == "minimal":
            ax.axis('off')
            ax.grid(False)
        elif style == "blueprint":
            ax.set_facecolor('#072448')
            ax.grid(True, color='#1E88E5', alpha=0.3, linestyle='-')
            
        ax.set_title(f"Artistic Visualization - {style.capitalize()}")
        
        self._figure = fig
        self._ax = ax
        
        return self
    
    def save(self, output_path: str, dpi: int = 300) -> str:
        """
        Save the visualization to a file.
        
        Args:
            output_path: Path where the file should be saved
            dpi: Resolution for the output image
            
        Returns:
            The path to the saved file
            
        Raises:
            ValueError: If no visualization has been created
        """
        if self._figure is None:
            raise ValueError("No visualization to save. Apply a style first.")
        
        directory = os.path.dirname(output_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
            
        self._figure.savefig(output_path, dpi=dpi, bbox_inches='tight')
        return output_path
    
    def show(self) -> None:
        """
        Display the visualization.
        
        Raises:
            ValueError: If no visualization has been created
        """
        if self._figure is None:
            raise ValueError("No visualization to show. Apply a style first.")
        
        plt.show()
    
    def __repr__(self) -> str:
        """Return a string representation of the GeoArt object."""
        if self.data is None:
            return "GeoArt(No data loaded)"
        
        if isinstance(self.data, gpd.GeoDataFrame):
            return f"GeoArt(Vector data: {len(self.data)} features)"
        else:
            shape_str = f"{self.data.shape}"
            return f"GeoArt(Raster data: {shape_str})" 