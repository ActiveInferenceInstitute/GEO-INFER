"""
Color palette module for managing and applying color schemes in geospatial visualizations.
"""

from typing import Dict, List, Optional, Tuple, Union

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap


class ColorPalette:
    """
    A class for creating and managing color palettes for artistic geospatial visualizations.
    
    The ColorPalette class provides methods for generating, manipulating, and
    applying color schemes based on color theory and aesthetic principles.
    
    Attributes:
        name: The name of the color palette
        colors: List of colors in the palette
        cmap: Matplotlib colormap generated from the palette
    """
    
    # Predefined color palettes
    PREDEFINED_PALETTES = {
        "viridis": ["#440154", "#414487", "#2a788e", "#22a884", "#7ad151", "#fde725"],
        "pastel": ["#a1c9f4", "#ffb482", "#8de5a1", "#ff9f9b", "#d0bbff", "#debb9b"],
        "earth": ["#5A3A29", "#614124", "#996633", "#C19A6B", "#A3C09A", "#87CEEB"],
        "bright": ["#ff00ff", "#00ffff", "#ffff00", "#ff0000", "#00ff00", "#0000ff"],
        "grayscale": ["#000000", "#333333", "#666666", "#999999", "#cccccc", "#ffffff"],
        "blue": ["#081d58", "#253494", "#225ea8", "#1d91c0", "#41b6c4", "#c7e9b4"],
        "autumn": ["#8B0000", "#FF8C00", "#FFD700", "#556B2F", "#8B4513", "#A0522D"],
        "sunset": ["#12355B", "#420039", "#FF9E00", "#FF4000", "#3A0088", "#420039"],
        "ocean": ["#006699", "#66CCCC", "#9999CC", "#006666", "#3399CC", "#003366"],
        "forest": ["#1b4332", "#2d6a4f", "#40916c", "#52b788", "#74c69d", "#b7e4c7"],
    }
    
    def __init__(
        self, 
        name: str = "viridis", 
        colors: Optional[List[str]] = None,
        n_colors: int = 256,
    ):
        """
        Initialize a ColorPalette object.
        
        Args:
            name: Name of the palette
            colors: List of color codes (hex, RGB, or named)
            n_colors: Number of colors to generate in the colormap
            
        Raises:
            ValueError: If the palette name is invalid and no colors are provided
        """
        self.name = name
        
        # Use provided colors or get from predefined palettes
        if colors is not None:
            self.colors = colors
        elif name in self.PREDEFINED_PALETTES:
            self.colors = self.PREDEFINED_PALETTES[name]
        else:
            raise ValueError(
                f"Invalid palette name: {name}. Available predefined palettes: "
                f"{', '.join(self.PREDEFINED_PALETTES.keys())}"
            )
            
        # Create matplotlib colormap
        self.cmap = self._create_colormap(n_colors)
    
    @classmethod
    def get_palette(cls, name: str) -> 'ColorPalette':
        """
        Get a predefined color palette by name.
        
        Args:
            name: Name of the predefined palette
            
        Returns:
            A ColorPalette object with the requested palette
            
        Raises:
            ValueError: If the palette name is not recognized
        """
        if name in cls.PREDEFINED_PALETTES:
            return cls(name=name, colors=cls.PREDEFINED_PALETTES[name])
        else:
            raise ValueError(
                f"Unknown palette: {name}. Available palettes: "
                f"{', '.join(cls.PREDEFINED_PALETTES.keys())}"
            )
    
    @classmethod
    def from_color_theory(
        cls, 
        base_color: str, 
        scheme: str = "complementary",
        n_colors: int = 6,
    ) -> 'ColorPalette':
        """
        Create a palette based on color theory relationships.
        
        Args:
            base_color: The base color to build the palette from
            scheme: The color scheme to use (complementary, analogous, triadic, etc.)
            n_colors: Number of colors to generate
            
        Returns:
            A new ColorPalette object
            
        Raises:
            ValueError: If the scheme is not supported
        """
        import colorsys
        from matplotlib.colors import to_rgb, to_hex
        
        # Convert base color to HSV
        r, g, b = to_rgb(base_color)
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        
        colors = []
        name = f"{scheme}_{base_color.replace('#', '')}"
        
        if scheme == "complementary":
            # Base color and its complement (180° apart on color wheel)
            colors.append(base_color)
            h_comp = (h + 0.5) % 1.0
            r_comp, g_comp, b_comp = colorsys.hsv_to_rgb(h_comp, s, v)
            colors.append(to_hex((r_comp, g_comp, b_comp)))
            
            # Add variations with different saturations and values
            for i in range(2, n_colors):
                h_var = h if i % 2 == 0 else h_comp
                s_var = max(0.2, s - (0.15 * (i // 2)))
                v_var = min(0.9, v + (0.1 * (i // 2)))
                r_var, g_var, b_var = colorsys.hsv_to_rgb(h_var, s_var, v_var)
                colors.append(to_hex((r_var, g_var, b_var)))
                
        elif scheme == "analogous":
            # Base color and colors adjacent to it on the color wheel
            angle = 0.08  # About 30° in the HSV color wheel
            
            for i in range(n_colors):
                h_temp = (h + (angle * (i - n_colors // 2))) % 1.0
                r_temp, g_temp, b_temp = colorsys.hsv_to_rgb(h_temp, s, v)
                colors.append(to_hex((r_temp, g_temp, b_temp)))
                
        elif scheme == "triadic":
            # Three colors evenly spaced around the color wheel
            for i in range(3):
                h_temp = (h + (i / 3)) % 1.0
                r_temp, g_temp, b_temp = colorsys.hsv_to_rgb(h_temp, s, v)
                colors.append(to_hex((r_temp, g_temp, b_temp)))
                
            # Add variations with different saturations and values
            for i in range(3, n_colors):
                base_idx = i % 3
                h_var = (h + (base_idx / 3)) % 1.0
                s_var = max(0.2, s - (0.1 * (i // 3)))
                v_var = min(0.9, v + (0.1 * (i // 3)))
                r_var, g_var, b_var = colorsys.hsv_to_rgb(h_var, s_var, v_var)
                colors.append(to_hex((r_var, g_var, b_var)))
                
        elif scheme == "monochromatic":
            # Variations of the same hue with different saturations and values
            for i in range(n_colors):
                s_var = max(0.1, min(1.0, s - 0.7 + (i / (n_colors - 1)) * 0.7))
                v_var = max(0.3, min(1.0, v - 0.5 + (i / (n_colors - 1)) * 0.7))
                r_var, g_var, b_var = colorsys.hsv_to_rgb(h, s_var, v_var)
                colors.append(to_hex((r_var, g_var, b_var)))
                
        else:
            raise ValueError(
                f"Unsupported color scheme: {scheme}. "
                "Supported schemes: complementary, analogous, triadic, monochromatic"
            )
            
        return cls(name=name, colors=colors, n_colors=n_colors)
    
    @classmethod
    def from_image(cls, image_path: str, n_colors: int = 6) -> 'ColorPalette':
        """
        Extract a color palette from an image.
        
        Args:
            image_path: Path to the image file
            n_colors: Number of colors to extract
            
        Returns:
            A new ColorPalette with colors extracted from the image
            
        Raises:
            FileNotFoundError: If the image file doesn't exist
            ValueError: If the image can't be processed
        """
        try:
            from PIL import Image
            from sklearn.cluster import KMeans
            
            # Load and resize image for faster processing
            img = Image.open(image_path)
            img = img.resize((100, 100))
            img_array = np.array(img)
            
            # Reshape the image data for clustering
            pixels = img_array.reshape(-1, 3)
            
            # Use K-means clustering to find dominant colors
            kmeans = KMeans(n_clusters=n_colors, random_state=42)
            kmeans.fit(pixels)
            
            # Convert cluster centers to hex colors
            colors = []
            for center in kmeans.cluster_centers_:
                # Ensure RGB values are in 0-1 range
                rgb = tuple(np.clip(center / 255.0, 0, 1))
                hex_color = f"#{int(rgb[0]*255):02x}{int(rgb[1]*255):02x}{int(rgb[2]*255):02x}"
                colors.append(hex_color)
                
            # Create a name based on the image filename
            import os
            name = f"image_{os.path.basename(image_path)}"
            
            return cls(name=name, colors=colors, n_colors=n_colors)
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Image file not found: {image_path}")
        except Exception as e:
            raise ValueError(f"Failed to extract colors from image: {str(e)}") from e
    
    def _create_colormap(self, n_colors: int) -> LinearSegmentedColormap:
        """
        Create a matplotlib colormap from the palette colors.
        
        Args:
            n_colors: Number of colors to interpolate in the colormap
            
        Returns:
            A matplotlib LinearSegmentedColormap
        """
        return LinearSegmentedColormap.from_list(self.name, self.colors, N=n_colors)
    
    def show(self, figsize: Tuple[int, int] = (10, 2)) -> None:
        """
        Display the color palette.
        
        Args:
            figsize: Figure size (width, height) in inches
        """
        # Create a gradient display of the colormap
        gradient = np.linspace(0, 1, 256)
        gradient = np.vstack((gradient, gradient))
        
        fig, ax = plt.subplots(figsize=figsize)
        ax.imshow(gradient, aspect='auto', cmap=self.cmap)
        ax.set_title(f"Color Palette: {self.name}")
        ax.set_axis_off()
        
        # Show individual color swatches
        n_colors = len(self.colors)
        fig, ax = plt.subplots(figsize=figsize)
        for i, color in enumerate(self.colors):
            ax.add_patch(plt.Rectangle((i, 0), 1, 1, color=color))
            
        ax.set_xlim(0, n_colors)
        ax.set_ylim(0, 1)
        ax.set_title(f"Colors in Palette: {self.name}")
        ax.set_axis_off()
        
        plt.tight_layout()
        plt.show()
        
    def invert(self) -> 'ColorPalette':
        """
        Create a new palette with inverted colors.
        
        Returns:
            A new ColorPalette with inverted colors
        """
        inverted_colors = self.colors.copy()
        inverted_colors.reverse()
        return ColorPalette(
            name=f"{self.name}_inverted",
            colors=inverted_colors,
        )
    
    def __repr__(self) -> str:
        """Return a string representation of the ColorPalette object."""
        return f"ColorPalette(name='{self.name}', colors={len(self.colors)})" 