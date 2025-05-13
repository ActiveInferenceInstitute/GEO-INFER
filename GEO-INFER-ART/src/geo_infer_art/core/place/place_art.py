"""
PlaceArt module for creating art based on specific locations and places.
"""

import os
from typing import Dict, List, Optional, Tuple, Union

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

from geo_infer_art.core.aesthetics import ColorPalette, StyleTransfer
from geo_infer_art.core.generation import ProceduralArt


class PlaceArt:
    """
    A class for creating art based on the unique characteristics of geographic locations.
    
    The PlaceArt class provides methods for generating artistic representations
    inspired by the features, culture, and atmosphere of specific places.
    
    Attributes:
        location: Information about the geographic location
        data: Geospatial data for the location
        image: The generated artistic representation
    """
    
    def __init__(
        self,
        location: Optional[Dict] = None,
        data: Optional[gpd.GeoDataFrame] = None,
    ):
        """
        Initialize a PlaceArt object.
        
        Args:
            location: Dictionary with location information (name, coordinates, etc.)
            data: GeoDataFrame with geospatial data for the location
        """
        self.location = location or {}
        self.data = data
        self.image = None
        self._figure = None
    
    @classmethod
    def from_coordinates(
        cls,
        lat: float,
        lon: float,
        name: Optional[str] = None,
        radius_km: float = 1.0,
        style: str = "abstract",
    ) -> 'PlaceArt':
        """
        Create place-based art from geographic coordinates.
        
        Args:
            lat: Latitude (-90 to 90)
            lon: Longitude (-180 to 180)
            name: Optional name of the location
            radius_km: Radius in kilometers to consider around the point
            style: Artistic style to apply ("abstract", "topographic", "cultural", etc.)
            
        Returns:
            A new PlaceArt object with generated art
            
        Raises:
            ValueError: If coordinates are invalid
        """
        # Validate coordinates
        if not -90 <= lat <= 90:
            raise ValueError("Latitude must be between -90 and 90 degrees.")
            
        if not -180 <= lon <= 180:
            raise ValueError("Longitude must be between -180 and 180 degrees.")
            
        # Create location dictionary
        location = {
            "name": name or f"Location {lat:.4f}, {lon:.4f}",
            "coordinates": (lat, lon),
            "radius_km": radius_km,
            "style": style,
        }
        
        # Create PlaceArt object
        place_art = cls(location=location)
        
        # Generate art based on style
        place_art._generate_art()
        
        return place_art
    
    @classmethod
    def from_place_name(
        cls,
        place_name: str,
        style: str = "abstract",
        include_data: bool = False,
    ) -> 'PlaceArt':
        """
        Create place-based art from a named location.
        
        Args:
            place_name: Name of the place (city, country, landmark, etc.)
            style: Artistic style to apply
            include_data: Whether to fetch and include geospatial data
            
        Returns:
            A new PlaceArt object with generated art
            
        Raises:
            ValueError: If the place cannot be found or geocoded
        """
        # For demonstration, we'll use some preset coordinates for well-known places
        # In a real implementation, this would use a geocoding service
        known_places = {
            "new york": (40.7128, -74.0060),
            "paris": (48.8566, 2.3522),
            "tokyo": (35.6762, 139.6503),
            "cairo": (30.0444, 31.2357),
            "sydney": (-33.8688, 151.2093),
            "rio de janeiro": (-22.9068, -43.1729),
            "cape town": (-33.9249, 18.4241),
            "moscow": (55.7558, 37.6173),
            "mumbai": (19.0760, 72.8777),
            "beijing": (39.9042, 116.4074),
        }
        
        place_lower = place_name.lower()
        if place_lower in known_places:
            lat, lon = known_places[place_lower]
        else:
            # Simulate geocoding with random coordinates
            # In a real implementation, use a geocoding service
            import random
            random.seed(hash(place_name))  # Deterministic based on name
            lat = random.uniform(-80, 80)
            lon = random.uniform(-179, 179)
        
        # Create location dictionary
        location = {
            "name": place_name,
            "coordinates": (lat, lon),
            "style": style,
            "radius_km": 5.0,  # Default radius for named places
        }
        
        # Create PlaceArt object
        place_art = cls(location=location)
        
        # Generate art
        place_art._generate_art()
        
        return place_art
    
    def _generate_art(self) -> None:
        """
        Generate art based on the location and specified style.
        """
        if not self.location:
            raise ValueError("Location information is required for art generation.")
            
        style = self.location.get("style", "abstract")
        coordinates = self.location.get("coordinates")
        
        if not coordinates:
            raise ValueError("Location coordinates are required for art generation.")
            
        lat, lon = coordinates
        
        if style == "abstract":
            self._generate_abstract_art(lat, lon)
        elif style == "topographic":
            self._generate_topographic_art(lat, lon)
        elif style == "cultural":
            self._generate_cultural_art(lat, lon)
        elif style == "mixed_media":
            self._generate_mixed_media_art(lat, lon)
        else:
            # Default to abstract if style not recognized
            self._generate_abstract_art(lat, lon)
            
    def _generate_abstract_art(self, lat: float, lon: float) -> None:
        """
        Generate abstract art based on location coordinates.
        
        Args:
            lat: Latitude
            lon: Longitude
        """
        # Use ProceduralArt with noise field algorithm
        art = ProceduralArt.from_geo_coordinates(
            lat=lat,
            lon=lon,
            algorithm="noise_field",
            additional_params={
                "octaves": 8,
                "persistence": 0.6,
                "lacunarity": 2.2,
                "scale": 120.0,
                # Use color palette based on latitude (warmer for lower latitudes)
                "color_palette": "sunset" if abs(lat) < 30 else 
                                "ocean" if abs(lat) >= 60 else "forest",
            }
        )
        
        # Store the image
        self.image = art.image
        
    def _generate_topographic_art(self, lat: float, lon: float) -> None:
        """
        Generate topographic-inspired art based on location coordinates.
        
        Args:
            lat: Latitude
            lon: Longitude
        """
        from geo_infer_art.core.generation import GenerativeMap
        
        # Create a bounding box around the coordinates
        # Approximate 1 degree as 111 km at the equator
        radius_deg = self.location.get("radius_km", 1.0) / 111.0
        # Adjust for longitude compression at higher latitudes
        lon_radius = radius_deg / max(0.1, np.cos(np.radians(abs(lat))))
        
        bbox = (lon - lon_radius, lat - radius_deg, lon + lon_radius, lat + radius_deg)
        
        # Use GenerativeMap to create topographic art
        gen_map = GenerativeMap.from_elevation(
            region=bbox,
            resolution=800,
            abstraction_level=0.7,
            style="contour_flow",
        )
        
        # Store the image
        self.image = gen_map.image
        
    def _generate_cultural_art(self, lat: float, lon: float) -> None:
        """
        Generate culture-inspired art based on location coordinates.
        
        Args:
            lat: Latitude
            lon: Longitude
        """
        # For demonstration, we'll use L-systems with parameters that vary by
        # geographic region (this is a simplification of cultural patterns)
        
        # Determine art parameters based on geographic region
        # This is a very simplified model that associates different 
        # pattern types with different regions of the world
        
        # Normalize coordinates to 0-1 range
        norm_lat = (lat + 90) / 180  
        norm_lon = (lon + 180) / 360
        
        # Create region-specific parameters
        if lon > -30 and lon < 60 and lat > 0 and lat < 40:
            # Europe/Middle East/North Africa - geometric patterns
            params = {
                "algorithm": "l_system",
                "axiom": "F+F+F+F",
                "rules": {"F": "FF+F+F+FF+F+FF-F"},
                "iterations": 3,
                "angle": 90,
                "color_palette": "sunset",
            }
        elif lon > 60 and lon < 150 and lat > 10 and lat < 50:
            # Asia - flowing organic patterns
            params = {
                "algorithm": "l_system",
                "axiom": "F",
                "rules": {"F": "FF+[+F-F-F]-[-F+F+F]"},
                "iterations": 4,
                "angle": 25,
                "color_palette": "ocean",
            }
        elif lon > -120 and lon < -30 and lat > 15 and lat < 50:
            # North America - angular and geometric
            params = {
                "algorithm": "voronoi",
                "num_points": 40,
                "point_clustering": 0.3,
                "edge_width": 1.2,
                "color_palette": "earth",
            }
        elif lat < 0:
            # Southern Hemisphere - more organic forms
            params = {
                "algorithm": "reaction_diffusion",
                "iterations": 60,
                "feed_rate": 0.037,
                "kill_rate": 0.06,
                "color_palette": "forest",
            }
        else:
            # Default - abstract noise
            params = {
                "algorithm": "noise_field",
                "octaves": 6,
                "persistence": 0.5,
                "color_palette": "pastel",
            }
            
        # Add geographic seed
        params["seed"] = int((norm_lat * 1000) + (norm_lon * 10000))
        
        # Create the procedural art
        art = ProceduralArt(
            algorithm=params.pop("algorithm"),
            params=params,
            resolution=(800, 800),
        )
        
        # Generate the art
        art.generate()
        
        # Store the image
        self.image = art.image
        
    def _generate_mixed_media_art(self, lat: float, lon: float) -> None:
        """
        Generate mixed media art combining multiple techniques.
        
        Args:
            lat: Latitude
            lon: Longitude
        """
        # First generate a base layer with noise field
        base_art = ProceduralArt.from_geo_coordinates(
            lat=lat,
            lon=lon,
            algorithm="noise_field",
            additional_params={
                "octaves": 6,
                "persistence": 0.5,
                "color_palette": "autumn",
            }
        )
        
        # Then add a cultural pattern layer
        # Simplified cultural pattern selection based on region
        if lon > 0:  # Eastern Hemisphere
            pattern_art = ProceduralArt(
                algorithm="l_system",
                params={
                    "axiom": "F",
                    "rules": {"F": "F+F-F-F+F"}, 
                    "iterations": 3,
                    "angle": 72,
                    "line_width": 0.8,
                    "seed": int(lat * 100 + lon),
                    "color_palette": "ocean",
                },
                resolution=(800, 800),
            )
        else:  # Western Hemisphere
            pattern_art = ProceduralArt(
                algorithm="voronoi",
                params={
                    "num_points": 30,
                    "point_clustering": 0.4,
                    "edge_width": 1.0,
                    "seed": int(lat * 100 + lon),
                    "color_palette": "forest",
                },
                resolution=(800, 800),
            )
            
        pattern_art.generate()
        
        # Combine the images with alpha blending
        if base_art.image is not None and pattern_art.image is not None:
            base_img = Image.fromarray(base_art.image)
            pattern_img = Image.fromarray(pattern_art.image)
            
            # Resize if needed
            base_width, base_height = base_img.size
            pattern_img = pattern_img.resize((base_width, base_height))
            
            # Convert to RGBA if not already
            if base_img.mode != 'RGBA':
                base_img = base_img.convert('RGBA')
            if pattern_img.mode != 'RGBA':
                pattern_img = pattern_img.convert('RGBA')
                
            # Blend images
            blended = Image.blend(base_img, pattern_img, alpha=0.7)
            
            # Store the result
            self.image = np.array(blended)
        else:
            # Fallback to base image if blending fails
            self.image = base_art.image
    
    def add_metadata_overlay(self, position: str = "bottom", opacity: float = 0.7) -> 'PlaceArt':
        """
        Add location metadata as an overlay on the artwork.
        
        Args:
            position: Position of the overlay ("top", "bottom", "left", "right")
            opacity: Opacity of the overlay (0.0 to 1.0)
            
        Returns:
            Self for method chaining
            
        Raises:
            ValueError: If no image has been generated
        """
        if self.image is None:
            raise ValueError("No image has been generated.")
            
        # Get location name
        location_name = self.location.get("name", "Unknown Location")
        lat, lon = self.location.get("coordinates", (0, 0))
        
        # Create a PIL image from the numpy array
        img = Image.fromarray(self.image)
        width, height = img.size
        
        # Create a new image with text overlay
        from PIL import ImageDraw, ImageFont
        
        # Create a drawing context
        draw = ImageDraw.Draw(img)
        
        # Try to get a font
        try:
            # Try to load a nice font
            font = ImageFont.truetype("Arial", 24)
        except IOError:
            # Fallback to default font
            font = ImageFont.load_default()
            
        # Create metadata text
        metadata_text = f"{location_name}\nLat: {lat:.4f}, Lon: {lon:.4f}"
        
        # Calculate text size
        text_size = draw.textsize(metadata_text, font=font)
        
        # Determine position
        if position == "bottom":
            text_position = ((width - text_size[0]) // 2, height - text_size[1] - 20)
        elif position == "top":
            text_position = ((width - text_size[0]) // 2, 20)
        elif position == "left":
            text_position = (20, (height - text_size[1]) // 2)
        elif position == "right":
            text_position = (width - text_size[0] - 20, (height - text_size[1]) // 2)
        else:
            text_position = ((width - text_size[0]) // 2, height - text_size[1] - 20)
            
        # Create semi-transparent background for text
        bg_padding = 10
        bg_bounds = (
            text_position[0] - bg_padding,
            text_position[1] - bg_padding,
            text_position[0] + text_size[0] + bg_padding,
            text_position[1] + text_size[1] + bg_padding,
        )
        
        # Draw background
        draw.rectangle(bg_bounds, fill=(0, 0, 0, int(255 * opacity)))
        
        # Draw text
        draw.text(text_position, metadata_text, fill=(255, 255, 255, 255), font=font)
        
        # Update the image
        self.image = np.array(img)
        
        return self
        
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
        if self.image is None:
            raise ValueError("No image generated. Generate art first.")
            
        # Create a new figure
        plt.figure(figsize=(10, 10))
        plt.imshow(self.image)
        plt.axis('off')
        plt.tight_layout()
        plt.show()
        
    def __repr__(self) -> str:
        """Return a string representation of the PlaceArt object."""
        location_name = self.location.get("name", "Unknown Location")
        style = self.location.get("style", "unknown")
        
        return f"PlaceArt(location='{location_name}', style='{style}')" 