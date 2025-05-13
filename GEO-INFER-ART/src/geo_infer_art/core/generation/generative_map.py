"""
GenerativeMap module for creating generative art from geospatial data.
"""

import os
from typing import Dict, List, Optional, Tuple, Union

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

from geo_infer_art.core.aesthetics import ColorPalette


class GenerativeMap:
    """
    A class for creating generative art from geospatial data.
    
    The GenerativeMap class provides methods for transforming geospatial data
    into artistic and abstract visualizations using various generative algorithms.
    
    Attributes:
        data: The underlying data used for generation
        metadata: Additional information about the data source
        image: The generated image as a numpy array
    """
    
    def __init__(
        self,
        data: Optional[np.ndarray] = None,
        metadata: Optional[Dict] = None,
    ):
        """
        Initialize a GenerativeMap object.
        
        Args:
            data: Base data used for generation
            metadata: Information about the data source
        """
        self.data = data
        self.metadata = metadata or {}
        self.image = None
        self._figure = None
        self._ax = None
        
    @classmethod
    def from_elevation(
        cls,
        region: Union[str, np.ndarray, Tuple[float, float, float, float]],
        resolution: int = 512,
        abstraction_level: float = 0.5,
        style: str = "contour",
    ) -> 'GenerativeMap':
        """
        Create generative art from elevation data.
        
        Args:
            region: Region name, custom elevation data, or bounding box coordinates
            resolution: Resolution of the output image
            abstraction_level: Level of abstraction (0.0 to 1.0)
            style: Style of the generative art ("contour", "flow", "particles", etc.)
            
        Returns:
            A new GenerativeMap object with generated art
            
        Raises:
            ValueError: If the region is invalid or the data cannot be retrieved
        """
        # Initialize the object
        gen_map = cls()
        
        # Load elevation data
        if isinstance(region, str):
            # Get elevation data for a named region
            elevation_data = cls._get_region_elevation(region, resolution)
            gen_map.metadata["region"] = region
        elif isinstance(region, np.ndarray):
            # Use provided elevation data
            elevation_data = region
            gen_map.metadata["region"] = "custom"
        elif isinstance(region, tuple) and len(region) == 4:
            # Get elevation data for a bounding box (min_lon, min_lat, max_lon, max_lat)
            elevation_data = cls._get_bbox_elevation(region, resolution)
            gen_map.metadata["region"] = f"bbox_{region}"
        else:
            raise ValueError(
                "Invalid region parameter. Expected region name, "
                "elevation array, or bounding box coordinates."
            )
            
        gen_map.data = elevation_data
        gen_map.metadata["data_type"] = "elevation"
        gen_map.metadata["abstraction_level"] = abstraction_level
        gen_map.metadata["style"] = style
        
        # Generate art based on style
        if style == "contour":
            gen_map._generate_contour_art(abstraction_level)
        elif style == "flow":
            gen_map._generate_flow_art(abstraction_level)
        elif style == "particles":
            gen_map._generate_particle_art(abstraction_level)
        elif style == "contour_flow":
            gen_map._generate_contour_flow_art(abstraction_level)
        else:
            raise ValueError(
                f"Unsupported style: {style}. Supported styles: "
                "contour, flow, particles, contour_flow"
            )
            
        return gen_map
    
    @staticmethod
    def _get_region_elevation(region: str, resolution: int = 512) -> np.ndarray:
        """
        Get elevation data for a named region.
        
        Args:
            region: Name of the region (e.g., "grand_canyon", "everest", "alps")
            resolution: Resolution of the output data
            
        Returns:
            Elevation data as a 2D numpy array
            
        Raises:
            ValueError: If the region is not supported or data can't be retrieved
        """
        # For demo purposes, generate synthetic elevation data
        # In a real implementation, this would fetch actual elevation data
        
        known_regions = {
            "grand_canyon": (36.0544, -112.2583, 30),  # lat, lon, elevation variation scale
            "everest": (27.9881, 86.9250, 100),
            "alps": (45.8333, 6.8667, 40),
            "mariana_trench": (11.3333, 142.2333, -80),
            "sahara": (23.4162, 25.6628, 5),
            "amazon": (-3.4653, -62.2159, 10),
            "great_barrier_reef": (-18.2871, 147.6992, -15),
        }
        
        if region not in known_regions:
            raise ValueError(
                f"Unknown region: {region}. Supported regions: "
                f"{', '.join(known_regions.keys())}"
            )
            
        # Get parameters for the region
        lat, lon, scale = known_regions[region]
        
        # Generate a fractal terrain using Perlin noise
        # (simplified approximation for demonstration)
        x = np.linspace(0, 10, resolution)
        y = np.linspace(0, 10, resolution)
        X, Y = np.meshgrid(x, y)
        
        # Create multi-scale noise for natural-looking terrain
        elevation = np.zeros((resolution, resolution))
        for octave in range(1, 7):
            frequency = 2 ** octave
            amplitude = 1.0 / frequency
            elevation += amplitude * np.sin(X * frequency * 0.3) * np.cos(Y * frequency * 0.3)
            
        # Scale to make the terrain more pronounced for certain regions
        elevation = elevation * scale
        
        # Add some random variation
        elevation += np.random.normal(0, abs(scale/20), elevation.shape)
        
        return elevation
    
    @staticmethod
    def _get_bbox_elevation(
        bbox: Tuple[float, float, float, float],
        resolution: int = 512
    ) -> np.ndarray:
        """
        Get elevation data for a bounding box.
        
        Args:
            bbox: Bounding box coordinates (min_lon, min_lat, max_lon, max_lat)
            resolution: Resolution of the output data
            
        Returns:
            Elevation data as a 2D numpy array
            
        Raises:
            ValueError: If the bounding box is invalid or data can't be retrieved
        """
        # For demo purposes, generate synthetic elevation data
        # In a real implementation, this would fetch actual elevation data
        
        min_lon, min_lat, max_lon, max_lat = bbox
        
        # Validate bbox
        if min_lon >= max_lon or min_lat >= max_lat:
            raise ValueError(
                "Invalid bounding box. Ensure min values are less than max values."
            )
            
        # Calculate center and scale for terrain generation
        center_lat = (min_lat + max_lat) / 2
        center_lon = (min_lon + max_lon) / 2
        
        # Scale based on the size of the bounding box
        # Larger areas have gentler terrain variation
        scale = 20 * (1 / (max(max_lon - min_lon, max_lat - min_lat) + 0.1))
        
        # Generate a fractal terrain using Perlin noise
        x = np.linspace(min_lon, max_lon, resolution)
        y = np.linspace(min_lat, max_lat, resolution)
        X, Y = np.meshgrid(x, y)
        
        # Create multi-scale noise
        elevation = np.zeros((resolution, resolution))
        for octave in range(1, 7):
            frequency = 2 ** octave
            amplitude = 1.0 / frequency
            elevation += amplitude * np.sin(X * frequency) * np.cos(Y * frequency)
            
        # Scale the terrain
        elevation = elevation * scale * 50
        
        # Add some random variation
        elevation += np.random.normal(0, scale, elevation.shape)
        
        return elevation
    
    def _generate_contour_art(self, abstraction_level: float = 0.5) -> None:
        """
        Generate contour-based art from elevation data.
        
        Args:
            abstraction_level: Level of abstraction (0.0 to 1.0)
        """
        if self.data is None:
            raise ValueError("No data available for generation.")
        
        # Determine number of contour levels based on abstraction
        # Higher abstraction means fewer contours
        max_contours = 50
        min_contours = 5
        n_contours = int(max_contours - abstraction_level * (max_contours - min_contours))
        
        # Create a figure for the contour plot
        fig, ax = plt.subplots(figsize=(10, 10), facecolor='white')
        
        # Get a colormap based on the abstraction level
        if abstraction_level < 0.3:
            cmap_name = "earth"
        elif abstraction_level < 0.7:
            cmap_name = "autumn"
        else:
            cmap_name = "ocean"
            
        palette = ColorPalette.get_palette(cmap_name)
        
        # Create contour plot
        contour = ax.contourf(
            self.data,
            levels=n_contours,
            cmap=palette.cmap,
            alpha=0.7,
        )
        
        # Add contour lines with varying linewidth
        line_contour = ax.contour(
            self.data,
            levels=n_contours // 2,
            colors='black',
            linewidths=0.5 + abstraction_level,
            alpha=0.6 + 0.4 * abstraction_level,
        )
        
        # Remove axes for artistic effect
        ax.set_axis_off()
        
        # Set tight layout
        plt.tight_layout()
        
        # Store the figure and convert to image
        self._figure = fig
        self._ax = ax
        
        # Convert matplotlib figure to image array
        self._figure_to_image()
        
    def _generate_flow_art(self, abstraction_level: float = 0.5) -> None:
        """
        Generate flow-based art from elevation data.
        
        Args:
            abstraction_level: Level of abstraction (0.0 to 1.0)
        """
        if self.data is None:
            raise ValueError("No data available for generation.")
        
        # Calculate gradient of the elevation data
        gradient_y, gradient_x = np.gradient(self.data)
        
        # Normalize gradients
        magnitude = np.sqrt(gradient_x**2 + gradient_y**2)
        gradient_x = gradient_x / (magnitude + 1e-8)  # Avoid division by zero
        gradient_y = gradient_y / (magnitude + 1e-8)
        
        # Determine parameters based on abstraction level
        density = 1.0 - abstraction_level  # Higher abstraction means lower density
        line_width = 0.5 + abstraction_level  # Higher abstraction means thicker lines
        
        # Create a figure
        fig, ax = plt.subplots(figsize=(10, 10), facecolor='black')
        
        # Get a colormap based on the abstraction level
        if abstraction_level < 0.3:
            cmap_name = "viridis"
        elif abstraction_level < 0.7:
            cmap_name = "sunset"
        else:
            cmap_name = "forest"
            
        palette = ColorPalette.get_palette(cmap_name)
        
        # Create stream plot
        n_points = int(30 * density)
        seed_points = np.random.rand(n_points, 2)
        
        # Scale seed points to data dimensions
        seed_points[:, 0] *= self.data.shape[0]
        seed_points[:, 1] *= self.data.shape[1]
        
        # Create streamplot
        stream = ax.streamplot(
            np.arange(0, self.data.shape[1]),
            np.arange(0, self.data.shape[0]),
            gradient_x,
            gradient_y,
            color=magnitude,
            linewidth=line_width,
            cmap=palette.cmap,
            density=density,
            arrowsize=0,  # No arrows for artistic look
            start_points=seed_points,
        )
        
        # Remove axes for artistic effect
        ax.set_axis_off()
        
        # Set aspect ratio and limits
        ax.set_aspect('equal')
        ax.set_xlim(0, self.data.shape[1])
        ax.set_ylim(0, self.data.shape[0])
        
        # Set tight layout
        plt.tight_layout()
        
        # Store the figure and convert to image
        self._figure = fig
        self._ax = ax
        
        # Convert matplotlib figure to image array
        self._figure_to_image()
        
    def _generate_particle_art(self, abstraction_level: float = 0.5) -> None:
        """
        Generate particle-based art from elevation data.
        
        Args:
            abstraction_level: Level of abstraction (0.0 to 1.0)
        """
        if self.data is None:
            raise ValueError("No data available for generation.")
        
        # Create a figure
        fig, ax = plt.subplots(figsize=(10, 10), facecolor='black')
        
        # Determine number of particles based on abstraction
        max_particles = 5000
        min_particles = 200
        n_particles = int(max_particles - abstraction_level * (max_particles - min_particles))
        
        # Get a colormap based on the abstraction level
        if abstraction_level < 0.3:
            cmap_name = "bright"
        elif abstraction_level < 0.7:
            cmap_name = "pastel"
        else:
            cmap_name = "grayscale"
            
        palette = ColorPalette.get_palette(cmap_name)
        
        # Scale data to 0-1 range
        data_min = np.min(self.data)
        data_max = np.max(self.data)
        data_range = data_max - data_min
        normalized_data = (self.data - data_min) / data_range if data_range > 0 else self.data * 0
        
        # Generate random positions weighted by elevation
        # Higher elevations have more particles
        probs = normalized_data.flatten() ** (2 - abstraction_level)
        probs = probs / np.sum(probs)
        
        indices = np.random.choice(
            np.arange(normalized_data.size),
            size=n_particles,
            p=probs
        )
        
        y_coords, x_coords = np.unravel_index(indices, normalized_data.shape)
        
        # Map elevation values to sizes
        sizes = normalized_data[y_coords, x_coords] * 20 + 1
        
        # Map elevation values to colors
        color_indices = (normalized_data[y_coords, x_coords] * 255).astype(int)
        colors = [palette.colors[min(i, len(palette.colors)-1)] for i in color_indices]
        
        # Create scatter plot
        scatter = ax.scatter(
            x_coords,
            y_coords,
            c=colors,
            s=sizes,
            alpha=0.7,
            edgecolor='none',
        )
        
        # Remove axes for artistic effect
        ax.set_axis_off()
        
        # Set aspect ratio and limits
        ax.set_aspect('equal')
        ax.set_xlim(0, self.data.shape[1])
        ax.set_ylim(0, self.data.shape[0])
        
        # Set tight layout
        plt.tight_layout()
        
        # Store the figure and convert to image
        self._figure = fig
        self._ax = ax
        
        # Convert matplotlib figure to image array
        self._figure_to_image()
        
    def _generate_contour_flow_art(self, abstraction_level: float = 0.5) -> None:
        """
        Generate a combination of contour and flow art from elevation data.
        
        Args:
            abstraction_level: Level of abstraction (0.0 to 1.0)
        """
        if self.data is None:
            raise ValueError("No data available for generation.")
        
        # Create a figure
        fig, ax = plt.subplots(figsize=(10, 10), facecolor='black')
        
        # Get color palettes
        palette1 = ColorPalette.get_palette("ocean")
        palette2 = ColorPalette.get_palette("autumn")
        
        # Determine number of contour levels based on abstraction
        n_contours = int(50 - abstraction_level * 40)
        
        # Calculate gradient for flow
        gradient_y, gradient_x = np.gradient(self.data)
        
        # Create contour plot with reduced opacity
        contour = ax.contourf(
            self.data,
            levels=n_contours,
            cmap=palette1.cmap,
            alpha=0.3,
        )
        
        # Add flow on top of contours
        magnitude = np.sqrt(gradient_x**2 + gradient_y**2)
        
        # Normalize gradients
        gradient_x = gradient_x / (magnitude + 1e-8)
        gradient_y = gradient_y / (magnitude + 1e-8)
        
        # Create streamplot with reduced density
        stream = ax.streamplot(
            np.arange(0, self.data.shape[1]),
            np.arange(0, self.data.shape[0]),
            gradient_x,
            gradient_y,
            color=magnitude,
            linewidth=1.0 + abstraction_level,
            cmap=palette2.cmap,
            density=0.8 - 0.5 * abstraction_level,
            arrowsize=0,
        )
        
        # Remove axes for artistic effect
        ax.set_axis_off()
        
        # Set aspect ratio and limits
        ax.set_aspect('equal')
        ax.set_xlim(0, self.data.shape[1])
        ax.set_ylim(0, self.data.shape[0])
        
        # Set tight layout
        plt.tight_layout()
        
        # Store the figure and convert to image
        self._figure = fig
        self._ax = ax
        
        # Convert matplotlib figure to image array
        self._figure_to_image()
        
    def _figure_to_image(self) -> None:
        """Convert the matplotlib figure to a numpy image array."""
        import io
        
        if self._figure is None:
            return
            
        # Save figure to a buffer
        buf = io.BytesIO()
        self._figure.savefig(buf, format='png', dpi=300, bbox_inches='tight')
        buf.seek(0)
        
        # Load buffer with PIL and convert to numpy array
        img = Image.open(buf)
        self.image = np.array(img)
        
    def save(self, output_path: str) -> str:
        """
        Save the generated art to a file.
        
        Args:
            output_path: Path where the file should be saved
            
        Returns:
            The path to the saved file
            
        Raises:
            ValueError: If no image has been generated
        """
        if self.image is None:
            raise ValueError("No image generated. Generate art first.")
            
        directory = os.path.dirname(output_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
            
        # Convert numpy array to PIL Image and save
        img = Image.fromarray(self.image)
        img.save(output_path)
        
        return output_path
        
    def show(self) -> None:
        """
        Display the generated art.
        
        Raises:
            ValueError: If no image has been generated
        """
        if self._figure is None:
            raise ValueError("No image generated. Generate art first.")
            
        plt.figure(self._figure.number)
        plt.show()
        
    def __repr__(self) -> str:
        """Return a string representation of the GenerativeMap object."""
        if self.data is None:
            return "GenerativeMap(No data loaded)"
            
        style = self.metadata.get("style", "unknown")
        region = self.metadata.get("region", "unknown")
        
        return f"GenerativeMap(style='{style}', region='{region}')" 