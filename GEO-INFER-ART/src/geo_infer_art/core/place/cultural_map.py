"""
CulturalMap module for creating maps that integrate cultural and historical contexts.
"""

import os
from typing import Dict, List, Optional, Tuple, Union

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from geo_infer_art.core.aesthetics import ColorPalette, StyleTransfer
from geo_infer_art.core.visualization import GeoArt


class CulturalMap:
    """
    A class for creating maps that integrate cultural and historical contexts of places.
    
    The CulturalMap class provides methods for generating maps that incorporate
    cultural elements, symbols, patterns, and historical data into geographic
    representations.
    
    Attributes:
        data: GeoDataFrame with geospatial and cultural data
        metadata: Additional information about the data and cultural context
        image: The generated map as a numpy array
    """
    
    def __init__(
        self,
        data: Optional[gpd.GeoDataFrame] = None,
        metadata: Optional[Dict] = None,
    ):
        """
        Initialize a CulturalMap object.
        
        Args:
            data: GeoDataFrame with geospatial and cultural data
            metadata: Additional information about the data and cultural context
        """
        self.data = data
        self.metadata = metadata or {}
        self.image = None
        self._figure = None
        self._cultural_elements = []
        
    @classmethod
    def from_region(
        cls,
        region_name: str,
        cultural_theme: str = "historical",
        style: str = "artistic",
    ) -> 'CulturalMap':
        """
        Create a cultural map for a specific named region.
        
        Args:
            region_name: Name of the region (country, city, cultural area)
            cultural_theme: Cultural theme to highlight ("historical", "linguistic", etc.)
            style: Visual style for the map
            
        Returns:
            A new CulturalMap object with generated map
            
        Raises:
            ValueError: If the region cannot be found
        """
        # Simplified region data
        # In a real implementation, this would fetch actual data for the region
        known_regions = {
            "mediterranean": {
                "bbox": (3.0, 30.0, 37.0, 47.0),
                "cultural_data": {
                    "historical": [
                        {"name": "Ancient Rome", "location": (12.4964, 41.9028), "period": "27 BCE-476 CE", "significance": "Empire"},
                        {"name": "Ancient Greece", "location": (23.7275, 37.9838), "period": "800-146 BCE", "significance": "Democracy"},
                        {"name": "Ancient Egypt", "location": (31.2357, 30.0444), "period": "3100-30 BCE", "significance": "Pyramid"},
                        {"name": "Carthage", "location": (10.1815, 36.8525), "period": "814-146 BCE", "significance": "Trade"},
                    ],
                    "linguistic": [
                        {"name": "Latin", "location": (12.4964, 41.9028), "family": "Indo-European", "script": "Latin"},
                        {"name": "Greek", "location": (23.7275, 37.9838), "family": "Indo-European", "script": "Greek"},
                        {"name": "Arabic", "location": (10.1815, 36.8525), "family": "Afro-Asiatic", "script": "Arabic"},
                    ],
                },
                "cultural_style": "classical",
            },
            "east_asia": {
                "bbox": (100.0, 20.0, 145.0, 45.0),
                "cultural_data": {
                    "historical": [
                        {"name": "Ancient China", "location": (116.4074, 39.9042), "period": "1600 BCE-1912 CE", "significance": "Empire"},
                        {"name": "Ancient Japan", "location": (139.6917, 35.6895), "period": "300 BCE-present", "significance": "Island nation"},
                        {"name": "Korea", "location": (126.9780, 37.5665), "period": "2333 BCE-present", "significance": "Peninsula"},
                    ],
                    "linguistic": [
                        {"name": "Mandarin", "location": (116.4074, 39.9042), "family": "Sino-Tibetan", "script": "Chinese"},
                        {"name": "Japanese", "location": (139.6917, 35.6895), "family": "Japonic", "script": "Kanji/Hiragana"},
                        {"name": "Korean", "location": (126.9780, 37.5665), "family": "Koreanic", "script": "Hangul"},
                    ],
                },
                "cultural_style": "east_asian",
            },
            "americas": {
                "bbox": (-125.0, 25.0, -65.0, 50.0),
                "cultural_data": {
                    "historical": [
                        {"name": "Maya", "location": (-90.5069, 19.5023), "period": "2000 BCE-1697 CE", "significance": "Calendar"},
                        {"name": "Aztec", "location": (-99.1332, 19.4326), "period": "1300-1521 CE", "significance": "Empire"},
                        {"name": "Inca", "location": (-72.5450, -13.1631), "period": "1438-1533 CE", "significance": "Roads"},
                    ],
                    "linguistic": [
                        {"name": "English", "location": (-98.5795, 39.8283), "family": "Indo-European", "script": "Latin"},
                        {"name": "Spanish", "location": (-99.1332, 19.4326), "family": "Indo-European", "script": "Latin"},
                        {"name": "Quechua", "location": (-72.5450, -13.1631), "family": "Quechuan", "script": "Latin"},
                    ],
                },
                "cultural_style": "indigenous",
            },
        }
        
        # Check if the region is known
        region_lower = region_name.lower()
        if region_lower not in known_regions:
            raise ValueError(
                f"Unknown region: {region_name}. Known regions: "
                f"{', '.join(known_regions.keys())}"
            )
            
        region_data = known_regions[region_lower]
        
        # Create metadata
        metadata = {
            "region_name": region_name,
            "bbox": region_data["bbox"],
            "cultural_theme": cultural_theme,
            "style": style,
            "cultural_style": region_data["cultural_style"],
        }
        
        # Get cultural data for the selected theme
        cultural_data = region_data["cultural_data"].get(cultural_theme, [])
        metadata["cultural_data"] = cultural_data
        
        # Create a simple GeoDataFrame for the region
        # In a real implementation, this would include actual geographic features
        import shapely.geometry as geometry
        
        # Create a bounding box polygon
        min_lon, min_lat, max_lon, max_lat = region_data["bbox"]
        bbox_polygon = geometry.box(min_lon, min_lat, max_lon, max_lat)
        
        # Create a GeoDataFrame with the region
        data = gpd.GeoDataFrame(
            {
                "name": [region_name],
                "geometry": [bbox_polygon],
                "cultural_style": [region_data["cultural_style"]],
            },
            crs="EPSG:4326",
        )
        
        # Create the CulturalMap object
        cultural_map = cls(data=data, metadata=metadata)
        
        # Generate the map
        cultural_map._generate_map()
        
        return cultural_map
    
    @classmethod
    def from_coordinates(
        cls,
        lat: float,
        lon: float,
        radius_km: float = 100.0,
        cultural_theme: str = "historical",
        style: str = "artistic",
    ) -> 'CulturalMap':
        """
        Create a cultural map centered on specific coordinates.
        
        Args:
            lat: Latitude (-90 to 90)
            lon: Longitude (-180 to 180)
            radius_km: Radius in kilometers to consider around the point
            cultural_theme: Cultural theme to highlight
            style: Visual style for the map
            
        Returns:
            A new CulturalMap object with generated map
            
        Raises:
            ValueError: If coordinates are invalid
        """
        # Validate coordinates
        if not -90 <= lat <= 90:
            raise ValueError("Latitude must be between -90 and 90 degrees.")
            
        if not -180 <= lon <= 180:
            raise ValueError("Longitude must be between -180 and 180 degrees.")
            
        # Approximate 1 degree as 111 km at the equator
        radius_deg = radius_km / 111.0
        # Adjust for longitude compression at higher latitudes
        lon_radius = radius_deg / max(0.1, np.cos(np.radians(abs(lat))))
        
        # Create a bounding box around the coordinates
        bbox = (lon - lon_radius, lat - radius_deg, lon + lon_radius, lat + radius_deg)
        
        # Create metadata
        metadata = {
            "center": (lat, lon),
            "radius_km": radius_km,
            "bbox": bbox,
            "cultural_theme": cultural_theme,
            "style": style,
        }
        
        # Determine the cultural style based on the location
        # This is a very simplified approach
        if lon > -30 and lon < 60:
            cultural_style = "eurasian"
        elif lon > 60 and lon < 150:
            cultural_style = "east_asian"
        elif lon > -120 and lon < -30:
            cultural_style = "americas"
        else:
            cultural_style = "oceanic"
            
        metadata["cultural_style"] = cultural_style
        
        # Generate some simulated cultural data
        # In a real implementation, this would fetch actual data for the region
        import random
        random.seed(int(lat * 100 + lon))  # Make it deterministic for the location
        
        cultural_data = []
        if cultural_theme == "historical":
            # Generate some historical sites
            num_sites = random.randint(3, 7)
            periods = ["Ancient", "Medieval", "Renaissance", "Modern", "Contemporary"]
            significance = ["Settlement", "Temple", "Monument", "Ruins", "Cultural center"]
            
            for i in range(num_sites):
                # Generate a location within the radius
                site_lat = lat + random.uniform(-radius_deg * 0.8, radius_deg * 0.8)
                site_lon = lon + random.uniform(-lon_radius * 0.8, lon_radius * 0.8)
                
                site_data = {
                    "name": f"Historical Site {i+1}",
                    "location": (site_lon, site_lat),
                    "period": random.choice(periods),
                    "significance": random.choice(significance),
                }
                cultural_data.append(site_data)
                
        elif cultural_theme == "linguistic":
            # Generate some linguistic data
            num_languages = random.randint(2, 5)
            families = ["Indo-European", "Sino-Tibetan", "Afro-Asiatic", "Austronesian"]
            scripts = ["Latin", "Cyrillic", "Arabic", "Devanagari", "Chinese"]
            
            for i in range(num_languages):
                # Generate a location within the radius
                lang_lat = lat + random.uniform(-radius_deg * 0.8, radius_deg * 0.8)
                lang_lon = lon + random.uniform(-lon_radius * 0.8, lon_radius * 0.8)
                
                lang_data = {
                    "name": f"Language {i+1}",
                    "location": (lang_lon, lang_lat),
                    "family": random.choice(families),
                    "script": random.choice(scripts),
                }
                cultural_data.append(lang_data)
                
        metadata["cultural_data"] = cultural_data
        
        # Create a simple GeoDataFrame for the region
        import shapely.geometry as geometry
        
        # Create a bounding box polygon
        min_lon, min_lat, max_lon, max_lat = bbox
        bbox_polygon = geometry.box(min_lon, min_lat, max_lon, max_lat)
        
        # Create a GeoDataFrame with the region
        data = gpd.GeoDataFrame(
            {
                "name": [f"Region around {lat:.4f}, {lon:.4f}"],
                "geometry": [bbox_polygon],
                "cultural_style": [cultural_style],
            },
            crs="EPSG:4326",
        )
        
        # Create the CulturalMap object
        cultural_map = cls(data=data, metadata=metadata)
        
        # Generate the map
        cultural_map._generate_map()
        
        return cultural_map
    
    def _generate_map(self) -> None:
        """
        Generate the cultural map based on the data and metadata.
        """
        if self.data is None:
            raise ValueError("Geospatial data is required to generate a map.")
            
        # Get map style
        style = self.metadata.get("style", "artistic")
        cultural_style = self.metadata.get("cultural_style", "default")
        
        # Generate the base map
        geo_art = GeoArt(data=self.data)
        
        # Select color palette based on cultural style
        if cultural_style == "classical":
            color_palette = "earth"
        elif cultural_style == "east_asian":
            color_palette = "ocean"
        elif cultural_style == "indigenous":
            color_palette = "forest"
        elif cultural_style == "eurasian":
            color_palette = "autumn"
        elif cultural_style == "oceanic":
            color_palette = "sunset"
        else:
            color_palette = "pastel"
            
        # Apply style to the map
        geo_art.apply_style(style="default", color_palette=color_palette)
        
        # Convert to image
        if geo_art._figure is not None:
            # Save figure to a buffer and load as image
            import io
            buf = io.BytesIO()
            geo_art._figure.savefig(buf, format='png', dpi=300, bbox_inches='tight')
            buf.seek(0)
            base_img = Image.open(buf)
            
            # Add cultural elements as overlays
            self._add_cultural_overlays(base_img)
            
            # Store the image
            self.image = np.array(base_img)
        else:
            raise ValueError("Failed to generate the base map.")
            
    def _add_cultural_overlays(self, base_img: Image.Image) -> None:
        """
        Add cultural elements as overlays on the base map.
        
        Args:
            base_img: The base map image to overlay elements on
        """
        # Get cultural data
        cultural_data = self.metadata.get("cultural_data", [])
        cultural_theme = self.metadata.get("cultural_theme", "historical")
        bbox = self.metadata.get("bbox")
        
        if not cultural_data or not bbox:
            return
            
        # Get image dimensions
        width, height = base_img.size
        
        # Calculate coordinate transformation function
        min_lon, min_lat, max_lon, max_lat = bbox
        lon_range = max_lon - min_lon
        lat_range = max_lat - min_lat
        
        def coord_to_pixel(lon, lat):
            """Convert geographic coordinates to pixel coordinates."""
            x = int((lon - min_lon) / lon_range * width)
            # Flip y-axis (latitude increases northward, but pixel coordinates increase downward)
            y = int(height - (lat - min_lat) / lat_range * height)
            return x, y
            
        # Create a drawing context
        draw = ImageDraw.Draw(base_img)
        
        # Try to get a font
        try:
            # Try to load a nice font
            font = ImageFont.truetype("Arial", 16)
            small_font = ImageFont.truetype("Arial", 12)
        except IOError:
            # Fallback to default font
            font = ImageFont.load_default()
            small_font = ImageFont.load_default()
            
        # Add cultural elements based on the theme
        if cultural_theme == "historical":
            # Add historical sites with period information
            for site in cultural_data:
                name = site.get("name", "Unknown")
                location = site.get("location")
                period = site.get("period", "Unknown period")
                significance = site.get("significance", "")
                
                if not location:
                    continue
                    
                # Convert coordinates to pixels
                lon, lat = location
                x, y = coord_to_pixel(lon, lat)
                
                # Draw a marker
                marker_radius = 5
                draw.ellipse(
                    (x-marker_radius, y-marker_radius, x+marker_radius, y+marker_radius),
                    fill=(200, 0, 0, 200),
                    outline=(0, 0, 0, 255),
                )
                
                # Draw site name and period
                text = f"{name}\n{period}"
                
                # Calculate text background
                text_width, text_height = draw.textsize(text, font=font)
                text_bg = (
                    x + marker_radius + 5,
                    y - text_height // 2,
                    x + marker_radius + 5 + text_width,
                    y - text_height // 2 + text_height,
                )
                
                # Draw text background
                draw.rectangle(
                    text_bg,
                    fill=(255, 255, 255, 180),
                    outline=(0, 0, 0, 255),
                )
                
                # Draw text
                draw.text(
                    (x + marker_radius + 5, y - text_height // 2),
                    text,
                    fill=(0, 0, 0, 255),
                    font=font,
                )
                
        elif cultural_theme == "linguistic":
            # Add linguistic data with language family information
            for lang in cultural_data:
                name = lang.get("name", "Unknown")
                location = lang.get("location")
                family = lang.get("family", "Unknown family")
                script = lang.get("script", "Unknown script")
                
                if not location:
                    continue
                    
                # Convert coordinates to pixels
                lon, lat = location
                x, y = coord_to_pixel(lon, lat)
                
                # Draw a marker
                marker_radius = 5
                draw.ellipse(
                    (x-marker_radius, y-marker_radius, x+marker_radius, y+marker_radius),
                    fill=(0, 100, 200, 200),
                    outline=(0, 0, 0, 255),
                )
                
                # Draw language name and family
                text = f"{name}\n{family} ({script})"
                
                # Calculate text background
                text_width, text_height = draw.textsize(text, font=font)
                text_bg = (
                    x + marker_radius + 5,
                    y - text_height // 2,
                    x + marker_radius + 5 + text_width,
                    y - text_height // 2 + text_height,
                )
                
                # Draw text background
                draw.rectangle(
                    text_bg,
                    fill=(255, 255, 255, 180),
                    outline=(0, 0, 0, 255),
                )
                
                # Draw text
                draw.text(
                    (x + marker_radius + 5, y - text_height // 2),
                    text,
                    fill=(0, 0, 0, 255),
                    font=font,
                )
                
        # Add a legend
        legend_text = f"Cultural Theme: {cultural_theme.capitalize()}"
        legend_width, legend_height = draw.textsize(legend_text, font=font)
        
        # Draw legend background
        legend_bg = (
            10,
            10,
            10 + legend_width + 10,
            10 + legend_height + 10,
        )
        
        draw.rectangle(
            legend_bg,
            fill=(255, 255, 255, 200),
            outline=(0, 0, 0, 255),
        )
        
        # Draw legend text
        draw.text(
            (15, 15),
            legend_text,
            fill=(0, 0, 0, 255),
            font=font,
        )
    
    def add_narrative(self, narrative: str, position: str = "bottom") -> 'CulturalMap':
        """
        Add a cultural narrative as text on the map.
        
        Args:
            narrative: Cultural narrative or story to add
            position: Position of the narrative ("top", "bottom", "left", "right")
            
        Returns:
            Self for method chaining
            
        Raises:
            ValueError: If the map has not been generated
        """
        if self.image is None:
            raise ValueError("Map must be generated before adding a narrative.")
            
        # Create a PIL image from the numpy array
        img = Image.fromarray(self.image)
        width, height = img.size
        
        # Create a drawing context
        draw = ImageDraw.Draw(img)
        
        # Try to get a font
        try:
            # Try to load a nice font
            font = ImageFont.truetype("Arial", 14)
        except IOError:
            # Fallback to default font
            font = ImageFont.load_default()
            
        # Format the narrative with wrapping
        max_width = width - 40  # Padding on both sides
        
        # Simple text wrapping
        words = narrative.split()
        lines = []
        current_line = []
        
        for word in words:
            # Check if adding this word exceeds the max width
            test_line = ' '.join(current_line + [word])
            test_width, _ = draw.textsize(test_line, font=font)
            
            if test_width <= max_width:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
                
        # Add the last line
        if current_line:
            lines.append(' '.join(current_line))
            
        wrapped_text = '\n'.join(lines)
        
        # Calculate text size
        text_width, text_height = draw.textsize(wrapped_text, font=font)
        
        # Determine position
        if position == "bottom":
            text_position = ((width - text_width) // 2, height - text_height - 20)
        elif position == "top":
            text_position = ((width - text_width) // 2, 20)
        elif position == "left":
            text_position = (20, (height - text_height) // 2)
        elif position == "right":
            text_position = (width - text_width - 20, (height - text_height) // 2)
        else:
            text_position = ((width - text_width) // 2, height - text_height - 20)
            
        # Create semi-transparent background for text
        bg_padding = 10
        bg_bounds = (
            text_position[0] - bg_padding,
            text_position[1] - bg_padding,
            text_position[0] + text_width + bg_padding,
            text_position[1] + text_height + bg_padding,
        )
        
        # Draw background
        draw.rectangle(bg_bounds, fill=(255, 255, 255, 200), outline=(0, 0, 0, 255))
        
        # Draw text
        draw.text(text_position, wrapped_text, fill=(0, 0, 0, 255), font=font)
        
        # Update the image
        self.image = np.array(img)
        
        return self
    
    def apply_cultural_style(self, style: str = "artistic") -> 'CulturalMap':
        """
        Apply a cultural artistic style to the map.
        
        Args:
            style: Name of the style to apply ("artistic", "historical", etc.)
            
        Returns:
            Self for method chaining
            
        Raises:
            ValueError: If the map has not been generated
            ImportError: If required dependencies are not available
        """
        if self.image is None:
            raise ValueError("Map must be generated before applying a cultural style.")
            
        # Convert numpy array to PIL Image
        img = Image.fromarray(self.image)
        
        # Get the cultural style
        cultural_style = self.metadata.get("cultural_style", "default")
        
        try:
            # Apply style transfer with a style appropriate for the cultural region
            from geo_infer_art.core.aesthetics import StyleTransfer
            
            # Map cultural styles to predefined style transfer styles
            style_mapping = {
                "classical": "watercolor",
                "east_asian": "ukiyo_e",
                "indigenous": "abstract",
                "eurasian": "impressionist",
                "oceanic": "oil_painting",
                "default": "watercolor",
            }
            
            transfer_style = style_mapping.get(cultural_style, "watercolor")
            
            # Apply style transfer
            styled_img = StyleTransfer.apply(
                geo_data=None,  # We're using our existing image
                style=transfer_style,
                content_image=img,
                style_weight=1e-2,
                content_weight=1e4,
                iterations=50,  # Reduced for speed
            )
            
            # Update the image
            self.image = np.array(styled_img)
            
        except ImportError:
            # If StyleTransfer is not available, apply a simpler filter
            import matplotlib.pyplot as plt
            from matplotlib.colors import LinearSegmentedColormap
            
            # Create a simplified artistic effect
            img_array = np.array(img)
            
            # Apply a color shift based on cultural style
            if cultural_style == "classical":
                # Warm sepia tone
                r, g, b = img_array[:, :, 0], img_array[:, :, 1], img_array[:, :, 2]
                sepia_r = (r * 0.393 + g * 0.769 + b * 0.189).clip(0, 255).astype(np.uint8)
                sepia_g = (r * 0.349 + g * 0.686 + b * 0.168).clip(0, 255).astype(np.uint8)
                sepia_b = (r * 0.272 + g * 0.534 + b * 0.131).clip(0, 255).astype(np.uint8)
                img_array = np.stack([sepia_r, sepia_g, sepia_b], axis=2)
                
            elif cultural_style == "east_asian":
                # Cool blue tone
                r, g, b = img_array[:, :, 0], img_array[:, :, 1], img_array[:, :, 2]
                blue_r = (r * 0.8).clip(0, 255).astype(np.uint8)
                blue_g = (g * 0.9).clip(0, 255).astype(np.uint8)
                blue_b = (b * 1.2).clip(0, 255).astype(np.uint8)
                img_array = np.stack([blue_r, blue_g, blue_b], axis=2)
                
            self.image = img_array
            
        return self
        
    def save(self, output_path: str) -> str:
        """
        Save the generated cultural map to a file.
        
        Args:
            output_path: Path where the file should be saved
            
        Returns:
            The path to the saved file
            
        Raises:
            ValueError: If no map has been generated
        """
        if self.image is None:
            raise ValueError("No map generated to save.")
            
        directory = os.path.dirname(output_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
            
        # Convert numpy array to PIL Image and save
        img = Image.fromarray(self.image)
        img.save(output_path)
        
        return output_path
        
    def show(self) -> None:
        """
        Display the generated cultural map.
        
        Raises:
            ValueError: If no map has been generated
        """
        if self.image is None:
            raise ValueError("No map generated to display.")
            
        # Create a new figure
        plt.figure(figsize=(10, 10))
        plt.imshow(self.image)
        plt.axis('off')
        plt.tight_layout()
        plt.show()
        
    def __repr__(self) -> str:
        """Return a string representation of the CulturalMap object."""
        region_name = self.metadata.get("region_name", "Unknown Region")
        cultural_theme = self.metadata.get("cultural_theme", "unknown")
        
        return f"CulturalMap(region='{region_name}', theme='{cultural_theme}')" 